"""Membuat diagram hubungan tabel (ERD) rancangan database MVP (SVG dan PNG).

Cara pakai:  python3 buat_diagram_erd.py
Hasil     :  diagram-8-hubungan-tabel-mvp.svg dan .png

Sumber rancangan: ../rancangan-database-mvp.md. Memakai FILL, FONT, esc, ekspor_png dari buat_diagram.py.
Warna baris: hijau kebiruan = kolom baru, kuning = kolom turunan (dijaga database), oranye = sementara.
"""
from buat_diagram import FILL, FONT, esc, ekspor_png

W, H = 1500, 1030
BARIS, KEPALA = 22, 30
out = []

WARNA_BARIS = {'baru': FILL['teal'][0], 'turunan': FILL['kuning'][0], 'sementara': FILL['oranye'][0], '': '#ffffff'}


def tabel(x, y, w, nama, baris, putus=False, catatan=None, warna_kepala='#dae8fc'):
    """baris = [(nama_kolom, tanda_kanan, jenis)] dengan jenis di WARNA_BARIS; mengembalikan fungsi y_baris(i)."""
    h = KEPALA + len(baris) * BARIS
    dash = ' stroke-dasharray="7,4"' if putus else ''
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#333" stroke-width="1.6"{dash}/>')
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{KEPALA}" fill="{warna_kepala}" stroke="#333" stroke-width="1.6"{dash}/>')
    out.append(f'<text x="{x + w / 2}" y="{y + 20}" text-anchor="middle" font-family="{FONT}" font-size="15" '
               f'font-weight="bold" fill="#111">{esc(nama)}</text>')
    for i, (kol, tanda, jenis) in enumerate(baris):
        yy = y + KEPALA + i * BARIS
        out.append(f'<rect x="{x}" y="{yy}" width="{w}" height="{BARIS}" fill="{WARNA_BARIS[jenis]}" stroke="#bbb" stroke-width="0.8"/>')
        tebal = ' font-weight="bold"' if tanda.startswith('PK') else ''
        out.append(f'<text x="{x + 10}" y="{yy + 15}" font-family="{FONT}" font-size="13" fill="#111"{tebal}>{esc(kol)}</text>')
        out.append(f'<text x="{x + w - 10}" y="{yy + 15}" text-anchor="end" font-family="{FONT}" font-size="12" fill="#555">{esc(tanda)}</text>')
    if catatan:
        out.append(f'<text x="{x}" y="{y + h + 16}" font-family="{FONT}" font-size="12" fill="#555">{esc(catatan)}</text>')
    return lambda i: y + KEPALA + i * BARIS + BARIS / 2


def garis(titik, putus=False, panah=False):
    d = 'M ' + ' L '.join(f'{px:.1f},{py:.1f}' for px, py in titik)
    ex = ' stroke-dasharray="6,4"' if putus else ''
    mk = ' marker-end="url(#panah)"' if panah else ''
    out.append(f'<path d="{d}" fill="none" stroke="#333" stroke-width="1.6"{ex}{mk}/>')


def label(x, y, t, anc='start', warna='#b46504', ukuran=13):
    out.append(f'<text x="{x}" y="{y}" text-anchor="{anc}" font-family="{FONT}" font-size="{ukuran}" '
               f'font-weight="bold" fill="{warna}">{esc(t)}</text>')


# ---------- tabel ----------
dev = tabel(620, 70, 260, 'devices', [
    ('device_id', 'PK', ''), ('is_active', '', ''), ('created_at', '', '')])

alr = tabel(60, 300, 330, 'alert_logs', [
    ('id  (= event_id dari ESP)', 'PK', ''), ('device_id', 'FK devices', ''), ('created_at', '', ''),
    ('resolved_at', '', ''), ('alert_type', 'sementara', 'sementara')],
    catatan='satu baris per episode peringatan')

sr = tabel(520, 250, 460, 'sensor_readings', [
    ('id', 'PK', ''), ('device_id', 'FK devices', ''), ('nonce', 'unik bersama device_id', ''),
    ('measured_at', '', ''), ('received_at', '', ''), ('co_ppm', '', ''), ('co2_ppm', '', ''),
    ('co_peak_ppm', '', ''), ('co2_peak_ppm', '', ''), ('co_peak_second', '', ''), ('co2_peak_second', '', ''),
    ('co_level', '0 normal, 1 waspada, 2 bahaya', 'baru'), ('co2_level', '0 normal, 1 waspada, 2 bahaya', 'baru'),
    ('buzzer_state', 'on / off', 'baru'), ('window_status', '0 atas, 50 bawah, null bergerak', ''),
    ('event_id', 'FK alert_logs (boleh kosong)', 'baru'),
    ('status', 'turunan dari co_level dan co2_level', 'turunan')],
    catatan='satu baris per 5 detik')

