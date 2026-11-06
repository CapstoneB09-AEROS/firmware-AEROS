# Isi X-Banner AEROS

Disusun 4 November 2026. Enam bagian: latar belakang, permasalahan, solusi, implementasi, evaluasi dan hasil, kesimpulan. Teks di bawah sengaja pendek supaya terbaca dari jarak 1-2 meter. Penjelasan lengkap tiap angka ada di [materi-ppt-expo.md](materi-ppt-expo.md). Bagian terakhir berisi hal yang **harus dicek sebelum cetak**.

Penanda: ✔ terbukti dari data kita atau sumber yang sudah dibaca · ◐ dikutip dari C-251, belum diverifikasi · ✖ belum terbukti. Sumber IEEE: [daftar-pustaka.md](../referensi/daftar-pustaka.md) [19], [27], [28].

---

## JUDUL

**AEROS: Prototipe Pemantau Kualitas Udara Kabin Kendaraan**
*Automatic Environmental Response and On-board Safety*
Sensor CO dan CO2 · Peringatan Bertingkat · Respons Jendela Otomatis · Data ke Aplikasi

(Judul resmi C-251: "Prototipe Sistem Pemantauan Kualitas Udara Kabin Kendaraan Berbasis Sensor CO dan CO2 dengan Peringatan dan Aktuasi Otomatis".)

Isi nama tim, nomor kelompok (B-09), dan dosen pembimbing di bagian kepala.

---

## 1. LATAR BELAKANG

- Pengemudi di kota besar sering terjebak macet berjam-jam. Mode AC **sirkulasi dalam** membuat udara kabin tidak berganti.
- **CO2** dari napas penumpang menumpuk, dan **CO** dari kendaraan lain bisa masuk ke kabin. Keduanya **tidak bisa dirasakan** indra.
- Studi 51 mobil ber-AC di Hong Kong: **96%** melewati 1.000 ppm CO2, **16%** melewati 5.000 ppm, rata-rata **±3.400 ppm** saat berkendara; ±73% mobil memakai sirkulasi dalam ✔ [27].
- CO2 tinggi menurunkan kemampuan mengambil keputusan (Satish dkk., 2012, 22 peserta) ✔ sumber, bukti dampaknya belum konsisten antar studi. Di kabin, ini berarti risiko kecelakaan.
- Studi Auckland: CO di kabin pernah mencapai **±170 ppm** saat mengikuti kendaraan tua yang berasap ✔ [28].
- Indonesia belum punya standar kualitas udara kabin kendaraan pribadi ◐.

## 2. PERMASALAHAN

**Pertanyaan utama:** bagaimana memantau CO dan CO2 di kabin secara real-time, memberi peringatan bertingkat, dan merespons otomatis, dengan biaya terjangkau (anggaran maksimal Rp2.000.000)?

- Penghuni **tidak merasakan** kenaikan gas → perlu peringatan dini otomatis.
- **Kabin 4 orang yang tertutup melewati 2.500 ppm dalam beberapa menit.** CO2 naik **207-268 ppm per menit** (uji Avanza dan Civic kami) ✔.
- Sensor murah **tidak selektif**: satu semprotan parfum menurunkan hambatan sensor CO sebesar 92% dalam 13 detik (terbaca seperti CO 72-83 ppm) ✔. Alarm harus peka tetapi tidak palsu.
- Sumber CO bisa **di luar** mobil. Membuka jendela di saat yang salah justru memasukkan CO.
- Peringatan **tidak boleh bergantung internet**.
- Sensor murah (semikonduktor) tanpa gas acuan → nilai CO hanya **estimasi**.

## 3. SOLUSI

*Bab ini menjawab pertanyaan utama di bab 2: **apa** yang dirancang. Cara mewujudkannya ada di bab 4.*

**AEROS: alat pemantau udara kabin yang bertindak sendiri sebelum pengemudi menyadari udara memburuk.**

**Fitur utama**
| Nama | Deskripsi | Kata kunci ikon |
|---|---|---|
| **Pantau Dini** | Membaca CO dan CO2 tiap detik, peringatan bertingkat lewat bunyi dan layar | `air quality sensor`, `gas cloud`, `alarm bell` |
| **Jendela Otomatis** | Turun saat bahaya, naik saat aman; uji arah tahu sumber CO di dalam atau luar mobil | `car window`, `window up down`, `car ventilation` |
| **Siaga Tanpa Internet** | Alarm tetap berbunyi tanpa internet; data dilaporkan ke aplikasi saat terhubung | `wifi off`, `offline mode`, `shield check` |

