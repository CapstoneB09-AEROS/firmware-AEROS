# Kerangka Bab 4 (Detail Implementasi) dan Pembagian Penulisan

Dibuat 18 Nov 2026. Rangka mengikuti template C-501: 4.1 Luaran dan Spesifikasi, 4.2 Batasan Masalah, 4.3 Detail Rancangan. Berkas LaTeX kosongnya ada di `thesis/kerangka_BAB_04.tex` (belum menggantikan `BAB_04.tex`, supaya tulisan yang sudah ada di editor online tidak tertimpa).

**Pembagian (asumsi, ubah bila salah):** chaa = firmware, spesifikasi, batasan, simulasi, penyatuan. Bara = perangkat keras. Lia = komunikasi dan backend (worker). Joce = basis data dan aplikasi.

## Aturan umum (berlaku untuk semua)
1. Bab 4 menjawab "bagaimana dibuat", sampai nilai dan parameter yang bisa ditiru. Tidak ada hasil uji (itu Bab 5), tidak ada perbandingan alternatif dan pustaka (itu Bab 3), dan tidak ada teori dasar (itu Bab 2). Cukup merujuk: "(Subbab 3.x)".
2. Tulis rancangan sebagai fakta rancangan, bukan sebagai kekurangan. Batasan ditulis sekali, di 4.2.
3. Tidak ada angka yang belum terverifikasi. Bila belum ada sumbernya, tulis `% TODO` dan laporkan.
4. Format: `\subsection` dan `\subsubsection` secukupnya, indentasi 4 spasi, tabel `longtable` dengan kolom `L{}`, `CO\textsubscript{2}`, istilah asing dimiringkan, rujukan memakai `\ref`, nomor daftar berhuruf (a., b., c.).
5. Satu parameter dituliskan di satu tempat. Tabel parameter firmware (4.3.3.7) menjadi acuan angka. Subbab lain merujuk ke sana.

## 4.1 Luaran dan Spesifikasi (chaa)
| Subbab | Isi | Sumber | Jangan masuk |
|---|---|---|---|
| 4.1.1 Luaran | Satu paragraf dan satu tabel jenis luaran: firmware di *development board*, prototipe sistem, simulasi lengkap dengan Python, sistem informasi (backend dan aplikasi). Sinkron dengan lembar luaran | hasil-dan-pengujian.md, kerangka-c501.md | Contoh template (asap, 1 THz) |
| 4.1.2 Spesifikasi | Tabel: No, Spesifikasi, Satuan, Standar, Keterangan, untuk 8 butir target C-251 (deteksi CO₂, deteksi CO, respons buzzer ≤ 5 detik, respons aktuator ≤ 10 detik, pembukaan panel, penutupan panel, waktu tampil data ≤ 20 detik, anggaran ≤ Rp2.000.000). Kolom Standar diisi acuan (NIOSH, WHO, datasheet) | hasil-dan-pengujian.md bagian 1 | Kolom capaian dan status (Bab 5). Baris tiap pemilik: respons buzzer dan aktuator (chaa dan Bara), waktu tampil data (Lia dan Joce), anggaran (Bara) |

## 4.2 Batasan Masalah (chaa, tiap pemilik menambah butir bagiannya)
| Subbab | Isi | Sumber | Jangan masuk |
|---|---|---|---|
| 4.2.1 Fitur yang disediakan | Daftar bernomor fitur fungsional: pemantauan CO dan CO₂, peringatan bunyi dan LCD, pembukaan dan penutupan jendela otomatis, tombol "Saya Tahu", pengiriman data, aplikasi | keputusan.md | Rincian rancangan |
| 4.2.2 Fitur yang tidak disediakan dan alasan | Anti-jepit jendela, kalibrasi dengan gas acuan (tidak ada sumber CO yang aman), kontrol AC otomatis, enclosure kelas otomotif, uji getaran dan suhu kabin, antrean offline di flash. Satu kalimat alasan untuk tiap butir | batasan-sistem.md, perbandingan-c251.md | Hasil uji. Pembelaan berlebihan |
| 4.2.3 Batasan operasi sensor | Kondisi yang tidak boleh dilanggar (pelarut, silikon, asap rokok merusak lapisan MiCS, catu pemanas 4,9 sampai 5,1 V). Tulis sebagai ketentuan pakai | batasan-sistem.md bagian A | Hasil pengukuran catu atau R₀ unit |

