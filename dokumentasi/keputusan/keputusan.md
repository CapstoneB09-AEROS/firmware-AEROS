# Keputusan (yang sudah ditetapkan)

Versi 27 Oktober 2026. Satu tempat untuk semua keputusan yang sudah final atau dipakai sebagai dasar firmware. Yang belum diputuskan ada di [belum-diputuskan.md](belum-diputuskan.md). Alasan dan bukti ada di dokumen yang ditautkan.

Status: **Diputuskan** (oleh pengguna atau tim), **Sementara** (dipakai di rancangan, diuji ulang nanti), **Terbukti** (ada data atau sumber yang dibaca). `[C251]` = dokumen rencana awal tim (14 Agustus 2026, **tidak direvisi**). C-501 = laporan hasil, tenggat setelah expo.

## 1. Gambaran sistem
Kabin mobil tertutup bisa dipenuhi CO2 dari napas dalam hitungan menit, dan CO dari kendaraan lain bisa ikut masuk. Prototipe AEROS membaca CO2 (NDIR MH-Z19C) dan memperkirakan CO (semikonduktor MiCS-5524 lewat ADS1115), lalu memberi peringatan bertingkat dan membuka jendela. Tanpa gas CO asli atau alat pembanding, nilai CO hanya **estimasi indikatif**. Keputusan alarm dan jendela dibuat di ESP32 tiap 1 detik dan **tidak bergantung internet**.

Yang tidak dikerjakan: kalibrasi dengan gas CO standar, kompensasi suhu dan kelembapan, pengujian formal di kendaraan nyata (uji mobil dilaporkan sebagai uji eksplorasi tambahan), anti-jepit jendela.

## 2. Aturan alarm dan jendela
| Keputusan | Nilai | Dasar | Status |
|---|---|---|---|
| CO waspada | estimasi **>= 35 ppm** bertahan **30 detik** | NIOSH REL 35 ppm, WHO 1 jam sekitar 30 ppm; biaya tindakan keliru kecil ([peringatan-dan-ambang.md](peringatan-dan-ambang.md) B) | Sementara (30 detik) |
| CO bahaya | **>= 87 ppm**, tanpa konfirmasi; aturan jendela sama dengan 35 ppm | WHO 15 menit 87 ppm | Diputuskan 25 Okt |
| Ambang CO dalam ppm estimasi | bukan perubahan relatif | keputusan pengguna; ppm bergantung R0, jadi selalu berlabel estimasi | Diputuskan 25 Okt (B2) |
| Uji arah (CO dalam atau luar) | jendela dibuka, **30 detik**; Rs turun **> 25%** dari awal uji = sumber luar, jendela ditutup; CO turun = sumber dalam, tetap terbuka; **tidak jelas = anggap luar dan tutup** | kriteria 8% dan 15% terlampaui gerakan alami Rs; 25% tidak pernah terlampaui tanpa gas dalam sekitar 28.000 detik ([analisis/ringkasan-temuan.md](../analisis/ringkasan-temuan.md)) | Diputuskan 27 Okt (B5, B6 sementara) |
| CO selesai | **< 30 ppm selama 60 detik** | sekitar 6 kali konstanta waktu filter | Sementara (B7) |
| Prioritas | **CO menang atas CO2**; selama aturan CO aktif, aturan CO2 diabaikan | keputusan tim | Diputuskan 25 Okt |
| Setelah menutup karena sumber luar | uji arah tidak diulang sampai CO selesai | mencegah paparan berulang | Sementara |
| CO2 peringatan | **>= 2500 ppm**, 3 bacaan valid berturut-turut | Satish 2012 (bukti lemah, jadi peringatan lembut) | Sementara |
| CO2 tindakan | **>= 4000 ppm** (bukan 4500), 3 bacaan valid, bila aturan CO tidak aktif | akurasi sensor sekitar ±250 ppm, jeda sensor sekitar 200 ppm saat naik cepat, batas paparan kerja 5000 ppm, pedoman ISS 4000-5000 (A2 dan A3 di peringatan-dan-ambang.md); naik 500 ppm lagi hanya menambah sekitar 2,5 menit | Diputuskan 27 Okt |
| CO2 selesai | **< 2500 selama 3 bacaan (10 detik)** dan jendela terbuka minimal 20 detik | data Avanza: ditutup di bawah 2500 sudah cukup, CO2 terus turun sesudahnya | Sementara (B8) |
| Jendela | bukaan **setengah lewat waktu motor** (`WAKTU_SETENGAH`, diukur per mobil); tahan sampai bacaan < 2500; **maks. 180 detik**, **min. 20 detik**; jeda tertutup minimal **5 menit** | saran teman elektro; data Avanza (95-110 detik sampai < 2500, siklus 15,6 menit) | Sementara (B9) |
| Anti-jepit | **tidak dibangun**, ditulis sebagai batasan; tanyakan apakah jendela Classy punya anti-jepit pabrik | waktu dan risiko | Diputuskan 27 Okt |
| Sensor gagal | satu sensor gagal: tampilkan peringatan sensor itu, **sensor sehat tetap menjalankan aturannya**. Kedua gagal: GANGGUAN tanpa aksi otomatis. ADS1115 tidak ada: tampilkan error dan coba lagi | aman saat gagal | Diputuskan 25 Okt (B10) |
| Data tidak valid | nilai 410 atau 500 setelah sensor mulai ulang **bukan** "udara aman"; aksi yang sudah aktif tidak dibatalkan bacaan seperti itu | log MH-Z19C | Sementara |
| Jaringan | alarm, buzzer, dan jendela **tidak bergantung internet**; kegagalan jaringan tidak boleh menghentikan alarm | rencana awal [C251] | Diputuskan |

