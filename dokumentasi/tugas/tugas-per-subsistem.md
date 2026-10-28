# Tugas dan Parkir per Subsistem

Versi 27 Oktober 2026. Satu daftar tugas yang dikelompokkan per subsistem, dengan **parkir** (ditunda, jangan dikerjakan dulu) di tiap kelompok. Keputusan yang sudah final ada di [keputusan.md](../keputusan/keputusan.md), yang masih terbuka di [belum-diputuskan.md](../keputusan/belum-diputuskan.md), uji di [pengujian/](../pengujian/rencana-uji.md).

Aturan kerja: (1) angka di firmware punya status `Terbukti`, `Sebagian`, atau `Asumsi` ([parameter-dan-sumber.md](../keputusan/parameter-dan-sumber.md)); (2) jangan mengubah angka di kode sebelum statusnya jelas atau keputusannya dicatat; (3) temuan baru dicatat di berkas yang sesuai, bukan hanya di chat; (4) ide baru yang belum waktunya masuk ke **Parkir**; (5) ringkasan hasil pencarian dianggap belum terverifikasi sampai sumber aslinya dibuka; (6) `src/main.cpp` (v0) tidak diubah tanpa izin eksplisit, firmware baru ditulis di cabang `firmware-baru`.

## Jadwal menuju expo (30 Oktober 2026)
PCB belum datang, jadi demo dirancang **berjalan di breadboard**; PCB hanya bonus.

| Hari | Fokus | Status |
|---|---|---|
| Min 25 | Uji mobil 1 dan baseline kamar, firmware lama | selesai |
| Sen 26 | Uji kamar pagi, ruang rapat, uji mobil Avanza; ESP baru diunggah | selesai |
| Sel 27 | Keputusan desain, analisis kode tim, uji parfum; **firmware gabungan lapis 1** (menunggu "tulis"); bertemu tim | berjalan |
| Rab 28 | Uji gabungan sampai aplikasi; uji mobil dengan firmware baru bila sempat; susun diorama | belum |
| Kam 29 | Rekam video 3 menit, latihan demo; **firmware dibekukan siang hari** | belum |
| Jum 30 | Expo | |

**Batas minimum demo:** CO2 naik karena napas lalu bunyi dan jendela bergerak; kasus CO lewat **mode simulasi berlabel**; data di LCD, dan di aplikasi bila MQTT sempat jadi (bila tidak, tampilkan data rekaman). **Dipotong dulu bila perlu:** PCB, tabel sensitivitas lengkap, sisa verifikasi sumber, uji mobil tambahan, jendela Classy asli (cadangan: servo dengan panel mika seperti rencana awal).

## 1. Firmware (ESP32, pengguna dan asisten)
| Tugas | Status | Catatan |
|---|---|---|
| Firmware gabungan lapis 1: SMA 6, validasi, pemanasan 180 detik, aturan CO dan CO2, status 5 level, bunyi, LCD, mode simulasi, `WAKTU_SETENGAH` | menunggu "tulis" | di cabang `firmware-baru`; ganti isi `sensorOriginal.inl` kode tim dengan inti baru, antarmuka berupa struktur data (bukan teks CSV) |
| Perbaiki kode tim agar bisa dikompilasi (`lcd` dan `prefs` terdefinisi dua kali), pakai `huge_app.csv`, jangan berhenti total bila konfigurasi atau flash gagal | menunggu firmware gabungan | lihat [analisis-kode-tim.md](../analisis/analisis-kode-tim.md) |
| Bandingkan firmware lama dan baru dengan memutar ulang log yang sama | setelah firmware baru | noise, jumlah alarm, perpindahan status |
| T1 uji mandiri saat menyala, T2 watchdog dan alasan reset | usulan | [komunikasi.md](../keputusan/komunikasi.md) bagian 7 |
| Ubah `VCC` di kode sekali setelah buck terpasang, lalu ukur R0 ulang | menunggu PCB | tulis VCC di tiap log |
| Skrip tabel sensitivitas (konfirmasi dan pemulihan lawan alarm palsu) | opsional | |

**Parkir:** buzzer terpisah untuk CO2 (selesai diputuskan, bunyi pendek); alarm berbasis kadar dikali waktu; penyaring lonjakan tunggal (median lalu EMA); baseline adaptif; kompensasi suhu dan kelembapan.

