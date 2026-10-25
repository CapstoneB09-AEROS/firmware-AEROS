"""Membandingkan filter (SMA, EMA, median) pada Rs mentah MiCS-5524 dari log serial.

Cara pakai (Python 3 saja, tanpa library tambahan):
    python3 filter_compare.py <file_log.csv> [jumlah_baris_terakhir]
Contoh:
    python3 filter_compare.py data-baseline-t3314-4313.csv 1000

Input : baris CSV dari firmware (t_s,V_mV,Rs_kohm,Rs_per_R0,CO_ppm_est,CO2_ppm,status_CO,status_CO2).
        Boleh berawalan jam, seperti hasil "pio device monitor -f time -f log2file"
        (contoh: "11:40:13.564 > 20,50.09,821.0,..."). Baris rusak dilewati.
        Hanya sesi terakhir (t_s naik terus) di file itu yang dipakai. Satu file log = satu sesi.
Proses: Rs mentah dihitung ulang dari V_mV (VCC dan RL di bawah harus sama dengan firmware),
        lalu tiap filter diterapkan dan dinilai (noise, korelasi lag-1, t90 simulasi, lonjakan buatan +30%).
Batas : untuk udara bersih. Uji lonjakan memakai lonjakan buatan dan uji t90 memakai simulasi
        penurunan Rs 50% mendadak, bukan kejadian gas nyata.
"""
import sys, re, math, statistics as st, collections

LOG = sys.argv[1]
N_LAST = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
VCC, RL = 4.64, 9970.0

rows = []
CLOCK = re.compile(r'^(\d\d:\d\d:\d\d(?:\.\d+)?)\s*>\s*')   # awalan jam dari "pio device monitor -f time"
for n, l in enumerate(open(LOG, encoding='utf-8', errors='replace'), 1):
    l = l.rstrip('\n')
    m = CLOCK.match(l)
    clock = m.group(1) if m else ''
    if m:
        l = l[m.end():]
    p = l.split(',')
    if len(p) == 8 and p[0].isdigit():
        try:
            rows.append(dict(line=n, clock=clock, t=int(p[0]), v=float(p[1]), rsema=float(p[2]) if p[2] != 'n/a' else None,
                             ppm=float(p[4]), co2=None if p[5] == 'n/a' else int(p[5]), stco=p[6], stco2=p[7]))
        except ValueError:
            pass

# sesi terakhir (t naik terus)
start = 0
for i in range(1, len(rows)):
    if rows[i]['t'] < rows[i - 1]['t']:
        start = i
rows = rows[start:]
rows = rows[-N_LAST:]
print(f"Baris dipakai: {len(rows)}  t_s {rows[0]['t']} -> {rows[-1]['t']}  (baris file {rows[0]['line']}-{rows[-1]['line']})")
if rows[0]['clock']:
    print(f"Jam: {rows[0]['clock']} -> {rows[-1]['clock']}")
print("Status CO:", dict(collections.Counter(r['stco'] for r in rows)))
gaps = [(rows[i - 1]['t'], rows[i]['t']) for i in range(1, len(rows)) if rows[i]['t'] != rows[i - 1]['t'] + 1]
print("Celah waktu:", gaps if gaps else "tidak ada")

# Rs mentah (per detik, sudah rata-rata 16 sampel di firmware) dari tegangan
x = []
for r in rows:
    v = r['v'] / 1000.0
    ok = 0.0005 < v < VCC - 0.001 and 'SATURASI' not in r['stco'] and 'ERR' not in r['stco']
    x.append(RL * (VCC - v) / v if ok else None)
valid = [a for a in x if a is not None]
print(f"Rs mentah valid: {len(valid)} dari {len(x)}  rentang {min(valid)/1000:.0f}-{max(valid)/1000:.0f} kOhm  rata-rata {st.mean(valid)/1000:.0f} kOhm")
# isi sampel tidak valid dengan nilai valid terakhir supaya filter tetap berjalan
y, last = [], valid[0]
for a in x:
    if a is not None:
        last = a
    y.append(last)


def sma(s, n):
    out = []
    for i in range(len(s)):
        w = s[max(0, i - n + 1): i + 1]
        out.append(sum(w) / len(w))
    return out


