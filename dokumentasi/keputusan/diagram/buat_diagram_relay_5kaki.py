"""Membuat diagram jalur lengkap satu kanal jendela: GPIO ESP32 -> modul relay driver (perfboard) -> relay 5 kaki -> motor (SVG dan PNG).

Cara pakai:  python3 buat_diagram_relay_5kaki.py
Hasil     :  diagram-9-modul-relay-ke-relay-5-kaki.svg (dan .png bila qlmanage dan sips ada)

Gambar atas  = wiring seperti di hardware-wiring.md bagian 3 (30 ke aki, 87 ke motor).
Gambar bawah = pola 87a (Usulan, belum diuji): 30 ke motor, 87 ke +12 V, 87a ke GND.
Digambar satu kanal (TURUN, GPIO26); kanal NAIK (GPIO25) identik.
Memakai helper dari buat_diagram_relay.py dan Kanvas dari buat_diagram.py.
"""
from buat_diagram import Kanvas
from buat_diagram_relay import t, kawat, titik, terminal, resistor, MERAH, HITAM, BIRU

W, H = 1400, 1220
ORANYE, HIJAU, UNGU = '#e08a00', '#1a7f37', '#7a2a8a'


def pad(k, x, y, nomor, ket, tx, ty, anchor='middle'):
    k.out.append(f'<circle cx="{x}" cy="{y}" r="9" fill="#fff" stroke="{HITAM}" stroke-width="2"/>')
    t(k, tx, ty, f'Terminal {nomor} {ket}', 12, True, anchor=anchor)


def esp32(k, oy, gpio=26, kanal='TURUN'):
    k.out.append(f'<rect x="30" y="{oy + 270}" width="120" height="200" fill="#e8f0fe" stroke="{HITAM}" stroke-width="1.6"/>')
    t(k, 90, oy + 355, 'ESP32', 15, True, anchor='middle')
    t(k, 90, oy + 380, f'GPIO{gpio}', 13, True, BIRU, 'middle')
    t(k, 90, oy + 398, f'(kanal {kanal})', 12, False, '#444', 'middle')
    kawat(k, [(150, oy + 320), (250 - 40, oy + 320)], BIRU)
    titik(k, 150, oy + 320, BIRU)
    titik(k, 150, oy + 430)
    t(k, 40, oy + 434, 'GND', 12, True)