## 4.3 Detail Rancangan
### 4.3.1 Arsitektur Sistem (chaa)
Satu diagram blok dan satu paragraf. Blok: sensor, ESP32, aktuator, antarmuka lokal, jaringan, worker, basis data, aplikasi. Tegaskan fungsi peringatan dan jendela tetap berjalan lokal di ESP32. Gunakan DFD level 0 dan 1 serta diagram alur utama. Sumber: komunikasi.md, diagram/. Jangan memuat rincian tiap blok (ada di subbab berikutnya).

### 4.3.2 Perangkat Keras (Bara)
| Sub-subbab | Isi | Jangan masuk |
|---|---|---|
| Daftar komponen dan pin | Tabel komponen dan fungsi, tabel pin ESP32 dan konektor PCB, skematik. Satu sumber pin: samakan dengan kode | Pin yang berbeda antar dokumen. Pin tombol Wi-Fi dan pin relay naik harus dikonfirmasi dulu |
| Catu daya | 12 V kendaraan ke *buck converter* 5 V, distribusi ke ESP32 (regulator internal 3,3 V), sensor, LCD, relay. Nilai rancangan saja | Tegangan catu terukur di bawah spesifikasi (itu Bab 5) |
| Akuisisi sinyal MiCS-5524 | Pembagi tegangan dengan R_L = 9,97 kΩ, jalur ke ADS1115 kanal A0, alamat I²C, rentang penguat otomatis (±1,024 V, ±2,048 V, ±4,096 V dan batas naik 92% turun 40%) | Rumus Rs (Bab 2). Perbandingan ADC (3.2). R₀ unit |
| Penggerak jendela | Relay lima kaki, driver dua kanal (PN2222A, 470 Ω, 10 kΩ), arah arus, hubungan relay dengan sakelar bawaan, interlock dua relay | Anti-jepit (4.2.2) |
| Antarmuka lokal | LCD I²C 16×2 (0x27), buzzer GPIO27, tombol | Penjelasan LCD atau buzzer umum (Bab 2) |
Sumber: hardware-wiring.md, diagram 7 sampai 11, skematik dan PCB. Dasar level tegangan I²C (LCD 5 V pada bus bersama ADS1115 3,3 V): tulis bila Bara sudah punya rujukan datasheet, kalau belum jangan ditulis.

### 4.3.3 Firmware (chaa)
| Sub-subbab | Isi | Jangan masuk |
|---|---|---|
| 4.3.3.1 Struktur dan siklus | Dua tugas (sensor dan jaringan), siklus 1 detik, jaringan tidak menahan siklus sensor | Alasan memilih (Bab 3) |
| 4.3.3.2 Pengolahan CO | Rs dari tegangan ADS1115, SMA 6 pada Rs, kurva Rs/R₀ = 3,46 c^−0,840 (bentuk Bab 2: A ≈ 4,4 dan B ≈ −1,19), R₀ dari kalibrasi udara bersih (perintah `r`, 120 detik) | Cara digitasi kurva secara rinci. Nilai R₀ unit |
| 4.3.3.3 Pengolahan CO₂ | Pembacaan UART MH-Z19C, validasi checksum, tanpa filter, pemanasan 180 detik | Pembandingan MH-Z19B |
| 4.3.3.4 Status dan bunyi | Tabel lima status (PEMANASAN, NORMAL, WASPADA, BAHAYA, GANGGUAN) dengan pemicu, bunyi, dan tampilan. Prioritas CO atas CO₂. Bunyi CO diulang tiap 60 detik sampai 5 menit, bunyi CO₂ sekali | Kasus CO tinggi saat baru menyala (jawab dulu: lihat catatan sidang) |
| 4.3.3.5 Aturan CO | Konfirmasi 30 detik untuk waspada, bahaya ≥ 87 ppm, uji arah 30 detik dengan batas 25%, kondisi selesai (< 30 ppm 60 detik). Diagram 2 dan 3 | Basis angka (Bab 3.5) |
| 4.3.3.6 Aturan CO₂ dan jendela | Peringatan 2.500 ppm, tindakan 4.000 ppm, jendela setengah paling lama 180 detik, selesai < 2.500 ppm 10 detik, bip 0,5 detik dan jeda 3 detik sebelum jendela naik. Diagram 4 | Hasil uji waktu naik |
| 4.3.3.7 Tabel parameter | Satu tabel konstanta firmware (nama, nilai, satuan, subbab sumber). Acuan angka semua bab | Parameter berstatus "usulan" tanpa keterangan |
Sumber: algoritma-firmware.md, keputusan.md, parameter-dan-sumber.md, sensorOriginal.inl.

