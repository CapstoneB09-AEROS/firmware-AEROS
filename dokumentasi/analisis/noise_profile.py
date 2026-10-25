"""Profil noise tegangan MiCS dan CO2 dari satu sesi log serial.

Cara pakai (Python 3 saja, tanpa library tambahan):
    python3 noise_profile.py <file_log> [detik_awal_dibuang]
Contoh:
    python3 noise_profile.py ../../logs/device-monitor-261025-115335.log 300

Input : log berformat CSV firmware, boleh berawalan jam ("HH:MM:SS.mmm > ...").
        Hanya segmen terpanjang tanpa celah waktu setelah masa awal yang dipakai.
Isi   : (1) noise per blok 15 menit, (2) apakah goyangan bertambah besar bersama sinyal (multiplikatif)
        atau tetap (aditif), (3) goyangan bergantian tiap detik: amplitudo dan perkiraan periode sumbernya,
        (4) bentuk sebaran noise, (5) noise CO2.
Batas : kamar yang diam, satu sesi. Penyebab goyangan tidak dibuktikan oleh skrip ini.
"""
import sys, re, math, statistics as st

LOG = sys.argv[1]
SKIP = int(sys.argv[2]) if len(sys.argv) > 2 else 300
VCC, RL = 4.64, 9970.0
CLOCK = re.compile(r'^(\d\d:\d\d:\d\d(?:\.\d+)?)\s*>\s*')

rows = []
for l in open(LOG, encoding='utf-8', errors='replace'):
    l = l.rstrip('\n')
    m = CLOCK.match(l)
    clock = m.group(1) if m else ''
    if m:
        l = l[m.end():]
    p = l.split(',')
    if len(p) == 8 and p[0].isdigit():
        try:
            rows.append(dict(clock=clock, t=int(p[0]), v=float(p[1]),
                             co2=None if p[5] == 'n/a' else int(p[5]), stco=p[6]))
        except ValueError:
            pass

# sesi terakhir, lalu segmen terpanjang tanpa celah setelah masa awal
start = 0
for i in range(1, len(rows)):
    if rows[i]['t'] < rows[i - 1]['t']:
        start = i
rows = [r for r in rows[start:] if r['t'] >= SKIP]
segs, cur = [], [rows[0]]
for r in rows[1:]:
    if r['t'] == cur[-1]['t'] + 1:
        cur.append(r)
    else:
        segs.append(cur)
        cur = [r]
segs.append(cur)
seg = max(segs, key=len)
print(f"Segmen terpanjang tanpa celah: {len(seg)} detik, t_s {seg[0]['t']} -> {seg[-1]['t']}")
if seg[0]['clock']:
    print(f"Jam: {seg[0]['clock']} -> {seg[-1]['clock']}")
print(f"Jumlah segmen: {len(segs)} (celah di antaranya diabaikan)")

v = [r['v'] for r in seg]                        # mV, rata-rata 16 sampel per detik di firmware
ok = [0.5 < x < 1000 * (VCC - 0.001) for x in v]
n = len(v)


def movavg(x, half):
    out = []
    for i in range(len(x)):
        w = x[max(0, i - half): i + half + 1]
        out.append(sum(w) / len(w))
    return out


trend = movavg(v, 15)                            # tren lokal 31 detik
res = [a - b for a, b in zip(v, trend)]          # mV
rs = [RL * (VCC - x / 1000.0) / (x / 1000.0) for x in v]
rtrend = movavg(rs, 15)
rrel = [(a - b) / b * 100 for a, b in zip(rs, rtrend)]   # persen


def lag1(x):
    m = st.mean(x)
    num = sum((x[i] - m) * (x[i + 1] - m) for i in range(len(x) - 1))
    den = sum((a - m) ** 2 for a in x)
    return num / den


