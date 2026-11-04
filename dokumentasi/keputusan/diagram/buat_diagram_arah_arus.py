"""Membuat diagram visual arah arus dua relay 5 kaki untuk jendela (SVG dan PNG).

Cara pakai:  python3 buat_diagram_arah_arus.py
Hasil     :  diagram-11-arah-arus-relay-jendela.svg (dan .png bila qlmanage dan sips ada)

Pola kaki 87a (Usulan, belum diuji): kaki 30 = kabel motor, 87 = +12 V, 87a = GND.
Atas: arus motor saat NAIK (GPIO25 HIGH) dan saat TURUN (GPIO26 HIGH). Bawah: arus koil satu kanal.
Memakai Kanvas dari buat_diagram.py dan helper dari buat_diagram_relay.py.
"""
from buat_diagram import Kanvas
from buat_diagram_relay import t, kawat, titik, resistor, MERAH, HITAM, BIRU

W, H = 1400, 1180
ARUS, ABU, HIJAU = '#e5484d', '#b8b8b8', '#1a7f37'
Y_12V, Y_GND = 110, 540
Y_ATAS, Y_TENGAH, Y_BAWAH = 230, 285, 340   # kontak 87, kaki 30 / pivot, kontak 87a
LEBAR_PANEL = 690


def panah(k, x, y, arah, warna=ARUS, u=9):
    pts = {'kanan': [(x + u, y), (x - u, y - u * 0.8), (x - u, y + u * 0.8)],
           'kiri': [(x - u, y), (x + u, y - u * 0.8), (x + u, y + u * 0.8)],
           'bawah': [(x, y + u), (x - u * 0.8, y - u), (x + u * 0.8, y - u)],
           'atas': [(x, y - u), (x - u * 0.8, y + u), (x + u * 0.8, y + u)]}[arah]
    k.out.append('<polygon points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) + f'" fill="{warna}" stroke="#fff" stroke-width="1"/>')


def relay_sisi(k, ox, kiri, nama, gpio, menyala):
    """Satu relay. kiri=True: relay NAIK di sisi kiri, kaki 30 menghadap motor di kanan. Cermin untuk TURUN."""
    def X(x):
        return ox + (x if kiri else LEBAR_PANEL - x)
    arah_pusat = 'kanan' if kiri else 'kiri'
    arah_luar = 'kiri' if kiri else 'kanan'
    anchor, off = ('start', 10) if kiri else ('end', -10)
    # kotak relay
    x0 = min(X(50), X(230))
    k.out.append(f'<rect x="{x0}" y="150" width="180" height="250" fill="#fff" stroke="{HITAM}" stroke-width="2.5"/>')
    ax = 'start' if kiri else 'end'
    t(k, X(55), 126, f'RELAY {nama}', 14, True, anchor=ax)
    t(k, X(55), 142, f'(GPIO{gpio})', 12, False, '#444', ax)
    # koil
    cx = X(87)
    k.out.append(f'<rect x="{cx - 25}" y="230" width="50" height="110" fill="{"#c8e6c9" if menyala else "#f3e5f5"}" '
                 f'stroke="{HIJAU if menyala else "#555"}" stroke-width="2"/>')
    t(k, cx, 282, 'KOIL', 12, True, anchor='middle')
    t(k, cx, 300, '85-86', 11, False, anchor='middle')
    t(k, cx, 366, 'koil', 12, True, HIJAU if menyala else '#666', 'middle')
    t(k, cx, 382, 'MENYALA' if menyala else 'mati', 12, True, HIJAU if menyala else '#666', 'middle')
    # kawat dari rail ke 87 dan dari 87a ke GND
    wa = ARUS if menyala else ABU          # jalur 87 (aktif hanya bila tuas naik)
    wb = ABU if menyala else ARUS          # jalur 87a (aktif hanya bila tuas turun)
    kawat(k, [(X(170), Y_12V), (X(170), Y_ATAS)], wa, 6 if menyala else 3)
    kawat(k, [(X(170), Y_BAWAH), (X(170), Y_GND)], wb, 3 if menyala else 6)
    titik(k, X(170), Y_12V, MERAH)
    titik(k, X(170), Y_GND, HITAM)
    # tuas
    ujung = Y_ATAS if menyala else Y_BAWAH
    kawat(k, [(X(170), Y_TENGAH), (X(170), ujung)], ARUS, 6)
    for y in (Y_ATAS, Y_BAWAH):
        k.out.append(f'<circle cx="{X(170)}" cy="{y}" r="5" fill="#fff" stroke="{HITAM}" stroke-width="2"/>')
    k.out.append(f'<circle cx="{X(170)}" cy="{Y_TENGAH}" r="6" fill="{HITAM}"/>')
    t(k, X(170) + off, Y_ATAS - 8, '87', 12, True, anchor=anchor)
    t(k, X(170) + off, Y_BAWAH + 18, '87a', 12, True, anchor=anchor)
    t(k, X(170) + off, Y_TENGAH - 10, '30', 12, True, anchor=anchor)
    # kaki 30 -> kabel motor
    xm = ox + 345 + (-40 if kiri else 40)
    kawat(k, [(X(170), Y_TENGAH), (xm, Y_TENGAH)], ARUS, 6)
    k.out.append(f'<circle cx="{X(230)}" cy="{Y_TENGAH}" r="8" fill="#fff" stroke="{HITAM}" stroke-width="2"/>')
    # panah arus
    if menyala:   # dari +12 V ke motor
        panah(k, X(170), 165, 'bawah')
        panah(k, X(170), 255, 'bawah')
        panah(k, X(200), Y_TENGAH, arah_pusat)
        panah(k, X(268), Y_TENGAH, arah_pusat)
    else:         # dari motor ke GND
        panah(k, X(268), Y_TENGAH, arah_luar)
        panah(k, X(200), Y_TENGAH, arah_luar)
        panah(k, X(170), 312, 'bawah')
        panah(k, X(170), 450, 'bawah')
    t(k, X(268), Y_TENGAH - 18, '+12 V' if menyala else 'GND', 13, True, MERAH if menyala else HITAM, 'middle')


def panel(k, ox, naik):
    nama = 'NAIK' if naik else 'TURUN'
    warna = '#0b5cad' if naik else '#b45309'
    t(k, ox + 20, 32, f'JENDELA {nama} ({"tutup" if naik else "buka"})', 19, True, warna)
    t(k, ox + 20, 54, 'GPIO25 = HIGH, GPIO26 = LOW' if naik else 'GPIO26 = HIGH, GPIO25 = LOW', 14, True, '#333')
    kawat(k, [(ox + 20, Y_12V), (ox + 670, Y_12V)], MERAH, 6)
    kawat(k, [(ox + 20, Y_GND), (ox + 670, Y_GND)], HITAM, 6)
    t(k, ox + 20, Y_12V - 14, '+12 V dari aki (lewat fuse 15-20 A)', 13, True, MERAH)
    t(k, ox + 20, Y_GND + 24, 'GND (minus aki)', 13, True)
    relay_sisi(k, ox, True, 'NAIK', 25, naik)
    relay_sisi(k, ox, False, 'TURUN', 26, not naik)
    # motor
    mx, my = ox + 345, Y_TENGAH
    k.out.append(f'<circle cx="{mx}" cy="{my}" r="40" fill="#e6f4ea" stroke="{HIJAU}" stroke-width="3"/>')
    t(k, mx, my + 9, 'M', 26, True, HIJAU, 'middle')
    t(k, mx, 352, 'arus motor', 12, True, ARUS, 'middle')
    t(k, mx, 370, 'kiri → kanan' if naik else 'kanan → kiri', 13, True, ARUS, 'middle')
    t(k, mx, 396, 'kabel NAIK  |  kabel TURUN', 11, False, '#555', 'middle')
    # keterangan
    if naik:
        baris = ['Relay NAIK menarik: kabel NAIK dapat +12 V.',
                 'Relay TURUN lepas: kabel TURUN tertahan di GND.',
                 'Beda tegangan 12 V di motor, arus dari kiri ke kanan.']
    else:
        baris = ['Relay TURUN menarik: kabel TURUN dapat +12 V.',
                 'Relay NAIK lepas: kabel NAIK tertahan di GND.',
                 'Beda tegangan 12 V di motor, arus dari kanan ke kiri (kebalikan).']
    for i, b in enumerate(baris):
        t(k, ox + 20, 600 + i * 19, b, 13, i == 2)


def arus_koil(k):
    y12, yg = 790, 1085
    t(k, 30, 718, 'ARUS KOIL (kecil): sama untuk kanal NAIK (GPIO25) dan TURUN (GPIO26)', 18, True, '#0b3d91')
    t(k, 30, 740, 'Arus ini hanya menyalakan koil relay. Arus motor yang besar ada di gambar atas, lewat kontak 30/87/87a.', 12, False, '#444')
    kawat(k, [(300, y12), (900, y12)], MERAH, 6)
    kawat(k, [(100, yg), (900, yg)], HITAM, 6)
    t(k, 300, y12 - 14, '+12 V (terminal 5)', 13, True, MERAH)
    t(k, 100, yg + 22, 'GND (terminal 6)', 13, True)
    # jalur koil
    titik(k, 640, y12, MERAH)
    kawat(k, [(640, y12), (640, 830)], ARUS, 5)
    k.out.append('<rect x="595" y="830" width="90" height="80" fill="#c8e6c9" stroke="#1a7f37" stroke-width="2"/>')
    t(k, 640, 866, 'KOIL', 13, True, anchor='middle')
    t(k, 640, 884, '≈80 Ω', 12, False, anchor='middle')
    t(k, 655, 818, 'kaki 85', 12, True)
    t(k, 700, 903, 'kaki 86', 12, True)
    kawat(k, [(640, 910), (640, 940)], ARUS, 5)
    kawat(k, [(640, 1020), (640, yg)], ARUS, 5)
    titik(k, 640, yg)
    # transistor
    k.out.append('<rect x="595" y="940" width="90" height="80" fill="#2b2b2b" stroke="#24292f" stroke-width="1.6"/>')
    t(k, 640, 976, 'PN2222A', 12, True, '#fff', 'middle')
    t(k, 640, 992, '(NPN)', 11, False, '#fff', 'middle')
    t(k, 604, 984, 'B', 12, True, '#8ab4ff')
    t(k, 662, 957, 'C', 12, True, '#8ab4ff')
    t(k, 662, 1013, 'E', 12, True, '#8ab4ff')
    # dioda paralel koil
    kawat(k, [(800, y12), (800, 840)], '#999', 3)
    titik(k, 800, y12, MERAH)
    k.out.append('<line x1="784" y1="840" x2="816" y2="840" stroke="#24292f" stroke-width="3"/>')
    k.out.append('<polygon points="800,840 786,880 814,880" fill="#fff" stroke="#24292f" stroke-width="2"/>')
    kawat(k, [(800, 880), (800, 925), (640, 925)], '#999', 3)
    titik(k, 640, 925, ARUS)
    t(k, 826, 855, 'Dioda 1N4007:', 12, True, '#555')
    t(k, 826, 871, 'tidak dialiri saat', 12, False, '#555')
    t(k, 826, 887, 'relay menyala', 12, False, '#555')
    # basis
    k.out.append(f'<circle cx="120" cy="980" r="11" fill="#fff" stroke="{BIRU}" stroke-width="2.5"/>')
    t(k, 120, 956, 'GPIO25 / GPIO26', 13, True, BIRU, 'middle')
    t(k, 120, 1004, '3,3 V saat HIGH', 12, False, '#444', 'middle')
    kawat(k, [(131, 980), (220, 980)], BIRU, 4)
    resistor(k, 260, 980, '470 Ω')
    kawat(k, [(300, 980), (595, 980)], BIRU, 4)
    titik(k, 470, 980, BIRU)
    resistor(k, 470, 1040, '', vertikal=True)
    t(k, 455, 1045, '10 kΩ', 13, anchor='end')
    kawat(k, [(470, 980), (470, 1005)], BIRU, 3)
    kawat(k, [(470, 1075), (470, yg)])
    titik(k, 470, yg)
    t(k, 330, 962, 'arus basis ≈5 mA', 12, True, BIRU)
    t(k, 700, 975, 'arus koil ≈150 mA', 12, True, MERAH)
    # panah
    panah(k, 170, 980, 'kanan', BIRU, 8)
    panah(k, 530, 980, 'kanan', BIRU, 8)
    panah(k, 470, y12, 'kanan', ARUS, 8)
    panah(k, 580, y12, 'kanan', ARUS, 8)
    panah(k, 640, 812, 'bawah', ARUS, 8)
    panah(k, 640, 928 - 4, 'bawah', ARUS, 8)
    panah(k, 640, 1055, 'bawah', ARUS, 8)
    # urutan
    langkah = ['Urutan kejadian:',
               '1. GPIO HIGH (3,3 V). Arus basis kecil mengalir:',
               '    GPIO → 470 Ω → basis → emitor → GND.',
               '2. Transistor menyala, kolektor tersambung ke GND.',
               '3. Arus koil mengalir: +12 V → kaki 85 → koil',
               '    → kaki 86 → kolektor → emitor → GND.',
               '4. Koil jadi magnet, tuas pindah: kaki 30 lepas dari',
               '    87a dan menempel ke 87.',
               '5. GPIO LOW: transistor mati, arus koil berhenti,',
               '    tuas kembali ke 87a.']
    for i, b in enumerate(langkah):
        t(k, 1005, 800 + i * 21, b, 13, i == 0)


def diagram11():
    k = Kanvas(W, H, 'Diagram 11. Arah arus dua relay 5 kaki untuk jendela (pola kaki 87a, Usulan)')
    k.out.append('<g transform="translate(0,40)">')
    panel(k, 5, True)
    panel(k, 705, False)
    k.out.append('<line x1="700" y1="20" x2="700" y2="660" stroke="#ccc" stroke-width="2" stroke-dasharray="4,6"/>')
    k.out.append('<rect x="30" y="662" width="1340" height="30" fill="#fffbe6" stroke="#d4a72c"/>')
    t(k, 46, 682, 'Diam: GPIO25 LOW dan GPIO26 LOW. Kedua tuas di 87a, kedua kabel motor ke GND, tidak ada beda tegangan, tidak ada arus. '
                  'Kedua HIGH dilarang di firmware.', 12, True, '#7a5b00')
    arus_koil(k)
    k.out.append('</g>')
    t(k, 30, H - 12, 'Merah tebal + panah = jalur arus (arah arus konvensional, dari + ke -). Abu-abu = kabel ada tetapi tidak dialiri. Pola 87a belum diuji, perlu konfirmasi teman hardware.', 12, False, '#444')
    k.simpan('diagram-11-arah-arus-relay-jendela.svg', legenda=False)


if __name__ == '__main__':
    diagram11()
    print('selesai')