## 3. Pengolahan sinyal dan kalibrasi
| Keputusan | Nilai | Dasar | Status |
|---|---|---|---|
| Interval siklus | **tepat 1 detik** | syarat filter jumlah genap | Diputuskan |
| Filter CO | **SMA 6 pada Rs** (sebelum dibagi R0). Cadangan: SMA 8 (jalan bergelombang, alarm palsu), SMA 4 (lebih cepat), EMA 0,1 (bila pola 2 detik hilang di PCB) | sekitar 95% goyangan Rs berupa pola bergantian tiap detik; jumlah genap menghapusnya; SMA 6 lebih halus dari EMA 0,2 di kamar dan mobil ([analisis/filter.md](../analisis/filter.md)) | Sementara (B12) |
| Filter CO2 | tidak ada, hanya tolak data rusak | sensor sudah lambat (T90 < 120 detik) | Sementara |
| Pemanasan | **180 detik** untuk CO **dan** CO2; selama pemanasan LCD tidak menampilkan angka sensor itu (`----`), serial tetap mencatat, data dikirim dengan penanda | MH-Z19C: nilai palsu sampai detik 64 (4 dari 5) dan 128 (1); MiCS: nyala dingin 26 Okt pagi Rs 156 -> sekitar 1650 kOhm dalam 3 menit ([algoritma-firmware.md](algoritma-firmware.md) 2.7) | Diputuskan 27 Okt (B11) |
| Kurva CO | **A = 3,7, beta = 0,856** (satu paket) | pembacaan grafik datasheet; digitalisasi piksel memberi 3,46 dan 0,840, selisih < 1,5% di 35-100 ppm ([parameter-dan-sumber.md](parameter-dan-sumber.md) A1) | Diputuskan 27 Okt |
| R0 | **satu nilai tetap 1730 kOhm**, berlabel estimasi; ukur ulang **sekali** (perintah `r`, udara bersih) setelah buck terpasang | R0 kamar tidak cocok di mobil (Rs/R0 0,30-0,69), dan R0 ini di atas batas datasheet 100-1500 kOhm | Diputuskan 27 Okt (B1) |
| VCC di kode | **4,64 V** sampai buck terpasang; lalu ubah sekali dan ukur R0 ulang; catat VCC di tiap log | pengukuran 26 Okt: pin MiCS 4,64-4,79 V (di bawah 4,9 V datasheet) | Diputuskan 26 Okt |
| Kalibrasi otomatis CO2 (ABC) | dimatikan untuk mobil | manual Winsen | Usulan, perlu konfirmasi (B16) |
| ppm CO | selalu **estimasi indikatif**; pesan "kemungkinan CO atau gas lain" | tanpa gas acuan; sensor tidak selektif (uji parfum: Rs -92%, estimasi 72-83 ppm) | Terbukti (sifat sensor) |

## 4. Status, bunyi, dan tampilan (ringkas)
Rincian dan pseudocode di [algoritma-firmware.md](algoritma-firmware.md) bagian 2.10.

