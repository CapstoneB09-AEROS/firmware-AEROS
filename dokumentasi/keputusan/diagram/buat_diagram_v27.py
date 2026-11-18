"""Membuat lima diagram firmware v2.7 (SVG dan PNG) dari firmware-v2/src/sensorOriginal.inl.

Cara pakai:  python3 buat_diagram_v27.py
Hasil     :  diagram-v27-1-alur-siklus.png, diagram-v27-2-pengolahan-sinyal.png,
             diagram-v27-3-mesin-status.png, diagram-v27-4-aturan-co.png,
             diagram-v27-5-aturan-co2.png   (dan berkas .svg dan .pdf vektor-nya)

Butuh Python 3 bawaan dan Google Chrome (untuk mengubah SVG menjadi PNG). Gaya dan bentuk
memakai kelas Kanvas dari buat_diagram.py. Isi diagram mengikuti kode v2.7, bukan rancangan lama:
nama fungsi dan angka di tiap kotak bisa dicari di sensorOriginal.inl.
"""
import os
import shutil
import subprocess

import buat_diagram as bd
from buat_diagram import Kanvas, FONT, esc

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def sub(t):
    """Teks aman untuk SVG; angka 2 subskrip Unicode dibuat subskrip SVG yang proporsional."""
    return esc(t).replace('\u2082', '<tspan baseline-shift="sub" font-size="75%">2</tspan>')


class K(Kanvas):
    def teks(self, cx, cy, baris, ukuran=14, tebal=False, warna='#111'):
        n = len(baris)
        y0 = cy - (n - 1) * bd.LH / 2 + 5
        tb = ' font-weight="bold"' if tebal else ''
        for i, b in enumerate(baris):
            self.out.append(f'<text x="{cx:.1f}" y="{y0 + i * bd.LH:.1f}" text-anchor="middle" font-family="{FONT}" '
                            f'font-size="{ukuran}" fill="{warna}"{tb}>{sub(b)}</text>')

    def lab(self, x, y, baris, anc='start', warna='#333', tebal=False, ukuran=13):
        tb = ' font-weight="bold"' if tebal else ''
        for i, b in enumerate(baris):
            self.out.append(f'<text x="{x:.1f}" y="{y + i * 16:.1f}" text-anchor="{anc}" font-family="{FONT}" '
                            f'font-size="{ukuran}" fill="{warna}"{tb}>{sub(b)}</text>')

    def kotak_putus(self, x, y, w, h, judul):
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="none" stroke="#999" '
                        f'stroke-width="1.4" stroke-dasharray="8,5"/>')
        self.lab(x + 12, y + 18, [judul], warna='#666', ukuran=12)

    def simpan2(self, nama):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                f'<defs><marker id="panah" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
                f'<polygon points="0,0 10,4 0,8" fill="#333"/></marker></defs>'
                f'<rect width="100%" height="100%" fill="#ffffff"/>'
                )
        with open(nama, 'w', encoding='utf-8') as f:
            f.write(head + '\n'.join(self.out) + '</svg>')
        png = nama.replace('.svg', '.png')
        if os.path.exists(CHROME):
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--default-background-color=FFFFFFFF',
                            f'--screenshot={os.path.abspath(png)}', f'--window-size={self.w},{self.h}',
                            '--force-device-scale-factor=2', 'file://' + os.path.abspath(nama)],
                           capture_output=True, timeout=120)
            # PDF vektor (tajam di semua ukuran): halaman seukuran gambar, tanpa margin
            pdf = nama.replace('.svg', '.pdf')
            html = nama.replace('.svg', '_tmp.html')
            isi = open(nama, encoding='utf-8').read()
            with open(html, 'w', encoding='utf-8') as f:
                f.write(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{self.w}px {self.h}px;margin:0}}'
                        f'html,body{{margin:0;padding:0}}svg{{display:block}}</style></head><body>{isi}</body></html>')
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                            f'--print-to-pdf={os.path.abspath(pdf)}', 'file://' + os.path.abspath(html)],
                           capture_output=True, timeout=120)
            os.remove(html)
        else:
            print('Chrome tidak ditemukan: hanya SVG dibuat')


