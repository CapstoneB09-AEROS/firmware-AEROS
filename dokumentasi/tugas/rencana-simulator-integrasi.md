# Rencana Simulator Integrasi (ESP palsu)

Versi 5 November 2026. Berkas ini adalah **acuan tunggal** selama simulator dikembangkan: tujuan, skenario, keputusan, tahapan, dan status. Bila ada yang berubah, ubah di sini dulu.

Latar belakang: hardware masih bermasalah, jadi perlu rencana cadangan untuk membuktikan bahwa **firmware, komunikasi, database, dan aplikasi terhubung** dan data benar-benar mengalir.

Dasar teknis (tidak diulang di sini): kontrak pesan di [rancangan-worker-mvp.md](../keputusan/rancangan-worker-mvp.md) bagian 2, tabel di [rancangan-database-mvp.md](../keputusan/rancangan-database-mvp.md), pembagian kerja di [tugas-database-mvp.md](tugas-database-mvp.md).

## 1. Ringkas

Satu skrip Node di `worker/`, `simulator-skenario.js`, yang berperan sebagai ESP: mengirim status `ONLINE`, lalu telemetri versi 4 bertanda tangan HMAC ke HiveMQ, mengikuti satu skenario, dan diakhiri `OFFLINE`. Worker yang sudah ada menerimanya seperti menerima ESP asli. Tidak ada kode worker atau firmware yang diubah.

Ada empat skenario: normal, CO2 tinggi, CO tinggi, dan CO bersama CO2 tinggi.

Ada **tiga jalur** untuk menjalankan skenario yang sama: (1) simulator Node (bagian 7), (2) ESP asli dengan perintah serial `q<ppm>` dan `p<ppm>` (firmware-v2, manual), (3) **firmware v3 dummy**: ESP murni tanpa sensor yang memainkan skenario sendiri (bagian 12). Tabel skenario di bagian 6 dipakai ketiganya.

## 2. Apa yang dibuktikan dan tidak

| Dibuktikan | Tidak dibuktikan |
|---|---|
| Format pesan, tanda tangan, dan topik sesuai kontrak (diperiksa oleh worker asli) | Sensor membaca gas dengan benar |
| HiveMQ ke worker: pesan diterima, ditolak bila salah | Firmware ESP menghasilkan pesan itu (hanya dibuktikan oleh uji meja ESP, lihat [uji 8](../pengujian/laporan/uji-8-meja-wifi-mqtt-firmware-v2.3-2026-11-03.md)) |
| Worker ke database: bacaan, peringatan, dan `device_state` tertulis | Relay, buzzer, dan jendela |
| Siklus peringatan: dibuat, naik tingkat, ditutup | Angka ambang final (diganti belakangan) |
| Aplikasi menampilkan status dan peringatan dari database | Kinerja di mobil |

Kalimat aman untuk penguji: *"Ini simulasi jalur data karena hardware belum siap. Pesannya memakai format dan tanda tangan yang sama dengan firmware, dan data tercatat berlabel DEMO."*

## 3. Alur dan bukti tiap tahap

| Tahap | Apa yang terjadi | Bukti yang dikumpulkan |
|---|---|---|
| 1. Simulator ke broker | publish ke `aeros/<device>/status` dan `aeros/<device>/telemetry` | log simulator "terkirim"; pesan terlihat di web client HiveMQ |
| 2. Broker ke worker | worker memeriksa versi, HMAC, waktu, aturan keselarasan | log worker `[READING] ... DEMO` (bukan `[READING REJECTED]`) |
| 3. Worker ke database | `alert_logs` dibuat dulu, lalu `sensor_readings`, lalu `device_state` | baris di tiga tabel; `v_alerts` dan `v_alert_gas` |
| 4. Worker ke simulator | ACK bertanda tangan di `aeros/<device>/telemetry/ack` | log simulator "ACK diterima" (bukti worker benar-benar menyimpan) |
| 5. Database ke aplikasi | aplikasi membaca `device_state` dan `v_alerts` | tangkapan layar aplikasi tiap fase skenario |

