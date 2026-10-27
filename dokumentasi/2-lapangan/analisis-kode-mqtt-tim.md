# Analisis Kode MQTT Tim (ESP32 Wi-Fi dan Worker)

Tanggal 27 Oktober 2026. Yang diperiksa: salinan folder `iot-mainproject 2` milik teman, sekarang ada di `kode-tim/iot-mainproject/` (folder ini di-ignore git, bukan kode kita). Bagian pertama folder itu adalah firmware ESP32 (`AEROS-mqtt/`), bagian kedua program Node.js (`mqtt-sensor-worker/`) yang menyimpan data ke Supabase.

Pembanding: [rancangan-data.md](../1-utama/rancangan-data.md) dan draf [pseudocode-baru.md](../1-utama/pseudocode-baru.md) bagian 2.8.

> **Catatan 27 Okt (sore):** bagian 1 sampai 6 menganalisis versi 2 (`iot-mainproject 2`). Versi terbaru (`iot-mainproject 3`) berubah banyak dan dianalisis di **bagian 7**. Beberapa temuan di bagian 1 sampai 6 sudah tidak berlaku.

## 1. Kesimpulan singkat

1. **Jalur datanya sudah bagus dan aman**: pesan bertanda tangan HMAC, TLS dengan sertifikat diperiksa, data tidak dihapus dari ESP sebelum database membalas, dan data tidak dobel. Itu lebih kuat dari rancangan kita. Sebaiknya dipakai, bukan ditulis ulang.
2. **Tapi belum bisa digabung begitu saja dengan sensor kita**, karena tiga hal: (a) semua jalan di satu loop yang bisa tertahan beberapa detik, padahal siklus sensor harus tepat 1 detik; (b) angka CO dan CO2 masih acak (mode demo), dan aturan alarmnya jauh lebih sederhana dari rencana kita; (c) **kodenya belum muat di ESP32** dengan tabel partisi bawaan.
3. **Kode ini belum pernah dites** pada ESP, broker, atau database (kata README-nya sendiri). Yang sudah saya buktikan hanya: kodenya bisa dikompilasi, lihat bagian 4.

## 2. Cocokkan dengan 8 butir pemeriksaan

| # | Butir | Hasil | Bukti |
|---|---|---|---|
| 1 | Siklus 1 detik tidak boleh tertahan | **Tidak** | Satu loop untuk semuanya. Penyambungan TLS (`mqtt.connect`, main.cpp:797), pemindaian Wi-Fi (baris 528 dan 666), dan tulis berkas antrean semuanya menahan loop. Pengambilan data tiap 10 detik (baris 30), bukan 1 detik |
| 2 | Alarm jalan tanpa internet | **Sebagian** | `evaluateGasLocally` dipanggil di awal loop (baris 245 dan 869), jadi tidak menunggu internet. Tapi hanya tiap 10 detik, memakai angka acak, aturannya cuma "CO ≥ 35 atau CO2 ≥ 2500", tanpa uji arah, jendela, filter, pemanasan. `BUZZER_PIN = -1` (baris 35) berarti buzzer mati |
| 3 | Topik dan QoS sesuai rancangan kita | **Beda** | Mereka: `aeros/data` (satu topik untuk semua perangkat), `aeros/{id}/data/ack`, `status`, `command`, `command/ack`. Kita: `aeros/{id}/telemetry`, `event`, `status`, `cmd/ack`. Tidak ada topik `event`. Status huruf besar `ONLINE`/`OFFLINE` |
| 4 | Last will, nonce, simulasi, versi firmware | **Hampir** | Last will ada (retained, QoS 1). Nonce acak 128 bit. Bendera simulasi ada, namanya `demo`. Field versi firmware (`fw`) **tidak ada** |
| 5 | Telemetri 5 detik dan antrean kejadian | **Sebagian** | Telemetri tiap 10 detik. Antrean di flash (LittleFS, tahan mati listrik, maks. 360). Satu antrean saja, tanpa kejadian terpisah. "Kejadian" hanya berupa `event_id` di dalam telemetri |
| 6 | Perintah konfirmasi ("Saya Tahu") | **Sebagian** | Perintah `MUTE_BUZZER` bertanda tangan, berlaku 120 detik, harus cocok dengan alarm yang sedang aktif. Tapi **di folder ini** tidak ada kode yang membuat baris `alert_logs` (blocker 5 di README mereka). Bisa jadi sudah ada di bagian lain (Supabase, Flutter) yang tidak ikut disalin: perlu dikonfirmasi |
| 7 | Sumber jam | **Jelas** | Jam dari NTP di ESP32. Bila belum sinkron, dikirim `timestamp:0` dan `time_valid:false`, server memakai jam terima. Ini menjawab bagian jam dari B14 |
| 8 | Tidak ada rahasia di repo | **Aman** | `secrets.h`, `root_ca.h`, `.env` masuk `.gitignore`. Di salinan hanya ada file contoh kosong dan kunci uji berlabel `TEST_ONLY` |