### 4.3.4 Komunikasi dan Backend (Lia)
| Sub-subbab | Isi | Jangan masuk |
|---|---|---|
| Topik dan format pesan | Topik telemetri dan status per perangkat, isi pesan versi 3 (tabel bidang dan batas nilai), string yang ditandatangani | Perbandingan HTTP lawan MQTT (3.3.2) |
| Keamanan pesan | TLS dengan sertifikat diperiksa, HMAC-SHA256, nonce, jendela waktu, ACK bertanda tangan | Penjelasan teori HMAC atau TLS (Bab 2) |
| Koneksi dan ketahanan | Penyangga RAM 4 data terbaru sampai ACK, data lebih tua 30 detik dibuang, sambung ulang, portal Wi-Fi (hotspot AEROS-Setup), sinkron waktu NTP, *last will* | Antrean flash (dimatikan) dan alasan teknisnya |
| Worker | Urutan validasi, penulisan ke Supabase, pengiriman ACK | Rincian uji (36 uji lulus) |
Sumber: komunikasi.md, rancangan-worker-mvp.md, diagram 5 dan 6.

### 4.3.5 Basis Data (Joce)
Empat tabel (`devices`, `sensor_readings`, `alert_logs`, `device_state`) dengan kolom dan kunci (tabel), hubungan dan ERD, `co_level` dan `co2_level` terpisah per gas, `status` kolom turunan, `device_state` sebagai *cache*, retensi 7 hari, pembacaan yang terkait peringatan dipertahankan. Jangan masuk: uji PostgreSQL 17 (Bab 5) dan perbandingan relasional lawan dokumen (3.6.2). Sumber: rancangan-database-mvp.md, data-dan-database.md, diagram ERD.

### 4.3.6 Aplikasi Seluler (Joce)
Autentikasi (email dan sandi, AuthGate, satu akun satu perangkat), halaman Beranda (status, nilai CO dan CO₂, aktuator), Riwayat (pembacaan dan episode peringatan), Notifikasi (FCM lewat *Database Webhook* dan *Edge Function*). Cukup satu paragraf dan satu tangkapan layar per halaman. Jangan masuk: perbandingan Flutter dan web (sudah di 3.6.3, hapus dari BAB_04) dan hasil uji aplikasi.

### 4.3.7 Simulasi Model Gas (chaa)
Model massa dari Bab 2 diterapkan dengan skrip Python: parameter (volume kabin, jumlah penumpang, G, N), skenario (CO₂ naik, sumber berhenti, jendela dibuka), luaran. Hanya rancangan simulasi. Perbandingan simulasi dengan uji ada di Bab 5. Sumber: pemodelan_bab4_simulasi.py, model-vs-uji.md bagian rancangan.

## Keputusan yang harus beres sebelum menulis
1. **Konfigurasi firmware yang dilaporkan:** v2.5 (jalur CO aktif) atau v2.6 (`CO_AKTIF = false`, uji tanpa CO). Laporan menjelaskan sistem CO dan CO₂, jadi tulis v2.5 (CO aktif) dan nyatakan konfigurasinya. Pemilik: chaa dan Bara.
2. **Pin relay naik:** kode memakai GPIO18, hardware-wiring.md GPIO25. **Pin tombol Wi-Fi:** komunikasi.md GPIO14, hardware-wiring.md GPIO32. Samakan ke kode. Pemilik: Bara.
3. **Sensor CO final:** MiCS-5524 (laporan) atau MQ-7 (folder `firmware-v3.1`). Bab 4 hanya satu. Pemilik: tim.
4. **Batas naik uji arah:** laporan 25%, kode masih 0,05 (`CO_KRITERIA_TURUN`). Samakan sebelum demo. Pemilik: chaa.
5. **Versi kontrak pesan:** komunikasi.md menyebut v3 (`r3`), kerangka menyebut v4. Pakai yang ada di kode. Pemilik: Lia.
6. **Anggaran:** hitung ulang dari nota. Pemilik: Bara.
7. **Gerak jendela:** sinyal GPIO terbukti, gerak fisik belum diukur (relay belum terpasang ke motor jendela pada catatan 5 Nov). Tulis rancangan, bukan klaim gerak. Pemilik: Bara.

## Urutan kerja
Bara menyelesaikan daftar pin dan catu (4.3.2) lebih dulu, lalu chaa mengisi tabel parameter (4.3.3.7) dan dua bagian lain merujuk ke sana. Lia dan Joce berjalan paralel. chaa menyatukan, menyamakan format, dan memeriksa tidak ada hasil uji atau perbandingan yang masuk.
