"""Analisis log uji mobil: noise, filter, dan perilaku CO (MiCS) serta CO2 (MH-Z19C).

Cara pakai (Python 3 saja, tanpa library tambahan):
    python3 analisis_mobil.py <file_log> [detik_awal_dibuang]
Contoh:
    python3 analisis_mobil.py ../../logs/device-monitor-261025-214144.log 120

Beda dengan noise_profile.py: toleran terhadap loncatan t_s 1 detik (itu hanya pembulatan millis()/1000,
bukan data hilang), jadi cocok untuk sesi pendek di mobil. Waktu dihitung dari jam di log.
Batas: tidak ada gas referensi, jadi ppm CO di sini tetap ESTIMASI. Penyebab perubahan Rs tidak dibuktikan.
"""
import sys, re, math, statistics as st

LOG = sys.argv[1]
SKIP = int(sys.argv[2]) if len(sys.argv) > 2 else 120
VCC, RL, R0 = 4.64, 9970.0, 1730000.0
A, BETA = 3.7, 0.856
PAT = re.compile(r'^(\d\d):(\d\d):(\d\d\.\d+) > (\d+),(-?[\d.]+),([\d.]+),([\d.]+),(\d+),(n/a|\d+),([^,]+),(.+?)\s*$')

rows = []
for l in open(LOG, 'rb').read().decode('latin1').splitlines():
    m = PAT.match(l)
    if m:
        h, mi, s, t, v, rse, ra, pp, co2, sc, s2 = m.groups()
        rows.append(dict(c=int(h) * 3600 + int(mi) * 60 + float(s), t=int(t), v=float(v) / 1000, rse=float(rse) * 1000,
                         ppm=int(pp), co2=None if co2 == 'n/a' else int(co2), sc=sc))
rows = [r for r in rows if r['t'] >= SKIP]
rows = [r for r in rows if 0.0005 < r['v'] < VCC - 0.001]
for r in rows:
    r['rs'] = RL * (VCC - r['v']) / r['v']
