"""Membuat diagram dua kanal jendela: GPIO25 (NAIK) dan GPIO26 (TURUN), dua modul relay driver, dua relay 5 kaki, satu motor (SVG dan PNG).

Cara pakai:  python3 buat_diagram_relay_dua_kanal.py
Hasil     :  diagram-10-dua-relay-naik-turun.svg (dan .png bila qlmanage dan sips ada)

Pola kaki 87a (Usulan, belum diuji): kaki 30 = kabel motor, 87 = +12 V, 87a = GND.
Memakai fungsi gambar dari buat_diagram_relay_5kaki.py.
"""
from buat_diagram import Kanvas
from buat_diagram_relay import t, kawat, titik, HITAM, MERAH, BIRU
from buat_diagram_relay_5kaki import esp32, driver, relay, aki_sekering, gnd_simbol, HIJAU

W, H = 1400, 1290
OY_NAIK, OY_TURUN = 60, 580
X_MOTOR, Y_MOTOR = 1345, 585


def kanal(k, oy, gpio, nama, t12, tkol, judul_warna):
    t(k, 30, oy + 5, f'KANAL {nama}: GPIO{gpio}', 17, True, judul_warna)
    driver(k, oy, t12, tkol)
    esp32(k, oy, gpio, nama)
    relay(k, oy, 'aki', 'motor', 'gnd', f'RELAY {nama} (5 kaki)')
    # 87 -> fuse -> aki
    kawat(k, [(988, oy + 160), (1040, oy + 160)], MERAH, 4)
    aki_sekering(k, 1040, oy + 160, '')
    # 87a -> GND
    kawat(k, [(988, oy + 380), (1060, oy + 380), (1060, oy + 395)], HITAM, 3)
    gnd_simbol(k, 1060, oy + 395)
    t(k, 1085, oy + 400, 'GND (minus aki)', 12, True)


def diagram10():
    k = Kanvas(W, H, 'Diagram 10. Dua relay 5 kaki untuk jendela: GPIO25 = NAIK, GPIO26 = TURUN, satu motor')
    kanal(k, OY_NAIK, 25, 'NAIK', 4, 3, '#0b5cad')
    k.out.append(f'<line x1="30" y1="{OY_TURUN - 22}" x2="{X_MOTOR - 130}" y2="{OY_TURUN - 22}" stroke="#bbb" stroke-width="2" stroke-dasharray="4,6"/>')
    kanal(k, OY_TURUN, 26, 'TURUN', 1, 2, '#b45309')
    # kabel motor: kaki 30 tiap relay -> motor
    kawat(k, [(988, OY_NAIK + 270), (X_MOTOR, OY_NAIK + 270), (X_MOTOR, Y_MOTOR - 36)], HIJAU, 4)
    kawat(k, [(988, OY_TURUN + 270), (X_MOTOR, OY_TURUN + 270), (X_MOTOR, Y_MOTOR + 36)], HIJAU, 4)
    k.out.append(f'<circle cx="{X_MOTOR}" cy="{Y_MOTOR}" r="36" fill="#e6f4ea" stroke="{HIJAU}" stroke-width="2.5"/>')
    t(k, X_MOTOR, Y_MOTOR + 8, 'M', 22, True, HIJAU, 'middle')
    t(k, X_MOTOR - 50, Y_MOTOR - 6, 'MOTOR', 12, True, HIJAU, 'end')
    t(k, X_MOTOR - 50, Y_MOTOR + 10, 'JENDELA', 12, True, HIJAU, 'end')
    t(k, X_MOTOR - 10, OY_NAIK + 258, 'kabel motor NAIK', 12, True, HIJAU, 'end')
    t(k, X_MOTOR - 10, OY_TURUN + 258, 'kabel motor TURUN', 12, True, HIJAU, 'end')
    # tabel keadaan
    y0 = OY_TURUN + 520
    k.out.append(f'<rect x="30" y="{y0}" width="{W - 60}" height="132" fill="#fffbe6" stroke="#d4a72c"/>')
    t(k, 46, y0 + 22, 'Apa yang terjadi pada motor', 14, True)
    baris = [
        ('GPIO25 LOW, GPIO26 LOW', 'kedua kabel motor ke GND lewat kaki 87a. Motor diam.', False),
        ('GPIO25 HIGH, GPIO26 LOW', 'kabel NAIK +12 V, kabel TURUN GND. Jendela NAIK (tutup).', False),
        ('GPIO25 LOW, GPIO26 HIGH', 'kabel TURUN +12 V, kabel NAIK GND. Jendela TURUN (buka).', False),
        ('GPIO25 HIGH, GPIO26 HIGH', 'kedua kabel +12 V, motor diam (tidak ada beda tegangan). Tetap DILARANG di firmware.', True),
    ]
    for i, (a, b, merah) in enumerate(baris):
        yy = y0 + 46 + i * 21
        t(k, 46, yy, a, 13, True, '#a40e26' if merah else '#111')
        t(k, 270, yy, b, 13, merah, '#a40e26' if merah else '#111')
    t(k, 30, H - 18, 'Terminal 5 (+12 V) dan terminal 6 (GND) di perfboard hanya satu, dipakai kedua kanal. Warna: merah = +12 V, hitam = GND, biru = sinyal basis, oranye = arus koil, hijau = kabel motor.', 12, False, '#444')
    k.simpan('diagram-10-dua-relay-naik-turun.svg', legenda=False)


if __name__ == '__main__':
    diagram10()
    print('selesai')
