"""Pemodelan Bab 4 (C-251) dan simulasi sistem AEROS dalam satu berkas.

Menggabungkan dua kode dari C-251:
  1. Notebook "Perhitungan Bab 4": Tabel 4.2 sampai 4.6 (waktu mencapai ambang dan waktu pemulihan CO2 dan CO)
     dengan Persamaan 4.2, 4.3, 4.4a, ditambah pengecekan rumus.
  2. Simulasi 30 menit dengan mesin status (AMAN atau WASPADA, prioritas CO atas CO2) dan servo jendela,
     untuk Toyota Avanza dan Honda Civic EG6, 1 dan 4 penumpang, tiga skenario CO luar.

Model: dC/dt = P - N (C - C_ext), dengan P = n * G * 1e6 / V (ppm per jam).
  Pers. 4.2 : C(t) = C_ext + (C0 - C_ext) exp(-N t)
  Pers. 4.3 : t = (1/N) ln[(C0 - C_ext) / (C_target - C_ext)]
  Pers. 4.4a: C_inf = C_ext + S * 1e6 / (V * N)         (S = n * G dalam L/jam)

Cara pakai (butuh numpy, pandas, matplotlib):
    python3 pemodelan_bab4_simulasi.py                   # tabel + pengecekan + simulasi + gambar
    python3 pemodelan_bab4_simulasi.py --tanpa-gambar    # hanya tabel dan pengecekan
    python3 pemodelan_bab4_simulasi.py --terukur         # simulasi dengan N dan G hasil ukur Avanza (lihat bagian PARAMETER)
                                                         # catatan: nilai itu hanya terukur untuk Avanza; hasil Civic dengan opsi ini tidak terukur
Hasil: ../hasil/pemodelan/ (CSV tiap tabel, ringkasan.txt, dan gambar PNG).

Perubahan dari kode asli (isi perhitungan tidak diubah):
  - Semua dijadikan satu berkas yang bisa dijalankan di luar Colab (tanpa display() dan tanpa /content/).
  - Nama parameter yang bentrok dibedakan: N_CLOSED_SIM (simulasi, 2,0 per jam) dan N_CLOSED_TABEL (tabel, 0,5 per jam);
    G_STANDARD dipakai bersama.
  - Simulasi memakai mesin status 2-keadaan (AMAN atau WASPADA) versi terbaru; versi lama 3-keadaan tidak disertakan.
  - Seed acak dibuat deterministik (hash() Python berubah tiap proses, jadi hasilnya tidak bisa diulang).
  - Label Tabel 4.4 dan 4.6 diambil dari nilai N yang dipakai. Di kode asli labelnya "Idle (N=0,5)" padahal nilainya 1,0.
  - Ekspor Excel dibuat opsional (butuh openpyxl); CSV selalu dibuat.

Penting: nilai volume kabin (V) dan sebagian parameter di C-251 adalah placeholder yang harus dicocokkan dengan Tabel 4.1 asli.
"""
import argparse
import os
import zlib
from collections import deque

import numpy as np
import pandas as pd

pd.set_option('display.float_format', lambda x: f'{x:,.4f}')

# =====================================================================================
# PARAMETER (Tabel 4.1). CEK DAN GANTI sesuai sumber asli.
# =====================================================================================
VEHICLES = {
    'Toyota Avanza': {'V_L': 2750.0},    # tengah 2,5-3,0 m3  (GANTI sesuai sumber [2])
    'Honda Civic EG6': {'V_L': 2150.0},  # tengah 2,0-2,3 m3  (GANTI sesuai sumber [3][4])
}
PASSENGER_SCENARIOS = [1, 4]

# CO2
G_STANDARD = 19.6              # L/jam/orang (rata-rata literatur [5])
G_LOW, G_HIGH = 15.0, 25.0     # rentang sensitivitas
C_EXT_CO2 = 400.0              # ppm, CO2 luar
C0_CO2 = 400.0                 # ppm, CO2 awal
C_TARGET_CO2 = 2500.0          # ppm, ambang WASPADA CO2
C_HYSTERESIS_CO2 = 2400.0      # ppm, ambang kembali ke NORMAL

