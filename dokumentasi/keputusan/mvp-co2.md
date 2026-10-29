# MVP Expo: Skema CO2 Saja

Versi 29 Oktober 2026. Keputusan pengguna: untuk expo (Jumat 30 Okt) yang diintegrasikan hanyalah jalur **CO2**. Sensor MiCS-5524 dan ADS1115 tetap terpasang di PCB tetapi **tidak dipakai** (tidak dibaca, tidak dikirim, tidak memicu alarm). Tujuan: satu jalur utuh dari hardware sampai aplikasi yang benar-benar jalan, bukan dua jalur yang setengah jalan.

Angka rancangan lengkap ada di [algoritma-firmware.md](algoritma-firmware.md); pesan data di [komunikasi.md](komunikasi.md). Dokumen ini hanya memotong cakupan.

## 1. Alur MVP
```
MH-Z19C --> ESP32 --(Wi-Fi, MQTT TLS)--> worker --> Supabase --> aplikasi
              |  aturan CO2 (di ESP, tanpa internet)                ^
              +-- LCD, buzzer, relay jendela (turun)                |
                                  "Saya Tahu" <---------------------+
```
Alarm dan jendela diputuskan di ESP32 dan tidak menunggu internet.

## 2. Apa yang dipakai dan apa yang diabaikan
| Bagian | MVP |
|---|---|
| MH-Z19C, pemanasan 180 detik, validasi | **dipakai** |
| Aturan CO2: peringatan ≥ 2500, tindakan ≥ 4000 (3 bacaan), selesai < 2500 selama 10 detik; jendela buka min 20 detik, maks 180 detik, jeda 300 detik | **dipakai** (angka rancangan, bukan mode pengembangan) |
| Buzzer (3 bip waspada, 3 detik bahaya), LCD, relay jendela turun (GPIO26) | **dipakai** |
| MiCS, ADS1115, R0, aturan CO, uji arah, simulasi CO | **diabaikan** (parkir) |
| Telemetri v3, antrean flash, ACK, tanda tangan, "Saya Tahu" | **dipakai** |

Bukti angka rancangan cocok untuk demo: di uji 6 napas ke kotak menaikkan CO2 sampai 2913 ppm, jadi ambang 2500 dan 4000 bisa dicapai di meja ([uji-6](../pengujian/laporan/uji-6-firmware-v1-2026-10-28.md)). 4000 mungkin sulit; siapkan simulasi CO2 atau kotak yang lebih kecil.

## 3. Pesan data: tanpa mengubah kontrak v3
| Field | Isi di MVP |
|---|---|
| `co2_ppm`, `co2_peak_ppm`, `co2_peak_second` | nilai nyata |
| `co_ppm`, `co_peak_ppm`, `co_peak_second` | `0`, `0`, `1` (worker menerima; aplikasi menampilkan "CO: tidak dipakai di MVP") |
| `status` | dari CO2: `normal` (< 2500), `waspada` (≥ 2500), `bahaya` (≥ 4000); selain `normal` wajib `event_id` |
| `window_status` | `null` (posisi tidak diketahui); alternatif 50 sesudah pulsa buka |
| `demo` | `false` untuk data napas nyata; `true` bila memakai simulasi |

Hasilnya: backend dan database tidak perlu diubah skemanya. Yang berubah hanya sisi ESP dan tulisan di aplikasi.

## 4. Pekerjaan sampai Jumat
| Urut | Pekerjaan | Siapa | Selesai bila |
|---|---|---|---|
| 1 | Pilih **satu ESP final yang Wi-Fi-nya hidup** (catatan lama: ESP firmware punya modul Wi-Fi rusak, ESP tim software punya Wi-Fi) | semua | satu ESP terpilih, bisa tersambung ke hotspot 2,4 GHz |
| 2 | Tambah sakelar `CO_AKTIF = false` di firmware (lewati ADS, CO dibuang dari LCD dan aturan) | pengguna dan asisten, **menunggu izin ubah `main.cpp`** | uji meja: CO2 saja jalan tanpa ADS |
| 3 | Gabungkan inti firmware ke proyek teman: ganti `sensorOriginal.inl`, perbaiki `lcd` dan `prefs` ganda, pakai `huge_app.csv`, setup tidak berhenti bila konfigurasi gagal | pengguna, asisten, teman backend | terkompilasi, tersambung MQTT |
| 4 | Status dan `event_id` dari aturan CO2, isi field `co_*` = 0 | firmware | satu pesan lolos worker, baris masuk `sensor_readings` |
| 5 | Hardware: ukur waktu turun jendela (`PULSA_BUKA_MS`), ukur 5 V dan ground, putuskan penutup jendela | hardware | angka tercatat |
| 6 | Aplikasi: tampilkan CO2 dan status, tulis "CO tidak dipakai", offline bukan berarti aman, tombol "Saya Tahu" | teman software | layar tampil dari data nyata |
| 7 | Uji ujung ke ujung: napas ke kotak, LCD, buzzer, jendela, data di aplikasi dalam hitungan detik | semua | skenario bagian 5 lulus |
| 8 | Rekam video cadangan dan data rekaman, daftar periksa demo | pengguna | siap dipakai bila Wi-Fi gagal |

