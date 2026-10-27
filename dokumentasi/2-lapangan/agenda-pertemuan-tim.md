# Agenda Pertemuan Tim: Hardware, Backend Komunikasi, dan Software

Dikumpulkan dari seluruh pekerjaan 25 Oktober 2026. Centang saat selesai. Tanda **[P1]** berarti sebaiknya dibicarakan lebih dulu (menghalangi pekerjaan lain atau menyangkut keselamatan).

Cara memakai: bawa laptop dengan folder `dokumentasi/` dan `logs/`. Setiap butir menyebut file asalnya.

## Skenario pertemuan (ringkas)

Wi-Fi tersambung tapi diam berbeda dengan Wi-Fi mengirim data (arus naik tajam sesaat saat kirim), jadi diuji terpisah.

1. **Buka (5 menit).** Tujuan: ESP final, uji dasar, keputusan Wi-Fi, jadwal sampai 29 Okt siang.
2. **Persiapan (10 menit).** Ganti ESP. Ukur 5V di pin sensor dan catat. Perbarui `VCC` di kode bila beda dari 4,64 V. Catat pinout PCB.
3. **Tahap A (30 menit): ESP baru, firmware lama, Wi-Fi mati.** Sambil jalan bahas **hardware**: pinout PCB, penggerak jendela (relay, arus, anti-jepit), waktu buka dan tutup jendela, tegangan ke ADS1115.
4. **Tahap B1 (15 menit): Wi-Fi tersambung, belum kirim.** Ukur 5V dan lihat noise.
5. **Tahap B2 (15 menit): kirim telemetri tiap 5 detik (kode tim).** Ukur 5V lagi. Sambil jalan bahas **backend**: format pesan, `sim_mode`, retensi, perubahan database.
6. **Bandingkan A, B1, B2 (10 menit).** 5V minimum dan maksimum, goyangan Rs, periode siklus 7 menit, ada tidaknya mulai ulang. Putuskan apakah catu sensor dipisah.
7. **Software (10 menit).** CO sebagai estimasi, pesan "kemungkinan CO atau gas lain", perangkat offline tidak tampil "aman".
8. **Wi-Fi di pseudocode (10 menit).** Periksa [pseudocode-baru.md](../1-utama/pseudocode-baru.md) bagian 2.8. Putuskan panjang antrean dan sumber jam. Perubahan ditulis setelah rapat.
9. **Jadwal dan tugas (10 menit).** Siapa memegang ESP dan sensor jam berapa untuk 4 sesi sensor. Siapa mengerjakan apa. Firmware dibekukan 29 Okt siang.
10. **Tutup.** Daftar keputusan, penanggung jawab, tenggat.

Rincian tiap butir ada di bagian 0–5 di bawah.

---

## 0. Keputusan bersama (semua orang)

- [ ] **[P1]** Satu ESP32 final untuk demo. ESP yang dipakai firmware punya modul Wi-Fi rusak, ESP tim software punya Wi-Fi. Pilih satu, lalu pindahkan kode sensor dan MQTT ke sana. Setelah ganti, ulangi uji kamar dengan Wi-Fi menyala (T22): ukur 5V di pin MiCS, perbarui `VCC` di kode, bandingkan noise dan siklus Rs dengan ESP lama.
- [ ] **[P1]** Cara menguji deteksi CO tanpa sumber CO (T16). C-251 menjanjikan "deteksi CO 4 dari 5 uji dengan sumber uji terkonsentrasi". Pilihan: ubah spesifikasi, uji dengan gas pereduksi pengganti (butana dari korek, **bukan CO**), mode simulasi berlabel, atau cari akses lab. Jangan membuat CO sendiri.
- [ ] Pertentangan isi C-251 (jumlah status, ambang CO2 di Bab 11, bukaan servo, bunyi buzzer, dan lain-lain; **cek di PDF**) dicatat sebagai bahan **C-501**. **C-251 tidak direvisi.** Rinciannya ada di [perbandingan-c251.md](../3-bukti/perbandingan-c251.md).
- [ ] Aturan alarm yang sudah disepakati (desain-peringatan.md E1): CO2 ≥ 2500 bunyi singkat dan peringatan di aplikasi, CO2 ≥ 4000 bunyi dan buka jendela, CO ≥ 35 bunyi dan buka jendela sebagai uji arah (CO naik lagi berarti sumber luar, jendela ditutup sampai CO turun), CO menang atas CO2, saran AC ditunda. **Konfirmasi ulang dengan tim dan dosen.**
- [ ] Nama dan warna status yang dipakai di seluruh sistem (firmware, LED, aplikasi).
- [ ] Lokasi sensor di kabin (T18). C-251 menyebut "konsol bawah dashboard karena CO2 lebih berat", yang bertentangan dengan asumsi model well-mixed.
- [ ] Daftar komponen dan anggaran terbaru (T20): MiCS-5524, ADS1115, LCD I2C menggantikan MQ-7. Batas Rp2.000.000 dan komponen tunggal Rp500.000.
- [ ] Siapa menulis apa untuk C-501 dari artefak uji.

