# Materi PPT Expo AEROS: "Ini dari mana? Skematiknya bagaimana?"

Disusun 4 November 2026, **diperiksa ulang terhadap kode pada 5 November 2026** (firmware **v2.5** di salinan kerja, worker `efa7d8d`). Isi diambil dari **kode yang ada sekarang** (firmware-v2, worker, SQL 4a/4b), lalu dicocokkan dengan dokumen dan hasil uji. Kalau dokumen lama bertentangan dengan kode, **kode yang dipakai** dan dokumen lama dicatat di bagian 10.

Ini ringkasan turunan untuk presentasi. Angka final tetap hidup di [keputusan.md](../keputusan/keputusan.md); wiring di [hardware-wiring.md](../keputusan/hardware-wiring.md). Kalau berbeda, perbaiki sumbernya, lalu perbarui berkas ini.

**Diagram dan rumus sudah berupa PNG** (siap tempel ke slide): [gambar-ppt-expo/diagram/](gambar-ppt-expo/diagram/) (10 diagram, sumber `.mmd` di folder yang sama) dan [gambar-ppt-expo/rumus/](gambar-ppt-expo/rumus/) (13 rumus, sumber LaTeX di [rumus.mjs](gambar-ppt-expo/rumus.mjs)). Cara membuat ulang ada di komentar [render.mjs](gambar-ppt-expo/render.mjs). Skematik dan PCB tetap memakai gambar KiCad di bagian 3.

Penanda: ✔ terbukti (ada data uji atau terbaca di kode) · ◐ sementara/usulan · ✖ belum terbukti.

---

## 1. Hasil evaluasi (baca ini dulu)

### 1.1 Yang sudah sinkron (aman dipresentasikan)

| Bagian | Bukti |
|---|---|
| Pin firmware = skematik (SDA21, SCL22, CO2 16/17, buzzer 27, relay turun 26, relay naik **18**, **tombol Wi-Fi 32** sejak 4 Nov) | kode `sensorOriginal.inl` baris 63-80. **Skematik KiCad 3 Nov masih menulis relay naik GPIO25**; perlu digambar ulang (P1-e) |
| Format pesan ESP = worker (`r4|...`, 17 bagian yang sama persis) | `main.cpp` `sampleAndQueue` vs `securityService.js` `canonicalReading` |
| Worker | 36 uji otomatis lulus (`npm test`, 4 Nov); repo sama dengan `origin/main` |
| Siklus CO2 sampai relay | uji 8: 11 pasang turun 1,5 s lalu naik 5 s, tidak ada yang terbalik |
| Data sampai database | uji 7 (Civic): 431 ACK untuk ±431 kiriman, tunda simpan median 1,45 s |
| Alarm tanpa internet | uji 8: 4 episode saat Wi-Fi mati, bunyi dan sinyal jendela tetap jalan |
| Rumus, konstanta, dan ambang di bagian 4 | dibaca ulang dari kode 5 Nov; rasio ambang (0,175 / 0,081 / 0,199) dan contoh ppm dihitung ulang, cocok |
| Angka model C-251 dan uji Civic (7.4) | dicocokkan ke [model-vs-uji.md](../analisis/model-vs-uji.md) dan uji 7, cocok |
| R0 5470 kΩ dan 36 uji worker | R0 tercatat di log monitor; `npm test` 5 Nov: 36 lulus, 0 gagal |

### 1.2 Yang belum sinkron (perbaiki atau siapkan jawabannya)