Urutan 1 dan 2 boleh dikerjakan bersamaan. Item 7 jangan digeser ke malam terakhir.

## 5. Skenario demo (lulus bila semuanya terjadi)
1. Nyalakan, tunggu pemanasan 3 menit (LCD tidak menampilkan angka selama pemanasan).
2. Napas ke kotak, CO2 naik melewati 2500: 3 bip, status `waspada` di LCD dan aplikasi.
3. Melewati 4000 (atau simulasi): bip 3 detik, relay jendela aktif, status `bahaya`.
4. "Saya Tahu" dari aplikasi mematikan bunyi saja.
5. CO2 turun di bawah 2500 selama 10 detik: status kembali `normal`.
6. Cabut Wi-Fi: alarm tetap bunyi dan aplikasi menampilkan "tidak terhubung", bukan "aman".

## 6. Risiko
| Risiko | Penanganan |
|---|---|
| Jendela tidak bisa ditutup oleh ESP (hanya relay turun) | putuskan hari ini: relay naik, servo diorama, atau tutup manual |
| ESP boot berulang dan LCD kacau (catu atau ground) | ukur 5 V; ESP final yang sama untuk semua uji; init ulang LCD berkala [usulan] |
| Wi-Fi expo tidak ada | hotspot 2,4 GHz sendiri; video cadangan |
| Waktu turun jendela belum diukur | ukur dengan `alat-uji/uji-relay-jendela` sebelum demo |
| Pesan v3 belum pernah lolos dengan firmware baru | item 4, hari pertama |

## 7. Parkir (sengaja tidak dikerjakan sebelum expo)
Semua yang berhubungan dengan CO: R0, kurva A dan β, filter Rs, uji arah, mode simulasi CO, kalibrasi di PCB; penutup jendela otomatis; PCB; uji mobil tambahan; T1 uji mandiri dan T2 watchdog.

## 8. Kesiapan saat ini (estimasi 29 Okt, ±10 poin)
Dihitung dari daftar periksa berbobot, bukan pengukuran. Aplikasi dan database belum kuperiksa langsung; nilainya dari daftar tugas.

| Bagian | Bobot | Nilai | Dasar |
|---|---|---|---|
| **Firmware (CO2 saja)** | | **sekitar 70%** | |
| CO2: baca, validasi, aturan | 35 | 90% | v1.3 diuji di meja, napas sampai 2913 ppm |
| LCD, buzzer, serial | 15 | 80% | jalan; LCD pernah kacau |
| Jendela (sinyal, waktu, tutup) | 20 | 40% | sinyal 2000 ms benar; gerak fisik belum diukur; tidak ada tutup |
| Kestabilan hardware | 15 | 30% | ESP boot berulang, 5 V belum diukur |
| Bisa dibekukan (cadangan, dokumen) | 15 | 90% | tag v1.3 |
| **Firmware (versi lengkap CO dan CO2)** | | **sekitar 55%** | bobot lain disesuaikan; jalur CO (bobot 30) hanya 20%: belum terkalibrasi, uji arah belum diuji |
| **Komunikasi ujung ke ujung** | | **sekitar 35%** | |
| Kontrak v3 dan worker | 20 | 70% | kode dan tes ada; hasil uji teman belum dilaporkan |
| Sisi ESP (Wi-Fi, MQTT, antrean) | 20 | 55% | ada, tetapi masih memakai sensor v0 dan belum terkompilasi apa adanya |
| Gabung dengan firmware baru | 25 | 0% | belum dimulai |
| Database | 10 | 60% | perbaikan `ON DELETE CASCADE` dan kolom puncak tertunda |
| Aplikasi | 10 | 50% | belum diperiksa; tugas label dan offline masih terbuka |
| Uji ujung ke ujung | 15 | 0% | belum pernah |

Bagian yang paling menentukan adalah **gabungan firmware dengan komunikasi (0%)** dan **uji ujung ke ujung (0%)**. Selama dua hal ini belum dikerjakan, persentase komunikasi tidak akan naik.
