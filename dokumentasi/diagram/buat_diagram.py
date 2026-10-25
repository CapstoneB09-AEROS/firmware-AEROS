"""Membuat diagram alur algoritma (SVG) untuk pseudocode-baru.md.

Cara pakai:  python3 buat_diagram.py
Hasil     :  diagram-1-alur-utama.svg, diagram-2-aturan-co-pemicu.svg,
             diagram-3-aturan-co-uji-arah.svg, diagram-4-aturan-co2.svg

Hanya memakai Python 3 bawaan. Gaya mengikuti contoh Gambar 8.11 di dokumen C-251:
oval = awal/akhir, jajar genjang = data masuk, persegi = proses, persegi bergaris ganda = sub-alur,
belah ketupat = keputusan, oranye = waspada, kuning = peringatan, hijau kebiruan = normal.
Tanda [Bn] menunjukkan bagian yang belum fix (lihat pseudocode-baru.md bagian 5).
"""
import os

FONT = "Helvetica, Arial, sans-serif"
LH = 18  # tinggi baris teks

FILL = {
    'putih': ('#ffffff', '#333333'),
    'oranye': ('#fad7ac', '#b46504'),
    'kuning': ('#fff2cc', '#b8922a'),
    'teal': ('#b0e3e6', '#0e8088'),
    'merah': ('#f8cecc', '#b85450'),
    'abu': ('#eeeeee', '#666666'),
    'biru': ('#dae8fc', '#5b7fb5'),
}


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class Bentuk:
    def __init__(s, cx, cy, w, h):
        s.cx, s.cy, s.w, s.h = cx, cy, w, h

    @property
    def atas(s): return (s.cx, s.cy - s.h / 2)
    @property
    def bawah(s): return (s.cx, s.cy + s.h / 2)
    @property
    def kiri(s): return (s.cx - s.w / 2, s.cy)
    @property
    def kanan(s): return (s.cx + s.w / 2, s.cy)


