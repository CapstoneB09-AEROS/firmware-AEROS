"""Membuat diagram alur data end-to-end (SVG dan PNG): ESP32 -> aktuator -> MQTT -> worker -> database -> aplikasi.

Cara pakai:  python3 buat_diagram_alur_data.py
Hasil     :  diagram-5-alur-data-ke-aplikasi.svg, diagram-6-alur-perintah-saya-tahu.svg

Memakai kelas Kanvas dari buat_diagram.py. Warna di diagram ini:
  hijau kebiruan = sudah ada di kode tim (kode-tim/iot-mainproject/)
  kuning         = usulan kita (pseudocode-baru.md bagian 2.8), belum ada di kode
  oranye         = aktuator
  abu            = bagian Flutter atau Supabase yang kodenya belum kita lihat (dugaan)
"""
import os
from buat_diagram import Kanvas, FONT, esc

LEBAR_LANE = 255


def lane(k, cx, judul, tinggi):
    k.out.append(f'<rect x="{cx - LEBAR_LANE / 2}" y="44" width="{LEBAR_LANE}" height="{tinggi - 100}" '
                 f'fill="#f6f8fa" stroke="#d0d7de" stroke-width="1"/>')
    k.out.append(f'<text x="{cx}" y="66" text-anchor="middle" font-family="{FONT}" font-size="14" '
                 f'font-weight="bold" fill="#24292f">{esc(judul)}</text>')


def legenda(k, y):
    items = [('teal', 'sudah ada di kode tim'), ('kuning', 'usulan kita (belum ada di kode)'),
             ('oranye', 'aktuator'), ('abu', 'dugaan: kode Flutter/Supabase belum dilihat')]
    from buat_diagram import FILL
    x = 40
    for w, t in items:
        f, st = FILL[w]
        k.out.append(f'<rect x="{x}" y="{y}" width="18" height="13" fill="{f}" stroke="{st}"/>')
        k.out.append(f'<text x="{x + 25}" y="{y + 11}" font-family="{FONT}" font-size="12" fill="#333">{esc(t)}</text>')
        x += 40 + len(t) * 6.6


