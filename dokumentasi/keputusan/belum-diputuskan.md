# Yang Belum Diputuskan

Versi 27 Oktober 2026. Semua butir terbuka di satu tempat, dengan usulan sebagai dasar diskusi (bukan keputusan). Yang sudah final ada di [keputusan.md](keputusan.md). Tugas per orang ada di [tugas-per-subsistem.md](../tugas/tugas-per-subsistem.md).

Tenggat: firmware dibekukan **Kamis 29 Okt siang**, expo **Jumat 30 Okt**.

## 0. Harus selesai sebelum Kamis siang (urut penting)
| # | Keputusan | Siapa | Kenapa mendesak |
|---|---|---|---|
| 1 | Waktu gerak motor jendela setengah (`WAKTU_SETENGAH`) di mobil demo | hardware (ukur), pengguna (catat) | Tanpa ini logika jendela tidak bisa diuji |
| 2 | Pin buzzer dan jendela di PCB | hardware | Firmware butuh pin pasti; GPIO14 sudah dipakai tombol Wi-Fi |
| 3 | Isi pesan versi 3 dikerjakan teman backend, atau tetap v2 untuk expo | teman backend | Menentukan apa yang boleh dikirim firmware |
| 4 | Tombol fisik "Saya Tahu" dan jenis buzzer | hardware | Menentukan apakah "bahaya lebih keras" mungkin |
| 5 | Teks aplikasi (B18) | teman software | Harus ada sebelum demo |
| 6 | Rencana cadangan demo | tim | Expo tidak boleh bergantung pada satu hal |

## 1. UX
| Kode | Belum diputuskan | Usulan |
|---|---|---|
| B15e | Tombol fisik "Saya Tahu" di perangkat atau hanya lewat aplikasi | tanya hardware; GPIO14 dipakai tombol portal Wi-Fi, jadi butuh pin lain |
| B15f | "Lebih keras" untuk bahaya | tergantung jenis buzzer: bila aktif, volume tetap dan pembeda hanya pola |
| B18c | Teks di aplikasi | wajib memuat: ppm CO "**estimasi, kemungkinan CO atau gas lain**"; "perangkat offline **bukan** berarti aman"; waktu data terakhir |
| NFR-03 | Batas gerakan jendela per 10 menit | diputuskan setelah uji di mobil demo |

## 2. Angka yang masih sementara
| Kode | Parameter | Nilai sekarang | Dasar | Cara menentukan |
|---|---|---|---|---|
| B3 | Konfirmasi CO | 30 detik | sementara | replay pada log atau tabel sensitivitas |
| B5 | Lama uji arah | 30 detik | pengamatan informal (korek) | uji dengan sumber nyata bila ada |
| B6 | Kriteria "CO dari luar" | Rs turun > 25% | tanpa gas tidak pernah lewat 25% dalam sekitar 28.000 detik; satu lonjakan nyata -54%; pintu dibuka -23% | uji ulang dengan data baru |
| B7 | Batas selesai CO | 30 ppm, 60 detik | sementara | replay atau tabel sensitivitas |
| B8 | CO2: konfirmasi dan selesai | 3 bacaan, < 2500, 10 detik | data Avanza | uji mobil lain |
| B9a | Lama jendela terbuka | min 20 detik, maks 180 detik | satu mobil | uji di mobil demo |
| B9b | Jeda tertutup minimum | 5 menit | siklus alami 15,6 menit | uji di mobil demo |
| B9c | `WAKTU_SETENGAH` | **belum ada angka** | harus diukur per mobil (Classy, Civic, Avanza) | stopwatch |
| B12 | Panjang filter final | SMA 6 | data kamar dan mobil | uji ulang di PCB dan jalan bergelombang |
| B13 | Sampel tidak valid di buffer filter | kosongkan buffer bila > 3 sampel berturut-turut tidak valid | usulan teknis | |
| B16 | Kalibrasi otomatis CO2 | dimatikan | usulan | konfirmasi tim |
| B17 | Isi mode simulasi | dua skenario (sumber dalam dan luar) | disusun saat menulis firmware | |
| - | Interval telemetri | 5 detik (kode tim 10 detik) | rancangan data | keputusan tim |
| - | Kapasitas antrean flash | 360 (dugaan sebenarnya sekitar 200) | dugaan littlefs | tes Wi-Fi mati sampai antrean penuh |
| - | Pemanasan CO | 180 detik | satu uji nyala dingin bersih | cukup; satu uji lagi menambah keyakinan |