class Kanvas:
    def __init__(s, w, h, judul):
        s.w, s.h, s.judul, s.out = w, h, judul, []

    def teks(s, cx, cy, baris, ukuran=14, tebal=False, warna='#111'):
        n = len(baris)
        y0 = cy - (n - 1) * LH / 2 + 5
        tb = ' font-weight="bold"' if tebal else ''
        for i, b in enumerate(baris):
            s.out.append(
                f'<text x="{cx:.1f}" y="{y0 + i * LH:.1f}" text-anchor="middle" font-family="{FONT}" '
                f'font-size="{ukuran}" fill="{warna}"{tb}>{esc(b)}</text>')

    def _warna(s, w):
        f, st = FILL[w]
        return f'fill="{f}" stroke="{st}" stroke-width="1.6"'

    def oval(s, cx, cy, w, h, baris, warna='putih'):
        s.out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{w / 2}" ry="{h / 2}" {s._warna(warna)}/>')
        s.teks(cx, cy, baris)
        return Bentuk(cx, cy, w, h)

    def persegi(s, cx, cy, w, h, baris, warna='putih'):
        s.out.append(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" {s._warna(warna)}/>')
        s.teks(cx, cy, baris)
        return Bentuk(cx, cy, w, h)

    def subalur(s, cx, cy, w, h, baris, warna='putih'):
        b = s.persegi(cx, cy, w, h, baris, warna)
        st = FILL[warna][1]
        for dx in (-w / 2 + 12, w / 2 - 12):
            s.out.append(f'<line x1="{cx + dx}" y1="{cy - h / 2}" x2="{cx + dx}" y2="{cy + h / 2}" stroke="{st}" stroke-width="1.6"/>')
        return b

    def jajar(s, cx, cy, w, h, baris, warna='putih'):
        k = 20
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
        pts = f'{x0 + k},{y0} {x1},{y0} {x1 - k},{y1} {x0},{y1}'
        s.out.append(f'<polygon points="{pts}" {s._warna(warna)}/>')
        s.teks(cx, cy, baris)
        return Bentuk(cx, cy, w, h)

    def belah(s, cx, cy, w, h, baris, warna='biru'):
        pts = f'{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}'
        s.out.append(f'<polygon points="{pts}" {s._warna(warna)}/>')
        s.teks(cx, cy, baris)
        return Bentuk(cx, cy, w, h)

    def garis(s, titik, label=None, lpos=None, warna='#333', panah=True, putus=False):
        d = 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in titik)
        extra = ' stroke-dasharray="6,4"' if putus else ''
        marker = ' marker-end="url(#panah)"' if panah else ''
        s.out.append(f'<path d="{d}" fill="none" stroke="{warna}" stroke-width="1.6"{extra}{marker}/>')
        if label:
            (x0, y0), (x1, y1) = titik[0], titik[1]
            dx, dy = x1 - x0, y1 - y0
            if abs(dy) >= abs(dx):
                lx, ly, anc = x0 + 10, y0 + (20 if dy > 0 else -8), 'start'
            elif dx > 0:
                lx, ly, anc = x0 + 12, y0 - 8, 'start'
            else:
                lx, ly, anc = x0 - 12, y0 - 8, 'end'
            if lpos:
                lx, ly = lpos
            s.out.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anc}" font-family="{FONT}" font-size="13" font-weight="bold" fill="{warna}">{esc(label)}</text>')

    def catatan(s, x, y, baris, warna='#555'):
        for i, b in enumerate(baris):
            s.out.append(f'<text x="{x}" y="{y + i * 16}" font-family="{FONT}" font-size="12" fill="{warna}">{esc(b)}</text>')

    def simpan(s, nama, legenda=True):
        if legenda:
            lx, ly = s.w - 400, 34
            s.out.append(f'<rect x="{lx}" y="{ly}" width="380" height="56" fill="#fafafa" stroke="#bbb"/>')
            for i, (w, t) in enumerate([('oranye', 'waspada / tindakan'), ('kuning', 'peringatan'), ('teal', 'normal / selesai')]):
                f, st = FILL[w]
                xx = [lx + 10, lx + 150, lx + 250][i]
                s.out.append(f'<rect x="{xx}" y="{ly + 10}" width="16" height="12" fill="{f}" stroke="{st}"/>')
                s.out.append(f'<text x="{xx + 22}" y="{ly + 21}" font-family="{FONT}" font-size="11" fill="#333">{t}</text>')
            s.out.append(f'<text x="{lx + 10}" y="{ly + 44}" font-family="{FONT}" font-size="11" fill="#333">[Bn] = bagian belum fix (lihat pseudocode-baru.md bagian 5)</text>')
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.w}" height="{s.h}" viewBox="0 0 {s.w} {s.h}">'
                f'<defs><marker id="panah" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
                f'<polygon points="0,0 10,4 0,8" fill="#333"/></marker></defs>'
                f'<rect width="100%" height="100%" fill="#ffffff"/>'
                f'<text x="{s.w / 2}" y="22" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="bold" fill="#111">{esc(s.judul)}</text>')
        with open(nama, 'w', encoding='utf-8') as f:
            f.write(head + '\n'.join(s.out) + '</svg>')
        ekspor_png(nama, s.w, s.h)


def ekspor_png(nama_svg, w, h):
    """Membuat PNG lewat Quick Look macOS (butuh qlmanage dan sips). Dilewati bila tidak ada."""
    import shutil, subprocess
    if not (shutil.which('qlmanage') and shutil.which('sips')):
        return
    m = max(w, h)
    isi = open(nama_svg, encoding='utf-8').read()
    isi = isi.replace(f'width="{w}" height="{h}" viewBox="0 0 {w} {h}"', f'width="{m}" height="{m}" viewBox="0 0 {m} {m}"', 1)
    tmp = nama_svg.replace('.svg', '_tmp.svg')
    open(tmp, 'w', encoding='utf-8').write(isi)
    ukuran = int(m * 1.6)
    subprocess.run(['qlmanage', '-t', '-s', str(ukuran), '-o', '.', tmp], capture_output=True)
    hasil = tmp + '.png'
    if os.path.exists(hasil):
        png = nama_svg.replace('.svg', '.png')
        subprocess.run(['sips', '-c', str(int(h * ukuran / m)), str(int(w * ukuran / m)),
                        '--cropOffset', '1', '1', hasil, '--out', png], capture_output=True)
        os.remove(hasil)
    os.remove(tmp)