---

## 1. Teman hardware

### 1.1 Keselamatan dan kerusakan perangkat
- [ ] **[P1]** **Tegangan MiCS ke ADS1115 melewati batas.** Pada log awal `V_mV` mencapai 3681 mV, sedangkan ADS1115 di 3,3 V punya batas mutlak input sekitar VDD + 0,3 V = 3,6 V (datasheet TI, [daftar-pustaka.md](../3-bukti/daftar-pustaka.md) [3], perlu dibaca langsung). Minta pembatas atau pembagi tegangan di jalur keluaran MiCS ke ADS1115.
- [ ] **[P1]** **Konektor USB longgar.** macOS mencatat perangkat CP2102 terlepas dan tersambung lagi pada 11:53:17 dan 11:53:34 (masing-masing sekitar 1 detik). Minta kabel atau konektor diperbaiki atau diganti.
- [ ] **[P1]** **MH-Z19C sempat mati sendiri** (log awal: CO2 `n/a` lalu kembali 410 dan 500, sekitar `t_s` 115). Cek catu daya dan sambungan. Manual Winsen: catu 4,5–5,5 V (tabel: 5,0 ±0,1 V) dan arus tidak kurang dari 150 mA.
- [ ] Rencana catu daya mobil: adaptor 12 V ke 5 V (kualitas, noise, penurunan saat mesin dinyalakan). Prototipe sekarang memakai USB laptop.

### 1.2 Pengukuran yang diminta (tidak merusak rangkaian)
- [ ] Ukur tegangan 5 V **di pin catu MiCS** dan **di pin Vin MH-Z19C**, dengan multimeter yang bisa mencatat nilai minimum dan maksimum, atau osiloskop. Tujuan: apakah ada goyangan tegangan dengan periode sekitar 2 detik.
- [ ] Ukur tegangan pemanas MiCS. Firmware memakai `VCC = 4.64` V (hasil ukur sebelumnya). Datasheet SGX meminta catu 4,9–5,1 V dan pemanas tipikal 2,4 V. Tanyakan apakah resistor seri pemanas ada di modul.
- [ ] Konfirmasi nilai resistor beban (firmware: 9970 Ω, minimal datasheet 820 Ω).

### 1.3 Konteks temuan untuk dijelaskan
- [ ] Hampir 95% goyangan Rs MiCS adalah pola bergantian tiap detik, proporsional terhadap sinyal, periode sumber sekitar 1,9954 atau 2,0047 detik, stabil 4 jam. Dugaan: catu pemanas ikut naik-turun karena beban berdenyut. **Belum terbukti.** Ringkasan: [analisis/ringkasan-temuan-2026-10-25.md](../analisis/ringkasan-temuan-2026-10-25.md).
- [ ] Rs naik-turun teratur dengan periode **7,01 menit (±13–17%)** pada udara bersih, muncul di dua hari berbeda, tidak hilang saat kipas dimatikan, mengecil saat AC menyala. Tidak dijelaskan di datasheet. Tanyakan apakah catu 5V atau ground ikut berayun dengan periode itu (ukur 15 menit). Rincian: [skenario-uji-mobil.md](skenario-uji-mobil.md) bagian 2.
- [ ] Rs bergeser lebih dari 50% dalam 4 jam di kamar (2045 ke sekitar 900–1000 kΩ). Penyebab belum diketahui. Tanyakan apakah ada sumber panas atau perubahan suhu pada modul.

### 1.4 Aktuator dan jendela
- [ ] **[P1]** Cara mengendalikan power window Daihatsu Classy (relay di jalur tombol, driver, tegangan 12 V, arus maksimum, sekring, isolasi dari ESP32).
- [ ] **[P1]** Risiko jari atau tubuh terjepit saat jendela menutup otomatis. Cek apakah anti-jepit aktif pada penutupan yang dikendalikan relay.
- [ ] Bukaan sebagian: power window biasa hanya naik dan turun selama tombol ditekan. Bukaan sebagian harus berbasis waktu jalan motor. Minta pengukuran waktu buka penuh dan tutup penuh tiap mobil (Classy, Civic), dan apakah ada umpan balik posisi.
- [ ] Jeda minimum antar gerakan jendela (batas dari motor).