## 4. Keputusan dan prasyarat

Butir bertanda **TERBUKA** perlu dijawab sebelum tahap uji ke database (bagian 9, T5). Tahap T1 sampai T4 tidak bergantung padanya.

| # | Butir | Usulan | Status |
|---|---|---|---|
| K1 | `device_id` simulator | `AEROS_DEMO_01`, supaya data `AEROS_01` (ESP asli) tidak tercemar. Harus terdaftar dan `is_active = true` di tabel `devices` (worker menolak perangkat yang tidak aktif) | TERBUKA: tanya teman database |
| K2 | Database tujuan | **Salinan/cabang database**, atau database asli setelah SQL 4a dijalankan. Jangan ke database asli sebelum 4a (worker baru menulis kolom yang belum ada) | TERBUKA: tergantung D6a di [tugas-database-mvp.md](tugas-database-mvp.md) |
| K3 | Worker menerima data demo | `ALLOW_DEMO_READINGS=true` di worker yang dipakai uji. Pesan simulator selalu `demo = true`, tidak pernah disamarkan sebagai data asli | Diputuskan |
| K4 | Aplikasi menampilkan `AEROS_DEMO_01` | Aplikasi mungkin hanya membaca `AEROS_01`. Alternatif: simulator memakai `AEROS_01` saat ESP asli mati (bacaan tetap berlabel DEMO) | TERBUKA: tanya teman aplikasi |
| K5 | Pengguna MQTT simulator | Pakai pengguna HiveMQ yang boleh publish `aeros/+/telemetry` dan `aeros/+/status`, dan subscribe `aeros/+/telemetry/ack`. Bawaan: baca dari `.env` worker; boleh diganti `SIM_MQTT_USERNAME` dan `SIM_MQTT_PASSWORD` | Usulan |
| K6 | Ambang yang dipakai simulator | Ambang rancangan: CO2 2500 (waspada) dan 4000 (bahaya), CO 35 dan 87. Ada satu tabel konstanta di bagian atas skrip, jadi mengganti ambang tidak mengubah skenario | Diputuskan |
| K7 | Data demo dibersihkan | Setelah uji, baris `AEROS_DEMO_01` dihapus atau dibiarkan sebagai bukti (putuskan bersama teman database; terkait D5) | TERBUKA |

## 5. Aturan pesan yang harus ditiru

Semua sudah dipaksa oleh `verifyReading` di worker, jadi simulator yang salah langsung ketahuan.

- `version = 4`; `co_level` dan `co2_level` 0, 1, atau 2 (dihitung dari ppm memakai tabel ambang K6); `status` tidak dikirim.
- Alarm (salah satu level lebih dari 0) wajib punya `event_id` (UUID); normal wajib `event_id = null`; `buzzer_state = on` hanya saat alarm.
- `timestamp` = waktu sekarang (worker hanya menyalin ke `device_state` bila umurnya kurang dari 90 detik), `time_valid = true`, `demo = true`.
- `nonce` 32 karakter hex, baru tiap pesan.
- Jeda antarpesan 5 detik (seperti ESP); ada opsi `--jeda 1` untuk uji cepat. Pesan harus terkirim berurutan.
- `window_status`: `0` jendela tertutup, `50` jendela terbuka, `null` saat bergerak (sama dengan `main.cpp`).
- `*_peak_ppm` tidak boleh kurang dari `*_ppm`; `*_peak_second` antara 1 dan 5.
- Perilaku `event_id` meniru firmware (`trackSensorAlarm`, `main.cpp:249`): satu `event_id` selama satu episode, **tetapi CO yang mulai saat CO2 sudah aktif membuat `event_id` baru** (episode CO baru). Ini menentukan skenario 4b di bawah.

## 6. Skenario