Alur kerja, perangkat keras, dan tampilan aplikasi ada di bab 4 Implementasi. Tabel di bawah untuk PPT dan jawaban lisan, tidak dimasukkan ke banner.

| Tantangan (bab 2) | Jawaban solusi |
|---|---|
| CO dan CO2 tidak berbau dan tidak terlihat | Sensor membaca terus tiap 1 detik; penghuni diberi tahu lewat bunyi dan layar |
| Alarm tidak boleh bergantung internet | Keputusan diambil di ESP32; internet hanya untuk melapor |
| Aktuator harus mengatur ventilasi kabin otomatis | Relay menggerakkan jendela: turun saat bahaya, naik saat udara aman lagi |
| Sumber CO bisa di luar mobil | **Uji arah** 30 detik: jendela dibuka, CO turun = sumber dalam, CO naik = sumber luar |
| Nilai CO hanya estimasi | Selalu ditandai "estimasi" |
| Anggaran maksimal Rp2.000.000 | Komponen murah (total belanja belum dihitung ulang, jangan tampilkan sebagai hasil) |

Baris "tidak ada pedoman kadar polutan kabin" belum dijawab di tabel ini: sumber ambang 2.500 dan 4.000 ppm belum saya cek ulang ke daftar pustaka. Isi bila sudah jelas.

## 4. IMPLEMENTASI

*Bab ini menunjukkan **apa yang sudah diwujudkan** dari solusi di bab 3 (firmware v2.4).*

**Satu diagram alur lengkap** · [6-implementasi-alur-gabungan.svg](diagram-banner/6-implementasi-alur-gabungan.svg)
- Bentuk diagram alur biasa (swimlane): satu warna = satu sistem (perangkat keras, firmware ESP32, cloud, aplikasi)
- Alur: sensor → ESP32 membaca dan memeriksa ambang → tentukan level → buzzer, LCD, relay jendela; paket data → HiveMQ → Worker → Supabase → aplikasi
- Dua angka terukur di dalamnya: 1,3 detik (ambang → bunyi dan sinyal jendela) dan 1,45 detik (tunda simpan ke database)
- Diagram 2, 3, 4, 5 tidak dipakai di banner; isinya sudah tergabung. Untuk PPT bila ditanya detail

**Perangkat keras** · diagram: [2-implementasi-perangkat-keras.svg](diagram-banner/2-implementasi-perangkat-keras.svg) · tambah foto PCB dan render 3D
- ESP32 DevKitC · sensor CO2 **MH-Z19C** (NDIR) · sensor CO **MiCS-5524** lewat **ADS1115** (16-bit)
- LCD 16x2 · buzzer · **driver relay** (PN2222A) untuk jendela turun dan naik · catu 12 V → buck 5 V (uji mobil: USB mobil)

**Cara kerja (firmware)** · diagram: [3-implementasi-alur-keputusan.svg](diagram-banner/3-implementasi-alur-keputusan.svg)
- Baca tiap **1 detik**, filter **SMA 6**, pemanasan sensor **180 detik**
- **CO2:** ≥ 2.500 ppm **waspada** (3 bip pendek) · ≥ 4.000 ppm **bahaya** (1 bip panjang + jendela turun 1,5 detik) · kembali < 2.500 ppm selama 10 detik → jendela naik 5 detik
- **CO (estimasi):** ≥ 35 ppm 30 detik waspada · ≥ 87 ppm bahaya · **uji arah 30 detik**: buka jendela, CO turun = sumber dalam, CO naik = sumber luar → minta jendela ditutup
- **Alarm, LCD, dan jendela berjalan di ESP32 tanpa internet**

**Komunikasi dan data** · diagram rinci: [4-implementasi-alur-data.svg](diagram-banner/4-implementasi-alur-data.svg) (untuk PPT) · tambah tangkapan layar aplikasi
- Data tiap **5 detik**, bertanda tangan **HMAC-SHA256**, lewat TLS ke **HiveMQ Cloud**
- **Worker Node.js** memeriksa tanda tangan, menyimpan ke **Supabase**, lalu membalas ACK
- Tiap peringatan tercatat sebagai satu **episode** yang menaut ke bacaan-bacaannya
- Aplikasi **Flutter** menampilkan nilai dan peringatan

## 5. EVALUASI DAN HASIL

*Angka dan sumber lengkap: [hasil-dan-pengujian.md](hasil-dan-pengujian.md) (termasuk naskah penjelasan lisan). Urutan di banner: deskripsi uji, tabel 1 dan 2 (CO2 dan CO, kolom sama, berdampingan), hasil, lalu tabel 3 target dan capaian.*