print("\n(1) Noise per blok 15 menit (semua segmen tanpa celah yang cukup panjang)")
print("jam       V rata2  noise V   noise Rs  goyang   bagian")
print("          (mV)     (mV)      (%)       +-(mV)   bergantian (%)")
blocks = []
for sg in segs:
    if len(sg) < 600:
        continue
    sv_ = [r['v'] for r in sg]
    tr_ = movavg(sv_, 15)
    rs_ = [a - b for a, b in zip(sv_, tr_)]
    rr_ = [RL * (VCC - x / 1000.0) / (x / 1000.0) for x in sv_]
    rt_ = movavg(rr_, 15)
    rl_ = [(a - b) / b * 100 for a, b in zip(rr_, rt_)]
    ev_ = movavg([((-1) ** i) * rs_[i] for i in range(len(sv_))], 30)
    for b in range(0, len(sg), 900):
        e = min(b + 900, len(sg))
        if e - b < 300:
            continue
        vm = st.mean(sv_[b:e])
        sdv = st.pstdev(rs_[b:e])
        sdr = st.pstdev(rl_[b:e])
        alt = st.mean(abs(rs_[i] - rs_[i - 1]) for i in range(max(b, 1), e)) / 2
        share = (st.mean(x * x for x in ev_[b:e]) / (sdv ** 2)) * 100 if sdv else 0
        blocks.append((vm, sdv, alt, sdr))
        clock = sg[b]['clock'][:5] if sg[b]['clock'] else str(sg[b]['t'])
        print(f"{clock:8s} {vm:8.2f} {sdv:8.2f} {sdr:9.2f} {alt:8.2f} {share:12.0f}")


def corr(a, b):
    ma, mb = st.mean(a), st.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den if den else float('nan')


print("\n(2) Aditif atau multiplikatif?")
vm_l = [b[0] for b in blocks]
sv_l = [b[1] for b in blocks]
al_l = [b[2] for b in blocks]
sr_l = [b[3] for b in blocks]
print(f"jumlah blok: {len(blocks)}; rentang V rata2 {min(vm_l):.1f}-{max(vm_l):.1f} mV")
print(f"korelasi antar blok: V rata2 vs noise V = {corr(vm_l, sv_l):+.2f}; V rata2 vs goyangan = {corr(vm_l, al_l):+.2f}; V rata2 vs noise Rs (%) = {corr(vm_l, sr_l):+.2f}")
print("Catatan: V rata2 tinggi berarti Rs rendah. Noise V yang naik bersama V menunjukkan goyangan yang proporsional terhadap sinyal.")
print("Bila noise Rs (%) hampir tetap walau V berubah, goyangan bersifat relatif terhadap Rs.")
print(f"rasio noise V terhadap V rata2 (persen): min {min(a / b * 100 for a, b in zip(sv_l, vm_l)):.1f}, maks {max(a / b * 100 for a, b in zip(sv_l, vm_l)):.1f}")

print("\n(3) Goyangan bergantian tiap detik (0,5 Hz)")
alt_signed = [((-1) ** i) * res[i] for i in range(n)]
env = movavg(alt_signed, 30)                     # amplitudo bertanda, jendela 61 detik
mx = max(abs(a) for a in env)
cross = [i for i in range(1, n) if env[i - 1] * env[i] < 0]
print(f"amplitudo bertanda: maks {mx:.2f} mV, rata-rata mutlak {st.mean(abs(a) for a in env):.2f} mV")
print(f"jumlah titik amplitudo menyentuh nol (gelombang pembeda): {len(cross)}")
if len(cross) >= 3:
    gaps_ = [cross[i + 1] - cross[i] for i in range(len(cross) - 1)]
    half = st.median(gaps_)
    print(f"selang antar titik nol: median {half:.0f} detik (min {min(gaps_)}, maks {max(gaps_)})")
    beat = 2 * half
    delta = 1.0 / beat
    print(f"periode gelombang pembeda sekitar {beat:.0f} detik, selisih frekuensi sekitar {delta * 1000:.2f} mHz")
    print(f"periode sumber gangguan sekitar {1 / (0.5 + delta):.4f} atau {1 / (0.5 - delta):.4f} detik (dua kemungkinan)")
    print("Catatan: perkiraan kasar. Tidak membuktikan sumbernya.")