x = [r['rs'] for r in rows]
n = len(x)
clk = lambda c: '%02d:%02d:%02d' % (c // 3600, c % 3600 // 60, c % 60)
print(f"Berkas: {LOG.split('/')[-1]}  | {n} detik data | {clk(rows[0]['c'])} -> {clk(rows[-1]['c'])}")


def sma(s, k):
    return [sum(s[max(0, i - k + 1):i + 1]) / len(s[max(0, i - k + 1):i + 1]) for i in range(len(s))]


def ema(s, a):
    o, e = [], s[0]
    for v in s:
        e += a * (v - e)
        o.append(e)
    return o


def ppm_of(rs):
    r = rs / R0
    return 0.0 if r >= 0.5 else (A / r) ** (1 / BETA)


# tren lambat: rata-rata terpusat 61 detik
W = 30
tr = [sum(x[max(0, i - W):i + W + 1]) / len(x[max(0, i - W):i + W + 1]) for i in range(n)]
idx = range(W, n - W)
res = [(x[i] - tr[i]) / tr[i] * 100 for i in idx]
alt = [res[i] * (1 if i % 2 == 0 else -1) for i in range(len(res))]
# komponen bergantian: rata-rata sinyal ber-tanda (-1)^i pada jendela 60 detik
sq = 0.0
for k in range(0, len(res) - 60, 60):
    c = sum(alt[k:k + 60]) / 60
    sq += c * c * 60
share = sq / sum(a * a for a in res) * 100 if res else 0
print("\n(1) Noise Rs mentah (setelah 16 sampel dirata-rata di firmware)")
print(f"    simpangan baku terhadap tren 61 dtk : {st.pstdev(res):.1f}%  (di meja, kamar diam: sekitar 13%)")
print(f"    bagian goyangan bergantian 0,5 Hz   : {share:.0f}%  (di meja sekitar 95%)")

print("\n(2) Filter pada data mobil (sisa goyangan relatif terhadap tren, makin kecil makin halus)")
for name, f in [('Mentah', lambda s: s), ('SMA 6', lambda s: sma(s, 6)), ('SMA 4', lambda s: sma(s, 4)),
                ('SMA 8', lambda s: sma(s, 8)), ('EMA 0.2 (firmware sekarang)', lambda s: ema(s, 0.2)),
                ('EMA 0.1', lambda s: ema(s, 0.1))]:
    y = f(x)
    r = [(y[i] - tr[i]) / tr[i] * 100 for i in idx]
    print(f"    {name:30s} sisa noise {st.pstdev(r):5.2f}%")

print("\n(3) Seberapa mulus ppm CO estimasi (R0 = 1730 kOhm bawaan kode)")
for name, y in [('EMA 0.2 (log)', [r['rse'] for r in rows]), ('SMA 6', sma(x, 6))]:
    p = [ppm_of(a) for a in y]
    flips = sum(1 for i in range(1, n) if (p[i] == 0) != (p[i - 1] == 0))
    print(f"    {name:14s} ppm min {min(p):5.1f} maks {max(p):5.1f} | detik berstatus 0 ppm: {sum(1 for a in p if a == 0)}"
          f" | lompatan 0<->~10: {flips} | detik >= 35 ppm: {sum(1 for a in p if a >= 35)}")
rat = [a / R0 for a in sma(x, 6)]
print(f"    Rs/R0 (SMA 6): min {min(rat):.3f}  maks {max(rat):.3f}  (di kamar bersih rasio sekitar 1,0; batas hitung ppm = 0,5)")

print("\n(4) Pergeseran Rs per menit (SMA 6, kOhm) dan CO2")
b = {}
for i, r in enumerate(rows):
    b.setdefault(int(r['c'] // 60), []).append((sma(x, 6)[i], r['co2']))
prev = None
for k, v in b.items():
    rs = st.mean(a for a, _ in v) / 1000
    c = [q for _, q in v if q is not None]
    d = '' if prev is None else f'{(rs - prev) / prev * 100:+5.0f}%'
    print(f"    {k // 60:02d}:{k % 60:02d} Rs {rs:7.0f}  {d:>6}   CO2 {min(c) if c else '-'}-{max(c) if c else '-'}")
    prev = rs

co = [r['co2'] for r in rows if r['co2'] is not None and r['t'] > 200 and r['co2'] > 600]
if len(co) > 30:
    d = [co[i] - co[i - 1] for i in range(1, len(co))]
    print(f"\n(5) CO2 MH-Z19C: selisih antar detik rata-rata mutlak {st.mean(abs(a) for a in d):.1f} ppm, simpangan {st.pstdev(d):.1f} ppm")

# (6) Siklus lambat Rs (hanya bila log cukup panjang, minimal 40 menit)
if n > 2400:
    nb = n // 30
    xs = [st.mean(x[i * 30:(i + 1) * 30]) for i in range(nb)]
    trb = [st.mean(xs[max(0, i - 40):i + 41]) for i in range(nb)]
    rb = [(xs[i] - trb[i]) / trb[i] for i in range(nb)]
    best = (0, 0)
    for p10 in range(40, 130):                      # periode 4,0 - 12,9 menit
        w = 2 * math.pi / (p10 / 10 * 2)
        a = sum(rb[i] * math.cos(w * i) for i in range(nb))
        b = sum(rb[i] * math.sin(w * i) for i in range(nb))
        amp = 2 * math.hypot(a, b) / nb
        if amp > best[0]:
            best = (amp, p10 / 10)
    print(f"\n(6) Siklus lambat Rs: periode terkuat {best[1]:.1f} menit, amplitudo +-{best[0] * 100:.1f}% dari Rs")
    q = nb // 4
    for k in range(4):
        w = 2 * math.pi / (best[1] * 2)
        a = sum(rb[i] * math.cos(w * i) for i in range(k * q, (k + 1) * q))
        b = sum(rb[i] * math.sin(w * i) for i in range(k * q, (k + 1) * q))
        print(f"    seperempat ke-{k + 1}: +-{2 * math.hypot(a, b) / q * 100:.1f}%")
