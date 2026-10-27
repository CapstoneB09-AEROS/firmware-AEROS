"""Membuat Diagram Aliran Data (DFD) untuk rancangan-data.md.

Cara pakai:  python3 buat_dfd.py
Hasil     :  dfd-0-konteks.svg/.png, dfd-1a-perangkat.svg/.png, dfd-1b-backend-aplikasi.svg/.png

Notasi (gaya DeMarco/Yourdon): persegi abu-abu = entitas luar, persegi bulat bernomor = proses,
dua garis sejajar = penyimpanan data, panah berlabel = aliran data.
Status: PERKIRAAN. Bagian backend dan aplikasi dipegang anggota tim lain.
"""
import os
from buat_diagram import Kanvas, Bentuk, esc, ekspor_png, FONT, LH


class DFD(Kanvas):
    def entitas(s, cx, cy, w, h, baris, putus=False):
        extra = ' stroke-dasharray="6,4"' if putus else ''
        s.out.append(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" fill="#e8e8e8" stroke="#444" stroke-width="2.2"{extra}/>')
        s.teks(cx, cy, baris, tebal=False)
        return Bentuk(cx, cy, w, h)

    def proses(s, cx, cy, w, h, nomor, baris, warna='putih'):
        f, st = {'putih': ('#ffffff', '#2b5fa8'), 'biru': ('#dae8fc', '#2b5fa8'), 'kuning': ('#fff2cc', '#b8922a'),
                 'teal': ('#b0e3e6', '#0e8088')}[warna]
        s.out.append(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="16" ry="16" fill="{f}" stroke="{st}" stroke-width="2"/>')
        s.out.append(f'<line x1="{cx - w / 2}" y1="{cy - h / 2 + 24}" x2="{cx + w / 2}" y2="{cy - h / 2 + 24}" stroke="{st}" stroke-width="1.2"/>')
        s.out.append(f'<text x="{cx}" y="{cy - h / 2 + 17}" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="bold" fill="#111">{esc(nomor)}</text>')
        n = len(baris)
        ytop = cy - h / 2 + 24
        ym = (ytop + cy + h / 2) / 2
        y0 = ym - (n - 1) * LH / 2 + 5
        for i, b in enumerate(baris):
            s.out.append(f'<text x="{cx}" y="{y0 + i * LH:.1f}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#111">{esc(b)}</text>')
        return Bentuk(cx, cy, w, h)

    def simpan_data(s, cx, cy, w, h, kode, baris):
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
        s.out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#fffbe6" stroke="none"/>')
        s.out.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#7a5c00" stroke-width="2.2"/>')
        s.out.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#7a5c00" stroke-width="2.2"/>')
        s.out.append(f'<line x1="{x0 + 38}" y1="{y0}" x2="{x0 + 38}" y2="{y1}" stroke="#7a5c00" stroke-width="1.6"/>')
        s.out.append(f'<text x="{x0 + 19}" y="{cy + 5}" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="bold" fill="#111">{esc(kode)}</text>')
        n = len(baris)
        yy = cy - (n - 1) * LH / 2 + 5
        for i, b in enumerate(baris):
            s.out.append(f'<text x="{(x0 + 38 + x1) / 2}" y="{yy + i * LH:.1f}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#111">{esc(b)}</text>')
        return Bentuk(cx, cy, w, h)

    def alir(s, titik, label=None, seg=None, dx=0, dy=0, panah=True):
        """Panah berlabel. seg = indeks segmen tempat label diletakkan (bawaan: segmen terpanjang)."""
        d = 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in titik)
        mk = ' marker-end="url(#panah)"' if panah else ''
        s.out.append(f'<path d="{d}" fill="none" stroke="#333" stroke-width="1.7"{mk}/>')
        if label:
            baris = label.split('\n')
            if seg is None:
                seg = max(range(len(titik) - 1), key=lambda i: abs(titik[i + 1][0] - titik[i][0]) + abs(titik[i + 1][1] - titik[i][1]))
            (x0, y0), (x1, y1) = titik[seg], titik[seg + 1]
            mx, my = (x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy
            lw = max(len(b) for b in baris) * 6.3 + 10
            lh = len(baris) * 15 + 4
            s.out.append(f'<rect x="{mx - lw / 2:.1f}" y="{my - lh / 2:.1f}" width="{lw:.1f}" height="{lh}" fill="#ffffff" fill-opacity="0.92"/>')
            for i, b in enumerate(baris):
                s.out.append(f'<text x="{mx:.1f}" y="{my - lh / 2 + 13 + i * 15:.1f}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#222">{esc(b)}</text>')

    def legenda(s):
        lx, ly = s.w - 430, 34
        s.out.append(f'<rect x="{lx}" y="{ly}" width="410" height="56" fill="#fafafa" stroke="#bbb"/>')
        s.out.append(f'<rect x="{lx + 10}" y="{ly + 10}" width="26" height="16" fill="#e8e8e8" stroke="#444" stroke-width="2"/>')
        s.out.append(f'<text x="{lx + 42}" y="{ly + 23}" font-family="{FONT}" font-size="11">entitas luar</text>')
        s.out.append(f'<rect x="{lx + 120}" y="{ly + 10}" width="26" height="16" rx="5" fill="#fff" stroke="#2b5fa8" stroke-width="2"/>')
        s.out.append(f'<text x="{lx + 152}" y="{ly + 23}" font-family="{FONT}" font-size="11">proses</text>')
        s.out.append(f'<line x1="{lx + 215}" y1="{ly + 10}" x2="{lx + 241}" y2="{ly + 10}" stroke="#7a5c00" stroke-width="2"/>')
        s.out.append(f'<line x1="{lx + 215}" y1="{ly + 26}" x2="{lx + 241}" y2="{ly + 26}" stroke="#7a5c00" stroke-width="2"/>')
        s.out.append(f'<text x="{lx + 247}" y="{ly + 23}" font-family="{FONT}" font-size="11">penyimpanan data</text>')
        s.out.append(f'<text x="{lx + 10}" y="{ly + 46}" font-family="{FONT}" font-size="11" fill="#a33">PERKIRAAN: backend dan aplikasi dipegang tim lain</text>')

    def simpan_dfd(s, nama):
        s.legenda()
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.w}" height="{s.h}" viewBox="0 0 {s.w} {s.h}">'
                f'<defs><marker id="panah" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
                f'<polygon points="0,0 10,4 0,8" fill="#333"/></marker></defs>'
                f'<rect width="100%" height="100%" fill="#ffffff"/>'
                f'<text x="{s.w / 2 - 120}" y="22" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="bold" fill="#111">{esc(s.judul)}</text>')
        with open(nama, 'w', encoding='utf-8') as f:
            f.write(head + '\n'.join(s.out) + '</svg>')
        ekspor_png(nama, s.w, s.h)