def driver(k, oy, t12=1, tkol=2):
    """Modul relay driver: sama dengan satu kanal di diagram 7. Keluaran: terminal 1 (+12 V) dan terminal 2 (kolektor)."""
    k.out.append(f'<rect x="190" y="{oy + 70}" width="450" height="410" fill="#fafafa" stroke="#555" stroke-width="1.6" stroke-dasharray="8,5"/>')
    t(k, 205, oy + 92, 'MODUL RELAY DRIVER (perfboard)', 14, True, '#555')
    # rel GND dan +12 V
    kawat(k, [(100, oy + 430), (640, oy + 430)], HITAM, 5)
    kawat(k, [(400, oy + 110), (580, oy + 110)], MERAH, 5)
    terminal(k, 400, oy + 110, 5, '(+12 V masuk)', kiri=True)
    pad(k, 230, oy + 430, 6, '(GND masuk)', 230, oy + 455, 'start')
    # basis
    resistor(k, 250, oy + 320, '470 Ω')
    kawat(k, [(290, oy + 320), (330, oy + 320)], BIRU)
    titik(k, 310, oy + 320, BIRU)
    kawat(k, [(310, oy + 320), (310, oy + 335)], BIRU)
    resistor(k, 310, oy + 370, '', vertikal=True)
    t(k, 295, oy + 375, '10 kΩ', 13, anchor='end')
    kawat(k, [(310, oy + 405), (310, oy + 430)])
    titik(k, 310, oy + 430)
    # transistor
    k.out.append(f'<rect x="330" y="{oy + 285}" width="90" height="80" fill="#2b2b2b" stroke="{HITAM}" stroke-width="1.6"/>')
    t(k, 375, oy + 322, 'PN2222A', 12, True, '#fff', 'middle')
    t(k, 375, oy + 338, '(NPN)', 11, False, '#fff', 'middle')
    t(k, 340, oy + 328, 'B', 12, True, '#8ab4ff')
    t(k, 395, oy + 301, 'C', 12, True, '#8ab4ff')
    t(k, 395, oy + 359, 'E', 12, True, '#8ab4ff')
    kawat(k, [(375, oy + 365), (375, oy + 430)], MERAH)
    titik(k, 375, oy + 430)
    # kolektor naik, dioda, terminal 2
    kawat(k, [(375, oy + 285), (375, oy + 210), (580, oy + 210)], ORANYE)
    kawat(k, [(480, oy + 110), (480, oy + 150)], MERAH)
    titik(k, 480, oy + 110, MERAH)
    k.out.append(f'<line x1="464" y1="{oy + 150}" x2="496" y2="{oy + 150}" stroke="{HITAM}" stroke-width="3"/>')
    k.out.append(f'<polygon points="480,{oy + 150} 466,{oy + 190} 494,{oy + 190}" fill="#fff" stroke="{HITAM}" stroke-width="2"/>')
    kawat(k, [(480, oy + 190), (480, oy + 210)], ORANYE)
    titik(k, 480, oy + 210, ORANYE)
    t(k, 505, oy + 175, '1N4007', 12, False, '#555')
    t(k, 505, oy + 148, 'garis = katoda', 11, False, '#555')
    pad(k, 580, oy + 110, t12, '(+12 V)', 580, oy + 90)
    pad(k, 580, oy + 210, tkol, '(kolektor)', 580, oy + 235)


def relay(k, oy, pin87, pin30, pin87a, judul='RELAY 5 KAKI (12 V)'):
    """Relay 5 kaki. Koil di kiri (85, 86). Kontak di kanan (87 atas, 30 tengah, 87a bawah). Tuas digambar posisi lepas (30-87a)."""
    k.out.append(f'<rect x="760" y="{oy + 110}" width="220" height="330" fill="#fff" stroke="{HITAM}" stroke-width="2.5"/>')
    t(k, 870, oy + 100, judul, 14, True, anchor='middle')
    # koil
    k.out.append(f'<rect x="780" y="{oy + 150}" width="60" height="120" fill="#f3e5f5" stroke="#555" stroke-width="1.6"/>')
    t(k, 810, oy + 205, 'KOIL', 12, True, anchor='middle')
    t(k, 810, oy + 223, '≈80 Ω', 11, False, anchor='middle')
    t(k, 810, oy + 239, '150 mA', 11, False, anchor='middle')
    for y, n in ((170, 85), (250, 86)):
        kawat(k, [(760, oy + y), (780, oy + y)], ORANYE if n == 86 else MERAH)
        k.out.append(f'<circle cx="760" cy="{oy + y}" r="8" fill="#fff" stroke="{HITAM}" stroke-width="2"/>')
        t(k, 752, oy + y - 10, f'kaki {n}', 13, True, anchor='end')
    # koil dari driver
    kawat(k, [(580, oy + 110), (690, oy + 110), (690, oy + 170), (752, oy + 170)], MERAH)
    kawat(k, [(580, oy + 210), (690, oy + 210), (690, oy + 250), (752, oy + 250)], ORANYE)
    # kontak: tuas vertikal di x=900, pivot di kaki 30
    kawat(k, [(900, oy + 270), (900, oy + 375)], HITAM, 4)          # posisi lepas: 30 - 87a (garis penuh)
    k.out.append(f'<line x1="900" y1="{oy + 270}" x2="900" y2="{oy + 168}" stroke="{UNGU}" stroke-width="3" stroke-dasharray="6,5"/>')
    k.out.append(f'<circle cx="900" cy="{oy + 270}" r="5" fill="{HITAM}"/>')
    k.out.append(f'<circle cx="900" cy="{oy + 160}" r="5" fill="#fff" stroke="{HITAM}" stroke-width="2"/>')
    k.out.append(f'<circle cx="900" cy="{oy + 380}" r="5" fill="#fff" stroke="{HITAM}" stroke-width="2"/>')
    t(k, 912, oy + 222, 'koil menyala', 11, False, UNGU)
    t(k, 912, oy + 238, '(putus-putus)', 11, False, UNGU)
    t(k, 912, oy + 330, 'koil mati', 11, False, '#333')
    for y, n, ket in ((160, 87, pin87), (270, 30, pin30), (380, '87a', pin87a)):
        kawat(k, [(900 if n != 30 else 900, oy + y), (972, oy + y)], HITAM, 3)
        k.out.append(f'<circle cx="980" cy="{oy + y}" r="8" fill="#fff" stroke="{HITAM}" stroke-width="2"/>')
        t(k, 960, oy + y - 10, f'kaki {n}', 13, True, anchor='end')
    t(k, 855, oy + 148, 'NO', 11, False, '#555', 'middle')
    t(k, 855, oy + 398, 'NC', 11, False, '#555', 'middle')
    t(k, 855, oy + 288, 'C (common)', 11, False, '#555', 'middle')


