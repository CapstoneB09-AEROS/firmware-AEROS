# Perbandingan Dokumen C-251 dengan Pekerjaan Sekarang

Dokumen yang dibandingkan: `rencana-awal/[v1] C251 B-09.pdf` (C-251, revisi 01, terbit 14 Agustus 2026, 11 bab). Dibandingkan dengan firmware dan dokumentasi per 25 Oktober 2026.

> **Catatan (25 Okt 2026):** C-251 **tidak akan direvisi**. Temuan di dokumen ini dipakai sebagai bahan penulisan **C-501** (laporan implementasi dan hasil, tenggat setelah expo), bukan sebagai daftar revisi.

**Batasan cara baca.** PDF dibaca dengan ekstraksi teks otomatis. Gambar, diagram, dan sebagian tabel tidak terbaca. Subskrip (misalnya "CO2" dan "CO") dan beberapa angka hilang atau tergabung. Semua temuan bertanda **[cek PDF]** harus dilihat langsung di halaman aslinya sebelum diperbaiki.

---

## 1. Ringkasan isi C-251

| Aspek | Isi rencana C-251 |
|---|---|
| Sistem | AEROS: ESP32 DevKitC V4, sensor CO **MQ-7**, sensor CO2 **MH-Z19B**, buzzer aktif, servo (mewakili jendela), MQTT, Supabase, aplikasi Flutter |
| Anggaran | Rp1.987.000 dari batas Rp2.000.000. Komponen tunggal maksimal Rp500.000 |
| Siklus baca | Tiap 5 detik |
| Filter | Rata-rata bergerak: CO 150 detik (M = 30, mengikuti siklus pemanasan MQ-7: 60 detik di 5 V dan 90 detik di 1,4 V), CO2 120 detik (M = 24, mengikuti T90 MH-Z19B) |
| Ambang | CO ≥ 35 ppm (acuan NIOSH), CO2 ≥ 2500 ppm (acuan studi Satish dan ASHRAE). Pemicu memakai nilai rata-rata |
| Pemulihan | CO sekarang < 30 ppm **dan** CO2 sekarang < 2400 ppm selama 60 detik, memakai nilai langsung, bukan rata-rata |
| Aksi | CO2 tinggi: buzzer dan servo membuka. CO tinggi: servo tertutup, buzzer, anjuran mode AC recirculation lewat aplikasi |
| Pengujian | Dalam kotak akrilik 40 × 30 cm, bukan kabin nyata. Spesifikasi: deteksi CO dari 5 uji ≥ 4 dari 5 |
| Daya | Port USB laptop. Catu mandiri direncanakan untuk C-501 |
| Batasan yang diakui | Sensitivitas silang (parfum beralkohol), drift, tidak automotive-grade, belum diuji getaran dan suhu kabin, tanpa enclosure, tanpa kontrol AC otomatis |

## 2. Yang sudah oke (selaras dengan pekerjaan sekarang)

| # | Hal | Keterangan |
|---|---|---|
| 1 | Arsitektur dasar | ESP32, sensor CO analog, sensor CO2 lewat UART, buzzer lokal yang tidak bergantung internet. Firmware sekarang berjalan mandiri |
| 2 | Antarmuka MH-Z19 | UART 9600 dan checksum sudah diperiksa terhadap manual Winsen dan cocok dengan kode |
| 3 | Rumus hambatan dan ppm | C-251 memakai Rs = RL × (Vc − Vout) / Vout dan PPM = A × (Rs/R0)^B. Sama dengan bentuk di `main.cpp` |
| 4 | Ambang CO 35 ppm | Nilainya sama dengan kode. Acuan NIOSH REL tercatat di desain-peringatan.md |
| 5 | Ambang CO2 2500 ppm | Sama dengan tingkat "peringatan" di desain-peringatan.md |
| 6 | Konsep histeresis dan jeda pemulihan | Ada di rencana dan di kode (nilainya berbeda, lihat bagian 3) |
| 7 | Penyaringan berbasis data | Bab 8.3.1 menyatakan parameter ditentukan dari profil data pengujian. Itu yang kita kerjakan di filtering.md |
| 8 | Batasan sensor dan prototipe | Bab 7 sudah mengakui sensitivitas silang, drift, tanpa uji getaran dan suhu, tanpa enclosure, daya USB laptop. Banyak yang bisa dipakai ulang di batasan-sistem.md |
| 9 | Penurunan 1000 ppm sebagai ambang | Bab 1 sendiri menyebut 96% mobil di studi Hong Kong melewati 1000 ppm. Itu mendukung keputusan kita tidak memakai 1000 sebagai ambang |
| 10 | Model dan uji mobil sejalan | Bab 10 memperkirakan 4 penumpang di Avanza mencapai ambang dalam hitungan menit. Uji mobil Anda mencapai 5000 ppm dalam 20–30 menit, dalam orde besaran yang sama (model lebih cepat, sejalan dengan pendekatan worst-case) |

