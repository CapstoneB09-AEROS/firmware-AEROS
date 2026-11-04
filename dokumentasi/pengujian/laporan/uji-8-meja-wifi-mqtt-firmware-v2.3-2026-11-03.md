# Uji 8: Uji meja firmware v2.3, Wi-Fi + MQTT + database, 3-4 November 2026

Catatan santai buat jaga-jaga. Bukan uji mobil: alat di meja, CO2 dinaikkan dengan ambang **pengembangan 700/800 ppm** (bukan 2500/4000). Firmware v2.3 (jendela pakai dua pin: GPIO26 turun 1,5 s, GPIO25 naik 5 s). Jam di log = jam laptop.

Berkas di `logs/`:

| Sesi | Berkas | Jam | Lama | Catatan |
|---|---|---|---|---|
| 1 | `device-monitor-261103-181316.log` | 18:13 - 21:50 | 3 j 37 m | alat sudah menyala sejak sekitar 17:45 (`t_s` mulai 1685) |
| 2 | `device-monitor-261103-223445.log` | 22:34 - 22:40 | 6 m | `t_s` mulai 179 |
| 3 | `device-monitor-261103-234332.log` | 23:43 - 23:50 | 7 m | `t_s` mulai 131 |
| 4 | `device-monitor-261103-235721.log` | 23:57 - 00:15 | 18 m | **boot baru**, pemanasan dan Wi-Fi terlihat dari awal |

Tidak ada lembar catatan, jadi apa yang dilakukan di tiap kejadian (napas ke kotak, dll.) **tidak tercatat**. Yang di bawah murni dari log.

## 1. Yang berjalan baik

| Hal | Hasil |
|---|---|
| Stabil | Tidak ada reset, `t_s` tidak pernah mundur, interval data median 1,000 detik. |
| Siklus CO2 | 13 episode waspada, 11 sampai bahaya. Jendela turun 1500 ms lalu naik 5000 ms: 11 pasang, tidak ada yang terbalik atau tertinggal. |
| Kecepatan | Bunyi dan sinyal GPIO26 keluar 6-12 ms setelah status berubah (deteksi butuh 3 bacaan berturut-turut). |
| Lama bahaya sampai aman | 40-96 detik, median 51 detik. |
| Tanpa internet | 4 episode (18:21 - 19:39) terjadi saat Wi-Fi mati: bunyi dan sinyal jendela tetap jalan. |
| Pengiriman | Saat Wi-Fi dan worker hidup, ACK datang 1 per 5 detik dan jumlahnya pas: sesi 2 = 70, sesi 3 = 68, sesi 4 = 185 ACK. Sesi 1, 20:20 - 21:10 = 120 ACK per 10 menit tanpa putus. |
| Data baru dikirim setelah pemanasan | Sesi 4: MQTT tersambung 23:59:11, ACK pertama 00:00:28 (pemanasan 180 detik baru selesai 00:00:18). |
| CO | Tidak ada alarm CO. Estimasi sempat naik sampai 81 ppm (20:54, Rs/R0 turun sampai 0,09), tapi di atas 35 ppm paling lama 15 detik, kurang dari syarat 30 detik. Jadi status CO tetap OK sesuai aturan. |

## 2. Masalah yang ketemu

**a. Data hilang 19:53 - 20:12 padahal tersambung.** Wi-Fi dan MQTT hidup, tapi tidak ada ACK selama 19,5 menit. Firmware membuang 241 sampel (sekitar 20 menit) karena penyangga penuh. ACK baru datang lagi 20:12:36 (antrean sempat "menunggu: 3"). Dari log alat tidak kelihatan penyebabnya, kemungkinan di sisi worker atau database. Tiga episode alarm (19:55, 20:05, 20:06) jatuh di periode ini.

**b. Wi-Fi hilang dua kali.** Hotspot `chaa` tidak terdeteksi dari awal log sampai 19:47, lalu lagi dari sekitar 21:15 sampai log berhenti. Sesuai desain (mode online), data saat itu tidak disimpan: log mencatat "total dibuang 1416" pada 19:46, kira-kira 2 jam data.

**c. Pulsa naik tidak persis 5000 ms.** 5 kali tepat 5000-5001 ms, 6 kali 5340-5346 ms. Pulsa turun selalu 1500-1501 ms. Selisih sekitar 0,34 detik, kecil. Penyebab belum diselidiki (di mode online baris STATUS juga telat sekitar 0,3 detik dibanding offline).

## 3. Belum terbukti

- Gerak jendela asli: log hanya menunjukkan sinyal GPIO, tidak ada video atau catatan.
- Ambang rancangan 2500/4000: uji ini memakai 700/800, jadi hanya membuktikan logika siklusnya.
- Jumlah baris di Supabase sama dengan yang dikirim: log hanya menunjukkan ACK, belum dibandingkan dengan isi tabel.
- Apakah event alarm 19:55 - 20:06 tersimpan di tabel event.

## 4. Yang perlu dicek

1. Log worker (Railway) atau Supabase pada 19:53 - 20:12: kenapa ACK berhenti.
2. Tabel event: apakah ada event untuk 19:55, 20:05, dan 20:06.
3. Lain kali uji meja: tulis lembar catatan singkat (jam + kegiatan) dan catat jam hotspot dimatikan atau dinyalakan.

Yang sudah tercakup dari rencana T22: alarm tetap bunyi tanpa internet (terpenuhi), `t_s` tidak melompat (terpenuhi), kapan antrean penuh tercatat (terpenuhi, 19:47:28 - 20:12:34). Yang belum: jumlah baris database sama dengan yang dikirim.
