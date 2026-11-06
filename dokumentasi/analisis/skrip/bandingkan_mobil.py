"""Membandingkan 5 uji mobil terakhir (4 penumpang) dengan satu cara hitung yang sama, hanya dari kolom log yang ada di semua versi firmware:
t_s, V_mV, Rs_kohm, Rs/R0, CO_ppm_est, CO2_ppm.  Siklus ditentukan dari deret CO2 (bukan dari event firmware), jadi firmware v0, v2.x sama-sama terbaca.

Jalankan : python3 -I bandingkan_mobil.py > ../hasil/hasil-bandingkan-mobil-2026-11-04.txt
Data     : ../data/uji-mobil-5-terakhir/<folder uji>/*.log (salinan dari ../../../logs/)
Catatan  : bacaan CO2 = 500 (pemanasan setelah alat nyala ulang) dibuang. Jendela dibuka dan ditutup MANUAL oleh penguji, jam bukaan tidak tercatat di log, jadi siklus dibaca dari bentuk kurva CO2.
"""
import glob, os, re, sys
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'uji-mobil-5-terakhir')
CEXT = 420.0   # ppm, CO2 luar (asumsi 400-450, sama dengan analisis_n.py)

# (folder, nama, jam mulai dipakai [detik dalam hari], keterangan). Avanza 26 Okt: penumpang ke-4 naik 19:53 (laporan uji 4).
UJI = [
    ('1-avanza-2026-10-26', 'Avanza 26 Okt (v0)',   19 * 3600 + 59 * 60,      'firmware v0, 4 orang (dipakai mulai 19:59, saat CO2 dasar setelah jendela ditutup)'),
    ('2-civic-2026-10-30',  'Civic 30 Okt (v2)',    18 * 3600 + 34 * 60,      'firmware v2.0, 4 orang'),
    ('3-ayla-2026-11-04',   'Ayla 4 Nov (v2.4)',    14 * 3600 + 52 * 60,      'firmware v2.4, 4 orang'),
    ('4-avanza-2026-11-04', 'Avanza 4 Nov (v2.4)',  18 * 3600 + 39 * 60,      'firmware v2.4, 4 orang'),
    ('5-civic-2026-11-04',  'Civic 4 Nov (v2.4)',   20 * 3600 + 8 * 60,       'firmware v2.4, 4 orang'),
]

BARIS = re.compile(r'(\d\d):(\d\d):(\d\d)\.\d+ > (\d+),([\d.]+|n/a),([\d.]+|n/a),([\d.]+|n/a),(\d+),(\d+),')

def baca(folder, mulai):
    t, v, rs, rasio, co, co2 = [], [], [], [], [], []
    for f in sorted(glob.glob(os.path.join(DATA, folder, '*.log'))):
        for l in open(f, encoding='utf-8', errors='replace').read().replace('\x00', '').split('\n'):
            m = BARIS.match(l)
            if not m: continue
            d = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            if d < mulai: continue
            c2 = int(m.group(9))
            if c2 <= 0 or c2 > 9000 or c2 == 500: continue   # 500 = nilai pengisi MH-Z19C saat pemanasan setelah alat nyala
            a, b = m.group(6), m.group(7)
            t.append(d); v.append(float(m.group(5)) if m.group(5) != 'n/a' else np.nan)
            rs.append(float(a) if a != 'n/a' else np.nan); rasio.append(float(b) if b != 'n/a' else np.nan)
            co.append(int(m.group(8))); co2.append(c2)
    o = np.argsort(t, kind='stable')
    return [np.array(x, float)[o] for x in (t, v, rs, rasio, co, co2)]