def aki_sekering(k, x, y, label):
    """Fuse 15-20 A lalu aki +12 V."""
    k.out.append(f'<rect x="{x}" y="{y - 14}" width="80" height="28" fill="#fff4e0" stroke="{HITAM}" stroke-width="1.6"/>')
    t(k, x + 40, y + 5, 'FUSE 15-20 A', 11, True, anchor='middle')
    k.out.append(f'<rect x="{x + 130}" y="{y - 24}" width="130" height="48" fill="#ffe5e5" stroke="{MERAH}" stroke-width="2"/>')
    t(k, x + 195, y - 2, 'AKI', 14, True, MERAH, 'middle')
    t(k, x + 195, y + 15, '+12 V', 12, True, MERAH, 'middle')
    kawat(k, [(x + 80, y), (x + 130, y)], MERAH)
    t(k, x + 40, y - 24, label, 11, False, '#555', 'middle')


def motor(k, x, y, label):
    k.out.append(f'<circle cx="{x}" cy="{y}" r="34" fill="#e6f4ea" stroke="{HIJAU}" stroke-width="2.5"/>')
    t(k, x, y + 7, 'M', 22, True, HIJAU, 'middle')
    t(k, x, y + 56, label, 12, True, HIJAU, 'middle')


def gnd_simbol(k, x, y):
    for i, w in enumerate((30, 20, 10)):
        k.out.append(f'<line x1="{x - w / 2}" y1="{y + i * 7}" x2="{x + w / 2}" y2="{y + i * 7}" stroke="{HITAM}" stroke-width="3"/>')


def panel_atas(k, oy):
    t(k, 30, oy + 5, 'A. Wiring di hardware-wiring.md sekarang: kaki 30 = +12 V aki, kaki 87 = kabel motor', 17, True, '#0b3d91')
    t(k, 30, oy + 28, 'Dari dokumen 28 Okt. Sambungan kontak ke motor ini Belum diketahui, minta konfirmasi teman hardware.', 12, False, '#a40e26')
    driver(k, oy)
    esp32(k, oy)
    relay(k, oy, 'motor', 'aki', 'kosong')
    # 87 -> motor TURUN
    kawat(k, [(988, oy + 160), (1130, oy + 160)], HIJAU, 4)
    motor(k, 1170, oy + 160, 'MOTOR JENDELA')
    t(k, 1060, oy + 148, 'kabel motor TURUN', 12, True, HIJAU, 'middle')
    t(k, 1170, oy + 232, 'kabel satunya: ke relay NAIK', 11, False, '#555', 'middle')
    # 30 -> fuse -> aki
    kawat(k, [(988, oy + 270), (1040, oy + 270)], MERAH, 4)
    aki_sekering(k, 1040, oy + 270, '')
    # 87a kosong
    kawat(k, [(988, oy + 380), (1030, oy + 380)], '#999', 2)
    t(k, 1040, oy + 385, '✕  dibiarkan kosong (tidak dipakai)', 12, True, '#777')
    # penjelasan
    t(k, 760, oy + 465, 'Koil mati: kaki 30 putus dari 87, motor tidak dapat daya.', 12, False, '#222')
    t(k, 760, oy + 483, 'Koil menyala: 30 tersambung ke 87, kabel motor TURUN dapat +12 V.', 12, False, '#222')
    t(k, 760, oy + 501, 'Risiko: bila saklar jendela asli masih terpasang dan menghubungkan kabel motor ke GND,', 12, True, '#a40e26')
    t(k, 760, oy + 517, '+12 V dari kaki 87 ke kabel itu = korsleting.', 12, True, '#a40e26')