def diagram1():
    k = Kanvas(1180, 1290, 'Diagram 1. Alur utama (setiap 1 detik)')
    mx = 450
    start = k.oval(mx, 70, 140, 44, ['MULAI'])
    baca = k.jajar(mx, 150, 380, 56, ['Baca CO2 (MH-Z19C) dan', 'tegangan MiCS (ADS1115)'])
    valid = k.belah(mx, 265, 320, 110, ['Kedua sensor', 'gagal atau tidak valid?'])
    hitung = k.persegi(mx, 390, 400, 84, ['Rs  >  filter SMA 6  >  rasio Rs/R0  >  ppm CO',
                                          'CO2 = angka sensor (tanpa filter)', '[B1] [B12]  baca ulang bila saturasi'])
    panas = k.belah(mx, 510, 320, 110, ['Masih masa', 'pemanasan?  [B11]'])
    sub_co = k.subalur(mx, 630, 400, 60, ['ATURAN CO', '(diagram 2 dan 3)'])
    aktif = k.belah(mx, 745, 320, 100, ['Aturan CO aktif?'])
    sub_co2 = k.subalur(mx, 860, 400, 60, ['ATURAN CO2', '(diagram 4)'])
    act2 = k.persegi(mx, 960, 400, 66, ['Aktuator mengikuti aturan CO2', '(2500: bunyi singkat, 4000: bunyi + buka jendela)'], 'kuning')
    keluar = k.subalur(mx, 1070, 620, 70, ['KELUARAN', 'LCD, serial CSV, kirim data (5 detik atau saat status berubah)  [B14] [B18]'])
    tunggu = k.persegi(mx, 1165, 340, 44, ['Tunggu sampai tepat 1 detik'])

    # kolom kanan
    gang = k.persegi(850, 265, 250, 84, ['status GANGGUAN', 'tidak ada aksi otomatis', '(kedua sensor gagal)  [B10]'], 'merah')
    nopanas = k.persegi(850, 510, 250, 60, ['tidak ada alarm', '(sensor masih memanas)'], 'abu')
    actco = k.persegi(850, 745, 250, 84, ['Aktuator mengikuti', 'aturan CO', '(aturan CO2 diabaikan)'], 'oranye')

    k.garis([start.bawah, baca.atas])
    k.garis([baca.bawah, valid.atas])
    k.garis([valid.bawah, hitung.atas], 'TIDAK')
    k.garis([valid.kanan, gang.kiri], 'YA')
    k.garis([hitung.bawah, panas.atas])
    k.garis([panas.kanan, nopanas.kiri], 'YA')
    k.garis([panas.bawah, sub_co.atas], 'TIDAK')
    k.garis([sub_co.bawah, aktif.atas])
    k.garis([aktif.kanan, actco.kiri], 'YA')
    k.garis([aktif.bawah, sub_co2.atas], 'TIDAK')
    k.garis([sub_co2.bawah, act2.atas])
    k.garis([act2.bawah, keluar.atas])
    # jalur kanan menuju KELUARAN lewat bus x=1100
    bus = 1100
    for b in (gang, nopanas, actco):
        k.garis([b.kanan, (bus, b.cy)], panah=False)
    k.garis([(bus, gang.cy), (bus, 1070), (keluar.kanan[0], 1070)])
    k.garis([keluar.bawah, tunggu.atas])
    k.garis([tunggu.kiri, (60, 1165), (60, 70), (start.kiri[0], 70)], 'ulangi')
    k.catatan(690, 860, ['Bila hanya SATU sensor gagal: tampilkan', 'peringatan sensor itu, aturan sensor yang', 'sehat tetap berjalan sesuai aturannya  [B10]'])
    k.catatan(560, 1230, ['Tombol "Saya Tahu" mematikan bunyi; bunyi juga mati sendiri setelah 5 menit  [B15]'])
    k.simpan('diagram-1-alur-utama.svg')