**Deskripsi uji** (satu baris atau kotak kecil)
- **5 percobaan** di 3 mobil (Avanza, Civic, Ayla), 26 Okt sampai 4 Nov 2026
- **4 penumpang**, jendela tertutup, mobil **berjalan di jalan kota** dengan kecepatan sekitar **20-60 km/jam**
- Alat AEROS di kabin mencatat CO2 dan CO tiap 1 detik; saat alarm bahaya, jendela dibuka manual oleh tim

**Tabel 1 · CO2** (satuan ppm; waspada ≥ 2.500, bahaya ≥ 4.000)

| Mobil | Median | Maks | % waktu ≥ waspada | % waktu ≥ bahaya | Status tertinggi |
|---|---|---|---|---|---|
| Avanza 26 Okt | 3.023 | 4.453 | 71% | 11% | tanpa alarm (v0) |
| Civic 30 Okt | 2.769 | 4.025 | 64% | < 1% | BAHAYA |
| Ayla 4 Nov | 2.864 | 4.410 | 61% | 6% | BAHAYA |
| Avanza 4 Nov | 2.746 | 4.064 | 58% | 2% | BAHAYA |
| **Civic 4 Nov** | **3.363** | **3.725** | **88%** | **0%** | **WASPADA** |

**Tabel 2 · CO estimasi** (satuan ppm; waspada ≥ 35, bahaya ≥ 87)

| Mobil | Median | Maks | % waktu ≥ waspada | % waktu ≥ bahaya | Status tertinggi |
|---|---|---|---|---|---|
| Avanza 26 Okt | 0 | 11* | 0% | 0% | tanpa alarm (v0) |
| Civic 30 Okt | – | – | – | – | CO belum aktif |
| Ayla 4 Nov | 0 | 17 | 0% | 0% | aman |
| Avanza 4 Nov | 0 | 0 | 0% | 0% | aman |
| **Civic 4 Nov** | **12** | **27** | **0%** | **0%** | **aman** |

\* Avanza 26 Okt memakai firmware v0 dengan R0 berbeda (1.730 kΩ lawan 1.878 kΩ), jadi hanya sebagai referensi, tidak sebanding dengan tiga uji 4 Nov. Civic 30 Okt (v2.0): sensor CO belum diaktifkan.

**Hasil CO2** (dua butir di bawah tabel; hasil CO ada di "Temuan CO" di bawah tabel 3)
- **CO2 melewati waspada di 5 dari 5 percobaan dan bahaya di 4 dari 5.** Dari 2.500 ke 4.000 ppm butuh 7-15 menit; setelah jendela dibuka, turun ke bawah 2.500 ppm dalam 58-97 detik.
- **Civic EG6 (1994) jarang menyentuh bahaya di kedua ujinya:** 30 Okt hanya 1 kali (maks 4.025 ppm), 4 Nov tidak pernah (maks 3.725 ppm) walau 88% waktunya di atas waspada. Sebagai pembanding, Ayla 5 kali dan Avanza (4 Nov) 3 kali. CO2 mendatar; diduga kabin mobil lama ini kurang kedap.

**Tabel 3 · Target dan capaian** (nomor, spesifikasi, dan target sama dengan Tabel 6.2 C-251)

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

Warna status: hijau-biru Tercapai · kuning Sebagian · abu-abu Belum. Merah tetap hanya untuk bahaya.

**Analisis target yang belum tercapai** (di bawah tabel 3)
- **Temuan CO (no 2): belum tercapai, 0 dari 5.**
  - **Hasil:** estimasi CO tidak pernah mencapai 35 ppm. Civic tertinggi (median 12, maks 27 ppm), penyebabnya belum terbukti.
  - **Kenapa tidak ada deteksi:** tidak ada sumber CO nyata atau gas acuan, dan membuat CO sendiri tanpa protokol keselamatan tidak kami lakukan.
  - **Kenapa hanya estimasi:** sensor tidak mengukur ppm, tetapi **hambatannya (Rs)**. ppm dihitung dari perbandingan **Rs/R0** memakai kurva datasheet.
  - **R0 adalah Rs di udara bersih**, diukur alat sendiri selama 120 detik. Di mobil, "udara bersih" tidak terjamin dan Rs sendiri berubah-ubah (Avanza yang sama: 925 kΩ lalu 2.021 kΩ). R0 meleset, ppm ikut meleset.
  - Sensor juga ikut bereaksi pada gas lain (parfum menurunkan hambatan 92% dalam 13 detik).
  - **Yang sudah terbukti:** 0 alarm CO palsu dalam ±9.700 bacaan di 3 uji mobil.
  - **Langkah berikut:** uji dengan gas CO acuan, kalibrasi R0 di udara bersih tiap uji.