## 3. Hardware dan kalibrasi
| Hal | Catatan | Siapa |
|---|---|---|
| R0 di atas batas datasheet | 1730 kOhm lawan 100-1500 kOhm; dugaan catu 4,64 V; ukur ulang sekali setelah buck | hardware |
| VCC di kode | ubah sekali setelah buck terpasang | pengguna dan hardware |
| Pengukuran 5 V dengan Min/Max 15 menit (ESP, pin MiCS, pin MH-Z19C) | belum dilakukan dengan Min/Max; bandingkan laptop baterai dan charger | hardware |
| Pin buzzer dan jendela di PCB | GPIO14 sudah dipakai | hardware |
| Relay jendela | arus, jenis, perilaku saat daya jatuh | hardware |
| Anti-jepit | tidak dibangun; apakah jendela Classy punya anti-jepit pabrik | hardware |
| Tombol portal Wi-Fi (GPIO14 ke GND, 5 detik) | ada di desain PCB atau tidak | hardware |
| Cara mendeteksi sensor mati sebentar tanpa ESP mulai ulang | sisa B11 | pengguna |
| Pengaruh Wi-Fi menyala terhadap Rs dan catu | uji T22 setelah firmware gabungan | pengguna |
| Siklus Rs sekitar 7-12 menit, +/-13-17% | penyebab belum diketahui; kandidat: catu, regulator, kondisi laptop | hardware |
| Tegangan MiCS ke ADS1115 | pernah 3,68 V, melewati batas sekitar 3,6 V pada catu 3,3 V | hardware |

## 4. Data, jaringan, backend
| Hal | Usulan | Siapa |
|---|---|---|
| Kolom `co_peak_*` di `sensor_readings`, dan field tambahan kita (`rs_r0_milli`, `kond_*`, `fase_*`, `fw`) | tambahkan bersama di dua sisi (ESP dan worker) | teman backend |
| `alert_logs`: simpan gas, nilai, ambang, sumber | ya, kecil | teman backend |
| Kebijakan antrean penuh | buang telemetri tertua, lindungi kejadian (kode tim menolak data baru) | teman backend |
| Tabel partisi ESP dan penyiapan LittleFS | `huge_app.csv`; folder `data/` untuk penyiapan sudah dihapus | teman backend |
| Akun HiveMQ, kunci HMAC, sertifikat | diisi lokal, tidak masuk git | teman backend |
| Retensi data | 5 detik disimpan 7 hari, `alert_logs` dan `actuator_logs` lama | teman backend |
| ACL HiveMQ | satu topik `aeros/data` untuk semua perangkat: disengaja? | teman backend |
| Perbaikan database | `ON DELETE CASCADE` -> `SET NULL`, `created_at` vs `measured_at`, `trigger_source` bawaan, indeks | teman backend |
| Hotspot 2,4 GHz untuk uji | | tim |
| Notifikasi di aplikasi | bagaimana dibuat sekarang, dan apakah `alert_logs.id` = `event_id` | teman software |
| Cara aplikasi membaca data | langsung dari database atau lewat layanan | teman software |
| Jam: NTP di ESP32 atau cap waktu server | NTP (sudah di kode tim) | selesai |

