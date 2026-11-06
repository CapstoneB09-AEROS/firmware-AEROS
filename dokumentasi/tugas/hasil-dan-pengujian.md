# Hasil dan Pengujian (bahan bab 5 x-banner)

Disusun 5 November 2026. Dua bagian: (1) tabel target dan capaian beserta analisis yang belum tercapai, (2) preview perbandingan 5 uji mobil. Angka tidak ditulis ulang di sini bila sudah ada di berkas sumber; tautan di tiap bagian.

Penanda: ✔ terpenuhi dan terbukti dari data · ◐ terpenuhi sebagian · ✖ belum terbukti atau belum diukur.

---

## 1. Target dan capaian

Nomor, spesifikasi, dan target sama dengan **Tabel 6.2 Spesifikasi Luaran C-251**. Capaian dari log uji mobil ([data/uji-mobil-5-terakhir/](../analisis/data/uji-mobil-5-terakhir/)), laporan [uji 7](../pengujian/laporan/uji-7-mobil-civic-firmware-v2-2026-10-30.md), dan [uji 8](../pengujian/laporan/uji-8-meja-wifi-mqtt-firmware-v2.3-2026-11-03.md).

| No | Spesifikasi | Target | Capaian | Status |
|---|---|---|---|---|
| 1 | Deteksi CO2 | 4 dari 5 uji (> 2.500 ppm) | **4 dari 5** uji menyalakan WASPADA; uji ke-5 (Avanza 26 Okt, v0) tanpa alarm | Tercapai |
| 2 | Deteksi CO | 4 dari 5 uji (> 35 ppm) | **0 dari 5.** Tidak ada sumber CO nyata; estimasi tertinggi 27 ppm | Belum |
| 3 | Waktu respons buzzer | ≤ 5 detik | **1,3 detik** | Tercapai |
| 4 | Waktu respons aktuator | ≤ 10 detik | sinyal **1,3 detik**; gerak jendela belum diukur | Sebagian |
| 5 | Keberhasilan pembukaan panel | 4 dari 5 uji (hanya saat CO2 > ambang) | **4 dari 5** uji benar: sinyal turun di **9 dari 9** episode bahaya, **0** sinyal salah | Tercapai (sinyal) |
| 6 | Keberhasilan penutupan panel | 4 dari 5 uji (CO tinggi, atau aman stabil 60 detik) | sinyal naik **9 dari 9** episode (3 uji); syarat 60 detik dan penutupan karena CO belum terpenuhi | Sebagian |
| 7 | Waktu tampil data di aplikasi | ≤ 20 detik | ke database **1,45 detik** (median); ke ponsel belum diukur | Sebagian |
| 8 | Anggaran perangkat keras | ≤ Rp2.000.000 | belum dihitung ulang setelah komponen berganti | Belum |

Cara hitung baris 5 dan 6 (dari kolom status dan status relay di log): episode bahaya (status CO2 masuk BAHAYA) Civic 30 Okt 1, Ayla 5, Avanza 4 Nov 3, Civic 4 Nov 0; pulsa turun (GPIO26) 1, 5, 3, 0; pulsa naik (GPIO25) 1, 5, 3, 0. Pulsa turun atau naik saat status WASPADA atau OK: 0.

Catatan baca:
- Spesifikasi awal menyebut kotak akrilik; hasil di atas dari kabin mobil dengan 4 orang.
- Spesifikasi C-251 menyebut panel terbuka saat CO2 > 2.500; firmware menurunkan jendela saat **bahaya (≥ 4.000)**, di 2.500 hanya bunyi.
- Jendela di uji mobil dibuka dan ditutup **manual**. Yang terbukti adalah sinyal GPIO, bukan jendela bergerak.
- Spesifikasi penutupan: CO2 < 2.400 dan CO < 30 ppm stabil 60 detik; firmware: CO2 < 2.500 ppm selama 10 detik (jalur CO2).