## 2. Hardware (teman hardware)
| Tugas | Prioritas |
|---|---|
| Ukur 5 V dengan Min/Max 15 menit di pin ESP, pin MiCS, pin MH-Z19C; ukur ulang setelah buck | tinggi |
| Waktu gerak motor jendela (setengah dan penuh) tiap mobil: Classy, Civic, Avanza | tinggi (P1) |
| Pin buzzer dan jendela di PCB; GPIO14 dipakai tombol portal Wi-Fi | tinggi (P1) |
| Tombol fisik "Saya Tahu" (pin lain) dan jenis buzzer (aktif atau pasif) | tinggi |
| Cara mengendalikan power window Classy: relay di jalur tombol, 12 V, arus maksimum, sekring, isolasi dari ESP32; perilaku saat daya jatuh | tinggi (P1) |
| Apakah anti-jepit pabrik aktif pada penutupan lewat relay | tinggi (P1); kita tidak membangunnya |
| Tegangan MiCS ke ADS1115 melewati batas (3,68 V pada catu 3,3 V): pembatas atau pembagi tegangan | tinggi (P1) |
| Konektor USB longgar (CP2102 terlepas dua kali pada 25 Okt) dan MH-Z19C sempat mati sendiri | tinggi (P1) |
| Buck converter: atur 5,0-5,05 V sebelum dihubungkan, sekitar 2 A, ground bersama, kapasitor, jangan memparalel USB dan buck | sedang |
| Tegangan pemanas MiCS dan resistor seri; nilai RL (firmware 9970 ohm, minimal datasheet 820 ohm) | sedang |
| Penjelasan siklus Rs sekitar 7-12 menit dan goyangan 0,5 Hz: apakah 5 V atau ground ikut berayun dengan periode itu | sedang |
| Housing: ventilasi ke sensor, jauh dari panas dan matahari, tahan debu; PCB: kapasitor dekat sensor, grounding | sedang |
| Catu mobil: adaptor 12 V ke 5 V (noise, penurunan saat mesin dinyalakan); sumber daya siaga | sedang |
| Pin yang dipakai sekarang: SDA 21, SCL 22, buzzer 25, UART2 RX 16 dan TX 17, LCD 0x27, ADS1115 0x48 | cocokkan dengan ESP final |

**Parkir:** sensor suhu dan kelembapan; kalibrasi dengan lab kampus atau gas standar (tidak ada akses; pengembangan lanjutan). Uji gas pengganti (korek tanpa api) hanya sedikit, singkat, ruang berventilasi, bukan di kabin atau area SPBU.

## 3. Komunikasi dan backend (teman backend)
| Tugas | Catatan |
|---|---|
| Kerjakan worker mengikuti pesan v3 (field tambahan, penanda pemanasan, kolom `co_peak_*`) | keputusan 27 Okt: worker mengikuti firmware ([komunikasi.md](../keputusan/komunikasi.md)) |
| `alert_logs`: simpan gas, nilai, ambang, sumber | pengisi: worker, `id = event_id` |
| Kebijakan antrean penuh, tabel partisi, penyiapan LittleFS | [belum-diputuskan.md](../keputusan/belum-diputuskan.md) bagian 4 |
| Akun HiveMQ, kunci HMAC, sertifikat (diisi lokal, tidak masuk git), hotspot 2,4 GHz untuk uji | |
| Perbaikan database: `ON DELETE CASCADE`, `created_at`, `trigger_source` bawaan, indeks, tugas penghapusan 7 hari ([data-dan-database.md](../keputusan/data-dan-database.md)) | cascade harus diperbaiki sebelum penghapusan dijadwalkan |
| Batas ukuran paket Supabase dan kuota data hotspot (sekitar 3,5 MB per hari pada 5 detik) | belum dicek |
| Uji dengan penerbit data palsu (dua skenario simulasi) | |
| ACL HiveMQ per perangkat | |
| Data uji untuk laporan disimpan terpisah sebagai CSV | |

**Parkir:** beberapa perangkat dengan kunci berbeda per perangkat; retensi berlapis (ringkasan 1 menit).

## 4. Aplikasi (teman software)
| Tugas | Catatan |
|---|---|
| CO ditampilkan sebagai **estimasi indikatif**, pesan "kemungkinan CO atau gas lain" | P1 |
| Perangkat offline tidak boleh tampil "aman": "data terakhir X detik lalu", tidak terhubung bila lebih dari 30 detik (T3) | P1 |
| Label **"simulasi"** yang jelas pada data simulasi | P1 |
| Data bertanda pemanasan tidak ditampilkan sebagai nilai nyata | setelah penanda ada |
| Notifikasi peringatan dan tombol "Saya Tahu" (mematikan bunyi, tidak memicu peringatan berulang untuk kejadian yang sama); pastikan `alert_logs.id` = `event_id` | |
| Warna status sesuai 5 status (hijau, kuning, merah) | |
| Grafik riwayat dari data 5 detik (7 hari) dan pemadatan titik; log kejadian | |
| Mode demo untuk expo; ukur latensi data bersama tim backend | |
| Rancangan tidak mengganggu pengemudi: sedikit interaksi, teks besar | |