## 3. Temuan yang perlu dibahas, urut dari yang paling penting

1. **Tidak muat di flash.** Hasil kompilasi: 1.322.629 byte, batasnya 1.310.720 byte. Kelebihan 11.909 byte, **sebelum** kode sensor kita ditambahkan. Perlu tabel partisi lain (misalnya `huge_app.csv`: aplikasi 3 MB tanpa OTA, area berkas 896 KB). Dengan itu kompilasi berhasil. Akibatnya: area berkas mengecil dari bawaan.
2. **Antrean 360 item mungkin tidak muat.** Dugaan (belum diuji): littlefs memakai satu blok 4 KB per berkas kecil, jadi 896 KB kira-kira hanya cukup sekitar 200 berkas, bukan 360. Uji dengan mematikan Wi-Fi 30 menit dan lihat kapan "antrean penuh" muncul.
3. **Siklus 1 detik.** Cara menyelesaikannya sama dengan draf kita (2.8): jaringan dan LittleFS dipindah ke satu tugas FreeRTOS terpisah (inti 0), sensor dan alarm tetap di loop utama (inti 1), keduanya dihubungkan lewat satu antrean kecil. Semua akses LittleFS dan MQTT harus di tugas yang sama karena objeknya tidak aman dipakai dua tugas sekaligus.
4. **LCD dipakai dua pihak.** Firmware Wi-Fi menulis "MQTT connecting", "WiFi gagal", dan sebagainya ke LCD (`showLCD`). Itu akan menimpa tampilan ppm kita. Perlu satu pemilik LCD: tugas jaringan cukup mengirim status pendek (misalnya ikon Wi-Fi di pojok), bukan menulis sendiri.
5. **Bentuk pesan belum cukup untuk data kita.**
   - `co_ppm` dan `co2_ppm` harus bilangan bulat (worker menolak desimal).
   - `status` hanya `normal`, `waspada`, `bahaya`. Tidak ada tempat untuk `PEMANASAN` atau `GANGGUAN`, padahal selama pemanasan CO kita tidak boleh dikirim sebagai angka biasa.
   - Field tambahan kita (`rs_r0`, `fase_co`, `co_ok`, `fw`, `co_ppm_maks`) belum ada. Setiap field yang masuk tanda tangan HMAC harus diubah di **dua sisi sekaligus** (ESP dan worker), jadi sebaiknya ditetapkan sekaligus sebagai versi 3 bukan satu per satu.
   - Worker menolak `demo:true` secara bawaan, jadi mode simulasi kita butuh `ALLOW_DEMO_READINGS=true` saat uji.
6. **Kejadian belum ada jalurnya di kode ini.** Gerakan jendela otomatis dan uji arah tidak punya topik. Worker hanya menangani perintah manual `MUTE_BUZZER` ke `actuator_logs`. README mereka menyebut "backend akan membuat `alert_logs` dengan `event_id` dari ESP32 sebagai id-nya". Kalau notifikasi di aplikasi sudah jalan, kemungkinan pembuatnya ada di Supabase (trigger atau Edge Function) atau Flutter, **di luar folder yang saya terima**. Yang harus dipastikan: apakah baris itu memakai `event_id` dari ESP32 sebagai `id`. Kalau memakai id lain, perintah "Saya Tahu" ditolak karena `alert_id` tidak cocok dengan alarm yang sedang aktif di ESP.
7. **Laju kirim 10 detik vs 5 detik di rancangan kita.** Keduanya wajar. Perlu satu keputusan. Antrean mereka mengirim satu pesan lalu menunggu balasan (maksimal satu pesan sekaligus), cukup untuk 5 atau 10 detik.
8. **Daya.** `WiFi.setSleep(false)` (baris 845) menaikkan arus Wi-Fi. Ini relevan dengan kecurigaan siklus Rs dan catu 5 V. Sudah tercakup di T22 (uji ulang 30 menit dengan Wi-Fi menyala).
9. **Penulisan flash tiap sampel.** Setiap pembacaan ditulis ke berkas lalu dihapus setelah ACK, sekitar 8.600 kali sehari. Untuk demo tidak masalah, untuk jangka panjang perlu dipikirkan (LittleFS membagi keausan). Tulis hanya tiap 5 detik, bukan tiap 1 detik.

## 3B. Hasil membaca kode saja (tanpa README)