- **Aktuator dan penutupan (no 4, 6): sinyal terbukti, gerak jendela belum.** Relay belum terpasang ke motor jendela. Penutupan di firmware: CO2 < 2.500 ppm selama 10 detik, spesifikasi 60 detik.
- **Tampil di aplikasi (no 7): belum diukur** sampai ponsel; langkah berikut: ukur dengan jam ponsel.
- **Anggaran (no 8): belum dihitung ulang** setelah komponen berganti.

**Keandalan** (pita kecil)
- Uji meja (v2.3): 13 peringatan, **11 siklus jendela turun 1,5 detik lalu naik 5 detik benar semua**; bunyi dan sinyal keluar 6-12 ms setelah status berubah ✔
- Alarm tetap berbunyi saat **Wi-Fi mati** (4 episode) ✔

**Batasan:** jendela dibuka manual di uji mobil · nilai CO estimasi, belum diuji gas asli · satu uji per mobil per hari.

## 6. KESIMPULAN

*Merangkum panel Hasil Uji dan Evaluasi (deskripsi uji, tabel 1-3, analisis hasil uji, temuan CO), lalu batasan dan saran.*

**Kesimpulan**
- **CO2 terdeteksi dan direspons.** Dari 5 percobaan, CO2 melewati waspada di 5 dan bahaya di 4. Buzzer dan aktuator merespons dalam **1,3 detik** (target ≤ 5 dan ≤ 10 detik).
- **Dari 7 target, 6 tercapai.** Satu-satunya yang belum tercapai adalah **deteksi CO (0 dari 5)**.
- **CO belum tercapai karena tidak ada sumber CO nyata, dan nilainya hanya estimasi** (dihitung dari Rs/R0). Estimasi tertinggi 27 ppm, tidak pernah mencapai 35 ppm.
- **Civic EG6 (1994) jarang menyentuh bahaya di kedua uji** (1 kali di 30 Okt, tidak pernah di 4 Nov); CO2 mendatar, diduga kabin mobil lama ini kurang kedap.

**Batasan**
- **Nilai CO hanya estimasi:** belum diuji dengan gas CO asli, dan R0 diukur alat sendiri di udara yang tidak terjamin bersih.
- **Jendela dibuka manual** di uji mobil, jadi gerak jendela otomatis belum terbukti (yang terbukti sinyal ke relay).
- **Ambang tetap 4.000 ppm** tidak pernah tercapai di Civic yang diduga tidak kedap, sehingga jendela tidak turun.
- **Uji terbatas:** jumlah episode bahaya bergantung lama uji (36-76 menit) dan jumlah bukaan jendela, jadi tidak dinormalkan; 5 percobaan di 3 mobil, satu uji per mobil per hari; firmware berbeda antar uji, jadi hanya 3 uji (4 Nov) yang CO-nya sebanding.

**Saran pengembangan selanjutnya**
- **Uji CO dengan gas acuan** (atau pembanding detektor CO terkalibrasi) dan kalibrasi R0 di udara bersih tiap uji; bila anggaran ada, pakai sensor CO yang lebih selektif.
- **Pasang relay ke motor jendela** lalu ukur waktu dari sinyal sampai jendela bergerak, termasuk uji penutupan karena CO dan uji arah di mobil.
- **Ambang yang menyesuaikan mobil** (misalnya memakai laju kenaikan CO2, bukan hanya batas tetap) agar mobil yang tidak kedap tetap memicu tindakan.
- **Perbanyak dan standarkan uji:** beberapa uji per mobil, catat kecepatan, AC, dan jam buka-tutup jendela.

---

## Catatan desain

- Urutan baca: Judul → 1 → 2 → 3 → 4 → 5. Lima kotak dengan warna berbeda.
- Gambar yang disarankan: (a) diagram blok bagian 3, (b) foto alat dan skematik [skematik-pin-2026-11-03.png](../keputusan/diagram/skematik-pin-2026-11-03.png), (c) grafik CO2 uji Civic (naik, bahaya, turun saat jendela dibuka) dengan garis ambang 2.500 dan 4.000 ppm.
- Angka yang dibesarkan: **96%**, **3.413 ppm**, **1,3 detik**, **0 dari 431 data hilang**, **1,45 detik** (tunda simpan).
- Blok 5 memuat deskripsi uji, tabel CO2 dan CO (kolom sama, 5 percobaan, berdampingan), dua butir hasil CO2, tabel target dan capaian (8 baris seperti C-251), dan analisis yang belum tercapai; tanpa baris angka besar terpisah. Penjelasan keterbatasan uji ada di [hasil-dan-pengujian.md](hasil-dan-pengujian.md) untuk PPT.

