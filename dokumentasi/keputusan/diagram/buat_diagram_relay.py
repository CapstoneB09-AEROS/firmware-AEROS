"""Membuat diagram rangkaian perfboard relay driver jendela (SVG dan PNG), versi yang sudah dikoreksi (3 Nov 2026).

Cara pakai:  python3 buat_diagram_relay.py
Hasil     :  diagram-7-perfboard-relay-jendela.svg (dan .png bila qlmanage dan sips ada)

Koreksi pengguna 3 Nov 2026: GPIO25 = relay NAIK, GPIO26 = relay TURUN.
(Gambar sebelumnya menulis kebalikannya; sumber rangkaian: sketsa tangan perfboard-sketsa-tangan-2026-11-03.png.)
Memakai Kanvas dan ekspor_png dari buat_diagram.py.
"""
from buat_diagram import Kanvas, FONT, esc, ekspor_png

W, H = 1400, 820
RAIL_12V, RAIL_GND = 120, 700
MERAH, HITAM, BIRU = '#d1242f', '#24292f', '#1f6feb'


def t(k, x, y, s, ukuran=13, tebal=False, warna='#111', anchor='start'):
    tb = ' font-weight="bold"' if tebal else ''
    k.out.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{ukuran}" '
                 f'fill="{warna}"{tb}>{esc(s)}</text>')


def kawat(k, titik, warna=HITAM, lebar=3):
    d = 'M ' + ' L '.join(f'{x},{y}' for x, y in titik)
    k.out.append(f'<path d="{d}" fill="none" stroke="{warna}" stroke-width="{lebar}"/>')


def titik(k, x, y, warna=HITAM):
    k.out.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{warna}"/>')


def terminal(k, x, y, nomor, keterangan, kiri=True):
    k.out.append(f'<circle cx="{x}" cy="{y}" r="9" fill="#fff" stroke="{HITAM}" stroke-width="2"/>')
    if kiri:
        t(k, x - 16, y + 5, f'Terminal {nomor} {keterangan}', 13, True, anchor='end')
    else:
        t(k, x + 16, y + 5, f'Terminal {nomor} {keterangan}', 13, True)