# Laju pertukaran udara N (per jam)
N_CLOSED_TABEL = 0.5           # kabin tertutup / ventilasi minimal (Tabel 4.2 dan 4.3)
N_CLOSED_LOW, N_CLOSED_HIGH = 1.0, 3.0           # simulasi: idle, rentang literatur
N_CLOSED_SIM = (N_CLOSED_LOW + N_CLOSED_HIGH) / 2.0
N_OPEN_LOW, N_OPEN_HIGH = 13.3, 26.1             # simulasi: jendela terbuka
N_OPEN_SIM = (N_OPEN_LOW + N_OPEN_HIGH) / 2.0
N_RECOVERY_IDLE = 1.0          # kendaraan diam (revisi)
N_RECOVERY_SLOW_20KMH = 3.5    # kendaraan bergerak lambat ~20 km/jam, mengacu Yang dkk. [8]
N_INFILTRASI = {'Kendaraan diam': 0.5, 'Bergerak lambat': 1.5}

# CO
C0_CO = 5.0                    # ppm, kabin bersih
C_TARGET_CO = 35.0             # ppm, ambang WASPADA CO
C_RECOVERY_CO = 30.0           # ppm, histeresis
C_EXT_CO_VALUES = {'Macet ringan (umum)': 30.0, 'Ekstrem (di belakang diesel diam)': 200.0}
C_EXT_RECOVERY_CO = 5.0        # ppm, CO luar normal

# Ambang dan waktu mesin status (sesuai diagram alir C-251)
CO2_WASPADA, CO2_RECOVERY = C_TARGET_CO2, C_HYSTERESIS_CO2
CO_WASPADA, CO_RECOVERY = C_TARGET_CO, C_RECOVERY_CO
WINDOW_CO2_S = 120
WINDOW_CO_S = 150
RECOVERY_HOLD_S = 60
DT_S = 5.0                     # interval baca (detik)
DT_H = DT_S / 3600.0
T_TOTAL_MIN = 30
N_STEPS = int(T_TOTAL_MIN * 60 / DT_S)

# Skenario CO luar untuk simulasi
ENV_SCENARIOS = {
    'Baseline (Tanpa Macet)': {'peak': 10.0, 'start_min': None},
    'Macet Ringan': {'peak': 30.0, 'start_min': 5.0},
    'Macet Ekstrem (Diesel Diam)': {'peak': 200.0, 'start_min': 5.0},
}
SIM_PASSENGERS = [1, 4]
FOCUS_ENVS = ['Macet Ringan', 'Macet Ekstrem (Diesel Diam)']
N_FOCUS = 4
STATE_COLORS = {'AMAN': '#2ecc71', 'WASPADA-CO2': '#f39c12', 'WASPADA-CO': '#e74c3c'}

# Hasil ukur dari log uji (lihat analisis/ringkasan-temuan.md baris 13), dipakai oleh --terukur.
# Avanza: N tertutup 0,5-2 (terbaik 1,0); N dua jendela depan setengah terbuka 46-79 (terbaik sekitar 60);
# G efektif sekitar 10,5 L/jam/orang (produksi CO2 nyata sekitar 54% dari model).
TERUKUR = {'N_closed': 1.0, 'N_open': 60.0, 'G': 10.5}


# =====================================================================================
# RUMUS INTI (Pers. 4.2, 4.3, 4.4a)
# =====================================================================================
def C_of_t(t, C_ext, C0, N):
    """Persamaan 4.2: konsentrasi pada waktu t (tanpa sumber internal)."""
    return C_ext + (C0 - C_ext) * np.exp(-N * t)


def time_to_target(C0, C_ext, C_target, N):
    """Persamaan 4.3: waktu (jam) mencapai C_target. NaN bila target tidak akan tercapai."""
    ratio = (C0 - C_ext) / (C_target - C_ext)
    if ratio <= 0:
        return np.nan
    return (1.0 / N) * np.log(ratio)


def C_inf_co2(C_ext, S_L_per_hr, V_L, N):
    """Persamaan 4.4a: konsentrasi kesetimbangan CO2 (ppm)."""
    return C_ext + (S_L_per_hr * 1e6) / (V_L * N)