| # | Temuan | Dampak di expo | Tindakan |
|---|---|---|---|
| ~~P1-a~~ **selesai 4 Nov** | Tombol Wi-Fi dipindah ke **GPIO32** ([main.cpp:53](../../firmware-v2/src/main.cpp#L53)) dan pesan serial diperbarui. **Belum dikompilasi dan belum diuji di alat** (PlatformIO tidak ada di mesin ini) | Bila tombol di PCB belum tersambung ke GPIO32 dan GND, portal tidak terbuka | Upload, lalu tahan tombol 5 detik: serial harus menulis "[BUTTON] Hold 5s terdeteksi". Belum di-commit |
| **P1-b** | **Mode ambang**: `MODE_PENGEMBANGAN = true` di berkas kerja ([sensorOriginal.inl:56](../../firmware-v2/src/sensorOriginal.inl#L56), belum di-commit; arsip v2.5 juga `true`). Commit v2.4 bernilai `false` | `true` = ambang 700/800 ppm (cocok untuk demo meja, napas ke sensor). `false` = 2500/4000 (cocok untuk mobil). Salah pilih = demo gagal atau data mobil salah | Putuskan per skenario dan **tulis di slide** ("mode demo meja" atau "mode rancangan"). Layar LCD baris bawah menulis "Mode pengembang" saat `true` |
| **P1-c** | **Versi pesan**: firmware v2.4 mengirim **versi 4**. Worker lama hanya paham versi 3 dan akan menolak versi 4 | Data tidak masuk database walau alat jalan | **Diperiksa 4 Nov (baca saja):** `cek-database.js` semua OK, kolom `co_level`, `co2_level`, `buzzer_state`, `event_id` dan view `v_alerts` ada (SQL 4a berlaku). 1644 baris berisi `buzzer_state`, terakhir 4 Nov 12:05 WIB, jadi worker versi baru **sedang menulis**. Belum diketahui: apakah SQL 4b sudah dijalankan |
| **P1-d** | Celah data **19:53:09-20:12:34 WIB** di uji 8 ([uji 8](../pengujian/laporan/uji-8-meja-wifi-mqtt-firmware-v2.3-2026-11-03.md) bagian 2a). **Terbukti di database:** 0 baris selama 19,4 menit, tetapi 2 peringatan tetap terbuat (20:05:30 dan 20:06:25) | Penguji bisa bertanya "datanya pernah hilang?" | **Dugaan kuat (belum terbukti):** saat itu worker baru sudah menulis (kolom baru terisi sejak 19:48) tetapi SQL 4b dijalankan, sehingga penulisan `status` ditolak database; peringatan dibuat dulu lalu bacaan gagal, sampai worker diatur `WRITE_STATUS_COLUMN=false` pukul ±20:12. Cocok dengan uji 3NF di [rancangan-database-mvp.md](../keputusan/rancangan-database-mvp.md) bagian 8.1. Konfirmasi dengan log Railway jam itu atau tanya teman backend. Sampai itu, klaim "tidak ada data hilang" hanya untuk uji 7 |
| ~~P2-a~~ **berubah di v2.5** | Jalur jendela **CO dan CO2 kini sama-sama memakai relay naik GPIO18** (lewat bip 0,5 s dan jeda 3 s dulu). Bedanya: CO2 turun 1,5 s, CO turun **10 s** ([PULSA_BUKA_MS, baris 83](../../firmware-v2/src/sensorOriginal.inl#L83)); naik selalu 5 s. Sebelum v2.5 jalur CO tidak punya sinyal tutup | Jawaban lama "CO hanya minta tutup manual" **sudah tidak benar** untuk v2.5 | Perbarui Q14. v2.5 belum di-commit dan belum diuji di mobil |
| **P1-e** | **Relay naik sekarang GPIO18** (keputusan 5 Nov; `PIN_JENDELA_NAIK`, [baris 80](../../firmware-v2/src/sensorOriginal.inl#L80)). Skematik KiCad, PCB, [hardware-wiring.md](../keputusan/hardware-wiring.md), dan gambar lama masih GPIO25. v2.5 belum diuji di alat | Slide yang memakai gambar skematik lama akan menulis GPIO25, beda dengan firmware | Gambar ulang skematik/perfboard dengan GPIO18 dan pindahkan kabel di alat; **belum saya ubah** |
| **P2-g** | **Batas total waktu turun 10 detik** ([JENDELA_TOTAL_MAKS_MS, baris 89](../../firmware-v2/src/sensorOriginal.inl#L89)) berlaku untuk pulsa turun jalur CO. Satu pulsa CO sudah 10 s, jadi episode CO kedua **ditolak** ("DITOLAK ... ketik n") sampai perintah `n` atau reboot. Pulsa siklus CO2 tidak dihitung | Di mobil, CO kedua dalam satu nyala tidak membuka jendela | Jangan klaim "selalu membuka" untuk CO; atau putuskan apakah batas ini dipertahankan |
| **P2-h** | Jalur CO: turun **10 s**, tetapi naik hanya **5 s** | Jendela bisa belum menutup penuh (waktu tempuh penuh belum diukur; tidak ada sensor posisi) | Catat sebagai batasan; ukur waktu tempuh jendela |
| P2-b | `co_level` untuk sumber **LUAR** dikirim **2 (bahaya)** di kode ([sensorBridge.cpp:89](../../firmware-v2/src/sensorBridge.cpp#L89)); rancangan DB menulis "1, usulan" | Beda angka antar dokumen | Pakai angka kode (2). Perbarui rancangan DB |
| P2-c | Posisi jendela hanya **estimasi timer** (0 = atas, 50 = bawah, null = bergerak). Tidak ada sensor posisi. Relay belum terpasang ke jendela mobil; di uji mobil jendela dibuka tim secara manual | "Jendela benar-benar bergerak?" | Jawab: yang terbukti sinyal GPIO (1,5 s dan 5 s). Gerak fisik belum terbukti |
| P2-d | Lama pulsa naik: 5000 ms (5 kali) dan ±5340 ms (6 kali). Pulsa turun selalu 1500 ms | Selisih ±0,34 s | Sebutkan "±0,3 s", penyebab belum diselidiki |
| P2-e | Pertanyaan keselamatan relay belum dijawab hardware: kabel motor di saklar asli bisa terhubung GND ([hardware-wiring.md](../keputusan/hardware-wiring.md) bagian 7-8) | Risiko korsleting bila disambung ke mobil | Jangan klaim "siap dipasang ke mobil"; klaim "sinyal dan driver relay sudah diuji di meja" |
| P2-f | R0 sensor CO masih harus **dikalibrasi ulang di mobil**; ppm CO selalu estimasi | Angka CO bisa diserang | Gunakan kalimat aman bagian 9 |

### 1.3 Penilaian singkat (sudut pandang dosen)

- **Kuat**: tiap angka punya sumber atau data; alarm tidak bergantung internet; pesan bertanda tangan; hasil uji nyata dari 3 mobil dan meja; ada pembanding model C-251 dengan kenyataan.
- **Lemah yang pasti ditanya**: CO belum dikalibrasi gas asli; jendela belum terbukti bergerak otomatis; satu mobil per angka jendela; ambang CO2 bukan standar medis tetapi pilihan rancangan.
- **Cara menjawab lemah**: nyatakan batasnya lebih dulu, lalu tunjukkan apa yang **sudah** terbukti (bagian 9).

---

## 2. Gambaran sistem (1 slide)

![01-gambaran-sistem](gambar-ppt-expo/diagram/01-gambaran-sistem.png)

Tiga kalimat inti untuk slide:
1. **Keputusan alarm dan jendela dibuat di ESP32 tiap 1 detik; internet hanya untuk melapor.**
2. Data dikirim tiap **5 detik**, bertanda tangan **HMAC**, disimpan database, baru dibalas **ACK**.
3. Peringatan tersimpan sebagai **episode** (`alert_logs`) yang menunjuk ke bacaan-bacaannya.

---

## 3. Skematik hardware

Gambar sumber: [skematik-pin-2026-11-03.png](../keputusan/diagram/skematik-pin-2026-11-03.png) (KiCad), [perfboard relay](../keputusan/diagram/diagram-7-perfboard-relay-jendela.png), [PCB atas](../keputusan/diagram/pcb-tampak-atas-2026-11-03.png) dan [bawah](../keputusan/diagram/pcb-tampak-bawah-2026-11-03.png). Gunakan gambar-gambar itu di slide; tabel di bawah untuk catatan pembicara.

### 3.1 Pin dan fungsi (ESP32 DevKitC)

| Komponen | Pin ESP32 | Jalur | Alasan |
|---|---|---|---|
| MH-Z19C (CO2) | GPIO16 (RX2), GPIO17 (TX2) | UART 9600 8N1, catu 5 V | sensor NDIR kirim ppm langsung |
| ADS1115 (pembaca analog MiCS) | GPIO21 (SDA), GPIO22 (SCL) | I2C alamat 0x48, catu 3,3 V | ADC ESP32 kasar dan tidak linear; ADS1115 16-bit |
| MiCS-5524 | A0 ADS1115 | catu 5 V, keluaran AO | sensor CO semikonduktor |
| LCD 16x2 | GPIO21/22 (satu jalur I2C dengan ADS1115) | alamat 0x27 | berbagi bus |
| Buzzer | GPIO27 | ke GND | bunyi peringatan |
| Relay **TURUN** (buka jendela) | **GPIO26** (TBout) | lewat driver perfboard | 1,5 s per episode bahaya CO2; 10 s untuk uji arah CO |
| Relay **NAIK** (tutup jendela) | **GPIO18** (dulu GPIO25, lihat P1-e) | lewat driver perfboard | 5 s, didahului bip 0,5 s dan jeda 3 s (v2.5) |
| Tombol Wi-Fi | **GPIO32** | ke GND; tahan 5 s | firmware sudah GPIO32 (4 Nov), belum diuji di alat |

Pin yang dipakai tidak ada yang bentrok. GPIO32 tidak punya konektor di PCB (kabel dari header). Konektor GPIO18 belum diperiksa di PCB.

### 3.2 Catu daya

```
Aki/USB mobil 12 V -> TBin -> buck DC-DC -> 5 V -> ESP32, MH-Z19C, MiCS, LCD
                                         ESP32 3V3 -> ADS1115
Aki 12 V (fuse 2 A)  -> koil relay (perfboard)
Aki 12 V (fuse 15-20 A) -> kontak relay 30 -> 87 -> motor jendela
SEMUA GND SATU JALUR: minus aki = buck OUT- = GND ESP32 = GND perfboard
```

- Uji mobil memakai **USB mobil** (alat menyala saat mobil menyala), bukan relay ke motor.
- Tanpa GND bersama, sinyal 3,3 V tidak punya acuan dan transistor tidak menyala.

### 3.3 Driver relay (dua kanal identik di perfboard)

```
GPIO -> 470 ohm -> basis PN2222A
                   basis -> 10 kohm -> GND   (relay lepas saat ESP boot/reset)
                   emitor -> GND
                   kolektor -> koil relay (kaki 86); kaki 85 -> +12 V
                   dioda 1N4007 melintang koil, garis (katoda) ke +12 V
```

| Komponen | Fungsi (jawaban singkat) | Angka (dihitung, belum diukur ◐) |
|---|---|---|
| ESP32 GPIO | hanya memberi sinyal 3,3 V, tidak kuat menarik koil | arus keluar ≈ 5,5 mA (rumus di bawah tabel) |
| 470 ohm | membatasi arus basis | (3,3 - 0,7) / 470 ≈ 5,5 mA |
| PN2222A | saklar elektronik; arus kecil mengendalikan arus koil | kuat 600 mA, koil ±150 mA |
| 10 kohm ke GND | menjaga basis tetap rendah saat ESP belum menyala | relay tidak klik waktu boot |
| Dioda 1N4007 | meredam lonjakan tegangan koil saat relay lepas | terbalik = korsleting |
| Dua relay | satu arah putar motor masing-masing | **tidak boleh HIGH bersamaan** |

![Arus basis transistor](gambar-ppt-expo/rumus/10-arus-basis.png)

Pengaman di firmware: pin lawan dipaksa LOW dulu sebelum pulsa, jeda LOW minimal 1 detik antar pulsa, batas satu pulsa 10 s ([ujiMulaiPulsa](../../firmware-v2/src/sensorOriginal.inl#L393)). Daftar lengkap di 4.6.

### 3.4 Jika ditanya soal hardware
- *"Kenapa ADS1115, bukan ADC ESP32?"* Hasil MiCS hanya puluhan mV; ADC internal ESP32 kasar. ADS1115 16-bit dengan gain otomatis 1,024 / 2,048 / 4,096 V.
- *"Kenapa ada transistor?"* GPIO tidak sanggup menarik koil relay; transistor jadi saklar.
- *"Kenapa 5 V dan 3,3 V campur?"* MH-Z19C, MiCS, LCD butuh 5 V; ADS1115 dicatu 3,3 V supaya sinyal I2C aman untuk ESP32. ✖ tegangan AO MiCS ke ADS1115 pernah terbaca 3,68 V (melewati batas ±3,6 V) dan masih perlu diukur ulang.

---

## 4. Firmware (versi **v2.5**)

Bagian ini dibaca dari kode `firmware-v2/src` pada 5 Nov. Tiap langkah menyebut **nama fungsi di kode** supaya bisa dibuka saat ditanya. Versi v2.5 menambah satu hal dibanding v2.4: **bip peringatan dan jeda sebelum jendela naik** (4.6). Logika sensor dan ambang tidak berubah dari v2.4.

> v2.5 belum di-commit dan belum diuji di mobil. Relay NAIK sekarang **GPIO18** (`sensorOriginal.inl:80`); arsip v2.5 dan skematik KiCad masih GPIO25.

### 4.1 Peta kode: siapa mengerjakan apa

![Arsitektur firmware](gambar-ppt-expo/diagram/02-arsitektur-firmware.png)

| Bagian | Berkas | Tugas |
|---|---|---|
| **Task sensor** (task FreeRTOS `AEROS_sensor`, stack 12 KB) | `sensorOriginal.inl` | baca sensor, filter, aturan alarm, buzzer, relay, LCD, cetak 1 baris CSV per detik |
| **Jembatan** | `sensorBridge.cpp` | menangkap baris CSV yang dicetak task sensor (10 kolom), menyimpan 128 sampel terakhir, menerjemahkan status menjadi angka tingkat (0, 1, 2) |
| **Loop utama (jaringan)** | `main.cpp` | Wi-Fi, portal, NTP, MQTT TLS, HMAC, kirim tiap 5 sampel, terima ACK |
| **Task tombol** | `main.cpp` (`portalButtonTask`) | memantau GPIO32; tahan 5 detik = hanya menaikkan satu penanda, portal dibuka oleh loop utama |

Kenapa dipisah lewat baris CSV: kode jaringan **tidak menyentuh** kode sensor, jadi Wi-Fi yang macet tidak bisa menunda buzzer atau relay. Inti sensor dijalankan **pertama** di `setup()`. Bila konfigurasi jaringan kosong atau rusak, inti sensor tetap jalan dan jaringan tidak dimulai.

### 4.2 Satu siklus 1 detik (`loop()` di `sensorOriginal.inl`)

![Siklus 1 detik](gambar-ppt-expo/diagram/03-siklus-1-detik.png)

| Langkah | Yang terjadi | Fungsi di kode |
|---|---|---|
| 1 | Minta CO2 ke MH-Z19C (perintah 9 byte `FF 01 86 ...`), tunggu paling lama 0,5 detik, periksa awalan dan checksum | `readCO2` |
| 1 | Baca tegangan MiCS 16 kali lewat ADS1115, ambil rata-rata; gain dinaikkan otomatis bila hampir penuh | `bacaAds`, `bacaMics` |
| 2 | Valid bila tidak jenuh dan 0,5 mV ≤ V ≤ VCC − 1 mV. Tidak valid lebih dari 3 kali berturut-turut: filter dikosongkan | `loop`, `kosongkanFilter` |
| 3-4 | Tegangan → Rs → rata-rata 6 detik → rasio → ppm (rumus di 4.3) | `loop` |
| 5 | Selama 180 detik pertama: angka dicetak tetapi **tidak dipakai aturan** (MH-Z19C mengeluarkan 410/500 palsu saat dingin) | `co2Siap`, `coSiap` |
| 6 | Bila aturan CO sedang berjalan, aturan CO2 dilewati ("CO menang") | `aturanCO`, `aturanCO2` |
| 7 | Bunyi, relay, LCD diperbarui; 1 baris CSV dicetak | `servis`, `perbaruiLcd` |
| 8 | Tunggu sampai genap 1 detik. Selama menunggu, `servis()` dipanggil tiap 2 ms agar bunyi dan relay tepat waktu | akhir `loop` |

Kegagalan sensor:
- Satu sensor gagal: sensor yang sehat tetap jalan.
- Dua-duanya gagal: LCD "SENSOR GANGGUAN", **tidak ada aksi otomatis**.
- MiCS gagal (pemanasan, error, kalibrasi): CO dikirim sebagai 0 dan alarm CO mati, tetapi CO2 tetap dikirim (`sensorBridge.cpp:74-83`). Karena itu "CO = 0" di data berarti "tidak ada bacaan CO yang sah", **bukan** "udara bersih".

### 4.3 Dari tegangan sensor ke ppm CO

Ini jalur yang paling sering ditanya ("angka CO dari mana?"). Setiap langkah punya rumus, dan tiap rumus adalah satu baris di kode.

**Langkah A. Tegangan keluaran MiCS dibaca ADS1115** (`bacaAds`)

![Rumus ADS1115](gambar-ppt-expo/rumus/08-ads1115.png)

Gain otomatis: naik bila |V| > 92% rentang, turun bila |V| < 40% rentang di bawahnya. Alasan memakai ADS1115: tegangan MiCS di udara bersih hanya sekitar 8 mV, terlalu kecil untuk ADC bawaan ESP32.

**Langkah B. Hambatan sensor Rs** (pembagi tegangan dengan RL)

![Rumus Rs](gambar-ppt-expo/rumus/01-tegangan-ke-rs.png)

**Langkah C. Filter SMA 6** (rata-rata 6 hasil Rs terakhir, `bufRs[]`)

![Rumus SMA](gambar-ppt-expo/rumus/02-filter-sma6.png)

Ppm baru dihitung setelah buffer terisi 6. Alasan angka 6 ada di 7.1.

**Langkah D. Rasio terhadap udara bersih**

![Rumus rasio](gambar-ppt-expo/rumus/03-rasio.png)

R0 disimpan di memori ESP32 (NVS, kunci `r0`). Dikalibrasi lewat perintah serial `r`: 120 detik di udara bersih, ditolak bila selisih max-min > 40%. Nilai terakhir tersimpan: **5470 kΩ** (tercatat di log monitor).

**Langkah E. Rasio menjadi ppm** (kurva datasheet MiCS-5524)

![Rumus ppm CO](gambar-ppt-expo/rumus/04-kurva-ppm-co.png)

**Contoh angka** (R0 = 5470 kΩ):

![Contoh angka](gambar-ppt-expo/rumus/07-contoh-angka.png)

| Tegangan V | Rs | Rasio | ppm CO (estimasi) |
|---|---|---|---|
| 8,4 mV | 5497 kΩ | 1,005 | 0 (udara bersih) |
| 20,0 mV | 2303 kΩ | 0,421 | 12 |
| 47,9 mV | 955 kΩ | 0,175 | **35** (ambang waspada) |
| 90,0 mV | 504 kΩ | 0,092 | 75 |
| 101,8 mV | 444 kΩ | 0,081 | **87** (ambang bahaya) |

Ambang ppm diubah ke rasio supaya mudah dicek di tabel serial:

![Ambang dalam rasio](gambar-ppt-expo/rumus/05-ambang-dalam-rasio.png)

**CO2 tidak memakai rumus:** MH-Z19C mengirim ppm langsung. Kode hanya menyusun dua byte dan memeriksa checksum (`readCO2`):

![Checksum CO2](gambar-ppt-expo/rumus/09-checksum-co2.png)

Kalimat wajib di slide: **"ppm CO = estimasi dari kurva datasheet, belum dikalibrasi gas CO asli."** Alasan: R0 berubah (Rs turun >50% dalam 4 jam di kamar), sensor tidak selektif (parfum ikut terbaca), belum ada kompensasi suhu dan kelembapan.

### 4.4 Aturan CO2 (`aturanCO2`)

![Aturan CO2](gambar-ppt-expo/diagram/04-aturan-co2.png)

- **Syarat 3 bacaan berturut-turut** (`CO2_BACAAN_KONFIRMASI`): satu bacaan lonjakan tidak membuat alarm. Hitungan diulang dari 0 bila ada satu bacaan di bawah ambang.
- **Bahaya (TINDAKAN)** diperiksa lebih dulu dari peringatan. Bila CO2 melonjak langsung ≥ 4000, status melompat ke TINDAKAN tanpa singgah di PERINGATAN.
- **Selesai:** di bawah 2500 ppm selama 10 detik berturut-turut. Setelah itu status NORMAL, buzzer berhenti, siklus jendela diizinkan menutup (4.6).
- **Dua ambang yang berbeda tujuan:** 2500 = peringatan lembut (bukti pengaruh kognitif lemah); 4000 = tindakan (batas kerja 5000 dikurangi margin sensor ±250 dan jeda sensor).
- Tingkat dikirim ke jaringan per gas: 0 normal, 1 waspada, 2 bahaya.
- **Sensor hilang bukan dianggap aman:** `gAmanCO2` hanya benar bila sensor terbaca dan pemanasan selesai, jadi tidak ada pulsa naik saat sensor mati.
- Mode meja (`MODE_PENGEMBANGAN = true`): ambang 700 / 800 / selesai < 700 supaya bisa dicoba dengan napas. **Salinan kerja sekarang `true`**; ubah ke `false` untuk mobil.

### 4.5 Aturan CO dengan uji arah (`aturanCO`)

![Aturan CO dan uji arah](gambar-ppt-expo/diagram/07-aturan-co-uji-arah.png)

Idenya: **buka jendela sebentar, lihat CO turun atau naik.** CO turun berarti sumbernya di dalam mobil (jendela dibiarkan terbuka). CO naik berarti sumbernya di luar, misalnya knalpot kendaraan lain (jendela ditutup lagi).

![Rumus uji arah](gambar-ppt-expo/rumus/06-uji-arah.png)

- Rs turun berarti CO naik, dan sebaliknya. Karena itu Rs **naik** > 5% dinilai "CO turun".
- Rs turun > 25% dinilai jelas luar. Perubahan di antaranya (naik ≤ 5%, turun ≤ 25%) **tidak jelas**, dan kode memilih **luar** (lebih aman: jendela ditutup).
- Angka 25% dipilih dari data: tanpa gas, Rs tidak pernah turun >25% dalam ±28.000 detik (7.3).
- CO ≥ 87 ppm langsung masuk uji arah tanpa menunggu 30 detik; level BAHAYA dibunyikan.
- Bunyi CO diulang tiap 60 detik, paling lama 5 menit. Bunyi CO2 **tidak** diulang.
- Selesai: CO < 30 ppm selama 60 detik. Selisih 35 (masuk) dan 30 (keluar) berfungsi sebagai **histeresis** supaya status tidak berkedip di sekitar ambang.
- Jalur jendela CO: **turun 10 detik** lewat GPIO26 (`bukaJendela`, `PULSA_BUKA_MS`), lalu bila sumber luar atau CO selesai, **naik 5 detik lewat GPIO18** dengan bip dan jeda dulu (4.6). Sebelum v2.5, jalur CO hanya menampilkan "Tutup jendela" di LCD tanpa sinyal naik.

### 4.6 Siklus jendela dan peringatan sebelum naik

Siklus CO2 (`servisUjiGpio26`):

![Siklus jendela CO2](gambar-ppt-expo/diagram/05-siklus-jendela-co2.png)

Yang baru di **v2.5**, supaya tidak ada yang terjepit sebelum jendela naik (`mulaiPraTutup`, `servisPraTutup`):

![Urutan tutup jendela](gambar-ppt-expo/diagram/06-urutan-tutup-jendela.png)

![Waktu tutup jendela](gambar-ppt-expo/rumus/13-waktu-tutup-jendela.png)

Pengaman yang ada di kode:

| Pengaman | Cara kerja | Fungsi |
|---|---|---|
| Pin lawan dipaksa LOW dulu | dua relay tidak pernah HIGH bersamaan | `ujiMulaiPulsa`, `pulsaJendela` |
| Jeda LOW minimal 1 detik antar pulsa | arah tidak boleh berbalik seketika | `UJI_JEDA_ANTAR_PULSA_MS` |
| Batas satu pulsa 10 detik | pulsa lebih panjang dipotong | `PULSA_MAKS_MS` |
| Semua keluaran LOW paling awal saat boot | relay tidak klik saat ESP menyala; basis juga ditarik 10 kΩ ke GND di perfboard | awal `setup()` |
| Bergantian turun-naik | tidak turun dua kali, tidak naik sebelum turun | `siklus` |
| Perintah `x` | menghentikan pulsa; saat pra-tutup, membatalkan dan menganggap jendela di ATAS | `jalankanPerintah` |

Batasan yang harus disebut: tidak ada sensor posisi dan tidak ada anti-jepit sungguhan. Bip 0,5 detik dan jeda 3 detik adalah **usulan** (komentar kode: "belum diuji di mobil"). Posisi jendela di telemetri hanya estimasi timer (0 = atas, 50 = bawah, `null` = bergerak).

### 4.7 Buzzer (`servisBunyi`, tanpa menunda program)

| Kejadian | Pola | Catatan |
|---|---|---|
| Waspada (CO atau CO2) | 3 bip pendek (300 ms nyala, 300 ms jeda) | |
| Bahaya (CO atau CO2) | 1 bip panjang 3 detik | |
| Sebelum jendela naik (v2.5) | 1 bip 500 ms | menimpa pola alarm yang sedang bunyi |
| Ulang CO | tiap 60 detik, maksimal 5 menit | CO2 tidak diulang |

Buzzer fisik GPIO27. Nilai `buzzer_state` di telemetri berasal dari status alarm gas, **bukan** dari bip tutup jendela.

### 4.8 LCD 16x2 (`perbaruiLcd`)

| Baris | Tampilan biasa | Arti |
|---|---|---|
| Atas | `CO  35ppm WARN` | angka CO, status `OK` / `WARN` / `DANG` / `LUAR`; `WARM` + `----` saat pemanasan; `ERR`; `CAL` saat kalibrasi. Kolom ke-4: `J` jendela terbuka (jalur CO), `S` simulasi |
| Bawah | `CO2 2500ppm WARN` | angka CO2 dan status |

Pesan khusus **menimpa baris gas yang lain** supaya angka gas penyebabnya tetap terlihat, dan bergantian tiap 2 detik dengan angka asli:

| Penyebab | Tampil di | Teks |
|---|---|---|
| CO2 | baris atas | "Jendela membuka" (min. 3 detik); "Udara aman" / "Tutup jendela" selama 20 detik **sejak pulsa naik mulai** |
| CO | baris bawah | "CO naik >35 ppm / Sedang dipantau"; "CO tinggi! / Jendela dibuka"; "Sumber CO diduga / dari dalam mobil" atau "dari luar mobil / Tutup jendela"; "CO sudah aman" |
| Dua sensor gagal | baris bawah | "SENSOR GANGGUAN" |

Catatan: di v2.5 jendela naik **otomatis**, tetapi teks "Tutup jendela" masih sama seperti versi manual. Teks ini baru muncul saat pulsa naik mulai, bukan saat bip.

### 4.9 Parameter, nilai di kode, sumber

Nilai dibaca dari kode 5 Nov. Dokumen lama [parameter-dan-sumber.md](../keputusan/parameter-dan-sumber.md) masih menulis EMA 0,2, pemanasan 300 detik, dan ABC aktif; itu **sudah tidak berlaku**.

| Parameter | Nilai | Sumber / dasar | Status |
|---|---|---|---|
| Interval siklus | 1 detik | syarat filter jumlah genap | ✔ |
| Sampel ADS1115 | 16 per siklus | rata-rata kasar noise ADC | ✔ |
| Filter CO | SMA 6 | analisis 13.000 baris: meredam 76% goyangan, lebih halus dari EMA 0,2 | ✔ (satu sesi kamar + 4 uji) |
| Pemanasan | 180 detik, CO dan CO2 | MH-Z19C angka palsu 410/500 sampai detik 64 (4 dari 5) dan 128 (1); MiCS Rs 156 → ±1650 kΩ dalam 3 menit | ✔ |
| Kurva CO | A = 3,46; β = 0,840 | digitalisasi piksel kurva datasheet SGX | ✔ pembacaan grafik, ✖ kalibrasi gas |
| RL, VCC | 9970 Ω, 4,64 V | hasil ukur | ✔ |
| R0 | 5470 kΩ (kalibrasi 2 Nov), kalibrasi ulang di mobil menyusul | perintah `r`, batas selisih max-min 40% | ◐ |
| CO waspada | ≥ 35 ppm estimasi selama 30 detik | NIOSH REL 35 ppm | ◐ (30 detik sementara) |
| CO bahaya | ≥ 87 ppm, tanpa konfirmasi | WHO 15 menit 87 ppm | ✔ sumber, keputusan |
| Uji arah | 30 detik; Rs turun > 25% = luar; naik > 5% = dalam; di antaranya = anggap luar | tanpa gas Rs tidak pernah turun > 25% dalam ±28.000 detik | ◐ |
| CO selesai | < 30 ppm selama 60 detik | ±6 kali konstanta waktu filter | ◐ |
| CO2 peringatan | ≥ 2500 ppm, 3 bacaan berturut-turut | Satish 2012 (bukti lemah, jadi peringatan lembut) | ◐ |
| CO2 bahaya/tindakan | ≥ 4000 ppm, 3 bacaan | batas kerja 5000 ppm dikurangi margin sensor ±250 ppm dan jeda 130-350 ppm | ◐ |
| CO2 selesai | < 2500 selama 10 detik | data Avanza: CO2 terus turun setelah jendela ditutup | ◐ |
| Mode meja | 700 / 800 / selesai < 700 | hanya untuk uji meja | ✔ (uji 8) |
| Bunyi waspada / bahaya | 3 bip pendek / 1 bip 3 detik | keputusan tim | ✔ |
| Ulang bunyi CO | tiap 60 detik, maksimum 5 menit | keputusan tim | ◐ |
| Pulsa turun CO2 | 1,5 detik, GPIO26 | uji v1.8: 1501 ms | ◐ (belum dicocokkan waktu tempuh penuh) |
| Pulsa turun CO | 10 detik, GPIO26; **total maksimal 10 detik sampai perintah `n` atau reboot** | `JENDELA_TOTAL_MAKS_MS` | ◐ lihat P2-g |
| Pulsa naik | 5 detik, GPIO18 | lebih lama dari turun agar sampai atas | ◐ |
| Bip + jeda sebelum naik (v2.5) | 0,5 detik + 3 detik | usulan, belum diuji di mobil | ◐ |
| Jeda antar pulsa | ≥ 1 detik; batas satu pulsa 10 detik | pengaman motor | ✔ |

### 4.10 Perintah serial (115200 baud, akhiri dengan Enter)

| Perintah | Fungsi |
|---|---|
| `r` | kalibrasi R0 di udara bersih, 120 detik |
| `d` | R0 kembali ke default |
| `p40` / `p0` | simulasi CO 40 ppm / matikan (data bertanda `demo`, ditolak worker) |
| `q900` / `q0` | simulasi CO2 900 ppm / matikan (melewati pemanasan) |
| `o` | uji relay turun 10 detik |
| `x` | hentikan relay sekarang; saat pra-tutup, batalkan penutupan |
| `n` | nolkan batas total waktu turun (setelah jendela dinaikkan manual) |
| `f` | ganti tampilan: ringkas, tabel lengkap, CSV lengkap |
| `i` / `h` | tampilkan semua parameter / bantuan |
| `s` | matikan bunyi (sisa fitur lama; "Saya Tahu" tidak dipakai di MVP) |

Baris CSV ringkas yang diambil jembatan, 10 kolom: `t_s, V_mV, Rs_kohm, Rs_per_R0, CO_ppm_est, CO2_ppm, status_CO, status_CO2, jendela, bunyi`. Status jendela di kolom 9: `ATAS_LOW`, `TURUN_HIGH`, `BAWAH_LOW`, `NAIK_HIGH`.

### 4.11 Jaringan di firmware (`main.cpp`)

![Alur jaringan firmware](gambar-ppt-expo/diagram/10-alur-jaringan-firmware.png)

Tiap 5 sampel dari jembatan, `sampleAndQueue` menyusun satu pesan: nilai **terakhir**, nilai **puncak** dan detik puncaknya (agar lonjakan singkat tidak hilang), tingkat per gas, status buzzer, posisi jendela, `event_id`, `nonce`, jam NTP, lalu menandatangani seluruh isi (5.3).

### 4.12 Jika ditanya soal firmware
Lihat bagian 9 (Q1-Q10, Q13, Q14).

---

## 5. Alur komunikasi

### 5.1 Topik MQTT (broker HiveMQ Cloud, port 8883, TLS)

| Topik | Arah | Isi |
|---|---|---|
| `aeros/AEROS_01/telemetry` | ESP → worker | data tiap 5 detik, QoS 0 |
| `aeros/AEROS_01/telemetry/ack` | worker → ESP | "sudah tersimpan", QoS 1, bertanda tangan |
| `aeros/AEROS_01/status` | ESP → semua | `ONLINE` (retained); `OFFLINE` lewat Last Will saat putus |

Topik perintah (`.../cmd`, `.../cmd/ack`) masih ada di firmware, tetapi **tidak dipakai** di MVP (fitur "Saya Tahu" dibuang).

### 5.2 Urutan satu data

![08-urutan-satu-data](gambar-ppt-expo/diagram/08-urutan-satu-data.png)

### 5.3 Isi pesan (versi 4)

| Field | Arti |
|---|---|
| `co_ppm`, `co2_ppm` | nilai terakhir dalam jendela 5 detik |
| `co_peak_ppm`, `co2_peak_ppm`, `*_peak_second` | puncak dan detik ke-berapa (agar lonjakan singkat tidak hilang) |
| `co_level`, `co2_level` | 0 normal, 1 waspada, 2 bahaya, **per gas** (status gabungan dihitung worker) |
| `buzzer_state`, `window_status` | `on/off`; 0 atas, 50 bawah, `null` bergerak (tidak pernah angka palsu) |
| `event_id` | UUID episode peringatan; `null` bila normal |
| `nonce`, `timestamp`, `time_valid` | acak 128 bit; jam NTP (0 dan `false` bila belum sinkron) |
| `demo` | `true` untuk data simulasi; worker menolaknya kecuali diizinkan |
| `signature` | HMAC-SHA256 atas string `r4|device|nonce|timestamp|valid|co|co2|coPeak|co2Peak|coDtk|co2Dtk|coLv|co2Lv|buzzer|window|event|demo` |

### 5.4 Keamanan (yang bisa diklaim)

| Lapis | Cara | Apa yang dicegah |
|---|---|---|
| TLS | sertifikat ISRG Root X1 diperiksa, tidak pernah `setInsecure()` | penyadapan, broker palsu |
| HMAC-SHA256 | kunci rahasia di ESP dan worker saja, perbandingan waktu-tetap | pesan palsu atau diubah |
| Nonce + kunci unik (`device_id`, `nonce`) di database | pesan ganda ditolak | pengulangan pesan |
| Jendela waktu | maks 90 hari lalu, 5 menit ke depan | stempel waktu ngawur |
| Daftar perangkat | `devices.is_active` | perangkat tak dikenal |
| ACK bertanda tangan | `dataack2|device|nonce|stored` | ESP percaya "tersimpan" padahal tidak |
| Last Will | `OFFLINE` otomatis dari broker | tahu perangkat putus |

![Rumus HMAC](gambar-ppt-expo/rumus/11-hmac.png)

Batas yang harus disebut: HMAC mencegah **pesan palsu**, bukan memastikan sensor mengukur dengan benar. Satu kunci untuk satu perangkat (prototipe).

### 5.5 Ketahanan jaringan

- Wi-Fi: 5 percobaan × 10 detik; gagal → tunggu 30 detik; password diduga salah → portal `AEROS-Setup` (192.168.4.1, 5 menit).
- MQTT: ulang tiap 5 detik; keep-alive 30 detik.
- Penyangga RAM **4 data**; tanpa ACK dikirim ulang tiap 6 detik; data tertahan > 30 detik **dibuang** (bukan dikirim terlambat).
- **Mode online-saja** (keputusan): saat jaringan putus data tidak disimpan. Alarm, buzzer, LCD, dan jendela tetap jalan. Alasannya: antrean flash terbukti tidak terkejar (±200 item, 27 detik per item).
- "Perangkat tidak terhubung" **bukan** berarti udara aman.

---

## 6. Worker dan database

### 6.1 Urutan kerja worker (`handleSensorMessage`)

1. Subscribe `aeros/+/telemetry` dan `aeros/+/status` (QoS 1); sambungan TLS dengan sertifikat diperiksa.
2. `verifyReading`: versi 3 atau 4, bentuk tiap field, puncak ≥ nilai, `event_id` wajib saat tidak normal, buzzer `on` hanya saat tidak normal, **HMAC**.
3. `device_id` di pesan harus sama dengan topik; data `demo` ditolak.
4. `assertActiveDevice`: perangkat harus ada dan aktif di tabel `devices`.
5. `pastikanPeringatan`: buat baris `alert_logs` dengan `id = event_id` **lebih dulu** (kunci tamu); duplikat sah diterima.
6. `persistReading`: simpan `sensor_readings`; duplikat `nonce` dibuktikan ada, lalu dianggap sukses.
7. `mirrorRecentTelemetry` (usaha terbaik): perbarui `device_state` dan tutup peringatan lama, **hanya** untuk data < 90 detik dan yang terbaru.
8. Kirim ACK bertanda tangan **hanya setelah** bacaan tersimpan.
9. Pesan `status`: `ONLINE` → `device_state.connection_status = online`; `OFFLINE` → `offline`.

Lingkungan: `WRITE_STATUS_COLUMN=false` (kolom `status` turunan), `ACCEPT_V3=true` sampai semua ESP v4. Satu worker aktif per perangkat. Tes: 36 lulus (`npm test` di repo `aeros-worker`).

### 6.2 Tabel database (rancangan MVP, SQL 4a dan 4b)

![09-erd-database](gambar-ppt-expo/diagram/09-erd-database.png)

(Kolom puncak `co_peak_*`, `co2_peak_*` dan waktu tidak ditampilkan agar muat.)

Alasan rancangan (untuk "kenapa tabelnya begini?"):
- **Tidak ada kolom "gas"**: satu peringatan bisa CO, CO2, atau keduanya. Tiap bacaan membawa `co_level` dan `co2_level`; gas, tingkat tertinggi, dan puncak dihitung di view `v_alert_gas` dan `v_alerts`. Ini menjaga **3NF** (kolom teks "CO,CO2" melanggar 1NF).
- `status` = tingkat tertinggi kedua gas, jadi dibuat **kolom turunan** (`generated always`): database yang menjaganya, tidak bisa tidak konsisten.
- Tingkat berupa **angka** karena `max()` pada teks menaruh `waspada` di atas `bahaya`.
- `device_state` adalah **pengecualian yang disengaja** (cache untuk realtime aplikasi).
- Ambang tidak disimpan di database, jadi mengganti ambang tidak mengubah skema.
- Hapus data 7 hari hanya untuk bacaan **tanpa** `event_id`; bukti peringatan tidak hilang.
- Diuji di PostgreSQL 17 lokal dengan 2401 bacaan nyata: `status` turunan sama 2401 dari 2401; 5 jenis data salah ditolak. **Belum** diuji di Supabase asli.

Urutan rilis aman: SQL 4a → worker baru → (ESP mati) SQL 4b → ESP v4 → `ACCEPT_V3=false`.

---

## 7. Cara kita menganalisis (bukti, bukan tebakan)

### 7.1 Filter: kenapa SMA 6
- Rekaman kamar 4 jam: Rs bergoyang ±13% per detik; **±95% goyangan adalah pola naik-turun bergantian tiap detik** (0,5 Hz), stabil, proporsional terhadap sinyal.
- Rata-rata **jumlah genap** menghapus pola itu (respons SMA jumlah genap bernilai nol tepat di 0,5 Hz; jumlah ganjil tidak). SMA 2/4/6/8/10 sama-sama meredam 76%; beda di kecepatan dan lonjakan: SMA 6 respons ±5 detik, lonjakan buatan lolos 4,9% (EMA 0,2: respons 10 detik, lolos 5,9%).
- Diulang di kamar, ruang rapat, 2 mobil: SMA 6 lebih halus dari EMA 0,2. SMA 8 cadangan.
- Sisa noise ±3% adalah gerakan lambat (tidak bisa disaring). Penyebab 0,5 Hz belum diketahui (dugaan catu pemanas) ✖.

### 7.2 Kalibrasi R0 dan sifat sensor
- R0 bukan konstan: Rs turun >50% dalam 4 jam di kamar. Karena itu ppm CO **selalu estimasi**.
- R0 dikalibrasi di udara bersih 120 detik dan disimpan di memori ESP; ditolak bila selisih max-min > 40%.
- Uji parfum: Rs turun 92% dalam 13 detik, estimasi 72-83 ppm. **Sensor tidak selektif** (alkohol, parfum ikut terbaca). Konfirmasi 30 detik menolak lonjakan singkat.

### 7.3 Dari mana kriteria uji arah
Kriteria 8% dan 15% terlampaui gerakan alami Rs. 25% **tidak pernah** terlampaui tanpa gas dalam ±28.000 detik (maks -21,4%), kecuali pintu dibuka (-23%). Jadi 25% dipilih sebagai batas "jelas naik". ✖ Belum diuji dengan sumber CO nyata (tidak boleh membuat CO sendiri).

### 7.4 Model pertukaran udara (dari proposal C-251, dibandingkan dengan kenyataan)

Model (n orang, G produksi CO2 per orang, V volume kabin, N laju pertukaran udara per jam, C_luar CO2 luar):

![Model pertukaran udara](gambar-ppt-expo/rumus/12-model-udara.png)

| Parameter | Model C-251 | Terukur | Kesimpulan |
|---|---|---|---|
| Produksi CO2 per orang G (L/jam) | 19,6 | ±10,5 (Avanza) | nyata ±54% dari model; model **konservatif** (waktu ke ambang 2× lebih cepat dari kenyataan) |
| N jendela tertutup (/jam) | 0,5-3 | Avanza 0,5-2 (cocok); Civic 6,6-11 (jauh lebih bocor, kasar) | beda antar mobil |
| N dua jendela depan setengah (/jam) | 13-26 | 46-79 (dengan jeda sensor) | model terlalu hati-hati |
| Laju naik CO2, 4 orang tertutup | 389-462 ppm/menit | **207-218** (Avanza), **213-268** (Civic) | |
| Waktu 2500 → 4000 ppm | 3,3-3,9 menit | ±7 menit (Avanza), ±15 menit (Civic) | |

Catatan: angka jendela berasal dari **satu mobil** (Avanza). Bila model dipakai di C-501, laporkan dua versi (asumsi C-251 dan parameter terukur). Detail: [model-vs-uji.md](../analisis/model-vs-uji.md).

### 7.5 Hasil uji lapangan dan KPI (sumber: [banner-hasil-uji-dan-kpi.md](../analisis/banner-hasil-uji-dan-kpi.md), [uji 7](../pengujian/laporan/uji-7-mobil-civic-firmware-v2-2026-10-30.md), [uji 8](../pengujian/laporan/uji-8-meja-wifi-mqtt-firmware-v2.3-2026-11-03.md))

| Ukuran | Hasil | Status |
|---|---|---|
| Kabin 4 orang tertutup lewat 2500 ppm | beberapa menit; naik 213-268 ppm/menit (Civic) | ✔ |
| Buzzer setelah ambang | ≤ 2 detik (target ≤ 5) | ✔ |
| Sinyal jendela setelah ≥ 4000 | 1,3 detik (target ≤ 10; gerak fisik belum diukur) | ✔ sinyal, ✖ gerak |
| Jendela dibuka manual: CO2 turun | 4025 → 2210 dalam 75 detik; 2881 → 1289 dalam ±80 detik | ✔ |
| Ke database | tunda simpan (received_at - measured_at) median 1,45 s, p95 1,68 s, maks 2,68 s | ✔ |
| Kehilangan data (uji 7) | 0 dari 431 | ✔ |
| Uji meja (uji 8) | 13 waspada, 11 bahaya, 11 pasang turun-naik benar, bunyi dan sinyal keluar 6-12 ms setelah status berubah | ✔ |
| Deteksi CO > 35 ppm | belum ada sumber CO nyata; estimasi sempat 81 ppm (≤ 15 detik, di bawah syarat 30 detik) | ✖ tidak bisa dibuktikan |
| Tampil di ponsel ≤ 20 detik | sisi ESP → database terpenuhi; sampai layar ponsel belum diukur | ✖ |

---

## 8. Yang sengaja **tidak** dibahas di slide (sudah dibuang atau di luar MVP)

| Jangan disebut | Alasan |
|---|---|
| "Saya Tahu", tabel `actuator_logs` | di luar MVP; dibuang daripada setengah jadi |
| Antrean offline di flash (LittleFS), "offline first" | diganti mode online-saja |
| Pesan versi 3 dan `status` yang dikirim ESP | sekarang versi 4: `co_level`, `co2_level` |
| EMA 0,2, MQ-7, MH-Z19B, filter 150 detik | digantikan SMA 6, MiCS-5524, MH-Z19C |
| Ambang 1000/2000/5000 dan CO 35/25 ppm dengan konfirmasi 10 detik | angka lama; sekarang 2500/4000 dan 30 detik |
| Servo/diorama, jendela "setengah lewat `WAKTU_SETENGAH`" | rencana awal; sekarang pulsa 1,5 s dan 5 s |
| "Jalur CO hanya meminta tutup manual" (LCD huruf `M`) | v2.5: CO ikut memakai relay naik GPIO18; `M` tidak muncul lagi di mode ini |
| Pembagian dua inti (inti 0 jaringan, inti 1 sensor) | usulan lama; kode sekarang: task sensor terpisah, jaringan di loop utama |

---

## 9. Jawaban siap pakai

### Kalimat aman
- "ppm CO adalah **estimasi** dari kurva datasheet, belum dikalibrasi gas referensi."
- "HMAC mencegah pesan palsu atau diubah; **tidak** menjamin sensor mengukur dengan benar."
- "Alarm dan jendela berjalan di ESP32 dan **tidak bergantung internet**."
- "Perangkat tidak terhubung **bukan** berarti udara aman."
- "Angka jendela berasal dari satu mobil; ini uji eksplorasi, bukan uji formal."
- Hindari kata: "akurat", "terkalibrasi", "alat keselamatan".

### Tanya-jawab cepat

| # | Pertanyaan | Jawaban singkat | Bukti |
|---|---|---|---|
| Q1 | Angka CO dari mana? | Hambatan sensor dikonversi lewat kurva datasheet (A = 3,46, beta = 0,84). Estimasi, belum gas asli | 4.3, digitalisasi kurva |
| Q2 | Kenapa 2500 dan 4000 ppm? | 2500 peringatan lembut (bukti kognitif lemah); 4000 = batas kerja 5000 dikurangi margin sensor ±250 ppm dan jeda sensor. Pilihan rancangan, bukan standar medis | [peringatan-dan-ambang.md](../keputusan/peringatan-dan-ambang.md) |
| Q3 | Kenapa SMA 6? | Goyangan 0,5 Hz ±95% dari noise; rata-rata genap menghapusnya; 6 detik responsif | 7.1 |
| Q4 | Kenapa pemanasan 180 detik? | MH-Z19C angka palsu sampai detik 128 pada nyala dingin; MiCS stabil ±3 menit | 4.9 |
| Q5 | Kenapa uji arah 30 detik dan 25%? | 25% tak pernah terlampaui tanpa gas dalam 28.000 detik. 30 detik pilihan sementara | 7.3 |
| Q6 | Kenapa ada transistor dan dioda? | GPIO tak kuat menarik koil; dioda meredam lonjakan koil | 3.3 |
| Q7 | Kenapa GND harus satu? | Sinyal 3,3 V butuh acuan yang sama dengan transistor | 3.2 |
| Q8 | Kalau internet mati? | Alarm, LCD, jendela jalan sendiri; data saat putus tidak disimpan (keputusan). Terbukti 4 episode di uji 8 | 5.5 |
| Q9 | Bagaimana data tidak bisa dipalsukan? | TLS + HMAC + nonce + daftar perangkat + ACK bertanda tangan; batas: tidak menjamin sensor benar | 5.4 |
| Q10 | Kenapa tidak simpan data offline? | Antrean flash tidak terkejar (±200 item, 27 detik per item); fitur setengah jadi dibuang | 5.5 |
| Q11 | Buktinya data sampai database? | 431 ACK untuk ±431 kiriman, tunda median 1,45 s (uji 7) | 7.5 |
| Q12 | Jendelanya benar-benar bergerak? | Belum terbukti. Terbukti: sinyal GPIO 1,5 s dan 5 s serta driver relay di meja. Uji mobil: jendela dibuka manual sesuai perintah LCD | P2-c |
| Q13 | Kalau sensor rusak? | Sensor sehat tetap jalan; dua-duanya gagal: "SENSOR GANGGUAN" tanpa aksi otomatis | 4.2 |
| Q14 | Beda jalur CO dan CO2 untuk jendela? | Sama-sama turun lalu naik lewat relay (v2.5). CO2: turun 1,5 s saat ≥ 4000. CO: turun 10 s untuk **uji arah**; bila sumber luar atau CO selesai, naik 5 s. Keduanya didahului bip 0,5 s dan jeda 3 s. Batas: v2.5 belum diuji di mobil; batas total turun 10 s per nyala (P2-g) | 4.5, 4.6 |
| Q15 | Kenapa tidak ada anti-jepit? | Tidak ada sensor jepit. Yang ada hanya peringatan: bip 0,5 s dan jeda 3 s sebelum naik (v2.5, usulan, belum diuji). Ditulis sebagai batasan | [keputusan.md](../keputusan/keputusan.md) |
| Q16 | Kenapa 3 level, bukan lebih? | Normal, waspada, bahaya cukup untuk tindakan berbeda: bunyi pendek lalu panjang + jendela | 4.9 |
| Q17 | Kenapa tabel `status` turunan? | Agar tidak melanggar 3NF dan tidak bisa tidak konsisten | 6.2 |
| Q18 | Apa beda model C-251 dengan hasil? | Produksi CO2 nyata ±54% dari model; model konservatif; N jendela terbuka lebih besar dari model | 7.4 |
| Q19 | Apa yang belum dikerjakan? | Kalibrasi CO gas asli, kompensasi suhu/kelembapan, uji formal di kendaraan, anti-jepit, sensor posisi jendela | [batasan-sistem.md](../keputusan/batasan-sistem.md) |
| Q20 | Akurasi CO2? | ±(50 ppm + 5%) menurut manual Winsen, ±250 ppm di 4000 ppm | 4.9 |

---

## 10. Dokumen yang sudah tidak sesuai kode (bahan pembersihan, **belum diubah**)

| Berkas | Yang usang |
|---|---|
| [dokumentasi/README.md](../README.md) | menulis firmware v1.8, expo 30 Okt, v2.0 |
| [komunikasi.md](../keputusan/komunikasi.md) | pesan versi 3, offline-first flash, dua tugas inti 0/1, "Saya Tahu", GPIO14, jalur versi 2 |
| [data-dan-database.md](../keputusan/data-dan-database.md) | rencana tabel lama (sudah digantikan [rancangan-database-mvp.md](../keputusan/rancangan-database-mvp.md)) |
| [algoritma-firmware.md](../keputusan/algoritma-firmware.md) bagian 5/5.1 | "tidak ada relay naik" |
| [hardware-wiring.md](../keputusan/hardware-wiring.md) bagian 5 | butir 1 (relay naik lewat GPIO26) **sudah teratasi di v2.3**; butir 2 (tombol GPIO14) masih benar |
| [parameter-dan-sumber.md](../keputusan/parameter-dan-sumber.md) | nilai kode lama (EMA 0,2, pemanasan 300 detik, ABC aktif, CO 35/25) |
| [banner-hasil-uji-dan-kpi.md](../analisis/banner-hasil-uji-dan-kpi.md) | "CO tidak dipakai di MVP" (CO sekarang aktif) dan skema hanya GPIO26 |
| [firmware-v2/README.md](../../firmware-v2/README.md) | topik `aeros/data`, string HMAC `device_id|timestamp|nonce|co_ppm|co2_ppm`, `worker_example`, `secrets.h.example` |
| Komentar kepala `sensorOriginal.inl` baris 1-40 | "Komunikasi BELUM ada", wiring tanpa GPIO25, perintah `p`/`o` lama |
| Komentar `main.cpp` baris 34-43 | "sketch asli memakai GPIO25" (sekarang relay naik), variabel `*_dummy` tak terpakai |

---

## 11. Urutan slide yang disarankan

1. Masalah dan tujuan (kabin tertutup, CO2 naik 200+ ppm/menit)
2. Gambaran sistem (bagian 2)
3. Skematik dan pin (3.1, gambar KiCad)
4. Catu daya dan driver relay (3.2, 3.3)
5. Arsitektur firmware dan siklus 1 detik (4.1, 4.2)
6. Dari tegangan ke ppm CO: rumus dan contoh angka (4.3)
7. Aturan CO2 dan CO (4.4, 4.5)
8. Siklus jendela dan peringatan sebelum naik (4.6)
9. Parameter dan sumbernya (4.9)
10. Alur komunikasi dan keamanan (4.11, 5.2, 5.4)
11. Worker dan database (6.1, 6.2)
12. Cara menganalisis: filter, kalibrasi, model (bagian 7)
13. Hasil uji dan KPI (7.5)
14. Batasan jujur dan rencana (bagian 9, kalimat aman)
15. Cadangan: tabel Q&A (bagian 9)

## 12. Daftar periksa sebelum expo

- [ ] Putuskan `MODE_PENGEMBANGAN` (meja = `true`, mobil = `false`) dan tulis di slide.
- [ ] Gambar ulang skematik dan perfboard dengan relay naik GPIO18 (P1-e); pastikan kabel di alat sama.
- [ ] Uji v2.5 di alat: bip 0,5 s, jeda 3 s, lalu relay naik 5 s; coba perintah `x` saat jeda.
- [ ] Putuskan batas total waktu turun 10 s untuk jalur CO (P2-g).
- [ ] Upload firmware baru, uji tombol Wi-Fi GPIO32 (tahan 5 detik), lalu simpan Wi-Fi expo (P1-a).
- [x] SQL 4a berlaku dan `node cek-database.js` semua OK (4 Nov).
- [ ] Satu uji ujung ke ujung dengan ESP menyala: pastikan baris baru masuk dan `device_state` online (data terakhir 4 Nov 12:05 WIB, perangkat sedang offline).
- [ ] Tanyakan ke teman backend: kapan SQL 4b dijalankan dan kapan `WRITE_STATUS_COLUMN=false` dipasang (P1-d).
- [ ] Pemanasan 3 menit sebelum penonton datang; rekaman video dan log CSV sebagai cadangan.
- [ ] Hotspot 2,4 GHz tersedia.