def panel_bawah(k, oy):
    t(k, 30, oy + 5, 'B. Pola kaki 87a (Usulan, belum diuji): kaki 30 = kabel motor, 87 = +12 V, 87a = GND', 17, True, '#0b3d91')
    t(k, 30, oy + 28, 'Kabel motor tertarik ke GND saat koil mati (mirip saklar asli), dan ke +12 V saat koil menyala. Perlu konfirmasi teman hardware.', 12, False, '#a40e26')
    driver(k, oy)
    esp32(k, oy)
    relay(k, oy, 'aki', 'motor', 'gnd')
    # 87 -> fuse -> aki
    kawat(k, [(988, oy + 160), (1040, oy + 160)], MERAH, 4)
    aki_sekering(k, 1040, oy + 160, '')
    # 30 -> motor
    kawat(k, [(988, oy + 270), (1130, oy + 270)], HIJAU, 4)
    motor(k, 1170, oy + 270, 'MOTOR JENDELA')
    t(k, 1060, oy + 258, 'kabel motor TURUN', 12, True, HIJAU, 'middle')
    t(k, 1170, oy + 342, 'kabel satunya: ke relay NAIK', 11, False, '#555', 'middle')
    # 87a -> GND
    kawat(k, [(988, oy + 380), (1060, oy + 380)], HITAM, 3)
    kawat(k, [(1060, oy + 380), (1060, oy + 395)], HITAM, 3)
    gnd_simbol(k, 1060, oy + 395)
    t(k, 1085, oy + 400, 'GND (minus aki)', 12, True)
    t(k, 760, oy + 465, 'Koil mati: kabel motor tersambung ke GND lewat 87a, motor diam.', 12, False, '#222')
    t(k, 760, oy + 483, 'Koil menyala: kabel motor lepas dari GND dan dapat +12 V lewat 87.', 12, False, '#222')
    t(k, 760, oy + 501, 'Bukan sekadar memindah kabel 87 ke 87a: itu membuat motor hidup saat koil mati.', 12, True, '#a40e26')


def diagram9():
    k = Kanvas(W, H, 'Diagram 9. Dari modul relay driver sampai relay 5 kaki dan motor (satu kanal: TURUN, GPIO26)')
    panel_atas(k, 40)
    k.out.append(f'<line x1="30" y1="640" x2="{W - 30}" y2="640" stroke="#bbb" stroke-width="2" stroke-dasharray="4,6"/>')
    panel_bawah(k, 660)
    t(k, 30, H - 12, 'Kanal NAIK (GPIO25) identik. Warna: merah = +12 V, hitam = GND, biru = sinyal basis, oranye = arus koil, hijau = kabel motor. GPIO25 dan GPIO26 tidak boleh HIGH bersamaan.', 12, False, '#444')
    k.simpan('diagram-9-modul-relay-ke-relay-5-kaki.svg', legenda=False)


if __name__ == '__main__':
    diagram9()
    print('selesai')