**Parkir:** uji pengguna kecil (5-10 orang) untuk cara peringatan.

## 5. Pengujian dan analisis (pengguna dan asisten)
| Tugas | Status |
|---|---|
| Uji parfum di mobil: satu semprotan, jendela tertutup, rekam 5 menit, di akhir sesi | belum |
| Uji jendela Civic atau mobil lain (N dan waktu motor) | belum |
| T22: setelah ganti ESP final, ukur 5 V dengan Wi-Fi aktif, perbarui `VCC`, ulangi uji kamar 30 menit dengan Wi-Fi (tahap A Wi-Fi mati, B1 tersambung diam, B2 kirim) dan bandingkan dengan log ESP lama | menunggu firmware gabungan dan akun |
| Uji gabungan sampai aplikasi | menunggu |
| Cocokkan model C-251 Bab 10 dengan data uji mobil berlog (T19) | opsional |
| Verifikasi sisa sumber: Scully, halaman OSHA CO2, Permenaker dan Permenkes, Persily, ADS1115, studi kabin (T3 sisa) | tertunda |
| Setelah PCB dan housing: ulangi uji singkat (baseline, noise, respons) dan kunci angka akhir (T14) | menunggu |

**Parkir:** uji cabut MH-Z19C (dibatalkan: dikhawatirkan merusak rangkaian; alternatif perangkat lunak: ubah interval siklus 1,0 ke 1,25 detik di firmware baru); membaca sumber filter (Smith bab 15) bila perlu.

## 6. Laporan dan demo
| Tugas | Catatan |
|---|---|
| Naskah expo, skrip video 3 menit, isi banner, konsep diorama | pengguna menulis, asisten membantu draf |
| T5 daftar periksa demo dan rekaman cadangan (hotspot 2,4 GHz, pemanasan 3 menit sebelum penonton datang, uji bip, cek R0) | usulan |
| Rencana cadangan demo | [belum-diputuskan.md](../keputusan/belum-diputuskan.md) bagian 6 |
| Kerangka C-501 (bab, sumber data, temuan mana yang masuk badan atau lampiran) | [kerangka-c501.md](kerangka-c501.md) |
| Bahan C-501: koreksi isi C-251 (T15, T17), cara uji CO (T16), lokasi sensor (T18), anggaran (T20); **C-251 tidak direvisi** | [analisis/perbandingan-c251.md](../analisis/perbandingan-c251.md) |
| Pembagian penulisan C-501 dari artefak uji | |
| Commit dan push dokumentasi dan log | menunggu izin |

## Pertemuan tim (skenario ringkas)
Wi-Fi tersambung tapi diam berbeda dengan Wi-Fi mengirim data (arus naik tajam sesaat saat kirim), jadi diuji terpisah.

1. **Buka (5 menit):** ESP final, uji dasar, keputusan Wi-Fi, jadwal sampai 29 Okt siang.
2. **Persiapan (10 menit):** ganti ESP; ukur 5 V di pin sensor; perbarui `VCC` bila beda dari 4,64 V; catat pinout PCB.
3. **Tahap A (30 menit):** ESP baru, firmware lama, Wi-Fi mati. Sambil jalan bahas **hardware** (pinout, penggerak jendela, anti-jepit, waktu motor, tegangan ke ADS1115).
4. **Tahap B1 (15 menit):** Wi-Fi tersambung, belum kirim. Ukur 5 V dan lihat noise.
5. **Tahap B2 (15 menit):** kirim telemetri tiap 5 detik. Ukur 5 V lagi. Sambil jalan bahas **backend** (format pesan, retensi, perubahan database).
6. **Bandingkan A, B1, B2 (10 menit):** 5 V minimum dan maksimum, goyangan Rs, periode siklus, ada tidaknya mulai ulang. Putuskan apakah catu sensor dipisah.
7. **Software (10 menit):** estimasi, "kemungkinan CO atau gas lain", offline tidak tampil "aman".
8. **Jadwal dan tugas (10 menit):** siapa memegang ESP dan sensor jam berapa; firmware dibekukan 29 Okt siang.
9. **Tutup:** daftar keputusan, penanggung jawab, tenggat.

Satu ESP final untuk demo harus dipilih lebih dulu: ESP yang dipakai firmware punya modul Wi-Fi rusak, ESP tim software punya Wi-Fi. Pilih satu, lalu pindahkan kode sensor dan MQTT ke sana.