Semua file `.js`, `.cpp`, `package.json`, `.env.example`, dan tes dibaca. Tidak ada file tersembunyi atau folder lain selain `AEROS-mqtt/` dan `mqtt-sensor-worker/`.

**Tabel Supabase yang disentuh kode:**

| Tabel | Operasi di kode | Siapa yang mengisi |
|---|---|---|
| `devices` | baca (cek aktif) | pihak lain |
| `sensor_readings` | **tulis** (insert) | worker |
| `device_state` | **tulis** (online/offline, ack_driver, ack_at, buzzer_state) | worker |
| `alert_logs` | **hanya baca dan update** `acknowledged_at`. **Tidak pernah insert** | pihak lain |
| `actuator_logs` | baca baris `pending` (lewat Realtime dan polling 15 detik), update `execution_status`. **Tidak pernah insert** | pihak lain (aplikasi) |

**Yang bisa disimpulkan dari kode:**
1. **Tidak ada kode notifikasi sama sekali** (tidak ada push, FCM, Firebase, atau webhook). Jadi kalau notifikasi sudah jalan, pembuatnya pasti komponen lain (aplikasi Flutter, trigger atau Edge Function di Supabase).
2. Worker **mengasumsikan** `alert_logs` dan `actuator_logs` sudah diisi pihak lain: ia menolak perintah kalau `alert_logs` dengan id itu tidak ada, dan `device_state.active_alert_id` dipakai tapi tidak pernah diisi oleh worker.
3. **`event_id` dari ESP32 dibuang worker saat menyimpan.** Baris yang di-insert ke `sensor_readings` hanya berisi `device_id, nonce, co_ppm, co2_ppm, status, window_status, measured_at, received_at` (sensorDataHandler.js). `event_id` dan `buzzer_state` tidak ikut tersimpan. Artinya, **kalau notifikasi dibuat dari isi database**, pembuatnya tidak punya cara mengetahui `event_id` dari ESP, sehingga `alert_logs.id` hampir pasti **bukan** `event_id`. Dalam keadaan itu tombol "Saya Tahu" akan ditolak ESP (alert_id tidak cocok). Satu-satunya jalan agar cocok: ada komponen lain yang ikut membaca pesan `aeros/data` langsung dari broker, atau worker diubah supaya menyimpan `event_id`.
4. Tes yang ada hanya menguji `sensor_readings` dan HMAC (basis data ditiru). Jalur perintah, ACK perintah, dan status online/offline **tidak ada tesnya**.
5. Worker hanya menerima satu perangkat dengan satu kunci rahasia bersama (`HMAC_SECRET`), dan komentarnya sendiri menyebut itu prototipe.

Yang belum bisa dipastikan dari kode: apakah alarm saat ini muncul di aplikasi lewat jalur lain (misalnya aplikasi membaca `sensor_readings.status`).

## 4. Cara saya memeriksa

- Salinan `AEROS-mqtt/` dikompilasi di folder sementara dengan `secrets.h` dan `root_ca.h` **kosong** (hanya salinan dari file contoh), tanpa diunggah ke ESP. Platform espressif32 8.0.0 (versi yang sama dengan proyek kita).
- Hasil: gagal dengan tabel partisi bawaan (flash 100,9%), berhasil dengan `huge_app.csv`.
- Kode worker dibaca, tapi `npm test` tidak dijalankan.
- Tidak ada kunci, kata sandi, atau sertifikat asli yang dilihat atau disalin.

## 5. Rencana penggabungan (usulan)

1. Pakai jalur data mereka sebagai dasar (HMAC, ACK, antrean, NTP). Topik dan format kita disesuaikan ke mereka, bukan sebaliknya, karena kodenya sudah ada.
2. Tetapkan bersama **pesan versi 3**: bilangan bulat, `status` plus `co_ok`/`co2_ok`/`panas`, `fw`, `sim`, topik `event`.
3. Tetapkan tabel partisi (`huge_app.csv`) dan uji kapasitas antrean.
4. Di firmware baru: sensor, alarm, dan jendela di loop utama; jaringan di tugas terpisah; satu antrean antar keduanya; LCD hanya dikelola firmware sensor.
5. Uji bertahap seperti T22: Wi-Fi mati, Wi-Fi nyala diam 15 menit, mengirim 15 menit. Bandingkan Rs dengan log ESP lama.

## 6. Pertanyaan untuk teman