def hr_to_min(x_hr):
    return x_hr * 60.0


def hr_to_sec(x_hr):
    return x_hr * 3600.0


# =====================================================================================
# TABEL 4.2 SAMPAI 4.6
# =====================================================================================
def tabel_4_2():
    """Waktu mencapai ambang WASPADA CO2 (2500 ppm), kabin tertutup."""
    rows = []
    for veh, p in VEHICLES.items():
        V = p['V_L']
        for n in PASSENGER_SCENARIOS:
            S = n * G_STANDARD
            C_inf = C_inf_co2(C_EXT_CO2, S, V, N_CLOSED_TABEL)
            t_hr = time_to_target(C0_CO2, C_inf, C_TARGET_CO2, N_CLOSED_TABEL)
            rows.append({'Kendaraan': veh, 'V (L)': V, 'n (penumpang)': n, 'S = n*G (L/jam)': S,
                         'C_inf (ppm)': C_inf, 't (jam)': t_hr, 't (menit)': hr_to_min(t_hr), 't (detik)': hr_to_sec(t_hr)})
    return pd.DataFrame(rows)


def tabel_4_3():
    """Sensitivitas waktu menuju WASPADA terhadap G (4 penumpang)."""
    G_values = {'Rendah (15)': G_LOW, 'Standar (19.6)': G_STANDARD, 'Tinggi (25)': G_HIGH}
    rows = []
    for veh, p in VEHICLES.items():
        V = p['V_L']
        for label, G in G_values.items():
            S = 4 * G
            C_inf = C_inf_co2(C_EXT_CO2, S, V, N_CLOSED_TABEL)
            t_hr = time_to_target(C0_CO2, C_inf, C_TARGET_CO2, N_CLOSED_TABEL)
            rows.append({'Kendaraan': veh, 'Skenario G': label, 'G (L/jam/orang)': G, 'S (L/jam)': S,
                         'C_inf (ppm)': C_inf, 't (menit)': hr_to_min(t_hr)})
    return pd.DataFrame(rows)


def _skenario_pemulihan():
    return {f'Idle (N={N_RECOVERY_IDLE:g})': N_RECOVERY_IDLE,
            f'~20 km/jam (N={N_RECOVERY_SLOW_20KMH:g})': N_RECOVERY_SLOW_20KMH}


def tabel_4_4():
    """Waktu pemulihan CO2 (dua jendela depan terbuka)."""
    starts = {'2.500 ppm (baru mencapai WASPADA)': 2500.0, '5.000 ppm (kondisi ekstrem)': 5000.0}
    rows = []
    for c_label, C_start in starts.items():
        for n_label, N_rec in _skenario_pemulihan().items():
            t_hr = time_to_target(C_start, C_EXT_CO2, C_HYSTERESIS_CO2, N_rec)
            rows.append({'Kondisi Awal': c_label, 'Skenario Kecepatan': n_label, 'N (jam^-1)': N_rec,
                         't (detik)': hr_to_sec(t_hr), 't (menit)': hr_to_min(t_hr)})
    return pd.DataFrame(rows)


def tabel_4_5():
    """Waktu mencapai ambang WASPADA CO (35 ppm), persamaan 4.2 tanpa sumber internal."""
    rows = []
    for cext_label, C_ext in C_EXT_CO_VALUES.items():
        for n_label, N in N_INFILTRASI.items():
            t_hr = time_to_target(C0_CO, C_ext, C_TARGET_CO, N)
            ok = not np.isnan(t_hr)
            rows.append({'Skenario C_ext': cext_label, 'C_ext (ppm)': C_ext, 'Skenario N': n_label, 'N (jam^-1)': N,
                         't (menit)': hr_to_min(t_hr) if ok else np.nan,
                         'Status': 'Ya' if ok else 'Tidak akan tercapai (C_ext < C_target)'})
    return pd.DataFrame(rows)