### 1.5 Prototipe dan perakitan
- [ ] Breadboard ke PCB: kualitas kontak, kapasitor di dekat sensor dan ESP32, grounding.
- [ ] Housing: slot ventilasi ke sensor, jauh dari panas dan sinar matahari langsung (manual MH-Z19C), tahan debu.
- [ ] Pin yang dipakai: SDA 21, SCL 22, buzzer 25, UART2 RX 16 dan TX 17. LCD 0x27, ADS1115 0x48. Cocokkan dengan ESP final.
- [ ] Sumber daya siaga: apa yang terjadi saat daya putus (semua sensor mulai dari awal).

### 1.6 Keselamatan uji
- [ ] Uji gas pengganti (korek tanpa api): sedikit, singkat, ruang berventilasi, tanpa api atau percikan, bukan di kabin mobil. Jangan menyalakan perangkat di area pompa SPBU.

---

## 2. Teman backend komunikasi (MQTT dan database)

Konteks: firmware sekarang hanya mencetak ke serial (115200). Belum ada Wi-Fi atau MQTT di kode sensor. Perkiraan ukuran data ada di [desain-data-dfd.md](../3-bukti/desain-data-dfd.md) (asumsi, belum diukur).

### 2.1 Kontrak data (agar bisa jalan paralel)
- [ ] **[P1]** Sepakati satu format pesan. Usulan isi: `device_id`, `ts`, `rs_kohm`, `co_ppm_est`, `co2_ppm`, `status_co`, `status_co2`, `alarm`, `window_cmd` atau `window_state`, `fw_version`, `sim_mode`.
- [ ] **[P1]** Penanda **`sim_mode`**: data dari mode simulasi harus berlabel jelas agar tidak tercampur dengan data nyata, juga di aplikasi.
- [ ] Laju kirim: telemetri tiap 5 detik (rata-rata dan maksimum per interval), pesan langsung saat status berubah. Keputusan alarm tetap di ESP32 tiap sekitar 1 detik dan **tidak bergantung internet**.
- [ ] Nama topik, kualitas layanan (QoS), pesan "last will" (perangkat offline), dan pesan status yang di-retain.
- [ ] **Sinkronisasi waktu**: ESP32 tidak punya jam nyata. Pakai NTP lewat Wi-Fi atau cap waktu server saat diterima. Putuskan satu.
- [ ] Jalur perintah dari aplikasi ke perangkat (tombol "Saya Tahu" mematikan buzzer). Keamanan: autentikasi, TLS bila bisa, kredensial **jangan ditulis di kode yang masuk repositori**.

### 2.2 Database dan retensi
- [ ] **[P1]** Pilih retensi (desain-data-dfd.md bagian 4): hapus semua lebih dari 7 hari, atau simpan data 5 detik 7 hari lalu ringkas jadi rata-rata dan maksimum 1 menit, atau simpan semua. Usulan: data 5 detik 7 hari, `alert_logs` dan `actuator_logs` disimpan lama.
- [ ] Tugas terjadwal menghapus atau meringkas data lama.
- [ ] Batas ukuran paket Supabase (belum diverifikasi, perlu dicek).
- [ ] **[P1]** Kontrak data minimal (7 butir) dan masalah skema yang ditemukan, terutama `ON DELETE CASCADE` yang menghapus catatan peringatan saat telemetri 7 hari dibersihkan: [rancangan-data.md](../1-utama/rancangan-data.md) bagian 4.1 dan 4.3, pertanyaan di 4.6.
- [ ] Data uji untuk laporan disimpan **terpisah sebagai CSV**, bukan hanya di database.

### 2.3 Keandalan dan pengujian
- [ ] Perilaku saat Wi-Fi atau hotspot putus (buffer atau dibuang, batas memori ESP32).
- [ ] Pustaka MQTT yang dipakai, dan ukuran memori yang tersisa di ESP32.
- [ ] Target latensi "data tampil di aplikasi ≤ N detik" (spesifikasi C-251): tentukan N, lalu cara mengukurnya (cap waktu di perangkat vs waktu muncul di aplikasi).
- [ ] Uji dengan penerbit data palsu, termasuk dua skenario simulasi (sumber CO dari dalam: CO turun saat jendela dibuka, sumber dari luar: CO naik).
- [ ] Hotspot ponsel: perkiraan kuota data per hari (perkiraan: sekitar 3,5 MB per hari pada 5 detik, 17 MB pada 1 detik, asumsi 200 byte per pesan).