## 3. Janggal dan sedang dikerjakan atau diubah

| # | Perbedaan | Dalam rencana | Sekarang | Status |
|---|---|---|---|---|
| 1 | Sensor CO | MQ-7 | MiCS-5524 + ADS1115 | Sudah diganti. Spesifikasi di dokumen perlu direvisi (T15) |
| 2 | Sensor CO2 | MH-Z19B, 0–5000 ppm, ±50 ppm | MH-Z19C, 400–5000 ppm, ±(50 ppm + 5%) | Sudah diganti. Akurasi baru lebih longgar, dan itu memengaruhi margin 4000 ppm (T2, T15) |
| 3 | Dasar filter CO | 150 detik mengikuti siklus pemanasan MQ-7 | MiCS tidak punya siklus pemanasan seperti itu | Dasar lama gugur. Filter sedang dianalisis (T9) |
| 4 | Siklus dan filter | 5 detik, rata-rata 150 dan 120 detik | 1 detik, EMA 0,2 (sekitar 10 detik) | Belum diputuskan (T9) |
| 5 | Ambang tindakan CO2 | 2500 ppm: buzzer dan jendela terbuka sekaligus | 2500 ppm: bunyi singkat. 4000 ppm: tindakan (buka jendela). 1000 ppm tidak dipakai | Sudah diputuskan di desain-peringatan.md. Belum masuk firmware (T8) |
| 6 | Pemicu alarm | Rata-rata bergerak | Nilai langsung dengan konfirmasi 10 detik | Menunggu T3 dan T10 |
| 7 | Kalibrasi | "Rekalibrasi manual sebelum tiap sesi" | R0 diukur dengan perintah `r` di udara bersih. Tidak ada referensi CO | Baseline sedang direkam (T1) |
| 8 | Penyimpanan data | MQTT dan Supabase | Log lokal ke file | Berbeda tujuan. Tidak masalah untuk tahap uji |

## 4. Janggal tetapi belum ada tindakan