Sumber tunggal isi skenario. Diubah 6 November 2026: **semua skenario naik bertahap**, bukan lompat. Dimainkan persis seperti ini oleh `firmware-v3-dummy/src/sensorBridge.cpp` (hasil uji di bagian 12.7). Simulator Node (bagian 7) belum dibuat dan harus memakai profil yang sama.

### 6.1 Profil waktu (sama untuk S1, S2, S3a, S3b)

Satu sampel per detik; satu pesan ke worker tiap 5 sampel. Nilai naik atau turun **linier per detik**.

| Fase | Lama | Keterangan |
|---|---|---|
| Normal | 10 detik | CO 0, CO2 700, jendela tertutup |
| **Naik bertahap, normal ke bahaya** | **300 detik (5 menit)** | gas naik linier sampai tepat di ambang bahaya pada detik terakhir; waspada tercapai di tengah jalan |
| Bahaya, jendela tertutup | 5 detik | gas di puncak (CO2 4100, CO 90) |
| Jendela turun | 5 detik | jendela `null` (bergerak) |
| Bahaya, jendela terbuka | 110 detik | gas tetap di puncak, jendela `50` |
| Turun, jendela terbuka | 60 detik | gas turun linier ke CO2 2400 / CO 30; tingkat bahaya bertahan sampai di bawah batas selesai |
| Jendela naik | 5 detik | gas ke normal, jendela `null` |
| Normal terakhir | 10 detik | CO2 800 / CO 0, jendela `0` |
| **Berhenti** | | tidak ada data lagi sampai ada perintah baru |

Hasil uji (komputer, 6 Nov): total **505 detik (8,4 menit)** per skenario; normal ke bahaya tepat 300 detik; tingkat bahaya berlangsung **sekitar 177 detik (3 menit)**; tidak ada sampel setelah berhenti. Pada ambang rancangan: CO2 waspada di detik ke-164 dari awal naik (2500 ppm), CO waspada di detik ke-120 (35 ppm).

**Aturan yang ditiru dari firmware** (`sensorOriginal.inl` `aturanCO2`, `main.cpp` `trackSensorAlarm`):
- Tingkat naik langsung dan **bertahan di tingkat tertinggi** sampai ppm turun di bawah batas selesai (CO2 < 2500, CO < 35), lalu langsung normal.
- Buzzer `on` selama ada alarm (waspada atau bahaya).
- Satu `event_id` per episode alarm; **CO yang mulai saat CO2 sudah alarm membuat `event_id` baru**.
- `window_status`: `0` tertutup, `50` terbuka, `null` bergerak.

### 6.2 Skenario

| Skenario | Perintah | Gas yang naik | Hasil yang diharapkan di database |
|---|---|---|---|
| S0 Normal | `0` | tidak ada | 40 detik (sekitar 8 baris) normal, tanpa peringatan; `device_state.status = normal` |
| S1 CO2 tinggi | `1` | CO2 700 ke 4000 (naik), 4100 (puncak) | **satu** peringatan: `tingkat = bahaya`, `gas = {CO2}`, ditutup; `alert_type` waspada lalu bahaya |
| S2 CO tinggi | `2` | CO 0 ke 87 (naik), 90 (puncak); CO2 tetap 700 | **satu** peringatan: `bahaya`, `gas = {CO}`; `v_alert_gas` tanpa CO2 |
| S3a CO dan CO2 bersamaan | `3` | keduanya naik bersamaan | **satu** peringatan: `bahaya`, `gas = {CO, CO2}` (dua baris di `v_alert_gas`) |
| S3b CO2 dulu, CO menyusul | `4` | CO2 naik dari awal; CO mulai naik di detik ke-180 (CO2 sudah 2680, waspada) dan mencapai bahaya bersamaan di detik ke-300 | **dua** peringatan: E1 `waspada`/`{CO2}` ditutup saat CO mulai alarm (sekitar detik ke-229); E2 `bahaya`/`{CO, CO2}` ditutup saat normal. Aplikasi akan menampilkan dua kartu; **perlu dikonfirmasi ke teman aplikasi** |