# ---------------------------------------------------------------------------------
def d1():
    k = K(1120, 1420, 'Diagram 1. Alur siklus 1 detik (loop, firmware v2.7)')
    mx = 420
    st = k.oval(mx, 70, 280, 44, ['MULAI SIKLUS (tiap 1 detik)'])
    baca = k.jajar(mx, 150, 480, 54, ['Baca sensor CO₂ dan sensor CO'])
    val = k.persegi(mx, 250, 480, 54, ['Periksa apakah data kedua sensor valid'])
    hit = k.persegi(mx, 360, 480, 66, ['Hitung Rs, rata-ratakan (SMA 6), ubah menjadi estimasi CO.', 'CO₂ dipakai langsung, tanpa filter'])
    pan = k.persegi(mx, 470, 480, 50, ['Pemanasan 180 detik: pembacaan belum dipakai aturan'], 'abu')
    gg = k.belah(mx, 580, 340, 104, ['Kedua sensor gagal', 'atau tidak valid?'])
    dco = k.belah(mx, 710, 340, 104, ['CO siap dipakai?', '(pemanasan selesai, data valid)'])
    j1 = 800
    dco2 = k.belah(mx, 890, 340, 104, ['Aturan CO tidak aktif', 'dan CO₂ siap?'])
    j2 = 980
    stt = k.persegi(mx, 1050, 480, 50, ['Atur bunyi dan gerak jendela sesuai status'])
    sub_st = k.subalur(mx, 1140, 400, 54, ['STATUS CO dan CO₂'])
    kel = k.subalur(mx, 1230, 560, 66, ['KELUARAN', 'Tampilkan di LCD dan kirim ke jaringan'])
    tg = k.persegi(mx, 1325, 420, 44, ['Tunggu sampai tepat 1 detik'])

    gang = k.persegi(850, 580, 250, 84, ['status GANGGUAN', 'aturan CO dan CO₂ dilewati', 'tidak ada aksi otomatis'], 'merah')
    sco = k.subalur(850, 710, 250, 66, ['ATURAN CO'], 'oranye')
    sco2 = k.subalur(850, 890, 250, 66, ['ATURAN CO₂'], 'kuning')

    k.garis([st.bawah, baca.atas]); k.garis([baca.bawah, val.atas]); k.garis([val.bawah, hit.atas])
    k.garis([hit.bawah, pan.atas]); k.garis([pan.bawah, gg.atas])
    k.garis([gg.kanan, gang.kiri], 'YA')
    k.garis([gg.bawah, dco.atas], 'TIDAK')
    k.garis([dco.kanan, sco.kiri], 'YA')
    k.garis([dco.bawah, (mx, j1)], 'TIDAK', panah=False)
    k.garis([sco.bawah, (850, j1), (mx, j1)], panah=False)
    k.garis([(mx, j1), dco2.atas])
    k.garis([dco2.kanan, sco2.kiri], 'YA')
    k.garis([dco2.bawah, (mx, j2)], 'TIDAK', panah=False)
    k.garis([sco2.bawah, (850, j2), (mx, j2)], panah=False)
    k.garis([(mx, j2), stt.atas])
    k.garis([stt.bawah, sub_st.atas]); k.garis([sub_st.bawah, kel.atas])
    bus = 1070
    k.garis([gang.kanan, (bus, gang.cy), (bus, 1230), kel.kanan])
    k.garis([kel.bawah, tg.atas])
    k.garis([tg.kiri, (60, 1325), (60, 70), st.kiri], 'ulangi')
    k.lab(560, 1385, ['Bila hanya satu sensor gagal: status gas itu ERR, aturan gas yang sehat tetap jalan.'], ukuran=12, warna='#555')
    k.simpan2('diagram-v27-1-alur-siklus.svg')


