"""Analisis log per fase: noise, filter, siklus lambat Rs, dan hubungan siklus dengan goyangan 0,5 Hz.

Cara pakai (Python 3 saja, tanpa library tambahan):
    python3 analisis_fase.py <file_log> [nama=HH:MM-HH:MM ...]
Contoh (uji kamar pagi 26 Okt):
    python3 analisis_fase.py ../../../logs/device-monitor-261026-090343.log \
        P1=09:08-09:45 P2=09:46-10:15 P3=10:16-10:47

Tanpa fase, seluruh log setelah 300 detik pertama dipakai sebagai satu fase.
Per fase: Rs rata-rata, goyangan mentah, bagian bergantian, sisa noise per filter, amplitudo siklus pada periode tetap
7,00 menit (420 detik), dan CO2. Di akhir: periode siklus lambat terkuat untuk seluruh log, jarak balik tanda
goyangan bergantian, dan korelasi keduanya.
Batas: tidak membuktikan sumber. Hubungan siklus lambat dengan goyangan bergantian adalah petunjuk, bukan bukti.
"""
import sys, re, math, statistics as st

LOG = sys.argv[1]
PAT = re.compile(r'^(\d\d):(\d\d):(\d\d\.\d+) > (\d+),(-?[\d.]+),([\d.]+),([\d.]+),(\d+),(n/a|\d+),([^,]+),(.+?)\s*$')
VCC, RL = 4.64, 9970.0
rows = []
for l in open(LOG, 'rb').read().decode('latin1').splitlines():
    m = PAT.match(l)
    if m:
        v = float(m[5]) / 1000
        if 0.0005 < v < VCC - 0.001:
            rows.append(dict(c=int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]), t=int(m[4]), rs=RL * (VCC - v) / v,
                             co2=None if m[9] == 'n/a' or int(m[9]) in (410, 500) else int(m[9])))
clk = lambda c: '%02d:%02d:%02d' % (c // 3600, c % 3600 // 60, c % 60)
hm = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60

phases = []
for a in sys.argv[2:]:
    nm, rg = a.split('=')
    s, e = rg.split('-')
    phases.append((nm, hm(s), hm(e)))
if not phases:
    phases = [('semua', rows[0]['c'] + 300, rows[-1]['c'])]


def sma(s, k):
    return [sum(s[max(0, i - k + 1):i + 1]) / len(s[max(0, i - k + 1):i + 1]) for i in range(len(s))]


def ema(s, a):
    o, e = [], s[0]
    for v in s:
        e += a * (v - e)
        o.append(e)
    return o


def cyc_amp(xb, per_s=420.0, binlen=30):
    """amplitudo (+-%) siklus pada periode tetap, setelah buang tren kuadrat"""
    n = len(xb)
    if n < 8:
        return None
    t = [(i + 0.5) * binlen for i in range(n)]
    # tren: rata-rata terpusat selebar satu periode
    k = int(per_s / binlen)
    tr = [st.mean(xb[max(0, i - k // 2):i + k // 2 + 1]) for i in range(n)]
    r = [(xb[i] - tr[i]) / tr[i] for i in range(n)]
    w = 2 * math.pi / per_s
    a = sum(r[i] * math.cos(w * t[i]) for i in range(n))
    b = sum(r[i] * math.sin(w * t[i]) for i in range(n))
    return 2 * math.hypot(a, b) / n * 100


print(f"Berkas: {LOG.split('/')[-1]} | {len(rows)} detik | {clk(rows[0]['c'])} -> {clk(rows[-1]['c'])}")
print("\nFase        jam              n    Rs rata2  goyang  bergantian | sisa noise: SMA6  EMA0,2 | siklus 7 mnt | CO2")
for nm, a, b in phases:
    seg = [r for r in rows if a <= r['c'] < b]
    if len(seg) < 120:
        print(nm, 'terlalu pendek')
        continue
    x = [r['rs'] for r in seg]
    n = len(x)
    W = 30
    tr = [st.mean(x[max(0, i - W):i + W + 1]) for i in range(n)]
    idx = range(W, n - W)
    res = [(x[i] - tr[i]) / tr[i] * 100 for i in idx]
    alt = [res[i] * (1 if i % 2 == 0 else -1) for i in range(len(res))]
    sq = sum((sum(alt[k:k + 60]) / 60) ** 2 * 60 for k in range(0, len(res) - 60, 60))
    share = sq / sum(v * v for v in res) * 100
    out = {}
    for nmf, f in (('SMA6', lambda s: sma(s, 6)), ('EMA', lambda s: ema(s, 0.2))):
        y = f(x)
        out[nmf] = st.pstdev([(y[i] - tr[i]) / tr[i] * 100 for i in idx])
    nb = n // 30
    xb = [st.mean(x[i * 30:(i + 1) * 30]) for i in range(nb)]
    amp = cyc_amp(xb)
    co = [r['co2'] for r in seg if r['co2'] is not None]
    print(f"{nm:10s} {clk(seg[0]['c'])[:5]}-{clk(seg[-1]['c'])[:5]} {n:6d} {st.mean(x) / 1000:8.0f} {st.pstdev(res):6.1f}% {share:8.0f}%   | {out['SMA6']:8.2f}% {out['EMA']:6.2f}% | "
          f"{'+-%.1f%%' % amp if amp is not None else '-':>9s}   | {min(co) if co else '-'}-{max(co) if co else '-'}")

# seluruh log: periode siklus lambat, jarak balik tanda goyangan bergantian, korelasi
ph = [r for r in rows if r['c'] >= rows[0]['c'] + 300]
x = [r['rs'] for r in ph]
n = len(x)
nb = n // 30
xs = [st.mean(x[i * 30:(i + 1) * 30]) for i in range(nb)]
trb = [st.mean(xs[max(0, i - 40):i + 41]) for i in range(nb)]
rb = [(xs[i] - trb[i]) / trb[i] for i in range(nb)]
best = []
for p in range(400, 1100):
    per = p / 100.0
    w = 2 * math.pi / (per * 2)
    a = sum(rb[i] * math.cos(w * i) for i in range(nb))
    b = sum(rb[i] * math.sin(w * i) for i in range(nb))
    best.append((2 * math.hypot(a, b) / nb, per))
best.sort(reverse=True)
print(f"\nSeluruh log (setelah 300 dtk pertama): periode siklus lambat terkuat {best[0][1]:.2f} menit, amplitudo +-{best[0][0] * 100:.1f}%")
xr = [(x[i] - st.mean(x[max(0, i - 30):i + 31])) / st.mean(x[max(0, i - 30):i + 31]) for i in range(n)]
env = [sum(xr[i] * (1 if i % 2 == 0 else -1) for i in range(k, k + 60)) / 60 for k in range(0, n - 60, 30)]
zc = [k * 30 for k in range(1, len(env)) if env[k - 1] * env[k] < 0]
gaps = [zc[i + 1] - zc[i] for i in range(len(zc) - 1)]
if gaps:
    print(f"Jarak balik tanda goyangan bergantian: median {st.median(gaps):.0f} detik ({len(zc)} kali balik)")
m = min(len(env), len(rb))
e2, sl = [env[k] ** 2 for k in range(m)], rb[:m]
ma, mb = st.mean(sl), st.mean(e2)
c = sum((p - ma) * (q - mb) for p, q in zip(sl, e2)) / math.sqrt(sum((p - ma) ** 2 for p in sl) * sum((q - mb) ** 2 for q in e2))
print(f"Korelasi siklus lambat dengan kuadrat amplitudo goyangan bergantian (lag 0): {c:.2f}")