def diagram5():
    W, H = 1600, 1400
    k = Kanvas(W, H, 'Diagram 5. Alur data dari sensor sampai aplikasi Flutter')
    X = [130, 395, 660, 925, 1190, 1455]
    for cx, j in zip(X, ['ESP32: tugas sensor', 'ESP32: tugas jaringan', 'Broker HiveMQ', 'Worker (Node.js)',
                         'Database Supabase', 'Aplikasi Flutter']):
        lane(k, cx, j, H)
    bw = 232

    s1 = k.jajar(X[0], 140, bw, 62, ['1. Baca MiCS (ADS1115)', 'dan MH-Z19C tiap 1 detik'])
    s2 = k.persegi(X[0], 250, bw, 70, ['2. Validasi, filter SMA 6,', 'hitung ppm CO', '(CO2 apa adanya)'])
    s3 = k.belah(X[0], 375, bw, 110, ['3. Lewat ambang', 'CO atau CO2?'])
    s4 = k.persegi(X[0], 510, bw, 92, ['4. Aktuator (tanpa', 'menunggu internet):', 'buzzer, jendela setengah,', 'LCD'], 'oranye')
    s5 = k.persegi(X[0], 640, bw, 100, ['5. Susun pesan:', 'telemetri tiap 5 detik,', 'kejadian segera. Nonce, jam,', 'event_id, tanda tangan HMAC'], 'kuning')
    sx = k.persegi(X[0], 790, bw, 80, ['Jaringan putus: data menumpuk', 'di flash. Sensor dan alarm', 'tetap jalan'], 'abu')
    sx2 = k.persegi(X[0], 1110, bw, 70, ['Tidak ada ACK yang benar:', 'berkas tetap, kirim ulang', 'tiap 6 detik'], 'abu')

    n6 = k.persegi(X[1], 640, bw, 92, ['6. Antrean RAM, lalu', 'TULIS KE FLASH dulu', '(offline first, LittleFS)'], 'teal')
    n7 = k.belah(X[1], 790, bw + 10, 120, ['7. Wi-Fi, NTP, dan', 'MQTT TLS tersambung?'])
    n8 = k.persegi(X[1], 930, bw, 92, ['8. Kirim berkas tertua', '(kejadian dulu), lalu', 'tunggu ACK'], 'teal')
    n12 = k.belah(X[1], 1110, bw + 10, 120, ['12. ACK benar?', '(HMAC dan nonce)'])
    n13 = k.persegi(X[1], 1240, bw, 60, ['13. Hapus berkas dari flash'], 'teal')

    b_st = k.persegi(X[2], 790, bw, 80, ['Topik status: ONLINE', '(retained). OFFLINE lewat', 'last will'], 'teal')
    b9 = k.persegi(X[2], 930, bw, 66, ['9. Topik aeros/data', '(TLS, sertifikat diperiksa)'], 'teal')
    b11 = k.persegi(X[2], 1110, bw, 66, ['11. Topik aeros/{id}/', 'data/ack'], 'teal')

    w10 = k.persegi(X[3], 930, bw, 92, ['10. Worker: cek HMAC,', 'umur jam, perangkat aktif', '(tabel devices)'], 'teal')
    w10b = k.persegi(X[3], 1030, bw, 62, ['Simpan sensor_readings', '(+ event_id: perubahan)'], 'kuning')
    w10c = k.persegi(X[3], 1130, bw, 92, ['Kejadian: tulis alert_logs', '(id = event_id) atau', 'actuator_logs (usulan 2.8.8)'], 'kuning')
    w10d = k.persegi(X[3], 1250, bw, 80, ['Kirim ACK_DATA ber-HMAC,', 'HANYA setelah semua', 'penulisan DB berhasil'], 'teal')

    d1 = k.persegi(X[4], 1030, bw, 56, ['Tabel sensor_readings'], 'abu')
    d2 = k.persegi(X[4], 1130, bw, 70, ['Tabel alert_logs,', 'actuator_logs,', 'device_state'], 'abu')

    f1 = k.persegi(X[5], 1030, bw, 70, ['Aplikasi menampilkan', 'nilai dan grafik terbaru', '(Realtime atau baca tabel)'], 'abu')
    f2 = k.persegi(X[5], 1130, bw, 70, ['Notifikasi dan layar', 'peringatan dari alert_logs', '(belum dicek)'], 'abu')

    k.garis([s1.bawah, s2.atas])
    k.garis([s2.bawah, s3.atas])
    k.garis([s3.bawah, s4.atas], 'YA')
    k.garis([s4.bawah, s5.atas])
    k.garis([s3.kiri, (20, 375), (20, 640), s5.kiri], 'TIDAK', lpos=(28, 430), panah=True)
    k.garis([s5.kanan, n6.kiri])
    k.garis([n6.bawah, n7.atas])
    k.garis([n7.kiri, sx.kanan], 'TIDAK', lpos=(270, 780))
    k.garis([n7.bawah, n8.atas], 'YA')
    k.garis([n7.kanan, b_st.kiri], 'YA', putus=True)
    k.garis([n8.kanan, b9.kiri])
    k.garis([b9.kanan, w10.kiri])
    k.garis([w10.bawah, w10b.atas])
    k.garis([w10b.bawah, w10c.atas])
    k.garis([w10c.bawah, w10d.atas])
    k.garis([w10b.kanan, d1.kiri])
    k.garis([w10c.kanan, d2.kiri])
    k.garis([d1.kanan, f1.kiri], putus=True)
    k.garis([d2.kanan, f2.kiri], putus=True)
    k.garis([w10d.kiri, (792, 1250), (792, 1110), b11.kanan])
    k.garis([b11.kiri, n12.kanan])
    k.garis([n12.bawah, n13.atas], 'YA')
    k.garis([n12.kiri, sx2.kanan], 'TIDAK', lpos=(270, 1100))
    k.garis([n8.bawah, (X[1], 990), (X[1], 1050)], panah=False, putus=True)
    k.garis([(X[1], 1050), n12.atas], putus=True)
    k.catatan(X[1] - 110, 1020, ['menunggu ACK'], '#666')
    k.catatan(40, 1290, ['Kunci: ESP32 memutuskan alarm dan menggerakkan aktuator SENDIRI (langkah 1 sampai 4).',
                         'Pengiriman (langkah 5 sampai 13) berjalan di tugas lain, jadi internet mati tidak menghentikan alarm.',
                         'Data hanya dihapus dari ESP setelah database membalas (langkah 12 dan 13). Pesan ganda ditolak lewat nonce.'], '#333')
    legenda(k, H - 70)
    k.simpan('diagram-5-alur-data-ke-aplikasi.svg', legenda=False)