**Pertanyaan untuk teman backend (hasil uji versi 3):**
1. Apakah versi ini berhasil dikompilasi di laptopmu, dan apa bedanya dengan file yang kuterima (`lcd` dan `prefs` terdefinisi dua kali)?
2. Tabel partisi apa yang dipakai, dan bagaimana LittleFS disiapkan?
3. Maukah worker menyimpan gas, nilai, ambang, dan sumber di `alert_logs`?
4. Setuju bila isi `sensorOriginal.inl` diganti inti sensor baru dengan antarmuka struktur (bukan teks CSV)?
5. Apakah grafik aplikasi menyaring data bertanda pemanasan (setelah penanda ditambahkan)?
6. Apakah kolom `co_peak_*` sudah dibuat di database?
7. Apakah tombol portal Wi-Fi ada di desain PCB?

## 5. Usulan tambahan ringan (menunggu persetujuan)
T1 uji mandiri saat menyala, T2 watchdog dan alasan reset, T3 "data terakhir X detik lalu" di aplikasi, T4 `fw`, `r0_kohm`, `rst` di pesan `ONLINE`, T5 daftar periksa demo dan rekaman cadangan. Rincian di [komunikasi.md](komunikasi.md) bagian 7.

## 6. Laporan dan demo
| Hal | Catatan |
|---|---|
| Rencana cadangan demo | jendela diganti diorama atau servo (rencana awal) bila mobil tidak aman; mode simulasi bila jaringan mati; rekaman video dan log CSV |
| Cara menguji deteksi CO tanpa sumber CO (T16) | gas pereduksi pengganti (butana dari korek, **bukan CO**), mode simulasi berlabel, atau ubah spesifikasi "4 dari 5 uji". Jangan membuat CO sendiri |
| Lokasi sensor di kabin (T18) | [C251] menyebut "konsol bawah dashboard karena CO2 lebih berat", bertentangan dengan asumsi well-mixed |
| Daftar komponen dan anggaran (T20) | MiCS-5524, ADS1115, LCD I2C menggantikan MQ-7; batas Rp2.000.000 dan komponen tunggal Rp500.000 |
| Pembagian C-501 | siapa menulis apa dari artefak uji |
| Koreksi isi C-251 | dicatat sebagai bahan C-501; C-251 tidak direvisi ([analisis/perbandingan-c251.md](../analisis/perbandingan-c251.md)) |
| Uji jendela Civic dan mobil lain | belum dilakukan |
| Cara mencatat batasan | ppm estimasi, anti-jepit tidak dibangun, angka jendela dari satu mobil, alarm bisa dipicu gas lain, offline bukan berarti aman |

## 7. Asumsi dan dugaan yang belum terbukti
| # | Asumsi atau dugaan | Cara membuktikan |
|---|---|---|
| S1 | Udara kamar bersih (CO mendekati nol) | tidak bisa dibuktikan tanpa alat; nyatakan sebagai asumsi |
| S2 | Goyangan Rs 0,5 Hz berasal dari catu pemanas atau siklus MH-Z19C | uji cabut MH-Z19C (dibatalkan); alternatif: ubah interval siklus firmware dari 1,0 ke 1,25 detik dan lihat apakah periode siklus lambat berubah |
| S3 | Siklus Rs lambat bukan akibat AC, kipas, pintu, atau orang; sumber tidak diketahui | uji dengan catu berbeda (buck converter) |
| S4 | USB putus karena konektor longgar | ganti kabel atau perbaiki sambungan |
| S5 | Rentang MH-Z19C berbatas atas 5000 ppm | cek stiker modul (T2) |
| S6 | Angka standar CO dan CO2 (OSHA, NIOSH, UL, WHO, Satish): sebagian terverifikasi dari teks asli, sisanya belum | [daftar-pustaka.md](../referensi/daftar-pustaka.md) bagian B dan C |
| S7 | Hasil tidak berubah di PCB dan housing | ulangi uji singkat setelah PCB (T14) |
| S8 | R0 di atas batas datasheet karena catu 4,64 V | ukur ulang R0 setelah buck |
| S9 | Mode AC tidak diandalkan sebagai tindakan | keputusan desain berdasarkan variasi antar mobil; dicatat saja |
