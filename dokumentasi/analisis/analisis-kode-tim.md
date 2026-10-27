# Analisis Kode Tim (ESP32 Wi-Fi dan Worker)

Analisis kode komunikasi temanmu: firmware ESP32 (`AEROS-mqtt/`) dan worker Node.js (`mqtt-sensor-worker/`). Salinan kode di `kode-tim/` (tidak masuk git). Tidak ada rahasia yang dibaca atau disalin; file `.env` asli tidak pernah dibuka. Pertanyaan untuk teman ada di [belum-diputuskan.md](../keputusan/belum-diputuskan.md) bagian 4; kontrak pesan di [komunikasi.md](../keputusan/komunikasi.md).

## 1. Versi 3 (`iot-mainproject 3`)

Salinan kode ada di `kode-tim/iot-mainproject-3/`. File `.env` asli di folder worker **tidak disalin dan tidak dibaca** (berisi rahasia). `.gitignore` di akar folder temanmu sudah memuat `.env`.

### 1.1 Yang berubah
1. **Firmware sensor kita (v0) dimasukkan tanpa diubah.** `sensorOriginal.inl` identik byte demi byte dengan `src/main.cpp` v0 (sudah kucek). Ia dijalankan di tugas terpisah lewat `sensorBridge.cpp`, yang menangkap baris CSV yang dicetak v0 lalu mengolahnya jadi data kirim. Jadi data nyata sudah dikirim, bukan acak lagi, dan siklus 1 detik tidak lagi tertahan jaringan. Ini sama dengan arsitektur dua tugas di pseudocode komunikasi.md bagian 4.2.
2. **Pesan versi 3 sudah ada**: `r3` dengan `co_peak_ppm`, `co2_peak_ppm`, dan detik puncaknya; telemetri tiap 5 detik (dari 5 sampel 1 detik); waktu tiap sampel dikoreksi bila sempat tertahan; `window_status = null` (bukan 0 palsu); `demo = false`.
3. **Topik mengikuti rancangan kita**: `aeros/{id}/telemetry`, `cmd`, `cmd/ack`, dan `telemetry/ack` (versi lama `aeros/data` tetap diterima worker).
4. **Worker menulis `alert_logs` dan `device_state` dari telemetri** (`telemetryStateService.js`): baris `alert_logs` dibuat dengan `id = event_id` dan ditutup saat kembali normal atau episode baru. Data lama dari antrean offline (lebih dari 90 detik) disimpan tapi tidak membuka ulang alarm. Ini menjawab keputusan "worker menulis `alert_logs`".
5. **Perintah jendela** (`WINDOW_OPEN`, `WINDOW_CLOSE`) diterima dan dibalas dengan tanda terima `received`. Motor belum ada, jadi worker mencatat "diterima, belum dijalankan" dan tidak pernah menandai berhasil. Itu jujur.
6. Ada tes baru (`actuator-v3`, `telemetry-state`), `Dockerfile` untuk worker, dan sensorBridge menjaga mute buzzer tetap berlaku walau v0 menyalakan pin lagi.