---

## Tentang isi C-251 (sudah pas atau belum?)

**Yang pas dan dipakai:** alur masalah macet → sirkulasi dalam → CO2 dan CO menumpuk; studi Hong Kong; konsep peringatan bertingkat; buzzer yang tidak bergantung internet; tidak ada standar kabin di Indonesia.

**Yang saya koreksi di banner:**

| Di C-251 | Di banner | Alasan |
|---|---|---|
| "OSHA menetapkan 35 ppm rata-rata 8 jam" (Bab 1) | tidak ditulis | 35 ppm adalah **NIOSH REL** (rata-rata sampai 10 jam, plafon 200 ppm). OSHA PEL adalah 50 ppm. Terverifikasi dari halaman NIOSH dan OSHA 25 Okt |
| "batas rekomendasi 1.000 ppm" | "melewati 1.000 ppm" saja | 1.000 ppm bukan batas kesehatan ASHRAE; hanya patokan lama untuk ventilasi |
| MQ-7 dan MH-Z19B | MiCS-5524 + ADS1115 dan MH-Z19C | komponen sudah diganti |
| Dua status AMAN dan WASPADA; CO tinggi → jendela **ditutup** + anjuran AC recirculation | tiga tingkat; CO → **uji arah** | rancangan berubah; mode AC tidak diandalkan |
| Servo, kotak akrilik, BLE | relay jendela, uji di mobil, Wi-Fi + MQTT | implementasi sekarang |
| Dampak kognitif 1.000 ppm "signifikan pada 6 dari 9 indikator" | "menurunkan kemampuan mengambil keputusan" | tinjauan ASHRAE 2025 menilai bukti belum konsisten |

## Cek sebelum cetak

- [x] Hong Kong terverifikasi ke artikel asli ([27]). Auckland: puncak ±170 ppm terverifikasi dari abstrak ([28]); "171 ppm dalam 10 detik" dan "pulih 11 menit" dari C-251 **tidak terverifikasi** dan sudah dibuang dari banner. Bila mau memakainya, buka teks lengkap MDPI di browser dan cari angkanya.
- [ ] Nomor kutipan C-251 tidak sama dengan [daftar-pustaka.md](../referensi/daftar-pustaka.md); jangan menyalin nomornya.
- [x] Hasil uji 3 mobil v2.4 (Ayla, Avanza, Civic 4 Nov) sudah masuk bab 5, dari [perbandingan-mobil-2026-11-04.md](../analisis/perbandingan-mobil-2026-11-04.md).
- [ ] Anggaran (target ≤ Rp2.000.000) **belum dihitung ulang** setelah komponen berganti, jadi tidak saya masukkan. Hitung dulu bila ingin menampilkannya.
- [ ] Tabel 3 sekarang memuat baris **anggaran** (no 8, "belum dihitung ulang") karena mengikuti Tabel 6.2 C-251. Hitung anggaran dulu bila ingin mengubahnya jadi angka.
- [ ] Hasil tampil di ponsel belum diukur. Jangan menulis "real-time di aplikasi" sebagai hasil terukur.
- [ ] Deskripsi uji "jalan kota, 20-60 km/jam" berasal dari penguji. Laporan uji 4 mencatat Avanza 26 Okt 20-40 km/jam di sebagian besar rute, tetapi **60-80 lalu lebih dari 100 km/jam pada 20:22-20:26**; kecepatan uji 4 Nov tidak tercatat di dokumen mana pun. Bila mau aman, tulis "umumnya 20-60 km/jam". Cek juga AC dan arah udara (sirkulasi dalam?) tiap uji; belum tercatat untuk 5 uji ini.
- [ ] Tabel 1 dan 2 mencampur firmware v0, v2.0, dan v2.4; hanya tiga uji 4 Nov yang memakai casing 3D, dan hanya tiga uji itu yang CO-nya sebanding. Angka 1,3 detik dan 0 dari 431 masih dari uji Civic 30 Okt, bukan dari v2.4.
- [ ] Versi firmware Civic 30 Okt: README log menulis v2.0, laporan uji 7 dan dokumen KPI menulis v2.1. Cek ke log sebelum menulis versi di banner.

## Status verifikasi (4 November 2026)