Jumlah baris `sensor_readings` per skenario sekitar 100 (505 detik, satu baris tiap 5 detik). Perintah `a` memainkan S1 sampai S3b berurutan (sekitar 34 menit).

Catatan: nilai disederhanakan. Firmware asli memerlukan konfirmasi (CO waspada 30 detik, CO2 beberapa bacaan) dan jeda pemulihan; skenario dummy tidak meniru penundaan itu, hanya urutan dan hasil akhirnya.

## 7. Rancangan skrip

- Berkas baru `worker/simulator-skenario.js`; `publish-uji.js` tidak diubah. Skenario ditulis sebagai data (daftar fase dan nilainya), bukan kode, supaya mudah diubah.
- Memakai fungsi worker yang sudah ada: `canonicalReading` dan `signatureFor` dari `src/services/securityService.js`. Tanda tangan tidak ditulis ulang.
- Tabel ambang K6 satu tempat; level dihitung dari ppm.
- Perilaku `event_id`: dibuat baru saat alarm dimulai; berubah bila CO mulai saat CO2 sudah aktif; `null` saat normal.
- Memakai konfigurasi `.env` yang sama dengan worker (`HIVEMQ_*`, `HMAC_SECRET`, `DEVICE_ID_CEK`); rahasia tidak pernah dicetak.
- Perintah:
  - `node simulator-skenario.js --skenario co2` : **hanya mencetak** pesan (tanpa mengirim), seperti `publish-uji.js`.
  - `... --kirim` : mengirim sungguhan. Nama skenario: `normal`, `co2`, `co`, `campuran`, `campuran-bertahap`.
  - `--jeda <detik>` (bawaan 5), `--device <id>`.
- Mendengarkan `aeros/<device>/telemetry/ack` dan mencetak berapa pesan yang di-ACK (bukti tahap 4).
- Menangani Ctrl+C: tetap mengirim `OFFLINE` sebelum keluar, supaya status retained tidak menggantung `ONLINE`.
- Tidak menulis ke database sendiri: semua lewat broker dan worker, supaya yang dibuktikan adalah jalur sebenarnya.

## 8. Pemeriksaan hasil

Tiap skenario selesai dengan satu daftar periksa; hasilnya dicatat sebagai bukti.

1. Log simulator: semua pesan terkirim dan di-ACK.
2. Log worker: tidak ada `[READING REJECTED]`.
3. Database (SQL atau `cek-database.js`): jumlah baris, `v_alerts`, `v_alert_gas`, `device_state` sesuai kolom "Hasil yang diharapkan".
4. Aplikasi: tangkapan layar tiap fase.
5. Catat di `pengujian/laporan/` (satu laporan, mengikuti format uji lain). Kesimpulan lintas uji tetap hanya di `analisis/ringkasan-temuan.md`.

## 9. Tahapan kerja dan status

| # | Tahap | Selesai bila | Butuh | Status |
|---|---|---|---|---|
| T0 | Rencana ini disetujui | pengguna setuju | | selesai |
| T1 | Kerangka skrip: konfigurasi, `ONLINE`/`OFFLINE`, satu pesan, mode cetak | `--skenario normal` mencetak pesan valid | tidak ada | belum |
| T2 | Skenario S0 dan S1 | pesan lolos `verifyReading` | tidak ada | belum |
| T3 | Skenario S2, S3a, S3b | sama | tidak ada | belum |
| T4 | Uji otomatis tanpa jaringan: tiap pesan tiap skenario lolos `verifyReading`, aturan `event_id` benar, level sesuai ambang | `npm test` lulus | tidak ada | belum |
| T5 | Uji sungguhan: simulator ke HiveMQ, worker, salinan database; isi daftar periksa bagian 8 | S0 sampai S3b sesuai hasil yang diharapkan | K1, K2, K3, kredensial MQTT | belum |
| T6 | Aplikasi menampilkan tiap skenario | tangkapan layar | K4, teman aplikasi | belum |
| T7 | Laporan uji dan bahan presentasi cadangan | laporan di `pengujian/laporan/` | T5, T6 | belum |