### 1.2 Masalah yang kutemukan
| # | Temuan | Bukti |
|---|---|---|
| 1 | **Tidak bisa dikompilasi apa adanya.** `lcd` dan `prefs` didefinisikan dua kali (main.cpp baris 59 dan 64, sensorOriginal.inl baris 37 dan 69) | Kompilasi di folder sementara gagal di tahap link. Menambah `static` pada dua baris itu di salinan sementara membuatnya lolos |
| 2 | **Tidak muat dengan partisi bawaan.** `platformio.ini` belum memakai `huge_app.csv`. Dengan `static` dan `huge_app.csv` hasilnya 1.343.786 byte (42,7% dari 3 MB), lebih besar dari batas bawaan 1.310.720 | Kompilasi |
| 3 | **Alarm mati total bila konfigurasi atau flash bermasalah.** `setup()` berhenti dengan `while (true)` (main.cpp baris 884 dan 894) **sebelum** tugas sensor dimulai (baris 918). Jadi bila `secrets.h` kosong atau sistem berkas belum disiapkan, sensor dan buzzer tidak jalan | Pembacaan kode |
| 4 | Folder `data/` untuk menyiapkan LittleFS dihapus, padahal `LittleFS.begin(false)` gagal pada flash kosong | Pembacaan kode |
| 5 | Sensor yang dipakai masih **v0**: filter EMA 0,2, pemanasan CO 5 menit, alarm CO 35 ppm 10 detik. Keputusan baru (SMA 6, 3 menit, uji arah, 5 status, pola bunyi, ambang 4000) belum masuk | `sensorOriginal.inl` |
| 6 | **Status database tidak sesuai keputusan kita:** alarm CO v0 dipetakan ke `bahaya` (padahal 35 ppm = waspada, bahaya 87 ppm), dan CO2 mengikuti label v0 (`SEDANG`/`TINGGI`), bukan 2500 dan 4000 | `main.cpp` (`sampleAndQueue`) |
| 7 | Jembatan membaca **teks CSV** v0. Kalau format CSV berubah di firmware baru, jembatan rusak diam-diam | `sensorBridge.cpp` |
| 8 | Data **pemanasan tidak dikirim** (sampel dibuang). Cocok dengan jalan mundur v2, tapi bukan ide "tetap terkirim dengan penanda" | `captureCsvLine` |
| 9 | `alert_logs` hanya berisi `alert_type = status`; gas, nilai, ambang, dan sumber belum | `telemetryStateService.js` |
| 10 | LCD dikuasai tugas sensor (benar), tapi belum ada indikator Wi-Fi | `main.cpp` |
| 11 | `README.md` firmware masih menjelaskan versi lama (aeros/data, 10 detik, HMAC lain) | README |
| 12 | Folder worker punya `.env` asli; pastikan tidak pernah masuk git (akar sudah mengabaikannya) | `.gitignore` |

### 1.3 Artinya untuk rencana kita
- **Arsitektur dan kontrak pesan sudah sejalan.** Yang perlu dilakukan kita adalah mengganti isi `sensorOriginal.inl` dengan inti sensor **baru** kita, dan memberi jembatan **struktur data** (bukan teks CSV): ppm, status 5 level, `kond` pemanasan atau gangguan, fase, `event_id`.
- Pesan v3 versi temanmu menjadi dasar. Field tambahan kita (`rs_r0_milli`, `kond_*`, `fase_*`, `fw`) ditambahkan bersama di dua sisi.
- Hal yang harus diperbaiki sebelum dipakai: butir 1 sampai 4 di atas (bisa dikompilasi, partisi, alarm tetap jalan saat konfigurasi gagal, penyiapan LittleFS).
- Hasil kompilasi dan perubahan `static` hanya di salinan sementara. Kode asli temanmu tidak kuubah.

## 2. Cara memeriksa
- Salinan `AEROS-mqtt/` dikompilasi di folder sementara dengan `secrets.h` dan `root_ca.h` **kosong** (nilai uji, bukan rahasia), tanpa diunggah ke ESP, memakai platform espressif32 8.0.0 (sama dengan proyek kita).
- Versi 2: gagal dengan tabel partisi bawaan (1.322.629 byte lawan batas 1.310.720); berhasil dengan `huge_app.csv`.
- Versi 3: gagal di tahap link (`lcd` dan `prefs` terdefinisi dua kali); dengan `static` pada dua baris itu di salinan sementara dan `huge_app.csv`, hasil 1.343.786 byte (42,7% dari 3 MB).
- Kode worker dibaca; tes worker (`npm test`) tidak dijalankan.
- Pengujian di ESP asli: firmware versi 2 sempat dijalankan di ESP kita dengan nilai uji (Wi-Fi tersambung ke hotspot tersimpan gagal karena hotspot tidak terlihat; antrean flash bekerja) lalu v0 dikembalikan.

## 3. Versi 2 (ringkas, sudah digantikan versi 3)
- Satu loop untuk semuanya dengan data acak (mode demo), telemetri 10 detik; alarm sederhana (CO >= 35 atau CO2 >= 2500) dan buzzer dinonaktifkan.
- Topik `aeros/data` untuk semua perangkat; tidak ada topik kejadian; status `ONLINE`/`OFFLINE` huruf besar.
- Worker hanya menyimpan `sensor_readings` dan status; `alert_logs` hanya dibaca (belum ada pembuatnya).
- Keamanan dan offline first sudah kuat sejak versi 2 (HMAC, TLS, nonce, ACK sebelum hapus, antrean LittleFS).