| Isi banner | Dicek ke | Hasil |
|---|---|---|
| Bagian 3: ambang, waktu pulsa, filter, pemanasan, alur data | **kode** `sensorOriginal.inl` dan `main.cpp` v2.4 | cocok |
| Pin, driver relay | skematik KiCad 3 Nov dan kode | cocok |
| Uji Civic (waspada 3×, bahaya 1×, 431 ACK, 1,3 detik, 75 detik, 5,8 menit) | **log mentah** `device-monitor-261030-183128.log` | cocok setelah dicek ulang |
| Uji meja (13 peringatan, 11 siklus, 6-12 ms, Wi-Fi mati) | laporan uji 8 | dari laporan, belum dihitung ulang dari log |
| Uji Avanza (207-218, 4.453, 95 detik) | [banner-hasil-uji-dan-kpi.md](../analisis/banner-hasil-uji-dan-kpi.md) dan laporan uji 4 | dari dokumen |
| Hong Kong | artikel asli (PMC) | cocok, rata-rata dibulatkan karena memakai nilai batas alat |
| Auckland | abstrak artikel asli | puncak ±170 ppm cocok; angka 10 detik dan 11 menit tidak terverifikasi, dibuang |
| Aplikasi Flutter menampilkan nilai dan peringatan | tidak ada kodenya di repo ini | **belum saya verifikasi** |

Yang saya koreksi dari versi pertama: rentang laju naik (207-268, bukan 213-268), "sensor CO turun 92%" (yang turun hambatan sensor), "2,6-4,6 detik ke database" (angka dari dokumen KPI lama, tidak bisa ditemukan di laporan uji 7 maupun log, diganti median 1,45 detik dari laporan), dan "PCB" dari daftar rencana (PCB sudah ada dan terpasang; yang belum casing).

**Perbedaan penting yang harus diketahui:** hasil uji lapangan datang dari firmware **v0 dan v2.1** (CO2 saja, satu pin relay). Banner menjelaskan **v2.4** (CO aktif, dua relay). Jalur CO dan siklus dua relay baru diuji di meja. Banner sudah menyebut ini, jangan dihapus.

Dokumen perencanaan [tugas-per-subsistem.md](tugas-per-subsistem.md) masih versi 27 Okt (jadwal expo 30 Okt, buzzer GPIO25) sehingga **tidak saya pakai** sebagai rencana terbaru; rencana terbaru yang dipakai: uji 3 mobil v2.4 di [rencana-uji.md](../pengujian/rencana-uji.md) bagian 2.0 dan keputusan 3-4 Nov.

---

# PANDUAN LAYOUT X-BANNER (gaya pitch deck, versi tegak)

Untuk dibuat sendiri di Canva, PowerPoint, atau Figma. Ukuran **dianggap 60 x 160 cm** (x-banner umum); **cek dulu ukuran asli ke percetakan atau panitia**, lalu skalakan zonanya. Isi teks mengikuti bagian 1-6 di atas, tetapi di banner ditulis jauh lebih pendek seperti di bawah.

## 1. Aturan kertas
- Buat kanvas **ukuran asli** (60 x 160 cm), bleed 0,5 cm, ekspor **PDF**. Gambar minimal 150 dpi pada ukuran asli.
- **Zona aman:** margin kiri-kanan 4 cm. Kosongkan **5 cm teratas** (penjepit) dan **10 cm terbawah** (tiang dan kantong). Jangan taruh teks penting di sana.
- Jarak baca 1,5-2 m. Hierarki: judul > angka besar > judul blok > isi > sumber.

## 2. Zona vertikal (dari atas)

| Zona | Tinggi (cm) | Isi | Visual |
|---|---|---|---|
| Kepala | 5-18 | Logo kampus, **AEROS**, subjudul, tim dan dosen | foto atau render alat |
| 1 Latar belakang | 18-36 | satu angka raksasa + paragraf pendek | ilustrasi kabin atau ikon |
| 2 Permasalahan | 36-56 | pertanyaan utama + deskripsi tantangan | **gambar dari Gemini** |
| 3 Solusi | 56-66 | deskripsi singkat + 3 fitur utama | ikon saja |
| 4 Implementasi | 66-108 | satu diagram alur lebar penuh, lalu satu baris foto | [diagram 6](diagram-banner/6-implementasi-alur-gabungan.svg) + foto PCB, render 3D, dua tangkapan layar aplikasi |
| 5 Hasil | 108-141 | tabel target dan capaian, deskripsi uji, tabel CO2 dan CO berdampingan (kolom sama, 5 percobaan), hasil, tabel target dan capaian, analisis yang belum tercapai | tanpa grafik |
| 6 Kesimpulan | 141-148 | 3 poin pendek | ikon centang |
| Sumber | 148-150 | sumber huruf kecil (16 pt) | tanpa visual |
| Dasar | 150-160 | pita warna polos (tanpa teks penting) | - |