def dfd0():
    k = DFD(1300, 700, 'DFD Level 0. Diagram konteks sistem AEROS')
    e1 = k.entitas(170, 230, 210, 80, ['Sensor MiCS-5524', '+ ADS1115'])
    e2 = k.entitas(170, 470, 210, 80, ['Sensor MH-Z19C'])
    p0 = k.proses(650, 350, 280, 170, '0', ['Sistem AEROS', '(ESP32, MQTT,', 'database, aplikasi)'], 'biru')
    e3 = k.entitas(1130, 230, 230, 90, ['Aktuator', '(jendela, buzzer, LCD)'])
    e4 = k.entitas(1130, 510, 230, 90, ['Pengemudi', '(aplikasi mobile)'])
    k.alir([e1.kanan, (400, 230), (400, 305), (510, 305)], 'tegangan MiCS (mV)', seg=0, dy=-14)
    k.alir([e2.kanan, (400, 470), (400, 395), (510, 395)], 'angka CO2 (ppm, UART)', seg=0, dy=-14)
    k.alir([(790, 305), (900, 305), (900, 230), e3.kiri], 'perintah jendela,\nbunyi, teks LCD', seg=2, dy=-22, dx=-8)
    k.alir([(790, 385), (880, 385), (880, 485), (1015, 485)], 'telemetri, peringatan,\nriwayat', seg=2, dy=-24)
    k.alir([(1015, 535), (840, 535), (840, 405), (790, 405)], 'konfirmasi "Saya Tahu"', seg=0, dy=16)
    k.simpan_dfd('dfd-0-konteks.svg')