1. Apakah kode ini pernah dikompilasi dan dijalankan di ESP asli? Tabel partisi apa yang dipakai?
2. (Keputusan 27 Okt: worker yang menulis `alert_logs` dengan `id = event_id`, lihat pseudocode 2.8.8; tinggal persetujuan pemilik worker.) Notifikasi di aplikasi sudah jalan: siapa yang membuat baris `alert_logs` (trigger, Edge Function, atau Flutter), dan apakah `id`-nya diisi dengan `event_id` dari ESP32? Dan `actuator_logs` otomatis (jendela, buzzer)?
3. Boleh pesan diubah ke versi 3 (bilangan bulat, field tambahan, topik `event`)? Siapa yang mengubah worker?
4. 5 atau 10 detik per telemetri?
5. Apakah satu topik `aeros/data` untuk semua perangkat disengaja, dan bagaimana aturan akses (ACL) di HiveMQ?
6. Pin buzzer dan pin jendela di PCB (GPIO14 sudah dipakai tombol Wi-Fi).


## 7. Versi terbaru (`iot-mainproject 3`), dianalisis 27 Okt 2026

Salinan kode ada di `kode-tim/iot-mainproject-3/`. File `.env` asli di folder worker **tidak disalin dan tidak dibaca** (berisi rahasia). `.gitignore` di akar folder temanmu sudah memuat `.env`.

### 7.1 Yang berubah
1. **Firmware sensor kita (v0) dimasukkan tanpa diubah.** `sensorOriginal.inl` identik byte demi byte dengan `src/main.cpp` v0 (sudah kucek). Ia dijalankan di tugas terpisah lewat `sensorBridge.cpp`, yang menangkap baris CSV yang dicetak v0 lalu mengolahnya jadi data kirim. Jadi data nyata sudah dikirim, bukan acak lagi, dan siklus 1 detik tidak lagi tertahan jaringan. Ini sama dengan arsitektur dua tugas di pseudocode 2.8.2.
2. **Pesan versi 3 sudah ada**: `r3` dengan `co_peak_ppm`, `co2_peak_ppm`, dan detik puncaknya; telemetri tiap 5 detik (dari 5 sampel 1 detik); waktu tiap sampel dikoreksi bila sempat tertahan; `window_status = null` (bukan 0 palsu); `demo = false`.
3. **Topik mengikuti rancangan kita**: `aeros/{id}/telemetry`, `cmd`, `cmd/ack`, dan `telemetry/ack` (versi lama `aeros/data` tetap diterima worker).
4. **Worker menulis `alert_logs` dan `device_state` dari telemetri** (`telemetryStateService.js`): baris `alert_logs` dibuat dengan `id = event_id` dan ditutup saat kembali normal atau episode baru. Data lama dari antrean offline (lebih dari 90 detik) disimpan tapi tidak membuka ulang alarm. Ini menjawab keputusan "worker menulis `alert_logs`".
5. **Perintah jendela** (`WINDOW_OPEN`, `WINDOW_CLOSE`) diterima dan dibalas dengan tanda terima `received`. Motor belum ada, jadi worker mencatat "diterima, belum dijalankan" dan tidak pernah menandai berhasil. Itu jujur.
6. Ada tes baru (`actuator-v3`, `telemetry-state`), `Dockerfile` untuk worker, dan sensorBridge menjaga mute buzzer tetap berlaku walau v0 menyalakan pin lagi.

### 7.2 Masalah yang kutemukan
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

### 7.3 Artinya untuk rencana kita
- **Arsitektur dan kontrak pesan sudah sejalan.** Yang perlu dilakukan kita adalah mengganti isi `sensorOriginal.inl` dengan inti sensor **baru** kita, dan memberi jembatan **struktur data** (bukan teks CSV): ppm, status 5 level, `kond` pemanasan atau gangguan, fase, `event_id`.
- Pesan v3 versi temanmu menjadi dasar. Field tambahan kita (`rs_r0_milli`, `kond_*`, `fase_*`, `fw`) ditambahkan bersama di dua sisi.
- Hal yang harus diperbaiki sebelum dipakai: butir 1 sampai 4 di atas (bisa dikompilasi, partisi, alarm tetap jalan saat konfigurasi gagal, penyiapan LittleFS).
- Hasil kompilasi dan perubahan `static` hanya di salinan sementara. Kode asli temanmu tidak kuubah.

### 7.4 Pertanyaan untuk teman
1. Apakah versi ini sudah berhasil dikompilasi di laptopmu? Kalau ya, apa bedanya dengan file yang kukirim (butir 1)?
2. Partisi apa yang dipakai, dan bagaimana LittleFS disiapkan?
3. Maukah worker menyimpan `gas`, `nilai`, dan `ambang` di `alert_logs`?
4. Setuju bila isi `sensorOriginal.inl` diganti dengan inti sensor baru, dengan antarmuka struktur (bukan CSV)?