T1 sampai T4 bisa dikerjakan sekarang, tanpa kredensial dan tanpa menyentuh database.

## 10. Risiko dan batasan

| Risiko | Penanganan |
|---|---|
| Data demo masuk ke database asli atau tampak seperti data sensor | `demo = true` di tiap pesan, `device_id` terpisah (K1), uji hanya di salinan (K2) |
| Worker lama di Railway/server menolak atau salah menulis | worker yang dipakai uji harus sudah versi baru dan `WRITE_STATUS_COLUMN` sesuai keadaan database (lihat [rancangan-worker-mvp.md](../keputusan/rancangan-worker-mvp.md) bagian 7) |
| Simulator dianggap bukti sensor | bagian 2 dan kalimat aman penguji; jangan dipresentasikan sebagai hasil uji alat |
| Status retained `ONLINE` menggantung | tangani Ctrl+C dan akhiri skenario dengan `OFFLINE` |
| Perilaku `event_id` firmware berubah | skenario S3b mengikuti `main.cpp` v2.5; periksa ulang bila `trackSensorAlarm` berubah |
| Buzzer di skenario hanya perkiraan | worker hanya memeriksa "buzzer on butuh alarm"; nilai buzzer per fase disesuaikan dengan firmware bila ada yang menilainya |

## 11. Di luar rencana ini

Simulasi perintah jendela, "Saya Tahu" (sudah dibuang dari MVP), antrean offline (tidak ada di MVP), uji beban, dan simulasi banyak perangkat sekaligus.

## 12. Jalur 3: firmware v3 dummy (ESP murni, data dummy)

Ditambahkan 6 November 2026. Tujuan: membuktikan worker bekerja memakai **ESP asli yang mengirim lewat Wi-Fi dan HiveMQ**, tanpa sensor, LCD, buzzer, atau relay terpasang. Satu-satunya beda dari firmware-v2 adalah **sumber datanya**. "Tidak terhubung ke apapun" dibaca: tanpa perangkat keras lain; Wi-Fi dan HiveMQ tetap dipakai karena itulah jalur yang dibuktikan.

### 12.1 Yang sudah ada dan belum

| Pertanyaan | Jawaban |
|---|---|
| Firmware dengan mode dummy dan skenario? | **Belum ada.** Konstanta `*_dummy` di `main.cpp` hanya penanda "belum ada penggerak jendela", bukan data dummy. |
| Yang paling dekat | firmware-v2 dengan `q<ppm>` (CO2) dan `p<ppm>` (CO) lewat serial: manual, hanya satu nilai tetap, dan `p` butuh `CO_AKTIF = true` serta pemanasan CO 180 detik. Tidak ada skenario berurutan. |
| Worker | **Tidak perlu diubah.** `worker/` di repo ini dan `aeros-worker` (repo tim `CapstoneB09-AEROS/worker-AEROS`) isi `src/` dan `test/`-nya identik (dibandingkan 6 November). Sudah menerima pesan `r4` dan `demo = true`. Hanya perlu pengaturan, bagian 12.4. |

### 12.2 Rancangan: ganti sumber data, jangan ubah yang lain

`main.cpp` (Wi-Fi, MQTT, HMAC, pesan versi 4, `event_id`, penyangga, ACK) hanya mengambil data lewat antarmuka `sensorBridge.h`. Jadi yang diganti cukup satu berkas:

| Berkas | Di v3 dummy |
|---|---|
| `main.cpp` | **salinan tanpa perubahan** (kecuali, bila diputuskan, `DEVICE_ID`, lihat K8) |
| `sensorBridge.h` | **tanpa perubahan** (antarmuka sama) |
| `sensorBridge.cpp` | **diganti**: bukan membaca sensor, melainkan pembangkit skenario yang mengisi `SensorSnapshot` satu sampel per detik |
| `sensorOriginal.inl` | **tidak dipakai** (tanpa MH-Z19C, MiCS, ADS1115, LCD, buzzer, relay) |
| `platformio.ini`, `include/` | salinan dari firmware-v2; `secrets.h` diisi sendiri |

Folder baru: `firmware-v3-dummy/`. **firmware-v2 dan `main.cpp` aslinya tidak disentuh.**

Karena `main.cpp` dipakai apa adanya, perilaku yang sama otomatis ikut: `demo = true` (lewat `simulated = true`), pembuatan `event_id`, **`event_id` baru saat CO mulai ketika CO2 sudah aktif** (skenario S3b), agregasi 5 sampel per pesan, dan tanda tangan `r4`. Ini bukti yang lebih kuat daripada simulator Node, karena kode pengiriman yang diuji adalah kode firmware sebenarnya.

Pembangkit skenario:
- Mengisi `coPpm`, `co2Ppm`, `coLevel`, `co2Level`, `coAlarm`, `windowState` (0 tertutup, 2 terbuka, 1/3 bergerak), `simulated = true`, tiap 1 detik. Level dihitung dari ppm memakai ambang K6.
- Tidak menyentuh pin apa pun (tidak ada `pinMode` atau `digitalWrite`), jadi aman tanpa hardware.
- Skenario dipilih lewat Serial Monitor (115200, "New Line"): `1` CO2, `2` CO, `3` gabungan bersamaan, `4` gabungan bertahap, `0` normal (bawaan setelah boot), `a` memainkan semua berurutan, `h` bantuan. Skenario yang sedang berjalan dicetak ke serial.
- Isi tiap skenario = tabel bagian 6 (satu sumber; tidak disalin di tempat lain). Bedanya hanya satuan waktu: fase dihitung dalam detik (pesan dikalikan 5).
- Buzzer di firmware ini tidak ada. `sensorBridgeBuzzerOn()` mengembalikan "on" saat ada alarm, supaya `buzzer_state` di pesan wajar dan lolos pemeriksaan worker.

### 12.3 Keputusan baru

| # | Butir | Usulan | Status |
|---|---|---|---|
| K8 | `device_id` firmware dummy | **`AEROS_DUMMY_01`** (satu konstanta di salinan `main.cpp`; harus terdaftar dan `is_active = true` di tabel `devices`). Dibedakan dari ESP asli supaya data tidak bercampur | **Diputuskan 6 Nov** (pengguna) |
| K9 | Cara memilih skenario | **Serial Monitor** | **Diputuskan 6 Nov** (pengguna) |
| K10 | Buzzer saat alarm | `on` selama ada alarm (waspada atau bahaya), sama dengan perilaku `sensorBridge` asli (`alarmFromSensor`). Pola bunyi asli tidak ditiru | Diputuskan |

### 12.4 Pengaturan worker (tanpa ubah kode)

| Pengaturan | Nilai | Catatan |
|---|---|---|
| `ALLOW_DEMO_READINGS` | `true` | **wajib**; tanpa ini semua pesan dummy ditolak (`demo = true`). Kembalikan ke kosong/`false` setelah uji. |
| `HMAC_SECRET` | sama dengan `HMAC_SECRET` di `secrets.h` ESP | seperti ESP asli |
| `devices` | `device_id` dummy terdaftar, `is_active = true` | oleh teman database |
| SQL 4a (`003-mvp-4a-tambahan.sql`) | sudah dijalankan di database tujuan | bila belum, jangan arahkan ke database asli |
| `WRITE_STATUS_COLUMN` | `false` bila database sudah 4b; `true` bila belum | sesuai [rancangan-worker-mvp.md](../keputusan/rancangan-worker-mvp.md) bagian 7 |
| Pengguna MQTT ESP | boleh publish `aeros/<device>/telemetry` dan `/status`, subscribe `/telemetry/ack` | pengguna ESP, bukan pengguna worker |
| Satu worker aktif | matikan worker laptop bila worker hosting hidup, atau sebaliknya | README worker |