def dfd1a():
    k = DFD(1640, 940, 'DFD Level 1A. Perangkat (ESP32 dan firmware)')
    o = 80  # geser kolom proses ke kanan agar label di sisi sensor muat
    e1 = k.entitas(110, 160, 190, 70, ['Sensor MiCS-5524', '+ ADS1115'])
    e2 = k.entitas(110, 360, 190, 70, ['Sensor MH-Z19C'])
    p11 = k.proses(430 + o, 260, 230, 110, '1.1', ['Akuisisi dan', 'validasi sensor'])
    p12 = k.proses(780 + o, 260, 240, 110, '1.2', ['Pengolahan sinyal', '(SMA 6, ppm CO)'])
    p13 = k.proses(1140 + o, 260, 250, 120, '1.3', ['Logika keputusan', '(aturan CO, CO2,', 'prioritas)'], 'kuning')
    p14 = k.proses(1140 + o, 560, 250, 110, '1.4', ['Aktuasi dan', 'tampilan'])
    p15 = k.proses(780 + o, 590, 240, 110, '1.5', ['Agregasi 5 detik dan', 'pengiriman data'])
    d6 = k.simpan_data(780 + o, 90, 240, 44, 'D6', ['memori NVS: R0'])
    d5 = k.simpan_data(430 + o, 470, 270, 44, 'D5', ['log serial CSV (lokal)'])
    e3 = k.entitas(1450 + o, 560, 170, 90, ['Aktuator', '(jendela,', 'buzzer, LCD)'])
    mq = k.entitas(780 + o, 830, 300, 70, ['Broker MQTT', '(lihat DFD 1B)'], putus=True)

    k.alir([e1.kanan, (300, 160), (300, 235), (p11.kiri[0], 235)], 'tegangan (mV)', seg=0, dy=-14)
    k.alir([e2.kanan, (300, 360), (300, 285), (p11.kiri[0], 285)], 'angka CO2 (ppm)', seg=0, dy=-14)
    k.alir([(545 + o, 260), (660 + o, 260)], 'data tervalidasi\n(V_mV, CO2,\nflag valid)', dy=-52)
    k.alir([(900 + o, 260), (1015 + o, 260)], 'Rs, ppm CO,\nCO2, flag', dy=-34)
    k.alir([(1140 + o, 320), (1140 + o, 505)], 'status dan perintah\n(jendela, bunyi, pesan)')
    k.alir([d6.bawah, (780 + o, 205)], 'R0', dx=18)
    k.alir([(690 + o, 315), (690 + o, 470), (565 + o, 470)], 'baris CSV\ntiap detik', seg=1, dy=-22)
    k.alir([(1050 + o, 320), (1050 + o, 430), (850 + o, 430), (850 + o, 535)], 'status dan kejadian\n(event)', seg=1, dy=-14)
    k.alir([(760 + o, 315), (760 + o, 535)], 'nilai terhitung', dy=-60)
    k.alir([(1265 + o, 560), (1365 + o, 560)], 'perintah,\nteks LCD', dy=-30)
    k.alir([(780 + o, 645), (780 + o, 795)], 'telemetri 5 detik\ndan pesan kejadian')
    k.alir([(930 + o, 830), (1140 + o, 830), (1140 + o, 615)], 'perintah ack\n("Saya Tahu")', seg=0, dy=-16)
    k.simpan_dfd('dfd-1a-perangkat.svg')