## 1b. Analisis target yang belum tercapai

**Deteksi CO (no 2), 0 dari 5, paling penting.**
1. **Tidak ada sumber CO yang aman.** Tim tidak punya gas acuan atau instrumen referensi, dan [perbandingan-c251.md](../analisis/perbandingan-c251.md) (T16) menetapkan jangan membuat CO sendiri tanpa protokol keselamatan. Spesifikasi awal (injeksi CO di kotak akrilik) tidak bisa dipenuhi dengan cara itu.
2. **Di mobil nyata CO tidak naik cukup tinggi.** Estimasi tertinggi 27 ppm (Civic 4 Nov), tidak pernah 35 ppm. Jadi alarm CO dan uji arah (sumber dalam atau luar) belum pernah dipicu di mobil.
3. **Kenapa nilai CO hanya estimasi (asal R0 dan ppm).**
   - MiCS-5524 tidak mengeluarkan ppm. Gas CO mengubah **hambatan sensor (Rs)**; ESP32 mengukur tegangannya lewat ADS1115, lalu menghitung Rs.
   - **R0 adalah Rs saat udara bersih**, dipakai sebagai titik nol. Alat mengukurnya sendiri: udara dibaca 120 detik lewat perintah kalibrasi, lalu disimpan (nilai bawaan 1.730 kΩ; hasil kalibrasi di Ayla 1.878 kΩ).
   - **ppm = dari Rs/R0** memakai kurva datasheet (Rs/R0 = 3,46 × ppm^−0,84, hasil digitalisasi grafik, untuk 25 °C dan 50% RH).
   - Maka ada empat sumber ketidakpastian. (a) R0 tergantung udara saat kalibrasi; di mobil "udara bersih" tidak terjamin, dan Rs mudah bergeser (Avanza yang sama: 925 kΩ pada 26 Okt, 2.021 kΩ pada 4 Nov). (b) R0 dari Ayla dipakai di Civic tanpa kalibrasi ulang. (c) Kurva datasheet bukan kondisi mobil (suhu, kelembapan). (d) Sensor tidak selektif: parfum menurunkan Rs 92% dalam 13 detik (terbaca 72-83 ppm), dan belum pernah dicek dengan gas CO asli.
   - Kalau R0 meleset, **semua** ppm ikut meleset, karena ppm dihitung dari Rs/R0. Karena itu ditulis **estimasi**.
4. **Yang sudah terbukti:** logika CO berjalan di firmware dan tidak ada alarm CO palsu dalam ±9.700 bacaan (3 uji, sekitar 2,7 jam). Ini bukti ketahanan terhadap alarm palsu, **bukan** bukti deteksi.
5. **Langkah berikut (saran):** uji dengan gas CO acuan atau pembanding detektor CO terkalibrasi; kalibrasi R0 di udara bersih tiap uji; pertimbangkan sensor CO yang lebih selektif bila anggaran dan waktu ada. Sampai itu terjadi, tulis CO sebagai estimasi.

**Aktuator dan penutupan (no 4, 6), sebagian.** Sinyal GPIO terbukti 9 dari 9, gerak fisik jendela belum diukur karena relay belum terpasang ke motor jendela. Syarat penutupan di firmware lebih longgar (10 detik, 2.500 ppm) dari spesifikasi (60 detik, 2.400 ppm); penutupan karena CO belum pernah diuji. Langkah: pasang relay ke motor jendela dan ukur dari sinyal sampai gerak.

**Tampil di aplikasi (no 7), sebagian.** Sampai database terukur, sampai layar ponsel belum. Langkah: ukur dengan jam ponsel dari bunyi alarm sampai tampil di aplikasi.

**Anggaran (no 8), belum.** Komponen sudah berganti, total belum dihitung ulang. Langkah: hitung dari daftar komponen dan harga beli.

---