def tabel_4_6():
    """Waktu pemulihan CO dari 35 ppm ke 30 ppm."""
    rows = []
    for n_label, N_rec in _skenario_pemulihan().items():
        t_hr = time_to_target(C_TARGET_CO, C_EXT_RECOVERY_CO, C_RECOVERY_CO, N_rec)
        rows.append({'Kondisi Awal': f'{C_TARGET_CO:.0f} ppm (baru mencapai WASPADA)', 'Skenario Kecepatan': n_label,
                     'N (jam^-1)': N_rec, 't (detik)': hr_to_sec(t_hr), 't (menit)': hr_to_min(t_hr)})
    return pd.DataFrame(rows)


def pengecekan_rumus():
    """Pengecekan konsistensi matematis rumus."""
    checks = []
    C_ext, C0, N = 400.0, 3000.0, 0.5
    checks.append(('C(0) = C0', np.isclose(C_of_t(0, C_ext, C0, N), C0)))
    checks.append(('C(t->inf) -> C_ext', np.isclose(C_of_t(1000, C_ext, C0, N), C_ext, atol=1e-3)))
    t_calc = time_to_target(C0, C_ext, 1500.0, N)
    checks.append(('round-trip time_to_target -> C_of_t', np.isclose(C_of_t(t_calc, C_ext, C0, N), 1500.0)))
    # Dengan S=78,4 L/jam dan V=2500 L, N perlu sekitar 1e5 agar suku sumber < 1 ppm
    checks.append(('C_inf dengan N sangat besar -> mendekati C_ext',
                   np.isclose(C_inf_co2(400.0, 78.4, 2500.0, 1e6), 400.0, atol=1.0)))
    checks.append(('C_inf naik saat N turun (ventilasi lebih buruk)',
                   C_inf_co2(400.0, 78.4, 2500.0, 0.1) > C_inf_co2(400.0, 78.4, 2500.0, 5.0)))
    return pd.DataFrame(checks, columns=['Pengecekan', 'Lolos'])


# =====================================================================================
# SIMULASI 30 MENIT (mesin status 2-keadaan, prioritas CO atas CO2, servo jendela)
# =====================================================================================
def co_ambient_profile(t_min, scenario_params, rng):
    """Profil C_ext CO (ppm) sesuai skenario lingkungan."""
    base = 8.0
    peak = scenario_params['peak']
    start = scenario_params['start_min']
    if start is None:
        return base + rng.normal(0, 1.5)
    if start <= t_min < start + 10:
        ramp = min(1.0, (t_min - start) / 2.0)
        return base + ramp * (peak - base) + rng.normal(0, peak * 0.03)
    if t_min >= start + 10:
        decay = np.exp(-(t_min - (start + 10)) / 3.0)
        return base + (peak - base) * decay + rng.normal(0, peak * 0.02)
    return base + rng.normal(0, 1.5)


def analytic_step(C, P, N, C_ext, dt_h):
    """Satu langkah waktu, solusi eksak Persamaan 4.1a."""
    if N <= 1e-9:
        return C + P * dt_h
    C_ss = C_ext + P / N
    return C_ss + (C - C_ss) * np.exp(-N * dt_h)