def dfd1b():
    k = DFD(1560, 920, 'DFD Level 1B. Backend (MQTT, database) dan aplikasi (mengikuti skema tim)')
    e1 = k.entitas(110, 190, 170, 80, ['Perangkat ESP32', '(dari DFD 1A)'])
    p21 = k.proses(400, 190, 220, 110, '2.1', ['Broker MQTT', '(terima dan', 'teruskan pesan)'])
    p22 = k.proses(760, 190, 240, 120, '2.2', ['Penyimpan data', '(validasi, cap waktu,', 'simpan)'])
    d5 = k.simpan_data(250, 420, 200, 44, 'D5', ['devices'])
    d4 = k.simpan_data(490, 420, 220, 44, 'D4', ['device_state'])
    d1 = k.simpan_data(730, 420, 230, 44, 'D1', ['sensor_readings'])
    d2 = k.simpan_data(970, 420, 210, 44, 'D2', ['alert_logs'])
    d3 = k.simpan_data(1220, 420, 230, 44, 'D3', ['actuator_logs'])
    p23 = k.proses(330, 660, 230, 110, '2.3', ['Penghapusan', 'data terjadwal'])
    p24 = k.proses(760, 660, 240, 110, '2.4', ['Layanan data', '(realtime dan riwayat)'])
    p25 = k.proses(1130, 660, 240, 120, '2.5', ['Aplikasi mobile', '(tampil, notifikasi,', 'konfirmasi)'], 'teal')
    e2 = k.entitas(1440, 660, 150, 80, ['Pengemudi'])

    k.alir([e1.kanan, p21.kiri], 'telemetri,\nkejadian', dy=-34)
    k.alir([(340, 135), (340, 95), (110, 95), (110, 150)], 'perintah ack', seg=1, dy=-12)
    k.alir([p21.kanan, p22.kiri], 'pesan telemetri\ndan kejadian', dy=-34)
    k.alir([(650, 250), (650, 300), (250, 300), (250, 398)], 'referensi perangkat', seg=1, dy=-12)
    k.alir([(690, 250), (690, 345), (490, 345), (490, 398)], 'perbarui status\nterkini', seg=1, dy=26)
    k.alir([(760, 250), (760, 398)], 'telemetri', dx=34)
    k.alir([(840, 250), (840, 345), (970, 345), (970, 398)], 'alert baru\ndan selesai', seg=1, dy=-24)
    k.alir([(880, 190), (1220, 190), (1220, 398)], 'log aktuator', seg=0, dy=-12)
    k.alir([(330, 605), (330, 550), (660, 550), (660, 442)], 'hapus data lebih dari 7 hari', seg=1, dy=22)
    k.alir([(490, 442), (490, 490), (700, 490), (700, 605)], 'status terkini', seg=1, dy=-12)
    k.alir([(790, 442), (790, 605)], 'riwayat sensor', dx=48)
    k.alir([(970, 442), (970, 560), (850, 560), (850, 605)], 'alert dan log', seg=1, dy=-12)
    k.alir([(1220, 442), (1220, 560), (970, 560)], None, panah=False)
    k.alir([p24.kanan, p25.kiri], 'data realtime\ndan riwayat', dy=-34)
    k.alir([(1250, 635), (1365, 635)], 'tampilan,\nnotifikasi', dy=-28)
    k.alir([(1365, 685), (1250, 685)], 'konfirmasi', dy=14)
    k.alir([(1170, 600), (1170, 520), (1030, 520), (1030, 442)], 'acknowledged_at', seg=1, dy=-12)
    k.alir([(1070, 720), (1070, 850), (40, 850), (40, 55), (400, 55), (400, 135)], 'perintah ack (ke broker)', seg=1, dy=-14)
    k.simpan_dfd('dfd-1b-backend-aplikasi.svg')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    dfd0()
    dfd1a()
    dfd1b()
    print('selesai: 3 DFD dibuat')