| Hal | Keputusan |
|---|---|
| Status | **5**: `PEMANASAN`, `NORMAL`, `WASPADA`, `BAHAYA`, `GANGGUAN`; jenis gas ditulis di baris LCD (`WASPADA CO`, `BAHAYA CO2`, `BAHAYA CO LUAR`). Di database tetap 3 nilai (`normal`, `waspada`, `bahaya`) plus penanda pemanasan atau gangguan |
| Bunyi waspada (CO >= 35 atau CO2 >= 2500) | 3 bip pendek (sekitar 2 detik), sekali saat masuk level |
| Bunyi bahaya (CO >= 87, CO2 >= 4000, CO luar) | 1 bip panjang (sekitar 3 detik), sekali saat masuk level |
| Pengulangan | CO: tiap 60 detik sampai kondisi turun atau "Saya Tahu", maksimum 5 menit. CO2: tidak diulang. Naik level selalu berbunyi |
| "Saya Tahu" | mematikan bunyi **saja**; alarm dan jendela tetap berjalan; bunyi muncul lagi bila naik ke bahaya |
| LCD 16x2 | angka seperti v0 (`CO: 12ppm`), tag status 4 karakter `OK/WARM/WARN/DANG/LUAR/ERR`, indikator Wi-Fi 1 karakter `W/w/-/P` di ujung kanan baris atas |
| Angka palsu masa pemanasan | tidak tampil di LCD dan aplikasi; tetap tercatat di serial |

## 5. Data dan komunikasi (ringkas)
Rincian di [komunikasi.md](komunikasi.md) dan [data-dan-database.md](data-dan-database.md).

| Keputusan | Nilai | Status |
|---|---|---|
| Laju | keputusan tiap 1 detik; telemetri tiap 5 detik (nilai terakhir dan puncak), tidak mengambil satu sampel tiap 5 detik | Sementara |
| Offline first | tulis ke flash dulu, hapus hanya setelah ACK database yang tanda tangannya benar | Diputuskan (kode tim) |
| Keamanan | HMAC-SHA256 pada telemetri, ACK, perintah; TLS dengan sertifikat diperiksa; nonce; last will; rahasia di luar git | Diputuskan (kode tim) |
| Pesan | versi 3 jadi acuan; **worker dan komunikasi mengikuti kebutuhan firmware dan data** | Diputuskan 27 Okt |
| `alert_logs` | worker menulisnya dengan `id = event_id` dari ESP32 | Diputuskan 27 Okt |
| Nilai tidak diketahui | dikirim `null`, tidak pernah angka palsu | Diputuskan (kode tim) |
| Jam | NTP di ESP32; `timestamp = 0` dan `time_valid = false` bila belum sinkron | Diputuskan (kode tim) |
| Portal Wi-Fi | hotspot `AEROS-Setup`, tombol GPIO14 ke GND 5 detik; Wi-Fi lama tidak dihapus sebelum yang baru berhasil | Diputuskan (kode tim) |
| Tabel partisi ESP | `huge_app.csv` (kode tim tidak muat di partisi bawaan) | Perlu disepakati dengan tim |