# ---------------------------------------------------------------------------------
def d2():
    k = K(1500, 640, 'Diagram 2. Alur pengolahan sinyal (CO dan CO2, firmware v2.7)')
    xs = [110 + 178 * i for i in range(7)]
    yc, y2 = 170, 430
    k.lab(30, 80, ['JALUR CO (MiCS, estimasi)'], tebal=True, ukuran=15, warna='#b46504')
    k.lab(30, 320, ['JALUR CO₂ (MH-Z19C, nilai langsung)'], tebal=True, ukuran=15, warna='#0e8088')
    w, h = 148, 110
    co = [
        (['Sensor MiCS', '(hambatan Rs', 'berubah oleh gas)'], 'putih'),
        (['Baca tegangan', 'sensor'], 'putih'),
        (['Periksa', 'nilai wajar'], 'kuning'),
        (['Rs', '= RL (VCC - V) / V', 'RL = resistor beban', 'VCC = tegangan catu'], 'putih'),
        (['Filter SMA 6', 'rata-rata 6 nilai', 'Rs terakhir'], 'biru'),
        (['Rs / R0', 'R0 = Rs di udara', 'bersih (hasil', 'kalibrasi)'], 'putih'),
        (['ppm CO estimasi', 'kurva datasheet:', 'Rs/R0 = k x c^-β', 'k dan β konstanta'], 'oranye'),
    ]
    bs = []
    for x, (t, wr) in zip(xs, co):
        bs.append(k.persegi(x, yc, w, h, t, wr))
    for a, b in zip(bs, bs[1:]):
        k.garis([a.kanan, b.kiri])

    c2 = [
        (['Sensor MH-Z19C'], 'putih'),
        (['Terima paket', 'data CO₂'], 'putih'),
        (['Periksa header', 'dan checksum'], 'kuning'),
        (['Kadar CO₂', '(tanpa filter)'], 'teal'),
    ]
    b2 = []
    for x, (t, wr) in zip(xs[:4], c2):
        b2.append(k.persegi(x, y2, w, h, t, wr))
    for a, b in zip(b2, b2[1:]):
        k.garis([a.kanan, b.kiri])
    k.lab(xs[2] - 40, y2 + 78, ['bacaan gagal: CO₂ tidak', 'terbaca (status ERR)'], anc='middle', ukuran=11, warna='#555')
    k.lab(xs[3] + 50, y2 + 78, ['pemanasan 180 detik:', 'belum dipakai aturan'], anc='middle', ukuran=11, warna='#555')

    ar = k.subalur(1330, 300, 220, 130, ['ATURAN CO', 'ATURAN CO₂', 'dan STATUS'], 'abu')
    k.garis([bs[6].kanan, (1330, yc), ar.atas])
    k.garis([b2[3].kanan, (1330, y2), ar.bawah])
    k.simpan2('diagram-v27-2-pengolahan-sinyal.svg')


# ---------------------------------------------------------------------------------
def d3():
    k = K(1500, 780, 'Diagram 3. Mesin status (status CO dan CO2 memakai mesin yang sama, v2.7)')
    k.kotak_putus(30, 250, 1440, 190, '')
    k.lab(45, 428, ['Berlaku untuk tiap gas (CO dan CO2) secara terpisah. GANGGUAN bisa terjadi dari status mana pun di dalam kotak ini.'], ukuran=12, warna='#666')
    y = 345
    pem = k.persegi(140, y, 190, 76, ['PEMANASAN', '(WARMUP)', '180 detik'], 'abu')
    nor = k.persegi(470, y, 190, 76, ['NORMAL', '(OK)'], 'teal')
    was = k.persegi(940, y, 190, 76, ['WASPADA', '3 bip pendek'], 'kuning')
    bah = k.persegi(1360, y, 190, 76, ['BAHAYA', '1 bip panjang 3 detik'], 'oranye')
    awal = k.oval(140, 130, 150, 40, ['Alat menyala'])
    k.garis([awal.bawah, (140, y - 38)])
    # maju
    k.garis([pem.kanan, nor.kiri])
    k.lab(305, y - 22, ['180 detik berlalu'], anc='middle', warna='#444')
    ya = y - 14
    k.garis([(565, ya), (845, ya)])
    k.lab(705, ya - 36, ['CO >= 35 ppm selama 30 detik', 'atau CO2 >= 2500 ppm, 3 bacaan'], anc='middle')
    k.garis([(1035, ya), (1265, ya)])
    k.lab(1150, ya - 52, ['CO >= 87 ppm,', 'uji arah = sumber luar,', 'atau CO2 >= 4000 (3 bacaan)'], anc='middle')
    # balik WASPADA -> NORMAL
    yb = y + 16
    k.garis([(845, yb), (565, yb)])
    k.lab(705, yb + 22, ['selesai: CO < 30 ppm 60 detik', 'atau CO2 < 2500 ppm 10 detik'], anc='middle')
    # lompat langsung NORMAL -> BAHAYA (busur atas), dan BAHAYA -> NORMAL (busur dalam)
    k.garis([(420, y - 38), (420, 150), (1410, 150), (1410, y - 38)])
    k.lab(915, 140, ['langsung dari NORMAL: CO >= 87 ppm, atau CO2 >= 4000 ppm selama 3 bacaan'], anc='middle')
    k.garis([(1310, y - 38), (1310, 200), (520, 200), (520, y - 38)])
    k.lab(915, 193, ['selesai: CO < 30 ppm 60 detik, atau CO2 < 2500 ppm 10 detik'], anc='middle')
    # GANGGUAN
    gang = k.persegi(760, 640, 260, 90, ['GANGGUAN', 'kedua sensor gagal', 'tidak ada aksi otomatis'], 'merah')
    k.garis([(700, 440), (700, 640 - 45)])
    k.lab(690, 536, ['kedua sensor gagal', 'atau tidak valid'], anc='end', ukuran=12)
    k.garis([(820, 640 - 45), (820, 440)], putus=True)
    k.lab(830, 500, ['salah satu sensor terbaca lagi:', 'kembali ke status sebelumnya', '(level tidak dihapus)'], ukuran=12)
    k.lab(1060, 600, ['Bila hanya SATU sensor gagal: status gas itu', 'jadi ERR, gas lain tetap berjalan normal.', 'Status LUAR tampil bila CO', 'berasal dari luar kabin.'],
          ukuran=12, warna='#555')
    k.lab(30, 690, ['Keluaran per status:', 'WARMUP/ERR = angka gas itu tampil ---- atau n/a', 'OK = bunyi mati'], ukuran=12, warna='#555')
    k.simpan2('diagram-v27-3-mesin-status.svg')