def resistor(k, cx, cy, teks, vertikal=False):
    w, h = (22, 70) if vertikal else (80, 24)
    k.out.append(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" fill="#f6e7c1" stroke="{HITAM}" stroke-width="1.6"/>')
    if vertikal:
        t(k, cx + 18, cy + 5, teks, 13)
    else:
        t(k, cx, cy + 5, teks, 13, anchor='middle')


def kanal(k, x0, judul, gpio, t_12v, t_kolektor, warna_judul, arah):
    # judul kanal
    t(k, x0 + 100, 62, judul, 18, True, warna_judul, 'middle')
    t(k, x0 + 100, 82, f'GPIO{gpio} HIGH = relay menarik = motor {arah}', 13, False, '#444', 'middle')
    xd, xk = x0 + 150, x0 + 320   # diode, koil
    # koil relay 85/86
    k.out.append(f'<rect x="{xk - 75}" y="165" width="150" height="125" fill="#f3e5f5" stroke="#555" stroke-width="1.6" stroke-dasharray="6,4"/>')
    t(k, xk, 200, 'KOIL relay', 13, True, anchor='middle')
    t(k, xk, 220, '85 atas, 86 bawah', 12, False, anchor='middle')
    t(k, xk, 238, '12 V, sekitar 150 mA', 12, False, anchor='middle')
    t(k, xk, 262, 'kontak 30/87 ke', 11, False, '#7a2a8a', 'middle')
    t(k, xk, 277, f'kabel motor {arah.upper()}', 11, True, '#7a2a8a', 'middle')
    kawat(k, [(xk, RAIL_12V), (xk, 165)], MERAH)
    titik(k, xk, RAIL_12V, MERAH)
    kawat(k, [(xk, 290), (xk, 340), (xd, 340)], '#e08a00')
    # dioda 1N4007: katoda (garis) ke +12 V
    kawat(k, [(xd, RAIL_12V), (xd, 190)], MERAH)
    titik(k, xd, RAIL_12V, MERAH)
    k.out.append(f'<polygon points="{xd},190 {xd - 14},250 {xd + 14},250" fill="#fff" stroke="{HITAM}" stroke-width="2"/>')
    k.out.append(f'<line x1="{xd - 16}" y1="190" x2="{xd + 16}" y2="190" stroke="{HITAM}" stroke-width="3"/>')
    kawat(k, [(xd, 250), (xd, 340)], '#e08a00')
    t(k, xd - 22, 232, '1N4007', 12, False, '#555', 'end')
    t(k, xd + 20, 186, 'garis = katoda', 11, False, '#555')
    titik(k, xd, 340, '#e08a00')
    terminal(k, xd, 155, t_12v, '(+12 V)')
    terminal(k, xd, 340 - 0, t_kolektor, '(kolektor)')
    # transistor
    kawat(k, [(xd, 340), (xd, 445)], '#e08a00')
    k.out.append(f'<rect x="{xd - 55}" y="445" width="110" height="110" fill="#2b2b2b" stroke="{HITAM}" stroke-width="1.6"/>')
    t(k, xd, 505, 'PN2222A', 13, True, '#fff', 'middle')
    t(k, xd, 523, '(NPN)', 12, False, '#fff', 'middle')
    t(k, xd + 8, 463, 'C', 13, True, '#8ab4ff')
    t(k, xd - 50, 505, 'B', 13, True, '#8ab4ff')
    t(k, xd + 8, 548, 'E', 13, True, '#8ab4ff')
    kawat(k, [(xd, 555), (xd, RAIL_GND)], MERAH)
    titik(k, xd, RAIL_GND)
    # basis: GPIO -> 470 -> basis, 10k ke GND
    gx = x0 - 120
    k.out.append(f'<circle cx="{gx}" cy="500" r="11" fill="#fff" stroke="{BIRU}" stroke-width="2.5"/>')
    t(k, gx, 478, f'GPIO{gpio}', 14, True, BIRU, 'middle')
    kawat(k, [(gx + 11, 500), (x0 - 60, 500)], BIRU)
    resistor(k, x0 - 20, 500, '470 Ω')
    kawat(k, [(x0 + 20, 500), (xd - 55, 500)], BIRU)
    nx = x0 + 70
    titik(k, nx, 500, BIRU)
    kawat(k, [(nx, 500), (nx, 565)], BIRU)
    resistor(k, nx, 600, '10 kΩ', vertikal=True)
    kawat(k, [(nx, 635), (nx, RAIL_GND)])
    titik(k, nx, RAIL_GND)


def diagram7():
    k = Kanvas(W, H, 'Diagram 7. Perfboard relay driver jendela (koreksi 3 Nov 2026): GPIO25 = NAIK, GPIO26 = TURUN')
    # rel
    kawat(k, [(40, RAIL_12V), (W - 40, RAIL_12V)], MERAH, 6)
    kawat(k, [(40, RAIL_GND), (W - 40, RAIL_GND)], HITAM, 6)
    terminal(k, 58, RAIL_12V - 20, 5, ': +12 V masuk', kiri=False)
    terminal(k, 58, RAIL_GND + 26, 6, ': GND masuk (minus aki, satu jalur dengan GND ESP32)', kiri=False)
    kanal(k, 220, 'KANAL NAIK (tutup jendela)', 25, 4, 3, '#0b5cad', 'naik')
    kanal(k, 800, 'KANAL TURUN (buka jendela)', 26, 1, 2, '#b45309', 'turun')
    # catatan
    k.out.append(f'<rect x="40" y="750" width="{W - 80}" height="56" fill="#fffbe6" stroke="#d4a72c"/>')
    t(k, 56, 772, 'Terminal 5 = +12 V dari aki lewat fuse. Arus koil (merah): +12 V -> koil -> kolektor -> emitor -> GND. Arus basis (biru): GPIO -> 470 Ω -> basis -> emitor, sekitar 5 mA.', 12)
    t(k, 56, 792, 'GPIO LOW: transistor mati, relay lepas, dioda hanya meredam lonjakan saat relay lepas. GPIO25 dan GPIO26 TIDAK BOLEH HIGH bersamaan.', 13, True, '#a40e26')
    k.simpan('diagram-7-perfboard-relay-jendela.svg', legenda=False)


if __name__ == '__main__':
    diagram7()
    print('selesai')