def simulate(V_L, n_penumpang, env_params, seed=0, n_closed=None, n_open=None, g=None):
    n_closed = N_CLOSED_SIM if n_closed is None else n_closed
    n_open = N_OPEN_SIM if n_open is None else n_open
    g = G_STANDARD if g is None else g
    rng = np.random.default_rng(seed)
    S = n_penumpang * g                    # L/jam
    P_co2 = S * 1e6 / V_L                  # ppm/jam

    C_co2, C_co = C0_CO2, 8.0
    state, sub_scenario = 'AMAN', None     # keadaan: 'AMAN' atau 'WASPADA'; sub: None, 'CO2_TINGGI', 'CO_TINGGI'
    servo, N_current = 0, n_closed
    recovery_timer = 0.0
    buf_co2 = deque(maxlen=int(WINDOW_CO2_S / DT_S))
    buf_co = deque(maxlen=int(WINDOW_CO_S / DT_S))
    log = {'t_min': [], 'co2': [], 'co': [], 'co2_avg': [], 'co_avg': [], 'state': [], 'servo': []}

    for i in range(N_STEPS):
        t_min = i * DT_S / 60.0
        c_ext_co_now = max(2.0, co_ambient_profile(t_min, env_params, rng))   # CO luar masuk lewat infiltrasi

        C_co2 = analytic_step(C_co2, P_co2, N_current, C_EXT_CO2, DT_H)
        C_co = analytic_step(C_co, 0.0, N_current, c_ext_co_now, DT_H)
        C_co2 = max(C_EXT_CO2 * 0.98, C_co2)
        C_co = max(2.0, C_co)

        buf_co2.append(C_co2)
        buf_co.append(C_co)
        co2_avg, co_avg = np.mean(buf_co2), np.mean(buf_co)
        co2_ready = len(buf_co2) == buf_co2.maxlen
        co_ready = len(buf_co) == buf_co.maxlen

        if state == 'AMAN':
            if co_ready and co_avg > CO_WASPADA:
                state, sub_scenario = 'WASPADA', 'CO_TINGGI'
            elif co2_ready and co2_avg > CO2_WASPADA:
                state, sub_scenario = 'WASPADA', 'CO2_TINGGI'
            recovery_timer = 0.0
        elif state == 'WASPADA':
            recovering = C_co < CO_RECOVERY and C_co2 < CO2_RECOVERY
            if recovering:
                recovery_timer += DT_S
                if recovery_timer >= RECOVERY_HOLD_S:
                    state, sub_scenario, recovery_timer = 'AMAN', None, 0.0
                    buf_co2.clear()
                    buf_co.clear()
            else:
                recovery_timer = 0.0
                # Prioritas CO memakai nilai real-time (bukan rata-rata) agar jendela langsung tertutup
                sub_scenario = 'CO_TINGGI' if C_co > CO_WASPADA else 'CO2_TINGGI'

        if state == 'AMAN':
            servo, N_current = 0, n_closed
        elif sub_scenario == 'CO2_TINGGI':
            servo, N_current = 90, n_open
        elif sub_scenario == 'CO_TINGGI':
            servo, N_current = 0, n_closed

        label = 'AMAN' if state == 'AMAN' else ('WASPADA-CO2' if sub_scenario == 'CO2_TINGGI' else 'WASPADA-CO')
        log['t_min'].append(t_min)
        log['co2'].append(C_co2)
        log['co'].append(C_co)
        log['co2_avg'].append(co2_avg)
        log['co_avg'].append(co_avg)
        log['state'].append(label)
        log['servo'].append(servo)
    return log


def jalankan_simulasi(**kw):
    results = {}
    for env_name, env_params in ENV_SCENARIOS.items():
        for veh, p in VEHICLES.items():
            for n in SIM_PASSENGERS:
                key = (env_name, veh, n)
                seed = zlib.crc32(repr(key).encode()) % 10000        # deterministik
                results[key] = simulate(p['V_L'], n, env_params, seed=seed, **kw)
    return results


def ringkas_simulasi(results):
    """Tabel ringkas: kapan status WASPADA pertama dan apa yang memicunya."""
    rows = []
    for (env, veh, n), log in results.items():
        waspada = [i for i, s in enumerate(log['state']) if s != 'AMAN']
        pertama = log['t_min'][waspada[0]] if waspada else np.nan
        rows.append({'Skenario CO luar': env, 'Kendaraan': veh, 'Penumpang': n,
                     'WASPADA pertama (menit)': pertama,
                     'Pemicu pertama': log['state'][waspada[0]] if waspada else '-',
                     'CO2 maks (ppm)': max(log['co2']), 'CO maks (ppm)': max(log['co']),
                     'Menit di WASPADA': len(waspada) * DT_S / 60.0})
    return pd.DataFrame(rows)


# =====================================================================================
# GAMBAR
# =====================================================================================
def _slug(env_name):
    return env_name.split(' (')[0].replace(' ', '_')