# ---------------------------------------------------------------------------------
def d4():
    k = K(1620, 1760, 'Diagram 4. Aturan CO (aturanCO, firmware v2.7)')
    mx = 330
    st = k.oval(mx, 75, 340, 44, ['ATURAN CO (dipanggil tiap detik)'])
    a = k.belah(mx, 170, 300, 100, ['faseCO =', 'TIDAK_AKTIF?'])
    b = k.belah(mx, 300, 300, 100, ['ppm CO >= 87?'])
    c = k.belah(mx, 430, 300, 100, ['ppm CO >= 35?'])
    c1 = k.persegi(mx, 545, 300, 50, ['konfirmasiCO + 1 (detik)'])
    d = k.belah(mx, 660, 300, 100, ['konfirmasiCO >= 30?'])
    akt = k.persegi(mx, 810, 440, 150, ['AKTIFKAN', 'faseCO = UJI_ARAH,  rsAwalUji = Rs,  waktuUji = 0',
                                        'level WASPADA (konfirmasi) atau BAHAYA (>= 87)', 'bunyi CO dimulai', 'bukaJendela: GPIO26 HIGH (motor turun)'], 'oranye')
    sel = k.oval(mx, 925, 200, 40, ['Selesai'], 'teal')
    kon0 = k.persegi(660, 430, 230, 50, ['konfirmasiCO = 0'])
    sl1 = k.oval(660, 520, 150, 36, ['Selesai'], 'teal')
    tun = k.persegi(660, 660, 230, 50, ['masih menunggu konfirmasi'], 'abu')
    sl2 = k.oval(660, 750, 150, 36, ['Selesai'], 'teal')
    k.garis([st.bawah, a.atas]); k.garis([a.bawah, b.atas], 'YA')
    k.garis([b.bawah, c.atas], 'TIDAK')
    k.garis([b.kiri, (60, 300), (60, 810), akt.kiri], 'YA')
    k.garis([c.kanan, kon0.kiri], 'TIDAK'); k.garis([kon0.bawah, sl1.atas])
    k.garis([c.bawah, c1.atas], 'YA'); k.garis([c1.bawah, d.atas])
    k.garis([d.kanan, tun.kiri], 'TIDAK'); k.garis([tun.bawah, sl2.atas])
    k.garis([d.bawah, akt.atas], 'YA'); k.garis([akt.bawah, sel.atas])

    rx = 1090
    r1 = k.persegi(rx, 170, 320, 60, ['bila ppm >= 87: level BAHAYA', 'dan bunyi (naik level selalu berbunyi)'], 'oranye')
    r2 = k.belah(rx, 285, 300, 90, ['faseCO = UJI_ARAH?'])
    r3 = k.persegi(rx, 395, 260, 44, ['waktuUji + 1 (detik)'])
    r4 = k.belah(rx, 500, 300, 90, ['waktuUji >= 30 detik?'])
    r5 = k.belah(rx, 630, 320, 100, ['Rs naik lebih dari 25%', 'dari rsAwalUji?'])
    dalam = k.persegi(1405, 630, 230, 100, ['SUMBER_DALAM', 'CO turun, jendela', 'tetap terbuka'], 'kuning')
    luar = k.persegi(rx, 775, 380, 128, ['SUMBER_LUAR', '(Rs turun > 25% atau tidak jelas)', 'level BAHAYA, tutup jendela:', 'bip 0,5 detik, jeda 3 detik,', 'GPIO18 HIGH 5 detik'], 'oranye')
    j = 905
    k.garis([a.kanan, r1.kiri], 'TIDAK')
    k.garis([r1.bawah, r2.atas])
    bus = 1560
    k.garis([r2.bawah, r3.atas], 'YA')
    k.garis([r2.kanan, (bus, 285)], 'TIDAK', panah=False)
    k.garis([r3.bawah, r4.atas])
    k.garis([r4.kanan, (bus, 500)], 'TIDAK', panah=False)
    k.garis([r4.bawah, r5.atas], 'YA')
    k.garis([r5.kanan, dalam.kiri], 'YA')
    k.garis([r5.bawah, luar.atas], 'TIDAK')
    k.garis([dalam.kanan, (bus, 630)], panah=False)
    k.garis([(bus, 285), (bus, j), (rx, j)], panah=False)
    k.garis([luar.bawah, (rx, j)], panah=False)
    r6 = k.belah(rx, 1010, 300, 90, ['ppm CO < 30?'])
    k.garis([(rx, j), r6.atas])
    r7 = k.persegi(rx, 1120, 260, 44, ['pemulihanCO + 1 (detik)'])
    r8 = k.belah(rx, 1230, 300, 90, ['pemulihanCO >= 60?'])
    r9 = k.persegi(rx, 1390, 440, 130, ['SELESAI', 'faseCO = TIDAK_AKTIF,  level NORMAL', 'bunyi CO OFF,  reset penghitung',
                                         'tutup jendela (kecuali CO2 sedang TINDAKAN)'], 'teal')
    pem0 = k.persegi(1425, 1010, 210, 44, ['pemulihanCO = 0'])
    j2 = 1520
    k.garis([r6.bawah, r7.atas], 'YA')
    k.garis([r6.kanan, pem0.kiri], 'TIDAK')
    k.garis([pem0.kanan, (bus, 1010)], panah=False)
    k.garis([r7.bawah, r8.atas])
    k.garis([r8.bawah, r9.atas], 'YA')
    k.garis([r8.kanan, (bus, 1230)], 'TIDAK', panah=False)
    k.garis([(bus, 1010), (bus, j2), (rx, j2)], panah=False)
    k.garis([r9.bawah, (rx, j2)], panah=False)
    r10 = k.persegi(rx, 1610, 440, 56, ['Ulangi bunyi CO tiap 60 detik,', 'maksimum 5 menit'])
    sl = k.oval(rx, 1710, 180, 38, ['Selesai'], 'teal')
    k.garis([(rx, j2), r10.atas]); k.garis([r10.bawah, sl.atas])
    k.simpan2('diagram-v27-4-aturan-co.svg')