## 6. Kebutuhan fungsional dan non-fungsional
| ID | Kebutuhan | Status |
|---|---|---|
| FR-01 | CO2 >= 2500 (3 bacaan valid): peringatan (3 bip pendek sekali) dan peringatan di aplikasi | Sementara |
| FR-02 | CO2 >= 4000 (3 bacaan valid) dan aturan CO tidak aktif: bahaya, 1 bip panjang, buka jendela setengah (waktu motor) | Sementara |
| FR-03 | CO2 < 2500 selama 3 bacaan dan jendela terbuka >= 20 detik: tutup jendela, hentikan bunyi | Sementara |
| FR-04 | CO estimasi >= 35 ppm bertahan 30 detik: waspada, buka jendela (uji arah) | Sementara |
| FR-05 | Uji arah 30 detik: Rs turun > 25% = sumber luar (tutup sampai CO < 30 ppm selama 60 detik); CO turun = sumber dalam (tetap terbuka); tidak jelas = luar | Diputuskan |
| FR-06 | Aturan CO menang atas CO2 | Diputuskan |
| FR-07 | Setelah menutup karena sumber luar, uji arah tidak diulang sampai aturan CO selesai | Sementara |
| FR-08 | CO >= 87 ppm: bahaya langsung tanpa konfirmasi | Diputuskan |
| FR-09 | Data tidak valid: tampilkan gangguan, **jangan** gerakkan jendela otomatis; 410/500 setelah mulai ulang bukan "aman" | Sementara |
| FR-10 | Pemanasan 180 detik untuk CO dan CO2; tidak ada alarm selama pemanasan; dihitung ulang bila sensor mati sebentar | Diputuskan |
| FR-11 | Pola bunyi dan pesan layar dibedakan (bagian 4) | Diputuskan |
| FR-12 | "Saya Tahu" mematikan bunyi saja; pengulangan CO berhenti sendiri setelah 5 menit | Diputuskan |
| FR-13 | Jendela lewat relay; bukaan berbasis waktu motor; jeda minimal 5 menit; anti-jepit tidak dibangun | Sementara |
| FR-14 | Alarm dan jendela tidak bergantung internet | Diputuskan |
| FR-15 | Data tiap 5 detik (nilai terakhir dan puncak) dan kejadian saat status berubah; data simulasi berlabel | Sementara |
| FR-16 | Mode simulasi untuk dua skenario (sumber dalam: CO turun saat jendela dibuka; sumber luar: CO naik), berlabel jelas | Sementara |
| NFR-01 | Keterlambatan total deteksi (filter, konfirmasi, respons) <= 10-20% waktu menuju bahaya (anggaran sekitar 60-120 detik untuk CO luar 200 ppm) | Sementara |
| NFR-02 | Bunyi <= 5 detik sejak status berubah; jendela mulai bergerak <= 10 detik | Dari rencana awal |
| NFR-03 | Jendela tidak membuka-menutup lebih dari N kali per 10 menit | Terbuka (N belum diputuskan) |
| NFR-04 | Alarm palsu pada data udara bersih: nol per jam | Sementara |
| NFR-05 | Nilai CO ditampilkan sebagai estimasi indikatif; pesan "kemungkinan CO atau gas lain" | Terbukti |
| NFR-06 | Perubahan kadar atau waktu pada uji tercatat bersama alasannya | Sementara |

## 7. Kode B yang sudah diputuskan
Kode B menghubungkan butir di [algoritma-firmware.md](algoritma-firmware.md) dengan keputusannya.

| Kode | Keputusan |
|---|---|
| B1 | R0 satu nilai tetap 1730 kOhm berlabel estimasi; ukur ulang sekali setelah buck |
| B2 | Ambang CO memakai angka ppm estimasi |
| B4 | Ambang bahaya CO 87 ppm; aturan jendela sama dengan 35 ppm |
| B5 | Uji arah 30 detik (sementara) |
| B6 | Kriteria 25%; tidak jelas = luar, tutup |
| B10 | Sensor sehat tetap jalan saat sensor lain gagal |
| B11 | Pemanasan 180 detik untuk keduanya |
| B15 | Pola bunyi dan "Saya Tahu" (bagian 4); tombol fisik dan jenis buzzer masih terbuka |
| B18 | Angka LCD, tag status, indikator Wi-Fi; teks aplikasi masih terbuka |

## 8. Cara menulis di laporan
Kalimat aman dan batasan ada di [batasan-sistem.md](batasan-sistem.md) dan [komunikasi.md](komunikasi.md) (bagian C). Prinsipnya: gunakan "estimasi", "indikatif", dan "peringatan dini"; jangan "akurat", "terkalibrasi", atau "alat keselamatan"; nyatakan dampak keterbatasan, bukan hanya fakta bahwa tidak dilakukan.

## Istilah
| Istilah | Arti sederhana |
|---|---|
| ppm | Bagian per sejuta, satuan kadar gas |
| Rs, R0 | Hambatan sensor sekarang, dan hambatan di udara bersih (patokan) |
| TWA | Rata-rata selama waktu kerja |
| IDLH | Kadar yang langsung berbahaya bagi nyawa |
| T90 | Waktu sampai pembacaan mencapai 90% dari perubahan sebenarnya |
| SMA, EMA | Dua cara merata-ratakan data agar lebih halus |
| Histeresis | Batas nyala dan batas padam dibuat berbeda agar alarm tidak nyala-mati terus |
| Uji arah | Membuka jendela sebentar untuk melihat apakah CO naik (sumber luar) atau turun (sumber dalam) |
| Peluruhan (decay) | Cara mengukur pertukaran udara dari seberapa cepat kadar gas turun |
| Offline first | Data ditulis ke flash dulu dan dikirim kemudian, jadi tidak hilang saat jaringan putus |