## 2. Preview perbandingan 5 uji mobil (4 orang, jendela tertutup)

Sumber lengkap: [perbandingan-mobil-2026-11-04.md](../analisis/perbandingan-mobil-2026-11-04.md) dan [hasil-bandingkan-mobil-2026-11-04.txt](../analisis/hasil/hasil-bandingkan-mobil-2026-11-04.txt). Semua angka dihitung ulang dengan satu cara dari log.

### Uji yang dibandingkan

| # | Mobil dan tanggal | Firmware | Durasi | Status tertinggi |
|---|---|---|---|---|
| 1 | Avanza, 26 Okt | v0 | 28 menit | tidak ada alarm |
| 2 | Civic EG6 1994, 30 Okt | v2.0 | 36 menit | BAHAYA |
| 3 | Ayla 2023, 4 Nov sore | v2.4 + casing 3D | 76 menit | BAHAYA |
| 4 | Avanza, 4 Nov malam | v2.4 + casing 3D | 63 menit | BAHAYA |
| 5 | Civic EG6 1994, 4 Nov malam | v2.4 + casing 3D | 45 menit | WASPADA saja |

### CO2 dan CO dengan kolom yang sama (5 percobaan)

Satuan ppm. Waspada CO2 ≥ 2.500, bahaya ≥ 4.000. Waspada CO ≥ 35, bahaya ≥ 87. CO adalah **estimasi**.

**CO2**

| Mobil | Median | Maks | % waktu ≥ waspada | % waktu ≥ bahaya | Status tertinggi |
|---|---|---|---|---|---|
| Avanza 26 Okt | 3.023 | 4.453 | 71% | 11% | tanpa alarm (v0) |
| Civic 30 Okt | 2.769 | 4.025 | 64% | < 1% | BAHAYA |
| Ayla 4 Nov | 2.864 | 4.410 | 61% | 6% | BAHAYA |
| Avanza 4 Nov | 2.746 | 4.064 | 58% | 2% | BAHAYA |
| **Civic 4 Nov** | **3.363** | **3.725** | **88%** | **0%** | **WASPADA** |

**CO estimasi**

| Mobil | Median | Maks | % waktu ≥ waspada | % waktu ≥ bahaya | Status tertinggi |
|---|---|---|---|---|---|
| Avanza 26 Okt | 0 | 11* | 0% | 0% | tanpa alarm (v0) |
| Civic 30 Okt | – | – | – | – | CO belum aktif |
| Ayla 4 Nov | 0 | 17 | 0% | 0% | aman |
| Avanza 4 Nov | 0 | 0 | 0% | 0% | aman |
| **Civic 4 Nov** | **12** | **27** | **0%** | **0%** | **aman** |

\* Avanza 26 Okt memakai firmware v0 dengan R0 berbeda (1.730 kΩ lawan 1.878 kΩ), jadi hanya sebagai referensi, tidak sebanding dengan tiga uji 4 Nov. Civic 30 Okt (v2.0): sensor CO belum diaktifkan. Waktu CO estimasi ≥ 10 ppm di uji 4 Nov: Civic **68%**, Ayla 16%, Avanza 0% (tidak sejajar dengan CO2, jadi tidak masuk tabel).

### CO2 naik dan turun, lima uji (untuk PPT)

| Uji | Laju naik 2.500–3.000 ppm (ppm/menit) | Dari 2.500 ke 4.000 ppm | Turun setelah jendela dibuka |
|---|---|---|---|
| Avanza 26 Okt | 205 | 7,4 menit | 97 detik |
| Civic 30 Okt | 110 | 15,2 menit | 67 detik |
| Ayla 4 Nov | 184 | 8,6–9,5 menit (4 siklus) | 58–74 detik |
| Avanza 4 Nov | 156 | 9,9–11,5 menit (3 siklus) | 65–67 detik |
| **Civic 4 Nov** | 101 | **tidak tercapai** (maks 3.725 ppm, > 40 menit di atas 2.500) | tidak ada pembukaan |