ds = tabel(1120, 300, 340, 'device_state', [
    ('device_id', 'PK, FK devices', ''), ('connection_status', '', ''), ('last_seen_at', '', ''),
    ('last_co_ppm', '', ''), ('last_co2_ppm', '', ''), ('status', '', ''), ('buzzer_state', '', ''),
    ('window_status', '', ''), ('active_alert_id', 'FK alert_logs', ''), ('updated_at', '', '')],
    putus=True, catatan='cache realtime (pengecualian 3NF yang disengaja)')

vag = tabel(1120, 660, 340, 'v_alert_gas  (view)', [
    ('alert_id', '', ''), ('gas', 'CO atau CO2', ''), ('tingkat_maks', '', ''), ('puncak_ppm', '', ''), ('mulai_at', '', '')],
    putus=True, warna_kepala='#eeeeee')

va = tabel(1120, 840, 340, 'v_alerts  (view, untuk aplikasi)', [
    ('id', '', ''), ('device_id', '', ''), ('created_at', '', ''), ('resolved_at', '', ''),
    ('tingkat', 'bahaya / waspada', ''), ('gas', 'larik, mis. {CO,CO2}', '')],
    putus=True, warna_kepala='#eeeeee')

# ---------- hubungan ----------
# devices 1 - N alert_logs
garis([(620, dev(1)), (225, dev(1)), (225, 300)])
label(606, dev(1) - 6, '1', 'end'); label(235, 292, 'N')
# devices 1 - N sensor_readings
garis([(750, 166), (750, 250)])
label(760, 184, '1'); label(760, 244, 'N')
# devices 1 - 1 device_state
garis([(880, dev(1)), (1290, dev(1)), (1290, 300)])
label(894, dev(1) - 6, '1'); label(1300, 292, '1')
# alert_logs 1 - N sensor_readings (lewat event_id)
garis([(390, alr(0)), (455, alr(0)), (455, sr(15)), (520, sr(15))])
label(398, alr(0) - 6, '1'); label(506, sr(15) - 6, 'N', 'end')
label(447, 520, 'event_id', 'end', '#555', 12)
out.append(f'<text x="447" y="536" text-anchor="end" font-family="{FONT}" font-size="12" fill="#555">device_id sama</text>')

# view: sensor_readings -> v_alert_gas -> v_alerts, alert_logs -> v_alerts
garis([(980, sr(11)), (1050, sr(11)), (1050, vag(1)), (1120, vag(1))], putus=True, panah=True)
garis([(1290, 660 + KEPALA + 5 * BARIS), (1290, 840)], putus=True, panah=True)
garis([(335, 300 + KEPALA + 5 * BARIS), (335, 960), (1120, 960)], putus=True, panah=True)
label(345, 955, 'alert_logs → v_alerts', 'start', '#555', 12)

# ---------- dihapus ----------
out.append(f'<rect x="520" y="700" width="420" height="140" fill="#f8cecc" stroke="#b85450" stroke-width="1.4"/>')
label(532, 722, 'Dibuang (bersama "Saya Tahu")', 'start', '#b85450', 14)
for i, t in enumerate(['tabel actuator_logs',
                       'alert_logs.reading_id dan acknowledged_at',
                       'device_state.ack_driver dan ack_at',
                       'sensor_readings.status sebagai kolom biasa',
                       '(diganti kolom turunan)']):
    out.append(f'<text x="532" y="{746 + i * 18}" font-family="{FONT}" font-size="13" fill="#333">{esc(t)}</text>')

# ---------- legenda ----------
lx, ly = 60, 960
items = [('teal', 'kolom baru'), ('kuning', 'kolom turunan (dijaga database)'), ('oranye', 'sementara, dibuang nanti')]
x = lx
out.append(f'<text x="{lx}" y="{ly + 40}" font-family="{FONT}" font-size="12" fill="#333">1 = satu, N = banyak. Garis putus = view atau cache. '
           f'Sumber: rancangan-database-mvp.md (3 Nov 2026).</text>')
for kunci, t in items:
    out.append(f'<rect x="{x}" y="{ly + 55}" width="18" height="13" fill="{FILL[kunci][0]}" stroke="{FILL[kunci][1]}"/>')
    out.append(f'<text x="{x + 25}" y="{ly + 66}" font-family="{FONT}" font-size="12" fill="#333">{esc(t)}</text>')
    x += 50 + len(t) * 6.6

# ---------- tulis ----------
judul = 'Diagram 8. Hubungan tabel database MVP (rancangan 3 November 2026)'
head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
        f'<defs><marker id="panah" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
        f'<polygon points="0,0 10,4 0,8" fill="#333"/></marker></defs>'
        f'<rect width="100%" height="100%" fill="#ffffff"/>'
        f'<text x="{W / 2}" y="26" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="bold" fill="#111">{esc(judul)}</text>')
nama = 'diagram-8-hubungan-tabel-mvp.svg'
with open(nama, 'w', encoding='utf-8') as f:
    f.write(head + '\n'.join(out) + '</svg>')
ekspor_png(nama, W, H)
print('ok', nama)