**Blok 4 Implementasi (tinggi total ±42 cm dari 42 cm yang tersedia):**
- Atas: [diagram 6 alur gabungan](diagram-banner/6-implementasi-alur-gabungan.svg) selebar banner (±52 cm), tinggi ±26 cm.
- Bawah: satu baris empat gambar sama besar (±12 x 14 cm): foto PCB, render 3D alat, dua tangkapan layar aplikasi (nilai dan peringatan).
- Pada lebar 52 cm, teks dalam diagram ±17-22 pt: terbaca dari ±1,5 m. Judul blok dan angka besar tetap di luar diagram. Tidak ada sisa ruang; kalau perlu, kecilkan baris foto, jangan diagram. Bila [diagram 7](diagram-banner/7-arsitektur-sistem-landscape.svg) dipakai (±52 x 22 cm), ada tambahan ±4 cm.

## 3. Gaya
- **Warna:** latar `#0B1F33` (biru tua) · kartu `#12304D` · teks `#FFFFFF` · **angka dan sorotan `#FFB020`** (kuning-oranye) · aman `#2EC4B6` · bahaya `#E63946`. Merah hanya untuk "bahaya", hijau-biru hanya untuk "aman", sama dengan status di alat.
- **Font:** dua saja. Judul dan angka: Montserrat atau Poppins Bold. Isi: Inter atau Open Sans.
- **Ukuran minimal pada ukuran asli:** judul AEROS 110 pt · judul blok 60 pt · **angka besar 150-220 pt** · isi 28 pt · sumber 16 pt.
- Rata kiri, kartu sudut membulat, jarak antar blok sama (3 cm), nomor blok 1-6 dalam lingkaran kuning.
- **Satu blok = satu pesan.** Maksimal 3 butir, tiap butir maksimal 8 kata. Kalau lebih panjang, pindahkan ke PPT.
- Sorot angka dengan warna kuning dan ukuran 3 kali teks sekitarnya. Kata penjelas angka di bawahnya, huruf kecil.
- Ikon satu gaya (garis tebal atau solid, jangan campur).

## 4. Isi ringkas tiap zona (siap disalin)

**Kepala:** AEROS · Pemantau Kualitas Udara Kabin Kendaraan · *Sensor CO dan CO2, peringatan bertingkat, respons jendela otomatis*

**1 Latar belakang**
- Angka raksasa: **96%**
- Kalimat: mobil ber-AC di Hong Kong melewati 1.000 ppm CO2 (51 mobil)
- Kecil: 16% melewati 5.000 ppm · rata-rata ±3.400 ppm
- Satu baris: CO2 dan CO tidak bisa dirasakan indra. CO2 tinggi dapat menurunkan kemampuan mengambil keputusan.

**2 Permasalahan** (gambar lebar di atas, lalu tiga kartu)
- Pertanyaan: *Bagaimana memantau CO dan CO2 di kabin secara real-time dan merespons otomatis, dengan biaya terjangkau?*
- Kartu 1 (ikon kabin): **207-268 ppm/menit**, kabin tertutup 4 orang melewati 2.500 ppm dalam beberapa menit
- Kartu 2 (ikon parfum): sensor murah tidak selektif, parfum menurunkan hambatan sensor **92%** dalam 13 detik
- Kartu 3 (ikon wifi dicoret): peringatan harus jalan **tanpa internet**
- Pita kecil: anggaran maksimal Rp2.000.000 · nilai CO hanya estimasi

**3 Solusi** (menjawab pertanyaan: *apa* yang dirancang; hanya pengenalan dan fitur, tanpa diagram)
- Kalimat pembuka: **AEROS: alat pemantau udara kabin yang bertindak sendiri sebelum pengemudi menyadari udara memburuk.**
- Fitur 1 (ikon `air quality sensor`): **Pantau Dini** · CO dan CO2 tiap detik, peringatan bertingkat
- Fitur 2 (ikon `car window`): **Jendela Otomatis** · turun saat bahaya, naik saat aman
- Fitur 3 (ikon `wifi off`): **Siaga Tanpa Internet** · alarm tetap berbunyi

**4 Implementasi** (menjawab: *apa yang sudah diwujudkan*; diagram alur lebar penuh, lalu baris foto)
- Judul kecil di atas diagram: **Alur dari sensor sampai aplikasi** (warna = sistem: perangkat keras, firmware, cloud, aplikasi)
- Keterangan baris foto: **PCB** · **Render 3D** · **Aplikasi: nilai** · **Aplikasi: peringatan**