def hms(x): return '%02d:%02d' % (x // 3600, x % 3600 // 60)

def halus(c, k=15):
    return np.convolve(np.pad(c, (k // 2, k // 2), mode='edge'), np.ones(k) / k, mode='valid')

def zigzag(t, c, ambang):
    """Titik balik bergantian (min, maks, ...) bila ayunan >= ambang ppm pada deret yang dihaluskan."""
    s = halus(c); pts = []; mode = None; hi = lo = 0
    for i in range(1, len(s)):
        if mode is None:
            if s[i] > s[hi]: hi = i
            if s[i] < s[lo]: lo = i
            if s[i] - s[lo] >= ambang: pts.append((lo, 'min')); mode = 'naik'; hi = i
            elif s[hi] - s[i] >= ambang: pts.append((hi, 'maks')); mode = 'turun'; lo = i
        elif mode == 'naik':
            if s[i] > s[hi]: hi = i
            elif s[hi] - s[i] >= ambang: pts.append((hi, 'maks')); mode = 'turun'; lo = i
        else:
            if s[i] < s[lo]: lo = i
            elif s[i] - s[lo] >= ambang: pts.append((lo, 'min')); mode = 'naik'; hi = i
    return s, pts

def kemiringan(t, c):
    if len(t) < 10: return None
    return np.polyfit(t - t[0], c, 1)[0] * 60

def ringkas(nama, ket, mulai, folder):
    t, v, rs, rasio, co, co2 = baca(folder, mulai)
    print('=' * 100); print(nama, '|', ket)
    dur = (t[-1] - t[0]) / 60
    celah = np.where(np.diff(t) > 20)[0]
    print('bacaan %d | %s sampai %s (%.0f menit) | celah > 20 detik: %d %s' % (len(t), hms(t[0]), hms(t[-1]), dur, len(celah),
          ['%s-%s' % (hms(t[i]), hms(t[i + 1])) for i in celah]))
    print('CO2: min %d | median %d | maks %d | %% waktu >= 2500: %.0f | >= 4000: %.0f' % (co2.min(), np.median(co2), co2.max(), 100 * np.mean(co2 >= 2500), 100 * np.mean(co2 >= 4000)))
    ok = ~np.isnan(rs)
    r0 = np.nanmedian(rs[ok] / rasio[ok]) if ok.any() else float('nan')
    print('Rs MiCS: median %.0f kOhm | persentil 5-95: %.0f-%.0f | Rs/R0 median %.2f (R0 terbaca %.0f kOhm) | korelasi Rs dan CO2 %.2f' % (
        np.nanmedian(rs), np.nanpercentile(rs, 5), np.nanpercentile(rs, 95), np.nanmedian(rasio), r0, np.corrcoef(rs[ok], co2[ok])[0, 1]))
    print('CO estimasi (ppm): median %.0f | persentil 95 %.0f | maks %.0f | %% waktu >= 10: %.0f | >= 35: %.0f | >= 87: %.0f' % (
        np.median(co), np.percentile(co, 95), co.max(), 100 * np.mean(co >= 10), 100 * np.mean(co >= 35), 100 * np.mean(co >= 87)))

    s, pts = zigzag(t, co2, 600)
    print('titik balik CO2 (ayunan >= 600 ppm):', ' '.join('%s %s %d' % (hms(t[i]), j, s[i]) for i, j in pts))
    naik, turun, semua_pt = [], [], []
    rentang = [(i, k) for (i, j), (k, l) in zip(pts, pts[1:]) if j == 'min' and l == 'maks']
    if pts and pts[-1][1] == 'min': rentang.append((pts[-1][0], len(t) - 1))   # naik terus sampai data habis (tanpa buka jendela)
    for (i, j), (k, l) in zip(pts, pts[1:]):
        if j == 'min' and l == 'maks':
            seg_t, seg_c = t[i:k + 1], co2[i:k + 1]
            a = (seg_c >= 2000) & (seg_c < 3000); b = (seg_c >= 3000) & (seg_c < 4000)
            naik.append((t[i], s[i], t[k], s[k], kemiringan(seg_t[a], seg_c[a]), a.sum(), kemiringan(seg_t[b], seg_c[b]), b.sum(), (s[k] - s[i]) / (t[k] - t[i]) * 60))
            # titik untuk regresi laju vs C: jendela 60 detik, buang 120 detik pertama (jeda sensor dan pencampuran)
            for q in range(i, k - 60):
                if t[q] - t[i] < 120: continue
                if t[q + 60] - t[q] > 90: continue   # melewati celah (alat mulai ulang)
                sl = (s[q + 60] - s[q]) / (t[q + 60] - t[q]) * 60
                semua_pt.append((s[q] + s[q + 60], sl))
        if j == 'maks' and l == 'min':
            seg_t, seg_c = t[i:k + 1], co2[i:k + 1]
            bawah = np.where(seg_c < 2500)[0]
            t25 = seg_t[bawah[0]] - t[i] if len(bawah) else np.nan
            turun.append((t[i], s[i], t[k], s[k], t25, (t[k] - t[i])))
    pita = {}
    for i, k in rentang:
        for q in range(i, k - 60):
            if t[q] - t[i] < 120 or t[q + 60] - t[q] > 90: continue
            c = (s[q] + s[q + 60]) / 2
            for lo, hi in ((2000, 2500), (2500, 3000), (3000, 3500), (3500, 4000)):
                if lo <= c < hi: pita.setdefault((lo, hi), []).append((s[q + 60] - s[q]) / (t[q + 60] - t[q]) * 60)
    print('laju naik per pita CO2 (median ppm/mnt, jumlah titik): ' + ' | '.join('%d-%d: %.0f (%d)' % (lo, hi, np.median(v), len(v)) for (lo, hi), v in sorted(pita.items())))
    for i, k in rentang:
        a = np.where(s[i:k + 1] >= 2500)[0]; b = np.where(s[i:k + 1] >= 4000)[0]
        if len(a): print('   naik mulai %s: lewat 2500 pukul %s%s' % (hms(t[i]), hms(t[i + a[0]]), (', lewat 4000 pukul %s, selisih %.1f menit' % (hms(t[i + b[0]]), (t[i + b[0]] - t[i + a[0]]) / 60)) if len(b) else ', TIDAK mencapai 4000 sampai data habis (CO2 terakhir %d)' % s[k]))
    print('-- siklus NAIK (min -> maks):  mulai | CO2 awal | selesai | CO2 akhir | laju 2000-3000 (dtk) | laju 3000-4000 (dtk) | rata-rata ppm/mnt')
    for n in naik:
        f = lambda x, d: ('%.0f (%d dtk)' % (x, d)) if x is not None else '-'
        print('   %s | %d | %s | %d | %s | %s | %.0f' % (hms(n[0]), n[1], hms(n[2]), n[3], f(n[4], n[5]), f(n[6], n[7]), n[8]))
    print('-- siklus TURUN (maks -> min): puncak | CO2 | dasar | CO2 dasar | detik puncak -> < 2500 | detik puncak -> dasar')
    for d in turun:
        print('   %s | %d | %s | %d | %s | %.0f' % (hms(d[0]), d[1], hms(d[2]), d[3], '%.0f' % d[4] if not np.isnan(d[4]) else 'tidak tercapai', d[5]))
    if len(semua_pt) > 50:
        x = np.array([p[0] / 2 for p in semua_pt]); y = np.array([p[1] for p in semua_pt])
        b, a = np.polyfit(x - CEXT, y, 1)          # laju(ppm/mnt) = a + b (C - CEXT)
        r = np.corrcoef(x - CEXT, y)[0, 1]
        print('regresi laju naik vs CO2 (%d titik, jeda sensor 120 dtk dibuang): P = %.0f ppm/mnt pada CO2 luar, N = %.1f per jam (kasar), r = %.2f' % (len(x), a, -b * 60, r))
    else:
        print('regresi laju naik vs CO2: data naik terlalu sedikit')
    return dict(nama=nama, naik=naik, turun=turun)

if __name__ == '__main__':
    for folder, nama, mulai, ket in UJI:
        ringkas(nama, ket, mulai, folder)