# ---------------------------------------------------------------------------------
def d5():
    k = K(1640, 1300, 'Diagram 5. Aturan CO2 dan siklus jendela (firmware v2.7)')
    mx = 370
    st = k.oval(mx, 75, 380, 44, ['ATURAN CO2 (faseCO TIDAK_AKTIF, CO2 siap)'])
    p1 = k.persegi(mx, 165, 460, 70, ['atasTindakan + 1 bila CO2 >= 4000, selain itu 0', 'atasPeringatan + 1 bila CO2 >= 2500, selain itu 0'])
    d2 = k.belah(mx, 300, 360, 110, ['atasTindakan >= 3 bacaan?'])
    d3 = k.belah(mx, 440, 400, 110, ['atasPeringatan >= 3 bacaan', 'dan faseCO2 = NORMAL?'])
    tind = k.persegi(830, 300, 290, 80, ['TINDAKAN (sekali)', 'faseCO2 = TINDAKAN', 'bunyi 1 bip panjang 3 detik'], 'oranye')
    per = k.persegi(830, 440, 290, 80, ['PERINGATAN (sekali)', 'faseCO2 = PERINGATAN', 'bunyi 3 bip pendek'], 'kuning')
    j1 = 560
    k.garis([st.bawah, p1.atas]); k.garis([p1.bawah, d2.atas])
    k.garis([d2.kanan, tind.kiri], 'YA'); k.garis([d2.bawah, d3.atas], 'TIDAK')
    k.garis([d3.kanan, per.kiri], 'YA')
    bus = 1010
    k.garis([tind.kanan, (bus, 300), (bus, j1), (mx, j1)], panah=False)
    k.garis([per.kanan, (bus, 440)], panah=False)
    k.garis([d3.bawah, (mx, j1)], 'TIDAK', panah=False)
    d4 = k.belah(mx, 670, 360, 100, ['faseCO2', 'tidak sama dengan NORMAL?'])
    k.garis([(mx, j1), d4.atas])
    s0 = k.oval(830, 670, 150, 38, ['Selesai'], 'teal')
    k.garis([d4.kanan, s0.kiri], 'TIDAK')
    d5 = k.belah(mx, 810, 360, 110, ['CO2 < 2500 ppm?'])
    k.garis([d4.bawah, d5.atas], 'YA')
    pm = k.persegi(mx, 925, 300, 46, ['pemulihanCO2 + 1 (detik)'])
    d6 = k.belah(mx, 1035, 360, 100, ['pemulihanCO2 >= 10?'])
    ok = k.persegi(mx, 1170, 440, 100, ['SELESAI', 'faseCO2 = NORMAL,  level NORMAL,  bunyi OFF', 'reset penghitung'], 'teal')
    sl = k.oval(mx, 1260, 180, 38, ['Selesai'], 'teal')
    p0 = k.persegi(830, 810, 250, 46, ['pemulihanCO2 = 0'])
    s1 = k.oval(830, 890, 150, 38, ['Selesai'], 'teal')
    w2 = k.persegi(830, 1035, 250, 46, ['masih menunggu'], 'abu')
    s2 = k.oval(830, 1110, 150, 38, ['Selesai'], 'teal')
    k.garis([d5.bawah, pm.atas], 'YA'); k.garis([pm.bawah, d6.atas])
    k.garis([d5.kanan, p0.kiri], 'TIDAK'); k.garis([p0.bawah, s1.atas])
    k.garis([d6.kanan, w2.kiri], 'TIDAK'); k.garis([w2.bawah, s2.atas])
    k.garis([d6.bawah, ok.atas], 'YA'); k.garis([ok.bawah, sl.atas])

    # panel siklus jendela
    px = 1370
    k.kotak_putus(1090, 40, 530, 1010, 'SIKLUS JENDELA (gBahayaCO2 = TINDAKAN, gAmanCO2 = NORMAL)')
    atas = k.persegi(px, 130, 330, 70, ['ATAS', 'jendela dianggap tertutup', 'GPIO26 dan GPIO18 LOW'], 'teal')
    turun = k.persegi(px, 330, 330, 70, ['TURUN', 'GPIO26 HIGH 1,5 detik', '(motor turun, jendela terbuka)'], 'oranye')
    bawah = k.persegi(px, 520, 330, 70, ['BAWAH', 'GPIO26 LOW, jendela terbuka', 'menunggu CO2 aman'], 'kuning')
    pra = k.persegi(px, 710, 330, 70, ['PRA-TUTUP', 'bip 0,5 detik,', 'jeda 3 detik'], 'putih')
    naik = k.persegi(px, 900, 330, 70, ['NAIK', 'GPIO18 HIGH 5 detik', '(motor naik, jendela tertutup)'], 'teal')
    k.garis([atas.bawah, turun.atas]); k.lab(px + 12, 232, ['gBahayaCO2 dan LOW', 'sudah >= 1 detik'])
    k.garis([turun.bawah, bawah.atas]); k.lab(px + 12, 428, ['timer 1,5 detik habis'])
    k.garis([bawah.bawah, pra.atas]); k.lab(px + 12, 618, ['gAmanCO2 dan LOW >= 1 detik'])
    k.garis([pra.bawah, naik.atas]); k.lab(px + 12, 808, ['bip dan jeda selesai'])
    k.garis([naik.kanan, (1590, 900), (1590, 130), atas.kanan]); k.out.append(f'<text transform="translate(1578,520) rotate(-90)" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#333">timer 5 detik habis</text>')
    k.garis([pra.kiri, (1130, 710), (1130, 520), bawah.kiri], putus=True)
    k.lab(1125, 612, ['batal:', 'CO2 tidak', 'lagi aman'], anc='end', ukuran=11, warna='#555')
    k.simpan2('diagram-v27-5-aturan-co2.svg')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for f in (d1, d2, d3, d4, d5):
        f()
    for asal, nama in (('diagram-v27-1-alur-siklus.pdf', 'fw_siklus.pdf'), ('diagram-v27-2-pengolahan-sinyal.pdf', 'fw_pengolahan.pdf')):
        if os.path.exists(asal):
            shutil.copyfile(asal, nama)   # nama yang dipakai laporan LaTeX
    print('selesai: 5 diagram v2.7')