def gambar_dashboard(results, outdir, sufiks=''):
    import matplotlib.pyplot as plt
    for env_name in ENV_SCENARIOS:
        for veh, p in VEHICLES.items():
            fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True, gridspec_kw={'height_ratios': [2, 2, 1.2, 1]})
            for n in SIM_PASSENGERS:
                log = results[(env_name, veh, n)]
                axes[0].plot(log['t_min'], log['co2'], label=f'{n} penumpang', linewidth=2)
                axes[1].plot(log['t_min'], log['co'], label=f'{n} penumpang', linewidth=2)
            axes[0].axhline(CO2_WASPADA, color='red', linestyle='--', alpha=0.6, label='Ambang WASPADA (2500 ppm)')
            axes[0].set_ylabel('CO2 (ppm)')
            axes[0].set_title(f'{veh} (V={p["V_L"] / 1000:.2f} m3), konsentrasi CO2\nSkenario: {env_name}{sufiks}')
            axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)
            axes[1].axhline(CO_WASPADA, color='red', linestyle='--', alpha=0.6, label='Ambang WASPADA (35 ppm)')
            axes[1].set_ylabel('CO (ppm)')
            axes[1].set_title(f'Konsentrasi CO, {env_name}')
            axes[1].legend(fontsize=8); axes[1].grid(alpha=0.3)
            for idx, n in enumerate(SIM_PASSENGERS):
                log = results[(env_name, veh, n)]
                for i in range(len(log['t_min']) - 1):
                    axes[2].axvspan(log['t_min'][i], log['t_min'][i + 1], ymin=idx * 0.5, ymax=idx * 0.5 + 0.45,
                                    color=STATE_COLORS[log['state'][i]])
            axes[2].set_yticks([0.22 + i * 0.5 for i in range(len(SIM_PASSENGERS))])
            axes[2].set_yticklabels([f'{n} penumpang' for n in SIM_PASSENGERS])
            axes[2].set_title('Status sistem (AMAN / WASPADA-CO2 / WASPADA-CO)')
            handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in STATE_COLORS.values()]
            axes[2].legend(handles, STATE_COLORS.keys(), loc='upper right', fontsize=7, ncol=4)
            for n in SIM_PASSENGERS:
                log = results[(env_name, veh, n)]
                axes[3].step(log['t_min'], log['servo'], where='post', label=f'{n} penumpang', linewidth=1.8)
            axes[3].set_ylabel('Servo (derajat)'); axes[3].set_xlabel('Waktu (menit)')
            axes[3].set_title('Posisi jendela (servo)')
            axes[3].legend(fontsize=8); axes[3].grid(alpha=0.3)
            plt.tight_layout()
            fname = os.path.join(outdir, f'fig3_dashboard_{veh.replace(" ", "_")}_{_slug(env_name)}{sufiks.replace(" ", "_")}.png')
            plt.savefig(fname, dpi=140)
            plt.close()
            print('Tersimpan:', fname)


def gambar_perbandingan(results, outdir, sufiks=''):
    """Avanza lawan Civic EG6 pada dua skenario paling berdampak (macet ringan dan ekstrem), 4 penumpang."""
    import matplotlib.pyplot as plt
    for env_name in FOCUS_ENVS:
        fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True, gridspec_kw={'height_ratios': [2, 2, 1.2, 1]})
        for veh in VEHICLES:
            log = results[(env_name, veh, N_FOCUS)]
            axes[0].plot(log['t_min'], log['co2'], label=veh, linewidth=2)
            axes[1].plot(log['t_min'], log['co'], label=veh, linewidth=2)
        axes[0].axhline(CO2_WASPADA, color='red', linestyle='--', alpha=0.6, label='Ambang WASPADA (2500 ppm)')
        axes[0].set_ylabel('CO2 (ppm)')
        axes[0].set_title(f'Perbandingan Avanza dan Civic EG6, {N_FOCUS} penumpang\nSkenario: {env_name}{sufiks}')
        axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)
        axes[1].axhline(CO_WASPADA, color='red', linestyle='--', alpha=0.6, label='Ambang WASPADA (35 ppm)')
        axes[1].set_ylabel('CO (ppm)')
        axes[1].legend(fontsize=8); axes[1].grid(alpha=0.3)
        for idx, veh in enumerate(VEHICLES):
            log = results[(env_name, veh, N_FOCUS)]
            for i in range(len(log['t_min']) - 1):
                axes[2].axvspan(log['t_min'][i], log['t_min'][i + 1], ymin=idx * 0.5, ymax=idx * 0.5 + 0.45,
                                color=STATE_COLORS[log['state'][i]])
        axes[2].set_yticks([0.22, 0.72]); axes[2].set_yticklabels(list(VEHICLES.keys()))
        axes[2].set_title('Status sistem (AMAN / WASPADA-CO2 / WASPADA-CO)')
        handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in STATE_COLORS.values()]
        axes[2].legend(handles, STATE_COLORS.keys(), loc='upper right', fontsize=7, ncol=3)
        for veh in VEHICLES:
            log = results[(env_name, veh, N_FOCUS)]
            axes[3].step(log['t_min'], log['servo'], where='post', label=veh, linewidth=1.8)
        axes[3].set_ylabel('Servo (derajat)'); axes[3].set_xlabel('Waktu (menit)')
        axes[3].legend(fontsize=8); axes[3].grid(alpha=0.3)
        plt.tight_layout()
        fname = os.path.join(outdir, f'fig_impactful_{_slug(env_name)}{sufiks.replace(" ", "_")}.png')
        plt.savefig(fname, dpi=140)
        plt.close()
        print('Tersimpan:', fname)