def diagram2():
    k = Kanvas(1250, 1010, 'Diagram 2. Aturan CO: pemicu')
    mx = 420
    start = k.oval(mx, 70, 200, 44, ['ATURAN CO'])
    a = k.belah(mx, 175, 320, 100, ['faseCO =', 'TIDAK_AKTIF?'])
    b = k.belah(mx, 310, 340, 100, ['ppmCO  >=  87 ppm (bahaya)?'])
    c = k.belah(mx, 450, 340, 100, ['ppmCO  >=  35 ppm (estimasi)?'])
    c1 = k.persegi(mx, 570, 300, 50, ['konfirmasiCO = konfirmasiCO + 1 detik'])
    d = k.belah(mx, 690, 340, 100, ['konfirmasiCO  >=  30 detik?', '[B3]'])
    akt = k.persegi(mx, 840, 400, 130, ['AKTIFKAN', 'faseCO = UJI_ARAH', 'bunyi CO ON,  jendela BUKA', 'rsAwalUji = Rs sekarang,  waktuUji = 0', '(bahaya 87 ppm: bunyi LEBIH KERAS)'], 'oranye')
    sel = k.oval(mx, 950, 300, 40, ['Selesai (kembali ke alur utama)'], 'teal')

    sub = k.subalur(880, 175, 340, 70, ['Uji arah dan pemulihan', '(diagram 3)'])
    selb = k.oval(880, 270, 220, 40, ['Selesai'], 'teal')
    kon0 = k.persegi(880, 450, 250, 50, ['konfirmasiCO = 0'])
    sel2 = k.oval(880, 540, 160, 40, ['Selesai'], 'teal')
    tunggu = k.persegi(880, 690, 250, 50, ['(masih menunggu konfirmasi)'], 'abu')
    sel3 = k.oval(880, 780, 160, 40, ['Selesai'], 'teal')

    k.garis([start.bawah, a.atas])
    k.garis([a.kanan, sub.kiri], 'TIDAK')
    k.garis([sub.bawah, selb.atas])
    k.garis([a.bawah, b.atas], 'YA')
    k.garis([b.bawah, c.atas], 'TIDAK')
    k.garis([b.kiri, (130, 310), (130, 840), akt.kiri], 'YA')
    k.garis([c.kanan, kon0.kiri], 'TIDAK')
    k.garis([kon0.bawah, sel2.atas])
    k.garis([c.bawah, c1.atas], 'YA')
    k.garis([c1.bawah, d.atas])
    k.garis([d.bawah, akt.atas], 'YA')
    k.garis([d.kanan, tunggu.kiri], 'TIDAK')
    k.garis([tunggu.bawah, sel3.atas])
    k.garis([akt.bawah, sel.atas])
    k.catatan(700, 880, ['Batas yang belum fix:', 'B3 waktu konfirmasi (30 detik)'])
    k.simpan('diagram-2-aturan-co-pemicu.svg')


def diagram3():
    k = Kanvas(1250, 1300, 'Diagram 3. Aturan CO: uji arah dan pemulihan')
    mx = 500
    start = k.oval(mx, 70, 260, 44, ['ATURAN CO (lanjutan)'])
    d = k.belah(mx, 170, 320, 100, ['faseCO =', 'UJI_ARAH?'])
    e = k.belah(mx, 305, 340, 110, ['waktuUji  >=  lama uji arah?', '[B5]'])
    f = k.belah(mx, 450, 360, 120, ['Rs turun lebih dari', 'kriteria "naik lagi"?', '[B6]'])
    luar = k.persegi(190, 610, 300, 130, ['faseCO = SUMBER_LUAR', 'CO naik lagi: sumber luar', 'jendela TUTUP dan KUNCI', '(tidak menguji ulang)', '(hasil tidak jelas: usulan sama) [B6]'], 'oranye')
    dalam = k.persegi(mx, 610, 290, 90, ['faseCO = SUMBER_DALAM', 'CO turun: jendela', 'tetap terbuka'], 'kuning')
    w = k.persegi(900, 305, 250, 50, ['waktuUji = waktuUji + 1 detik'])
    merge = 720
    g = k.belah(mx, 810, 340, 100, ['faseCO  tidak sama dengan', 'TIDAK_AKTIF?'])
    h = k.belah(mx, 960, 360, 120, ['ppmCO  <  30 ppm', 'selama 60 detik?', '[B7]'])
    reset = k.persegi(mx, 1110, 420, 90, ['faseCO = TIDAK_AKTIF,  bunyi CO OFF', 'jendela diserahkan ke aturan CO2', 'reset penghitung CO'], 'teal')
    sel_a = k.oval(mx, 1200, 200, 40, ['Selesai'], 'teal')
    sel_b = k.oval(900, 810, 160, 40, ['Selesai'], 'teal')
    pem0 = k.persegi(900, 960, 250, 50, ['pemulihanCO = 0'])
    sel_c = k.oval(900, 1045, 160, 40, ['Selesai'], 'teal')

    k.garis([start.bawah, d.atas])
    k.garis([d.bawah, e.atas], 'YA')
    k.garis([e.bawah, f.atas], 'YA')
    k.garis([e.kanan, w.kiri], 'TIDAK')
    k.garis([f.kiri, (190, 450), luar.atas], 'YA')
    k.garis([f.bawah, dalam.atas], 'TIDAK')
    # titik temu
    k.garis([luar.bawah, (190, merge), (mx, merge)], panah=False)
    k.garis([dalam.bawah, (dalam.cx, merge), (mx, merge)], panah=False)
    k.garis([w.bawah, (900, merge), (mx, merge)], panah=False)
    k.garis([d.kanan, (1120, 170), (1120, merge), (mx, merge)], 'TIDAK', panah=False)
    k.garis([(mx, merge), g.atas])
    k.garis([g.bawah, h.atas], 'YA')
    k.garis([g.kanan, sel_b.kiri], 'TIDAK')
    k.garis([h.bawah, reset.atas], 'YA')
    k.garis([h.kanan, pem0.kiri], 'TIDAK')
    k.garis([pem0.bawah, sel_c.atas])
    k.garis([reset.bawah, sel_a.atas])
    k.catatan(40, 810, ['Belum fix:', 'B5 lama uji arah', 'B6 kriteria "naik lagi"', 'dan hasil tidak jelas', 'B7 batas selesai (30 ppm)', 'dan waktu pemulihan (60 detik)'])
    k.simpan('diagram-3-aturan-co-uji-arah.svg')