def ema(s, a):
    out, e = [], s[0]
    for v in s:
        e = e + a * (v - e)
        out.append(e)
    return out


def med(s, n):
    out = []
    for i in range(len(s)):
        w = sorted(s[max(0, i - n + 1): i + 1])
        out.append(w[len(w) // 2])
    return out


FILTERS = collections.OrderedDict([
    ('Mentah (tanpa filter)', lambda s: s[:]),
    ('SMA 2', lambda s: sma(s, 2)),
    ('SMA 3', lambda s: sma(s, 3)),
    ('SMA 4', lambda s: sma(s, 4)),
    ('SMA 5', lambda s: sma(s, 5)),
    ('SMA 6', lambda s: sma(s, 6)),
    ('SMA 8', lambda s: sma(s, 8)),
    ('SMA 10', lambda s: sma(s, 10)),
    ('SMA 30', lambda s: sma(s, 30)),
    ('EMA 0.05', lambda s: ema(s, 0.05)),
    ('EMA 0.1', lambda s: ema(s, 0.1)),
    ('EMA 0.2 (firmware sekarang)', lambda s: ema(s, 0.2)),
    ('Median 5', lambda s: med(s, 5)),
    ('Median 5 lalu EMA 0.1', lambda s: ema(med(s, 5), 0.1)),
])

# tren lambat: rata-rata bergerak terpusat 121 detik dari sinyal mentah
W = 60
trend = []
for i in range(len(y)):
    w = y[max(0, i - W): i + W + 1]
    trend.append(sum(w) / len(w))
lo, hi = W + 30, len(y) - W  # buang tepi dan masa awal filter
idx = range(lo, hi)


def rel_noise(f, ft):
    res = [(f[i] - ft[i]) / trend[i] * 100 for i in idx]
    return st.pstdev(res)


def lag1(f):
    res = [(f[i] - trend[i]) / trend[i] for i in idx]
    m = st.mean(res)
    num = sum((res[i] - m) * (res[i + 1] - m) for i in range(len(res) - 1))
    den = sum((a - m) ** 2 for a in res)
    return num / den


def step_t90(fn):
    s = [1.0] * 100 + [0.5] * 200          # Rs turun mendadak 50% (gas naik)
    o = fn(s)
    tgt = 1.0 - 0.9 * 0.5
    for k in range(100, 300):
        if o[k] <= tgt:
            return k - 100
    return None


def spike_pass(fn):
    # lonjakan tunggal +30% di data nyata; tinggi sisa lonjakan pada keluaran filter (maks, relatif)
    res = []
    for p in (150, 300, 450, 600, 750):
        if p >= len(y) - 5:
            continue
        s = y[:]
        base = s[p]
        s[p] = base * 1.3
        o = fn(s)
        ref = fn(y)
        res.append(max(abs(o[k] - ref[k]) / ref[k] for k in range(p, min(p + 5, len(y)))) * 100)
    return st.mean(res)


alt = st.mean(abs(y[i] - y[i - 1]) / trend[i] for i in idx) / 2 * 100
print(f"Amplitudo goyangan detik-ke-detik rata-rata: sekitar +-{alt:.1f}% dari Rs")
print()
print(f"{'Filter':32s} {'noise (%)':>10s} {'turun':>7s} {'lag-1':>7s} {'t90 (dtk)':>10s} {'lonjakan +30% tersisa (%)':>27s}")
base_noise = None
for name, fn in FILTERS.items():
    f = fn(y)
    ft = fn(trend)
    nz = rel_noise(f, ft)
    if base_noise is None:
        base_noise = nz
    t90 = step_t90(fn)
    sp = spike_pass(fn)
    print(f"{name:32s} {nz:10.3f} {100 * (1 - nz / base_noise):6.0f}% {lag1(f):7.2f} {str(t90):>10s} {sp:27.1f}")
print()
print("noise (%) = simpangan baku Rs di sekitar tren lambat, relatif terhadap tren")
print("lag-1 negatif besar = goyangan bolak-balik tiap detik")
print("t90 = detik sampai keluaran filter menempuh 90% dari perubahan mendadak")
