"""Mengukur laju pertukaran udara N dari log CO2 dengan model yang sama seperti simulasi C-251:
dC/dt = P - N (C - Cext)        (Pers. 4.1a; solusi 4.2 dan 4.4a), P = n*G*1e6/V dalam ppm per jam.
Sensor MH-Z19C lambat (T90 < 120 detik), jadi pembacaan = model yang dilewatkan filter orde-1 dengan tau sekitar 52 detik.

Jalankan: python3 analisis_n.py ../../../logs/device-monitor-261026-193817.log   (Avanza)
          python3 analisis_n.py ../../../logs/device-monitor-261025-220026.log   (Civic: perkiraan kasar per fase)
Hasil   : ../hasil/hasil-n-2026-10-27.txt dan ../hasil/hasil-n-civic-2026-10-27.txt
"""
import re, sys
import numpy as np

TAU = 52.0           # detik, dari T90 < 120 s
CEXT = 420.0         # ppm, CO2 luar (asumsi 400-450)

def baca(path):
    t, c = [], []
    for l in open(path, encoding='utf-8', errors='replace').read().replace('\x00', '').split('\n'):
        m = re.match(r'(\d\d):(\d\d):(\d\d)\.\d+ > (\d+),([\d.]+),([\d.]+),([\d.]+),(\d+),(\d+),', l)
        if m:
            h, mi, s = map(int, m.groups()[:3]); t.append(h * 3600 + mi * 60 + s); c.append(int(m.group(9)))
    return np.array(t), np.array(c, float)