print("\n(4) Bentuk sebaran noise Rs (persen terhadap tren 31 detik)")
m = st.mean(rrel)
sd = st.pstdev(rrel)
skew = sum(((x - m) / sd) ** 3 for x in rrel) / n
kurt = sum(((x - m) / sd) ** 4 for x in rrel) / n - 3
print(f"simpangan baku {sd:.2f}%, kemiringan {skew:+.2f}, kurtosis lebih {kurt:+.2f} (0 untuk sebaran normal)")
pct = sorted(abs(x) for x in rrel)
print(f"persentil 50/90/99 dari |noise|: {pct[n // 2]:.2f}% / {pct[int(.9 * n)]:.2f}% / {pct[int(.99 * n)]:.2f}%")

print("\n(5) Noise CO2")
c = [r['co2'] for r in seg]
if all(x is not None for x in c):
    ct = movavg(c, 15)
    cres = [a - b for a, b in zip(c, ct)]
    d = [c[i] - c[i - 1] for i in range(1, n)]
    print(f"simpangan baku di sekitar tren 31 detik: {st.pstdev(cres):.2f} ppm; perubahan terbesar per detik: {max(abs(x) for x in d)} ppm")
    print(f"detik tanpa perubahan nilai: {sum(1 for x in d if x == 0) / len(d) * 100:.0f}%")
else:
    print("ada bacaan CO2 n/a pada segmen ini")


# ---------------------------------------------------------------------------
# (6) Filter jumlah genap vs ganjil terhadap goyangan bergantian
def sma(s, k):
    out = []
    for i in range(len(s)):
        w = s[max(0, i - k + 1): i + 1]
        out.append(sum(w) / len(w))
    return out


def ema(s, a):
    e, out = s[0], []
    for x in s:
        e += a * (x - e)
        out.append(e)
    return out


FILT = [('Mentah', lambda s: s[:]), ('SMA 2', lambda s: sma(s, 2)), ('SMA 3', lambda s: sma(s, 3)),
        ('SMA 4', lambda s: sma(s, 4)), ('SMA 5', lambda s: sma(s, 5)), ('SMA 6', lambda s: sma(s, 6)),
        ('SMA 8', lambda s: sma(s, 8)), ('SMA 10', lambda s: sma(s, 10)),
        ('EMA 0.2', lambda s: ema(s, 0.2)), ('EMA 0.1', lambda s: ema(s, 0.1))]
acc = {k: [] for k, _ in FILT}
for sg in segs:
    if len(sg) < 900:
        continue
    sv_ = [r['v'] for r in sg]
    rr_ = [RL * (VCC - x / 1000.0) / (x / 1000.0) for x in sv_]
    tr_ = movavg(rr_, 60)                         # tren lokal 121 detik
    for k, fn in FILT:
        f_, ft_ = fn(rr_), fn(tr_)
        for i in range(70, len(rr_) - 60):
            acc[k].append((f_[i] - ft_[i]) / tr_[i] * 100)
print("\n(6) Filter genap vs ganjil (noise Rs terhadap tren 121 detik, keterlambatan filter dikoreksi)")
base = st.pstdev(acc['Mentah'])
print(f"{'Filter':9s} {'noise Rs (%)':>13s} {'turun':>7s}")
for k, _ in FILT:
    sd = st.pstdev(acc[k])
    print(f"{k:9s} {sd:13.2f} {100 * (1 - sd / base):6.0f}%")
print(f"detik dianalisis: {len(acc['Mentah'])}")
print("Catatan: bila SMA 2 sudah sama baiknya dengan SMA 10, sisa noise adalah gerakan lambat (puluhan detik ke atas) yang tidak bisa dibuang filter pendek tanpa keterlambatan.")
