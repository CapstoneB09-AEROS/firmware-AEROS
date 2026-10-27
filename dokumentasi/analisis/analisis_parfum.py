"""Analisis uji parfum (ruangan): lonjakan Rs, estimasi ppm, lama di atas ambang, pemulihan, dan respons aturan baru.
Jalankan: python3 -I analisis_parfum.py ../../logs/device-monitor-261027-140826.log
Log berformat 'HH:MM:SS.mmm > t_s,V_mV,Rs,rasio,CO,CO2,status_CO,status_CO2' (ada penanda waktu dari monitor).
Aturan baru yang ditiru: SMA 6 pada Rs, ppm = (3.7/(Rs/R0))^(1/0.856) (0 bila rasio >= 0.5), R0 1730 kOhm,
waspada bila ppm >= 35 selama 30 detik berturut-turut, bahaya bila ppm >= 87.
"""
import re, sys
R0 = 1730.0
def ppm(rs):
    r = rs / R0
    return 0.0 if r >= 0.5 else (3.7 / r) ** (1 / 0.856)
def hms(x): return '%02d:%02d:%02d' % (x // 3600, x % 3600 // 60, x % 60)

rows = []
for l in open(sys.argv[1], encoding='utf-8', errors='replace').read().replace('\x00', '').split('\n'):
    m = re.match(r'(\d\d):(\d\d):(\d\d)\.\d+ > (\d+),([\d.]+),([\d.]+),([\d.]+),(\d+),(\d+),(\S+),(\S+)', l)
    if m:
        h, mi, s = map(int, m.groups()[:3])
        rows.append(dict(t=h * 3600 + mi * 60 + s, rs=float(m.group(6)), co_log=int(m.group(8)),
                         co2=int(m.group(9)), st=m.group(10)))
n = len(rows)
sma = [None if i < 5 else sum(x['rs'] for x in rows[i - 5:i + 1]) / 6 for i in range(n)]
p6 = [None if s is None else ppm(s) for s in sma]
print(f'Baris: {n}, {hms(rows[0]["t"])} sampai {hms(rows[-1]["t"])}')

# lonjakan: Rs turun > 25% (rata-rata 2 detik) dalam 15 detik
pair = [None if i == 0 else (rows[i]['rs'] + rows[i - 1]['rs']) / 2 for i in range(n)]
events, i = [], 20
while i < n - 15:
    ref = sum(pair[i - 10:i]) / 10
    if min(pair[i:i + 15]) < 0.75 * ref:
        j = next(k for k in range(i, i + 15) if pair[k] < 0.75 * ref)
        events.append((j, ref)); i = j + 60
    else:
        i += 1
print(f'Lonjakan terdeteksi: {len(events)}\n')
for k, (j, ref) in enumerate(events, 1):
    seg = range(j, min(n, j + 240))
    mn = min(seg, key=lambda a: rows[a]['rs'])
    print(f'--- Semprotan {k}: mulai sekitar {hms(rows[j]["t"])}, Rs sebelum {ref:.0f} kOhm')
    print(f'  Rs terendah (mentah) {rows[mn]["rs"]:.0f} kOhm pada {hms(rows[mn]["t"])} ({rows[mn]["t"] - rows[j]["t"]} detik setelah mulai), turun {100 * (1 - rows[mn]["rs"] / ref):.0f}%')
    pk_raw = max(ppm(rows[a]['rs']) for a in seg)
    pk6 = max((p6[a] for a in seg if p6[a] is not None), default=0)
    print(f'  Puncak ppm estimasi: mentah {pk_raw:.0f}, SMA 6 {pk6:.0f}, log v0 {max(rows[a]["co_log"] for a in seg)}')
    def run(vals, thr):
        best = cur = 0
        for a in seg:
            v = vals(a)
            cur = cur + 1 if v is not None and v >= thr else 0
            best = max(best, cur)
        return best
    r35 = run(lambda a: p6[a], 35); r87 = run(lambda a: p6[a], 87)
    print(f'  Di atas 35 ppm (SMA 6): paling lama {r35} detik berturut-turut; di atas 87 ppm: {r87} detik')
    print(f'  Waspada di aturan baru (35 ppm selama 30 detik): {"YA" if r35 >= 30 else "TIDAK"}; bahaya (87 ppm): {"YA" if r87 >= 1 else "TIDAK"}')
    al = [a for a in seg if rows[a]['st'].startswith('ALARM')]
    print(f'  Status ALARM firmware lama (v0): {len(al)} detik' + (f' ({hms(rows[al[0]]["t"])}-{hms(rows[al[-1]]["t"])})' if al else ''))
    for target in (0.9, 0.95):
        rec = next((a for a in range(mn, n) if pair[a] and pair[a] >= target * ref), None)
        print(f'  Pulih ke {int(target * 100)}% dari Rs awal: ' + (f'{rows[rec]["t"] - rows[mn]["t"]} detik setelah titik terendah' if rec else 'belum dalam data'))
    print()
print(f'CO2 selama uji: {min(x["co2"] for x in rows)}-{max(x["co2"] for x in rows)} ppm (tidak dipengaruhi parfum; perubahan dari orang dan napas)')