def diagram4():
    k = Kanvas(1250, 1190, 'Diagram 4. Aturan CO2 (hanya bila aturan CO tidak aktif)')
    mx = 420
    start = k.oval(mx, 70, 220, 44, ['ATURAN CO2'])
    d1 = k.belah(mx, 170, 340, 100, ['faseCO =', 'TIDAK_AKTIF?'])
    d2 = k.belah(mx, 300, 360, 110, ['CO2  >=  4000 ppm selama', '3 bacaan valid?  [B8]'])
    d3 = k.belah(mx, 430, 360, 110, ['CO2  >=  2500 ppm selama', '3 bacaan valid?  [B8]'])
    sel0 = k.oval(900, 170, 250, 50, ['Selesai', '(aturan CO2 diabaikan)'], 'teal')
    tind = k.persegi(900, 300, 330, 100, ['TINDAKAN', 'faseCO2 = TINDAKAN, bunyi ON', 'jendela BUKA sebesar bukaan mobil [B9]'], 'oranye')
    per = k.persegi(900, 430, 330, 100, ['PERINGATAN (sekali per kejadian)', 'bunyi singkat SATU KALI', 'peringatan ke aplikasi'], 'kuning')
    d4 = k.belah(mx, 740, 340, 100, ['faseCO2  tidak sama', 'dengan NORMAL?'])
    d5 = k.belah(mx, 880, 360, 110, ['CO2  <  2400 ppm selama', '60 detik?  [B8]'])
    norm = k.persegi(mx, 1020, 420, 90, ['faseCO2 = NORMAL,  bunyi OFF', 'jendela TUTUP,  reset penghitung CO2'], 'teal')
    sel1 = k.oval(mx, 1120, 200, 40, ['Selesai'], 'teal')
    sel2 = k.oval(900, 740, 160, 40, ['Selesai'], 'teal')
    pem0 = k.persegi(900, 880, 250, 50, ['pemulihanCO2 = 0'])
    sel3 = k.oval(900, 965, 160, 40, ['Selesai'], 'teal')

    k.garis([start.bawah, d1.atas])
    k.garis([d1.kanan, sel0.kiri], 'TIDAK')
    k.garis([d1.bawah, d2.atas], 'YA')
    k.garis([d2.kanan, tind.kiri], 'YA')
    k.garis([d2.bawah, d3.atas], 'TIDAK')
    k.garis([d3.kanan, per.kiri], 'YA')
    bus = 1150
    k.garis([tind.kanan, (bus, tind.cy)], panah=False)
    k.garis([per.kanan, (bus, per.cy)], panah=False)
    k.garis([(bus, tind.cy), (bus, 640), (mx, 640)], panah=False)
    k.garis([d3.bawah, (mx, 640)], 'TIDAK', panah=False)
    k.garis([(mx, 640), d4.atas])
    k.garis([d4.bawah, d5.atas], 'YA')
    k.garis([d4.kanan, sel2.kiri], 'TIDAK')
    k.garis([d5.bawah, norm.atas], 'YA')
    k.garis([d5.kanan, pem0.kiri], 'TIDAK')
    k.garis([pem0.bawah, sel3.atas])
    k.garis([norm.bawah, sel1.atas])
    k.catatan(40, 640, ['Belum fix:', 'B8 jumlah bacaan konfirmasi (3),', 'batas selesai 2400 dan 60 detik', 'B9 besar bukaan jendela per mobil,', 'jeda minimum antar gerakan'])
    k.simpan('diagram-4-aturan-co2.svg')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    diagram1()
    diagram2()
    diagram3()
    diagram4()
    print('selesai: 4 berkas SVG dibuat')