def diagram6():
    W, H = 1600, 1440
    k = Kanvas(W, H, 'Diagram 6. Alur perintah "Saya Tahu" dari aplikasi kembali ke ESP32')
    X = [130, 395, 660, 925, 1190, 1455]
    for cx, j in zip(X, ['Aplikasi Flutter', 'Database Supabase', 'Worker (Node.js)', 'Broker HiveMQ',
                         'ESP32: tugas jaringan', 'ESP32: tugas sensor']):
        lane(k, cx, j, H)
    bw = 232

    f0 = k.oval(X[0], 140, bw - 40, 50, ['Pengemudi menekan', '"Saya Tahu"'], 'abu')
    f1 = k.persegi(X[0], 260, bw, 92, ['Aplikasi menulis', 'actuator_logs: buzzer off,', 'pending, command_id,', 'alert_id'], 'abu')
    d1 = k.persegi(X[1], 260, bw, 62, ['Baris actuator_logs', 'status pending'], 'abu')
    w1 = k.persegi(X[2], 380, bw, 80, ['Worker menerima:', 'Realtime INSERT atau', 'polling tiap 15 detik'], 'teal')
    w2 = k.belah(X[2], 520, bw + 20, 130, ['alert_id ada, milik', 'perangkat ini, belum', 'selesai?'])
    d2 = k.persegi(X[1], 520, bw, 62, ['Ditolak. Baris tetap', 'pending'], 'abu')
    w3 = k.persegi(X[2], 670, bw, 80, ['Tanda tangani HMAC', '(issued_at = sekarang),', 'publish QoS 1'], 'teal')
    b1 = k.persegi(X[3], 670, bw, 56, ['aeros/{id}/command'], 'teal')
    n1 = k.belah(X[4], 800, bw + 20, 120, ['Tanda tangan benar', 'dan umur <= 120 detik?'])
    b2 = k.persegi(X[3], 800, 200, 62, ['Diabaikan, dicatat', 'di serial'], 'abu')
    s1 = k.belah(X[5], 940, bw + 20, 140, ['alert_id = alarm yang', 'aktif sekarang, dan', 'buzzer terpasang?'])
    s2 = k.persegi(X[5], 1080, bw, 60, ['Matikan bunyi'], 'oranye')
    n2 = k.persegi(X[4], 1080, bw, 62, ['Hasil: gagal', '(bunyi tidak diubah)'], 'abu')
    n3 = k.persegi(X[4], 1200, bw, 80, ['ACK perintah bertanda', 'tangan (berhasil atau', 'gagal)'], 'teal')
    b3 = k.persegi(X[3], 1200, bw, 56, ['aeros/{id}/command/ack'], 'teal')
    w4 = k.persegi(X[2], 1200, bw, 100, ['Cek HMAC dan kecocokan.', 'Bila berhasil: actuator_logs', '= success, alert_logs', '.acknowledged_at, ack_driver'], 'teal')
    d3 = k.persegi(X[1], 1200, bw, 62, ['Tabel diperbarui'], 'abu')
    f2 = k.persegi(X[0], 1200, bw, 70, ['Aplikasi menampilkan', '"sudah dikonfirmasi"', '(belum dicek)'], 'abu')

    k.garis([f0.bawah, f1.atas])
    k.garis([f1.kanan, d1.kiri], putus=True)
    k.garis([d1.bawah, (X[1], 380), w1.kiri], putus=True)
    k.garis([w1.bawah, w2.atas])
    k.garis([w2.kiri, d2.kanan], 'TIDAK', lpos=(535, 510))
    k.garis([w2.bawah, w3.atas], 'YA')
    k.garis([w3.kanan, b1.kiri])
    k.garis([b1.kanan, (X[4], 670), n1.atas])
    k.garis([n1.kiri, b2.kanan], 'TIDAK', lpos=(1070, 790))
    k.garis([n1.kanan, (X[5], 800), s1.atas], 'YA', lpos=(1330, 790))
    k.garis([s1.bawah, s2.atas], 'YA')
    k.garis([s1.kiri, (X[4], 940), n2.atas], 'TIDAK', lpos=(1320, 930))
    k.garis([s2.kiri, (1322, 1080), (1322, 1200), n3.kanan])
    k.garis([n2.bawah, n3.atas])
    k.garis([n3.kiri, b3.kanan])
    k.garis([b3.kiri, w4.kanan])
    k.garis([w4.kiri, d3.kanan])
    k.garis([d3.kiri, f2.kanan], putus=True)
    k.catatan(40, 1300, ['Kunci: "Saya Tahu" hanya mematikan bunyi bila alert_id perintah SAMA dengan alarm yang sedang aktif di ESP32.',
                         'Perintah lama atau milik alarm lain tidak bisa mematikan alarm baru. Perintah dibuat sendiri oleh worker, tidak diterima dari luar.',
                         'Syarat cocok: alert_logs.id harus sama dengan event_id dari ESP32 (keputusan 27 Okt, pseudocode 2.8.8).'], '#333')
    legenda(k, H - 70)
    k.simpan('diagram-6-alur-perintah-saya-tahu.svg', legenda=False)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    diagram5()
    diagram6()
    print('selesai: 2 diagram dibuat')