# =====================================================================================
# MAIN
# =====================================================================================
def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hasil', 'pemodelan'),
                    help='folder keluaran (bawaan: ../hasil/pemodelan)')
    ap.add_argument('--tanpa-gambar', action='store_true', help='lewati gambar simulasi')
    ap.add_argument('--terukur', action='store_true', help='simulasi dengan N dan G hasil ukur Avanza (hanya valid untuk Avanza), bukan asumsi C-251')
    ap.add_argument('--excel', action='store_true', help='simpan juga satu berkas Excel (butuh openpyxl)')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ringkasan = []

    tabel = {'tabel_4_2': tabel_4_2(), 'tabel_4_3': tabel_4_3(), 'tabel_4_4': tabel_4_4(),
             'tabel_4_5': tabel_4_5(), 'tabel_4_6': tabel_4_6(), 'pengecekan_rumus': pengecekan_rumus()}
    for nama, df in tabel.items():
        print(f'\n=== {nama.replace("_", " ").title()} ===')
        print(df.to_string(index=False))
        df.to_csv(os.path.join(a.out, nama + '.csv'), index=False)
        ringkasan.append(f'=== {nama} ===\n{df.to_string(index=False)}\n')
    if not tabel['pengecekan_rumus']['Lolos'].all():
        print('\nPERINGATAN: ada pengecekan rumus yang gagal.')

    if a.excel:
        try:
            with pd.ExcelWriter(os.path.join(a.out, 'AEROS_Bab4_Tabel_Hasil.xlsx')) as w:
                for nama, df in tabel.items():
                    df.to_excel(w, sheet_name=nama[:31], index=False)
            print('\nTersimpan: AEROS_Bab4_Tabel_Hasil.xlsx')
        except ImportError:
            print('\nopenpyxl tidak terpasang; Excel dilewati (CSV tetap dibuat).')

    kw, sufiks = {}, ''
    if a.terukur:
        kw = {'n_closed': TERUKUR['N_closed'], 'n_open': TERUKUR['N_open'], 'g': TERUKUR['G']}
        sufiks = ' (N dan G terukur)'
        print(f'\nSimulasi dengan nilai terukur: {TERUKUR}')
    results = jalankan_simulasi(**kw)
    sim = ringkas_simulasi(results)
    print('\n=== Ringkasan simulasi 30 menit' + sufiks + ' ===')
    print(sim.to_string(index=False))
    sim.to_csv(os.path.join(a.out, 'ringkasan_simulasi' + ('_terukur' if a.terukur else '') + '.csv'), index=False)
    ringkasan.append(f'=== ringkasan simulasi{sufiks} ===\n{sim.to_string(index=False)}\n')

    if not a.tanpa_gambar:
        try:
            import matplotlib
            matplotlib.use('Agg')
            gambar_dashboard(results, a.out, sufiks)
            gambar_perbandingan(results, a.out, sufiks)
        except ImportError:
            print('matplotlib tidak terpasang; gambar dilewati.')
    open(os.path.join(a.out, 'ringkasan' + ('_terukur' if a.terukur else '') + '.txt'), 'w', encoding='utf-8').write('\n'.join(ringkasan))


if __name__ == '__main__':
    main()