### 2.4 Untuk DFD
- [ ] Tambah proses di ESP32 "Agregasi 5 detik dan deteksi kejadian", keterangan retensi pada penyimpanan sensor, proses terjadwal "Hapus atau ringkas data lama", dan penyimpanan CSV uji di luar jalur sistem. Ganti MQ-7 dan MH-Z19B menjadi MiCS-5524 dengan ADS1115 dan MH-Z19C.

---

## 3. Teman software (aplikasi)

### 3.1 Cara menampilkan data dengan jujur
- [ ] **[P1]** Nilai CO ditampilkan sebagai **estimasi indikatif**, bukan angka akurat (belum dikalibrasi dengan referensi, tanpa kompensasi suhu dan kelembapan). Kalimat contoh di [batasan-sistem.md](../3-bukti/batasan-sistem.md).
- [ ] **[P1]** Pesan peringatan CO: "kemungkinan CO atau gas lain" (sensor tidak selektif), bukan "CO terdeteksi".
- [ ] Label **"simulasi"** yang jelas pada data dari mode simulasi.
- [ ] **Perangkat offline tidak boleh tampil sebagai "aman".** Jika tidak ada data lebih dari batas waktu (usulan 15 detik, perlu diputuskan), tampilkan "perangkat tidak terhubung".

### 3.2 Aturan peringatan di aplikasi
- [ ] CO2 ≥ 2500: peringatan di aplikasi (bersamaan dengan bunyi singkat di perangkat). CO2 ≥ 4000: bunyi dan buka jendela. CO ≥ 35: bunyi dan buka jendela (uji arah). Pola bunyi dan pesan di layar sebaiknya dibedakan antara CO dan CO2.
- [ ] Tombol "Saya Tahu": mematikan buzzer. Jangan memicu peringatan berulang untuk kejadian yang sama.
- [ ] Rancangan agar tidak mengganggu pengemudi: sedikit interaksi, teks besar, hanya yang penting yang muncul saat berkendara.

### 3.3 Riwayat dan tampilan
- [ ] Grafik riwayat dari data 5 detik (7 hari). Putuskan pemadatan titik untuk grafik panjang.
- [ ] Log kejadian: pelampauan ambang, tindakan sistem, pemulihan, dengan penanda waktu.
- [ ] Warna status sesuai keputusan di bagian 0 (hijau, kuning, merah).

### 3.4 Pengujian
- [ ] Ukur latensi dengan tim backend (bagian 2.3).
- [ ] Uji lewat mode simulasi: dua skenario sumber CO, dan CO2 naik sampai 2500 dan 4000.
- [ ] Mode demo untuk expo (data simulasi berlabel).

---

## 4. Apa yang disediakan firmware dan apa yang dibutuhkan

**Dari firmware (saya dan pemilik firmware):**
- [ ] Format serial CSV sekarang: `t_s, V_mV, Rs_kohm, Rs_per_R0, CO_ppm_est, CO2_ppm, status_CO, status_CO2`.
- [ ] Mode simulasi (dua skenario sumber CO) berlabel.
- [ ] Versi firmware dalam pesan.
- [ ] Aturan prioritas dan nilai sementara waktu tunggu (desain-peringatan.md E dan F).

**Dibutuhkan dari tim lain:**
- [ ] ESP final dan pin yang tersedia.
- [ ] Format pesan dan pustaka MQTT yang disepakati.
- [ ] Hasil pengukuran catu 5 V dari teman hardware.
- [ ] Cara mengendalikan power window (relay, waktu buka penuh) dan batas jeda antar gerakan.

---

## 5. Bahan yang dibawa ke pertemuan

| Bahan | Isi |
|---|---|
| [validasi-parameter.md](../3-bukti/validasi-parameter.md) | Parameter dan statusnya |
| [desain-peringatan.md](../3-bukti/desain-peringatan.md) | Aturan prioritas, waktu tunggu per keputusan |
| [desain-data-dfd.md](../3-bukti/desain-data-dfd.md) | Laju kirim, retensi, perubahan DFD |
| [batasan-sistem.md](../3-bukti/batasan-sistem.md) | Batasan sensor dan kalimat contoh |
| [perbandingan-c251.md](../3-bukti/perbandingan-c251.md) | Perbedaan C-251 dengan pekerjaan sekarang |
| [analisis/ringkasan-temuan-2026-10-25.md](../analisis/ringkasan-temuan-2026-10-25.md) | Temuan noise dan drift |
| [daftar-tugas.md](../1-utama/daftar-tugas.md) | Status semua tugas |