**5 Evaluasi dan hasil** (tinggi ±33 cm; kebutuhan ±35 cm: deskripsi uji ±3, tabel 1 dan 2 berdampingan ±10,5, hasil ±4, tabel 3 ±12,6 (9 baris x 1,4), analisis ±5)
- Kotak deskripsi uji di atas: 5 percobaan · 4 penumpang · jalan kota · 20-60 km/jam
- Tabel 1 **CO2** (kiri) dan Tabel 2 **CO estimasi** (kanan), masing-masing ±25 cm lebar, **kolom identik**; baris Civic 4 Nov disorot kuning
- Dua butir **Hasil CO2** di bawah kedua tabel
- Tabel 3 **Target dan capaian**: delapan baris persis seperti Tabel 6.2 C-251 (No, Spesifikasi, Target) ditambah kolom Capaian dan Status berwarna; **1,3 detik** dan **1,45 detik** dicetak tebal
- Di bawah tabel 3, **Analisis target yang belum tercapai** (**Temuan CO** paling besar; hasil CO dan alasan estimasi jadi satu di sini)
- Pita kecil: jendela dibuka manual di uji mobil · CO belum diuji gas asli · catatan bintang (\*) tabel CO
- Teks tabel minimal 24 pt. **Kalau kurang ±2 cm:** potong analisis non-CO menjadi satu baris, atau buang baris Avanza 26 Okt dari tabel 1 dan 2. Jangan kecilkan huruf

**6 Kesimpulan** (tiga kotak: Kesimpulan, Batasan, Saran; tiap kotak maksimal 3 butir pendek)
- Kesimpulan: CO2 terdeteksi dan direspons dalam **1,3 detik** · dari 7 target, **6 tercapai**, hanya **deteksi CO** yang belum · CO belum tercapai karena tidak ada sumber CO nyata dan nilainya estimasi
- Batasan: nilai CO estimasi, belum diuji gas asli · jendela dibuka manual, gerak otomatis belum terbukti · uji terbatas (5 percobaan, 3 mobil) dan ambang tetap tidak bereaksi di Civic
- Saran: uji CO dengan gas acuan dan kalibrasi R0 · relay ke motor jendela dan ukur geraknya · ambang yang menyesuaikan mobil, uji lebih banyak dan terstandar

**Sumber (16 pt):** Barnes dkk., IJERPH 15(4):611, 2018 · Satish dkk., EHP 120(12):1671-1677, 2012

## 5. Gambar yang dibutuhkan
| Gambar | Dari mana |
|---|---|
| Ilustrasi permasalahan (lebar, tanpa teks) | **Gemini**, prompt di bawah |
| Foto atau render alat | foto sendiri |
| Diagram solusi, perangkat keras, alur keputusan, alur data | sudah dibuat: 4 berkas SVG di [diagram-banner/](diagram-banner/). Impor ke Canva (unggah SVG) atau Figma; latarnya biru tua `#0B1F33` sama dengan latar banner |
| Foto PCB, render 3D alat, tangkapan layar aplikasi | dari kamu (blok 4 Implementasi) |
| Grafik CO2 uji Civic | opsional, tidak ada tempat di blok 5 yang baru; untuk PPT, dari log `device-monitor-261030-183128.log` (bisa dibuatkan) |
| Ikon | Canva, Flaticon, atau Material Icons satu set |

## 6. Prompt Gemini (hanya ilustrasi permasalahan)

```
Buatkan satu ilustrasi vektor datar (flat vector, gaya isometrik atau potongan samping) untuk x-banner, rasio lebar 3:1.
Isi: kabin mobil dilihat dari samping dengan dinding dibuka sebagian. Empat siluet penumpang, jendela tertutup, partikel gas abu-abu dan kuning-oranye memenuhi kabin. Pengemudi terlihat mengantuk. Di luar, di belakang mobil, ada truk tua dengan asap knalpot gelap yang mendekat ke kisi udara mobil.
Warna: latar biru tua #0B1F33, mobil biru #12304D, gas kuning-oranye #FFB020 dan abu-abu muda, aksen putih. Tanpa gradasi rumit.
WAJIB: tanpa teks, tanpa angka, tanpa logo, tanpa merek mobil. Sisakan ruang kosong di sisi kanan sekitar sepertiga lebar untuk teks. Resolusi setinggi mungkin.
```
Kalau hasilnya penuh detail atau ada tulisan aneh, minta: "sederhanakan, kurangi detail, hapus semua teks".