### Temuan utama

1. **Kabin tertutup dengan 4 orang melewati 2.500 ppm lalu 4.000 ppm dalam sekitar 7–11 menit** di Avanza dan Ayla. Laju naik 2.000–3.000 ppm sekitar 155–200 ppm/menit. ✔ terukur
2. **Civic berbeda.** CO2 naik cepat sampai sekitar 3.000, lalu melambat dan mendatar di **3.500–3.700 ppm** (pola sama di 30 Okt dan 4 Nov). Dugaan: kabin tidak kedap, jadi produksi CO2 penumpang seimbang dengan kebocoran. ✔ pola terukur · ✖ penyebab belum dibuktikan
3. **Ambang bahaya 4.000 ppm tidak pernah tercapai di Civic 4 Nov**, padahal CO2 bertahan di atas 2.500 ppm lebih dari 40 menit. Sistem hanya berada di WASPADA dan jendela tidak turun. Ini batasan ambang tetap pada mobil yang tidak kedap. ✔ terukur
4. **Sensor CO (MiCS) di Civic membaca rendah** (Rs/R0 median 0,43, lawan 0,78 di Ayla dan 1,08 di Avanza), dengan estimasi 12 ppm (maks 27). Penyebabnya belum bisa dipisahkan: gas masuk kabin, sensor masih menstabil, atau uap lain. **Jangan ditulis sebagai CO terukur.** ✖ dugaan
5. **Bip sebelum jendela naik (v2.5) belum pernah muncul** di log mana pun. ✖ belum teruji

### Keterbatasan (tulis di PPT, bukan di banner)
- Satu uji per mobil per hari; posisi alat, kecepatan, dan AC tidak dicatat sama.
- Jendela dibuka dan ditutup manual, jam tidak tercatat di log, jadi laju turun tidak bisa dibandingkan teliti.
- Firmware beda antar uji; hanya tiga uji terakhir memakai casing 3D.
- Alat mulai ulang dua kali di Civic 4 Nov (20:23 dan 20:52); penyebab belum diketahui.
- Dokumen lain menulis Civic 30 Okt memakai v2.1; perbandingan dan README log menulis v2.0. Tabel di atas mengikuti README log.

### Naskah penjelasan lisan (± 1 menit)

"Kami menguji AEROS lima kali di tiga mobil, yaitu Avanza, Civic, dan Ayla, dari 26 Oktober sampai 4 November. Setiap uji berisi empat orang, jendela tertutup, mobil berjalan di jalan kota dengan kecepatan sekitar 20 sampai 60 kilometer per jam. Pada CO2, kadar melewati batas waspada 2.500 ppm di kelima uji, dan melewati batas bahaya 4.000 ppm di empat uji. Dari 2.500 ke 4.000 ppm butuh sekitar 7 sampai 15 menit, dan setelah jendela dibuka, kadar turun di bawah 2.500 ppm dalam sekitar 1 sampai 1,5 menit. Satu uji berbeda, yaitu Civic 4 November: CO2 tidak pernah mencapai 4.000 ppm, mendatar di sekitar 3.500 sampai 3.700, jadi kabin ini kemungkinan tidak kedap, dan ambang tetap kami tidak membuat jendela turun. Pada CO, nilainya tidak pernah melewati 35 ppm di uji mana pun. Civic mencatat estimasi tertinggi, 27 ppm, tetapi ini estimasi dari sensor semikonduktor yang belum diuji dengan gas CO asli, jadi kami belum bisa menyebutnya sebagai CO yang terukur."

Yang perlu dicek sebelum dibacakan: kecepatan 20-60 km/jam (lihat catatan di [isi-x-banner.md](isi-x-banner.md), bagian Cek sebelum cetak) dan kalimat "kemungkinan tidak kedap" yang masih dugaan.