| # | Temuan | Mengapa janggal | Saran | Tugas |
|---|---|---|---|---|
| 1 | Spesifikasi "deteksi CO dari 5 uji ≥ 4 dari 5 dengan sumber uji terkonsentrasi di dalam kotak akrilik", dan Bab 7.6 menyebut "prosedur injeksi gas CO" | Tim tidak punya sumber CO atau instrumen referensi | Tentukan cara menguji yang bisa dilakukan, atau ubah spesifikasi. Jangan membuat CO sendiri tanpa protokol keselamatan | T16 |
| 2 | "Pendekatan kalibrasi tetap diterapkan untuk menjaga keandalan" (Bab 7.1) | Kalibrasi terhadap referensi tidak dilakukan | Ubah kalimat sesuai kondisi sebenarnya. Contoh kalimat ada di batasan-sistem.md | T15 |
| 3 | Jumlah status berbeda: dua (AMAN dan WASPADA) di Bab 4.4.2 dan 8.3.3, tiga (NORMAL, WASPADA, BAHAYA) di Bab 8.4.4 dan Bab 11 **[cek PDF]** | Rancangan tidak konsisten | Satukan | T17 |
| 4 | Bab 11 menyebut WASPADA CO2 ≥ 1000 ppm dan BAHAYA CO2 ≥ 2500 ppm, serta BAHAYA CO ≥ 100 ppm. Bab 4, 5, dan 8 menyebut WASPADA CO2 ≥ 2500 ppm **[cek PDF]** | Ambang bertentangan antar bab | Satukan, dan harus sejalan dengan keputusan di desain-peringatan.md | T17 |
| 5 | Bukaan servo: 100% (Tabel 4.2), 90° (Bab 8.3.3), sebagian dan penuh (Bab 8.4.4 dan Bab 11) **[cek PDF]** | Tidak konsisten | Satukan | T17 |
| 6 | Bunyi buzzer: kontinu saat WASPADA (Bab 8.1) vs putus-putus saat WASPADA dan kontinu saat BAHAYA (Bab 11) **[cek PDF]** | Tidak konsisten, dan berkaitan dengan UX | Satukan. Sejalan dengan rencana "bunyi singkat satu kali" di desain-peringatan.md | T17 |
| 7 | Lokasi sensor: "konsol bawah dashboard karena CO2 lebih berat", sementara Bab 8.2.6 menyebut dashboard menghadap kabin, dan acuan Mehel mengukur setinggi mulut penumpang | Alasan "CO2 lebih berat" bertentangan dengan asumsi model well-mixed di bab yang sama. Manual MH-Z19C juga meminta jauh dari panas dan sinar matahari | Tinjau lokasi dan dasarnya. Lokasi memengaruhi pembacaan | T18 |
| 8 | Anjuran mode AC recirculation untuk CO tinggi | Kita memutuskan tidak mengandalkan mode AC untuk CO2. Untuk CO luar, anjuran recirculation punya dasar tersendiri tetapi tidak ada bukti dari uji kita | Putuskan perlakuan CO dan CO2 secara terpisah dan tulis alasannya | T10 |
| 9 | Anggaran Rp1.987.000 dengan MQ-7 dan MH-Z19B | Komponen berubah (MiCS-5524, ADS1115, LCD I2C) | Perbarui daftar komponen dan anggaran | T20 |
| 10 | Bab 4.4.3 menyebut "prototipe C-501", dan jadwal menulis seminar C-251 selesai Juni 2026 padahal dokumen terbit 14 Agustus 2026 **[cek PDF]** | Kemungkinan salah ketik atau sisa revisi lama | Periksa | T17 |
| 11 | Bab 7.6 menyatakan pengujian di kendaraan nyata di luar cakupan, sementara tim sudah mencoba di mobil | Selisih antara rencana dan kegiatan | Jelaskan uji mobil sebagai uji eksplorasi tambahan, bukan pengujian formal | T11 |
| 12 | Model Bab 10 belum dibandingkan dengan data log nyata | Model tersedia, data nyata belum | Cocokkan setelah uji mobil berlog | T19 |
| 13 | C-251 menulis ambang 35 ppm CO sebagai rata-rata 8 jam dan menyebutnya OSHA di Bab 7.4 (dan NIOSH 8 jam di Bab 1 dan 4.2.1) **[cek PDF]** | Halaman asli: OSHA PEL 50 ppm (8 jam). 35 ppm adalah **NIOSH REL**, dengan rata-rata **sampai 10 jam**, ditambah plafon 200 ppm | Koreksi atribusi dan masa rata-rata. Terverifikasi dari halaman NIOSH dan OSHA tertanggal 25 Okt 2026 | T15 |
| 14 | C-251 Bab 4.2.2 mengaitkan ASHRAE Standar 62 dengan batas CO2 sekitar 1.200 ppm **[cek PDF, teks terpotong]**, dan Bab 1 menyebut "batas rekomendasi 1.000 ppm" | Dokumen ASHRAE 2025: Standard 62.1 **tidak memuat batas CO2** dalam ruang. Angka 1000 ppm berasal dari edisi 1989 yang dihapus, dan terkait ventilasi serta bau tubuh, bukan kesehatan | Koreksi atribusi. Tulis 1000 ppm sebagai kebiasaan lama untuk indikator ventilasi, bukan standar ASHRAE | T15 |

## 5. Pengecekan kasar model dan pengamatan Anda

Pengamatan: jendela dibuka 10 detik menurunkan CO2 sekitar 100–300 ppm (sekitar 10–30 ppm per detik). Bab 10 memakai laju pertukaran udara jendela terbuka N ≈ 13,3 per jam (angkanya terbaca sebagian dari tabel **[cek PDF]**). Dengan persamaan penurunan yang sama, dari 5000 ppm dan udara luar sekitar 400 ppm, laju awalnya N × (5000 − 400) / 3600 ≈ 17 ppm per detik. Itu berada dalam rentang pengamatan Anda. Ini pengecekan kasar, belum bukti: sensor CO2 lambat (T90 kurang dari 120 detik), jadi pengamatan Anda mungkin lebih kecil dari penurunan sebenarnya.