def hms(x): return '%02d:%02d:%02d' % (x // 3600, x % 3600 // 60, x % 60)
def jam(h, m, s=0): return h * 3600 + m * 60 + s

def lag(forcing, y0, dt=1.0):
    y = np.empty_like(forcing); y[0] = y0
    a = dt / TAU
    for k in range(len(forcing) - 1):
        y[k + 1] = y[k] + a * (forcing[k] - y[k])
    return y

def potong(t, c, a, b):
    i = (t >= a) & (t <= b)
    return t[i] - a, c[i]

def fit_tertutup(t, c, a, b):
    """Naik dengan jendela tertutup: C(t) = Css + (C0 - Css) e^{-Nt}; cari N, Css, C0 (kuadrat terkecil, N lewat grid)."""
    tt, y = potong(t, c, a, b)
    best = None
    for N_jam in np.arange(0.2, 40.0, 0.1):
        N = N_jam / 3600.0
        f1 = 1 - np.exp(-N * tt); f2 = np.exp(-N * tt)
        zero = np.zeros_like(y)
        L1 = lag(f1, 0.0); L2 = lag(f2, 0.0)
        hom = y[0] * np.exp(-tt / TAU)
        A = np.vstack([L1, L2]).T
        sol, res, *_ = np.linalg.lstsq(A, y - hom, rcond=None)
        r = np.sum((A @ sol + hom - y) ** 2)
        if best is None or r < best[0]:
            best = (r, N_jam, sol[0], sol[1])
    r, N_jam, Css, C0 = best
    rmse = (r / len(y)) ** 0.5
    P = (Css - CEXT) * N_jam
    return N_jam, Css, C0, P, rmse

def fit_buka(t, c, a_buka, a_tutup, a_akhir, P, N_tertutup):
    """Jendela dibuka dari a_buka sampai a_tutup, lalu tertutup sampai a_akhir. Cari N_buka dan C awal sejati."""
    tt, y = potong(t, c, a_buka, a_akhir)
    n_buka = int(a_tutup - a_buka)
    best = None
    for N_jam in np.arange(5.0, 120.0, 0.5):
        for C0 in np.arange(y[0] - 200, y[0] + 400, 10.0):
            C = np.empty(len(tt)); C[0] = C0
            for k in range(len(tt) - 1):
                Nk = (N_jam if k < n_buka else N_tertutup) / 3600.0
                C[k + 1] = C[k] + (P / 3600.0 - Nk * (C[k] - CEXT))
            yy = lag(C, y[0])
            r = np.sum((yy - y) ** 2)
            if best is None or r < best[0]:
                best = (r, N_jam, C0)
    r, N_jam, C0 = best
    return N_jam, C0, (r / len(y)) ** 0.5

def profil_tertutup(t, c, a, b):
    """RMSE terhadap N, untuk melihat seberapa kuat N tertutup ditentukan (kenaikan hampir lurus, jadi lemah)."""
    tt, y = potong(t, c, a, b)
    out = []
    for N_jam in (0.5, 1, 2, 3, 5, 8, 12):
        N = N_jam / 3600.0
        f1 = 1 - np.exp(-N * tt); f2 = np.exp(-N * tt)
        L1 = lag(f1, 0.0); L2 = lag(f2, 0.0); hom = y[0] * np.exp(-tt / TAU)
        A = np.vstack([L1, L2]).T
        sol, *_ = np.linalg.lstsq(A, y - hom, rcond=None)
        rm = (np.mean((A @ sol + hom - y) ** 2)) ** 0.5
        out.append((N_jam, rm, (sol[0] - CEXT) * N_jam))
    return out

def civic(t, c):
    """Civic: jendela tidak pernah dibuka, jadi hanya perkiraan kasar per fase: N = (P - kemiringan) / (C - Cext).
    P tidak diketahui; dipakai dua nilai: G_eff 10,5 (dari fit Avanza) dan G 19,6 (model C-251), 2 orang, V = 2150 L."""
    print('Mobil Honda Civic EG6, 25 Okt 2026, jendela tertutup, 2 orang (perkiraan kasar; log %s)' % sys.argv[1].split('/')[-1])
    print('Fase awal (22:00-22:03) dibuang: nilai CO2 masih placeholder MH-Z19C setelah menyala.\n')
    for nama, a, b in (('ngebut', jam(22, 4, 30), jam(22, 7, 0)), ('ngebut 60 km/jam + AC', jam(22, 8, 30), jam(22, 13, 30)),
                       ('20-30 km/jam', jam(22, 10, 0), jam(22, 14, 0))):
        i = (t >= a) & (t <= b)
        sl = np.polyfit(t[i], c[i], 1)[0] * 3600
        Cm = c[i].mean()
        out = []
        for G in (10.5, 19.6):
            P = 2 * G * 1e6 / 2150
            out.append('G %.1f: N = %.1f /jam' % (G, (P - sl) / (Cm - CEXT)))
        print('%s (%s-%s): C rata %.0f ppm, kemiringan %+.0f ppm/menit; %s' % (nama, hms(a), hms(b), Cm, sl / 60, ' | '.join(out)))
    print('\nPembanding asumsi simulasi C-251: N tertutup 0,5 (tabel) atau 1-3 (idle); pemulihan 20 km/jam 3,5.')

if __name__ == '__main__':
    t, c = baca(sys.argv[1])
    if '220026' in sys.argv[1]:
        civic(t, c)
        sys.exit()
    print('Mobil Avanza, 26 Okt 2026 (log %s)' % sys.argv[1].split('/')[-1])
    print('Model: dC/dt = P - N (C - Cext), Cext = %d ppm, sensor lag tau = %d detik\n' % (CEXT, TAU))
    # fase tertutup: setelah jendela 1 ditutup (sensor sudah di titik terendah) sampai jendela 2 dibuka
    a, b = jam(19, 59, 0), jam(20, 11, 40)
    N, Css, C0, P, rmse = fit_tertutup(t, c, a, b)
    print('1. Jendela tertutup, 4 orang, 20-40 km/jam (%s-%s)' % (hms(a), hms(b)))
    print('   N_tertutup = %.1f /jam, Css = %.0f ppm, P = %.0f ppm/jam (= %.0f ppm/menit), RMSE %.0f ppm' % (N, Css, P, P / 60, rmse))
    for V in (2500, 2750, 3000):
        print('   G_eff untuk V = %d L, 4 orang: %.1f L/jam/orang (model C-251: 19,6)' % (V, P * V / (4 * 1e6)))
    # rentang N tertutup bila fit dibatasi ke setengah awal atau akhir
    # fase jendela terbuka
    print()
    for nama, ab, at, ak in (('Jendela 1', jam(19, 56, 20), jam(19, 57, 55), jam(19, 59, 30)),
                              ('Jendela 2', jam(20, 11, 40), jam(20, 13, 30), jam(20, 15, 0))):
        Nb, C0b, rm = fit_buka(t, c, ab, at, ak, P, N)
        print('2. %s: dibuka %s, ditutup sekitar %s' % (nama, hms(ab), hms(at)))
        print('   N_buka = %.1f /jam (dua jendela depan setengah terbuka, 20-40 km/jam), RMSE %.0f ppm' % (Nb, rm))
    print('\n3. Seberapa kuat N tertutup ditentukan (RMSE untuk N tertentu; P ikut menyesuaikan)')
    for N_jam, rm, Pn in profil_tertutup(t, c, a, b):
        print('   N = %4.1f /jam: RMSE %4.0f ppm, P = %5.0f ppm/jam' % (N_jam, rm, Pn))
    print('\n4. Kepekaan terhadap konstanta waktu sensor (tau) dan CO2 luar')
    for tau in (30.0, 52.0, 70.0):
        for cext in (420.0,):
            TAU, CEXT = tau, cext
            Nn, Cs, C0, Pn, rm = fit_tertutup(t, c, a, b)
            n1, _, _ = fit_buka(t, c, jam(19, 56, 20), jam(19, 57, 55), jam(19, 59, 30), Pn, Nn)
            n2, _, _ = fit_buka(t, c, jam(20, 11, 40), jam(20, 13, 30), jam(20, 15, 0), Pn, Nn)
            print('   tau = %2d s: N_tertutup %.1f /jam, P %5.0f ppm/jam, N_buka jendela 1 = %.1f, jendela 2 = %.1f /jam' % (tau, Nn, Pn, n1, n2))
    print('\nPembanding asumsi simulasi C-251: N tertutup 0,5 (tabel) atau 1-3 (idle), N jendela terbuka 13,3-26,1, pemulihan 20 km/jam 3,5.')