### 12.5 Tahapan

| # | Tahap | Selesai bila | Status |
|---|---|---|---|
| V1 | Putuskan K8 dan K9 | dijawab | **selesai** (6 Nov) |
| V2 | Buat `firmware-v3-dummy/` (salinan firmware-v2, ganti `sensorBridge.cpp`, buang `sensorOriginal.inl`) | `pio run` lulus | **selesai** (6 Nov; flash 40,6%) |
| V3 | Pembangkit skenario S0 sampai S3b | serial mencetak urutan fase dan nilai yang sesuai bagian 6 | **selesai**; cetakan serial terlihat di ESP (6 Nov) |
| V4 | Uji tanpa jaringan: `event_id`, `co_level`, `co2_level`, `demo` benar per fase | sesuai tabel bagian 6 | **selesai di komputer** (12.7); uji di ESP belum |
| V5 | Unggah ke ESP kosong, isi `secrets.h`, jalankan S0 lalu S1 ke worker dan salinan database | `[READING] ... DEMO` di log worker, baris di `v_alerts` | **sebagian**: S1 versi cepat lolos ke Railway dan `v_alerts` (12.8); S0 dan S1 profil bertahap belum |
| V6 | S2, S3a, S3b, daftar periksa bagian 8, tangkapan layar aplikasi | semua sesuai "hasil yang diharapkan" | belum |

V2 sampai V4 tidak butuh kredensial dan tidak menyentuh database.

### 12.6 Batasan jalur 3

- Membuktikan jalur dan kode pengiriman firmware, **bukan** sensor, relay, atau buzzer.
- Pesan berlabel `demo = true` dan tercatat `DEMO`; sampaikan sebagai simulasi.
- ESP tanpa sensor tetap boleh dipasang dengan kabel USB biasa; tombol GPIO32 tidak perlu dipasang (memakai pull-up).

### 12.7 Hasil uji tanpa jaringan (V4)

6 November 2026, di komputer (bukan di ESP): `sensorBridge.cpp` dikompilasi dengan tiruan Arduino, tiap skenario dimainkan sampai berhenti, lima sampel digabung dan `event_id` dihitung dengan aturan `trackSensorAlarm`. Setelah profil bertahap (bagian 6.1): S1, S2, S3a, S3b masing-masing 505 sampel (8,4 menit); normal ke bahaya 300 detik; bahaya 176 sampai 177 detik; `event_id` satu di S1, S2, S3a dan dua di S3b; tidak ada sampel setelah berhenti (S0: 40 sampel). `main.cpp` v3 dummy hanya beda satu baris dari firmware-v2 (`DEVICE_ID`).

Batas jendela: `main.cpp` menggabung 5 sampel tanpa tahu kapan skenario dimulai, jadi satu pesan bisa memuat sampel dari dua langkah. Urutan pesan tetap sama dan puncak satu pesan bisa lebih tinggi dari nilai sekarang; keduanya lolos pemeriksaan worker.

### 12.8 Uji di ESP (6 November 2026)

- Firmware dummy versi pertama (skenario cepat, 65 detik) dimainkan dua kali ke worker Railway: dua peringatan `bahaya`/`{CO2}` muncul di `v_alerts` (`c31547ad`, `eb9c5425`), semua baris dengan `event_id` dan tingkat yang benar.
- Profil bertahap (bagian 6.1) sudah di-upload ke ESP dan boot terverifikasi (diam, Wi-Fi dan MQTT tersambung, tidak ada data terkirim). **Skenario bertahap belum dimainkan di ESP.**
- Perintah serial: `0` sampai `4`, `a`, `s` (berhenti), `h`. ESP tidak mengirim data sampai ada perintah dan berhenti sendiri setelah skenario selesai.
