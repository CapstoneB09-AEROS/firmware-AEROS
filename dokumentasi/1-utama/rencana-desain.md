# Rencana Desain Sistem Peringatan Kualitas Udara Kabin (CO dan CO2)

Prototipe AEROS, tim C-251. Versi 25 Oktober 2026. Ini dokumen utama. Catatan kerja yang lebih rinci ada di [desain-peringatan.md](../3-bukti/desain-peringatan.md) dan file lain di folder ini.

**Cara membaca status.** Setiap kebutuhan dan parameter diberi status:
- **Terbukti**: ada sumber yang sudah dibaca langsung atau data ukur sendiri.
- **Usulan**: masuk akal, tetapi belum diuji atau belum disepakati tim.
- **Konfirmasi**: butuh keputusan tim atau pengukuran sebelum dipakai.

Kutipan `[n]` mengacu ke [daftar-pustaka.md](../3-bukti/daftar-pustaka.md). `[C251]` adalah dokumen rencana awal tim. `[D]` adalah data ukur kami pada 25 Oktober 2026.

---

## Ringkasan

Kabin mobil yang tertutup bisa dipenuhi CO2 dari napas penumpang dalam hitungan menit, dan CO dari knalpot kendaraan lain bisa ikut masuk. Kami membuat prototipe yang membaca CO2 (sensor NDIR MH-Z19C) dan memperkirakan CO (sensor semikonduktor MiCS-5524), lalu memberi peringatan dan membuka jendela. Karena tidak punya gas CO asli maupun alat pembanding, nilai CO hanya **estimasi indikatif**.

Ide utamanya: (1) CO2 ≥ 2500 ppm hanya diberi peringatan lembut, dan ≥ 4000 ppm jendela dibuka; (2) CO ≥ 35 ppm membuat jendela dibuka sebagai **uji arah**: kalau CO naik lagi, sumbernya dari luar (misalnya truk), jadi jendela ditutup; (3) aturan CO selalu menang atas aturan CO2; (4) semua waktu tunggu diputuskan dari tiga hal: seberapa cepat bahaya datang, seberapa goyang sensor, dan hasil uji pada data.

---

## 1. Latar Belakang

### 1.1 Masalah
- Di mobil yang tertutup, CO2 dari napas menumpuk cepat. Menurut simulasi di [C251], 4 penumpang di Avanza mencapai batas peringatan dalam sekitar 5 menit (angka dari tabel yang terbaca sebagian, cek PDF). Dalam uji kasar tim, 4 orang di Avanza mencapai 5000 ppm (batas sensor) dalam 20–30 menit.
- CO adalah gas tak berwarna dan tak berbau. Dalam kemacetan, CO dari kendaraan di depan bisa masuk ke kabin [C251].
- Belum ada aturan wajib kualitas udara kabin pribadi di Indonesia [C251].
- Sensor murah bisa dipakai, tetapi punya keterbatasan yang harus diakui (lihat 2.1 dan bagian 5).

### 1.2 Tujuan
1. Memantau CO2 dan memperkirakan CO di kabin.
2. Memberi peringatan bertingkat yang tidak mengganggu.
3. Membuka atau menutup jendela secara otomatis dengan aturan yang masuk akal.
4. Setiap angka di sistem punya alasan: sumber, data, atau perhitungan.

### 1.3 Ruang lingkup
Yang dikerjakan: firmware pembaca sensor, aturan peringatan, uji dengan data, dan perancangan aliran data ke aplikasi. Yang **tidak** dikerjakan: kalibrasi dengan gas CO standar, kompensasi suhu dan kelembapan, dan pengujian formal di kendaraan nyata (uji mobil dilaporkan sebagai uji tambahan).

### 1.4 Pertanyaan desain yang harus dijawab
1. Pada kadar berapa dan kapan peringatan diberikan?
2. Berapa lama harus menunggu sebelum memutuskan, supaya tidak terlambat dan tidak bolak-balik?
3. Kapan jendela dibuka, dan kapan tidak?
4. Filter apa yang dipakai untuk menghaluskan pembacaan?

---

## 2. Tinjauan dan Perbandingan

### 2.1 Sensor

| | MiCS-5524 (CO) | MH-Z19C (CO2) |
|---|---|---|
| Cara kerja | Hambatan sensor berubah saat ada gas. Kita hitung ppm dari hambatan | Cahaya inframerah diserap CO2. Sensor mengirim angka ppm lewat UART |
| Rentang | CO 1–1000 ppm (kurva pada 25 °C dan 50% RH) [1] | 400–5000 ppm (varian 5000) [2] |
| Akurasi | Tidak ada nilai ppm resmi, hanya kurva grafik [1] | ±(50 ppm + 5%) [2] |
| Waktu respons | **Tidak ada di datasheet** [1] | T90 kurang dari 120 detik, preheat 1 menit [2] |
| Catu daya | 4,9–5,1 V (pemanas 2,4 V, 76 mW) [1] | 5,0 ±0,1 V (tabel) atau 4,5–5,5 V dan ≥ 150 mA (catatan) [2] |
| Hal yang merusak atau mengganggu | Pelarut organik, uap silikon, asap rokok (merusak lapisan). Bereaksi juga ke alkohol, hidrogen, amonia [1] | Panas dan sinar matahari langsung, debu, tekanan pada ruang plastik [2] |
| Kalibrasi | R0 di udara bersih (100–1500 kΩ antar unit) [1] | ABC otomatis tiap 24 jam, titik nol 400 ppm. Tidak cocok untuk ruang yang jarang kena udara luar [2] |

**Perbandingan dengan rencana awal:** [C251] memakai MQ-7 dan MH-Z19B. Kami beralih ke MiCS-5524 dan MH-Z19C. Akibatnya filter 150 detik di [C251] (berdasar siklus pemanasan MQ-7) tidak berlaku lagi, dan akurasi CO2 lebih longgar (±50 ppm menjadi ±(50 ppm + 5%)). Pada 4000 ppm, itu sekitar ±250 ppm.

### 2.2 Batas CO

| Sumber | Angka | Berlaku untuk | Arti sederhana |
|---|---|---|---|
| NIOSH REL [11][12] | 35 ppm rata-rata sampai 10 jam, plafon 200 ppm | Pekerja | Batas anjuran. Bukan "OSHA 8 jam" seperti tertulis di [C251] |
| OSHA PEL [12] | 50 ppm rata-rata 8 jam | Pekerja | Batas aturan |
| NIOSH IDLH [11] | 1200 ppm | Pekerja | Langsung berbahaya bagi nyawa |
| WHO 2010 [14] | 87 ppm (15 menit), 30 ppm (1 jam), 9 ppm (8 jam), 6 ppm (24 jam). Resmi dalam mg/m³: 100, 35, 10, 7 | Penghuni ruang | Dasar: kadar COHb dalam darah tidak lebih dari 2% |
| UL 2034 [15] | Alarm harus aktif dalam 60–240 menit pada 70 ppm, 10–50 menit pada 150 ppm, 4–15 menit pada 400 ppm | Alarm CO rumah | Selang waktu punya batas bawah **dan** atas. Alarm terlalu cepat dianggap gagal |

**Perbandingan dengan alarm kita.** Alarm kita jauh lebih cepat dari batas bawah UL, jadi alat ini **tidak boleh diklaim memenuhi UL 2034**. UL dipakai sebagai referensi bentuk saja: alarm adalah fungsi kadar **dan** waktu. Alasan kita boleh lebih sensitif: satu perjalanan mobil hanya sekitar 30–60 menit, dan tindakan yang dilakukan (membuka jendela) murah. Kelemahan: alarm palsu mengganggu, dan sensor tidak selektif.

### 2.3 Batas CO2

| Sumber | Temuan | Arti sederhana |
|---|---|---|
| NIOSH dan OSHA [16] | 5000 ppm rata-rata, jangka pendek 30.000 ppm (NIOSH), IDLH 40.000 ppm | Batas paparan kerja |
| ASHRAE 2025 [21] | CO2 dianggap tidak beracun sampai 5000 ppm. Pedoman ISS dan kapal selam menjaga 4000–5000 ppm untuk menurunkan sakit kepala (dikutip dari studi lain) | Mendukung 4000 sebagai batas tindakan |
| ASHRAE 2025 [21] | **1000 ppm bukan batas kesehatan dan bukan batas ASHRAE.** Berasal dari edisi 1989 yang dihapus, dan terkait bau tubuh dan ventilasi | Alasan tidak memakai 1000 sebagai ambang |
| Satish 2012 [19] | 22 peserta, 600, 1000, dan 2500 ppm, tiga sesi 2,5 jam. Hasil: penurunan kemampuan mengambil keputusan di 1000 dan lebih besar di 2500 (angka hasil dari ringkasan, bagian Results belum dibaca) | Dasar 2500 sebagai peringatan |
| Tinjauan ASHRAE [21] dan Scully 2019 [20] | Enam studi melaporkan hubungan dengan penurunan kognitif sekitar 1000 ppm, satu meragukan (Scully, pesertanya "astronaut-like"), lainnya tidak menemukan efek. Bukti dinilai tidak konsisten | Dasar 2500 lemah, jadi peringatan di 2500 sengaja lembut |

**Catatan penting:** di mobil, CO2 ≥ 1000 ppm tercapai tidak lama setelah pengguna masuk (menurut [C251], 96% mobil di studi Hong Kong melewati 1000 ppm). Karena itu 1000 tidak dipakai sebagai ambang.

### 2.4 Noise dan filter

Dari rekaman kamar 4 jam [D]:
- Sekitar **95% goyangan Rs adalah pola bergantian naik-turun tiap detik**, periode sumber sekitar 2 detik, stabil, dan **proporsional terhadap sinyal**. Jadi bukan noise pembacaan biasa. Dugaan: listrik pemanas ikut bergoyang karena ada beban berdenyut. **Belum terbukti.**
- Rata-rata bergerak jumlah **genap** meredam pola itu dengan baik, jumlah ganjil kurang.
- Memperpanjang filter tidak membuang sisa noise (sekitar 3%, gerakan lambat).
- Median tidak membantu (hanya turun 2%).

| Filter | Noise Rs (%) | Turun | Waktu respons 90% |
|---|---|---|---|
| Mentah | 13,9 | 0% | 0 detik |
| SMA 4 | 3,3 | 76% | 3 detik (lonjakan buatan +30% lolos 7,4%) |
| SMA 6 | 3,3 | 76% | 5 detik (lolos 4,9%) |
| SMA 8 | 3,3 | 76% | 7 detik (lolos 3,7%) |
| SMA 10 | 3,3 | 76% | 8 detik |
| EMA 0,2 (kode sekarang) | 3,6 | 74% | 10 detik (lolos 5,9%) |
| EMA 0,1 | 3,1 | 77% | 21 detik |
| Median 5 | 13,6 | 2% | 2 detik |

**Perbandingan dengan rencana awal:** [C251] memakai rata-rata 150 detik (CO) dan 120 detik (CO2) dan siklus 5 detik. Data kami menunjukkan filter sependek 2–4 detik sudah cukup untuk noise CO. Untuk CO2, sensor sudah lambat (T90 hingga 120 detik), jadi tidak perlu filter tambahan.

### 2.5 Hasil ukur lain

- **R0 tidak konstan.** Rs di kamar tanpa gas yang diketahui turun lebih dari 50% dalam sekitar 4 jam (dari sekitar 2045 ke sekitar 900–1000 kΩ). Penyebab belum diketahui (kelembapan, suhu, atau drift). Konsekuensi: nilai ppm absolut CO tidak bisa dipercaya, dan keputusan sebaiknya memakai **perubahan relatif**.
- **CO2 stabil**: noise sekitar 3–4 ppm dan tidak ada bacaan rusak setelah pemanasan. Konfirmasi singkat (sekitar 3 detik) cukup untuk menolak satu bacaan salah.
- **Gangguan perangkat**: USB sempat putus dua kali (konektor longgar) dan MH-Z19C sempat mati sendiri satu kali. Semua menyebabkan sensor mulai dari awal.
- **Tegangan MiCS** pernah mencapai 3,68 V, melewati batas input ADS1115 pada catu 3,3 V (sekitar 3,6 V) [3] (datasheet TI belum dibaca langsung).

### 2.6 Rencana awal dan keadaan sekarang

| Hal | [C251] | Sekarang |
|---|---|---|
| Sensor CO | MQ-7 | MiCS-5524 + ADS1115 |
| Sensor CO2 | MH-Z19B | MH-Z19C |
| Siklus | 5 detik | 1 detik untuk keputusan, 5 detik untuk kirim data |
| Filter | Rata-rata 150 s (CO), 120 s (CO2) | SMA 2–4 untuk CO, tanpa filter untuk CO2 (usulan) |
| Ambang CO2 | 2500: bunyi dan buka jendela | 2500: bunyi singkat. 4000: bunyi dan buka jendela |
| Aksi CO tinggi | Jendela tertutup, saran AC | Jendela dibuka sebagai uji arah, ditutup bila CO naik lagi. Saran AC ditunda |
| Pemulihan | CO < 30 dan CO2 < 2400 selama 60 detik | Sama |
| Kalibrasi | "Rekalibrasi manual sebelum uji" | R0 diukur di udara bersih, tidak ada referensi CO |

Beberapa kesalahan atau pertentangan di [C251] sudah dicatat di [perbandingan-c251.md](../3-bukti/perbandingan-c251.md): atribusi 35 ppm CO (NIOSH, rata-rata sampai 10 jam, bukan OSHA 8 jam), atribusi 1000 ppm ke ASHRAE, jumlah status, dan ambang CO2 di Bab 11.

---

## 3. Rencana Akhir (Kebutuhan)

### 3.1 Kebutuhan fungsional

| ID | Kebutuhan | Dasar | Status |
|---|---|---|---|
| FR-01 | CO2 ≥ 2500 ppm (3 bacaan valid berturut-turut): bunyi singkat satu kali dan peringatan di aplikasi | [19][21], keputusan tim | Usulan |
| FR-02 | CO2 ≥ 4000 ppm (3 bacaan valid berturut-turut) dan aturan CO tidak aktif: bunyi dan buka jendela. Besar bukaan dihitung per mobil | 5000 ppm batas kerja [16], ISS dan kapal selam 4000–5000 [21], margin sensor (akurasi sekitar ±250 ppm dan keterlambatan sekitar 130–350 ppm di 4000) | Usulan |
| FR-03 | CO2 < 2400 ppm selama 60 detik berturut-turut: jendela ditutup dan bunyi dihentikan | [C251] | Konfirmasi (diuji dengan sapuan) |
| FR-04 | CO estimasi ≥ 35 ppm bertahan 30 detik: bunyi dan buka jendela (uji arah) | NIOSH REL 35 ppm [11], WHO 1 jam sekitar 30 ppm [14], biaya tindakan keliru kecil | Usulan (30 detik belum berdasar data) |
| FR-05 | Uji arah: setelah jendela dibuka dan waktu uji lewat, bila CO naik lagi melebihi kriteria, sumber dari luar. Jendela ditutup dan tetap tertutup sampai CO < 30 ppm selama 60 detik. Bila CO turun, jendela tetap terbuka sampai CO < 30 ppm selama 60 detik | Model konsentrasi [C251, Pers. 4.3], metode peluruhan [21] | Konfirmasi |
| FR-06 | **Aturan CO menang atas CO2.** Selama aturan CO aktif, aktuator mengikuti aturan CO dan aturan CO2 diabaikan | Keputusan tim 25 Okt | Disepakati tim |
| FR-07 | Setelah menutup karena sumber luar, uji arah tidak diulang sampai aturan CO selesai | Mencegah paparan berulang | Usulan |
| FR-08 | CO sangat tinggi: tingkat bahaya langsung, tanpa menunggu konfirmasi. Angka: 87 ppm (WHO 15 menit). Aturan jendela sama dengan CO ≥ 35 ppm (uji arah), bunyi dibuat lebih keras | [14] | Disepakati (25 Okt malam) |
| FR-09 | Data tidak valid (CO2 `n/a`, ADC mentok atau tidak masuk akal): tampilkan gangguan dan **jangan** gerakkan jendela otomatis. Nilai 410 atau 500 setelah sensor mulai ulang bukan "udara aman" | Aman saat gagal | Usulan |
| FR-10 | Masa pemanasan: tidak ada alarm CO selama pemanasan MiCS (usulan 5 menit) dan CO2 (3 menit). Dihitung ulang bila sensor mati sebentar | [D], [2] | Usulan |
| FR-11 | Pola bunyi dan pesan layar dibedakan untuk CO dan CO2 | UX | Usulan |
| FR-12 | Tombol "Saya Tahu" mematikan bunyi. Bunyi mati sendiri setelah 5 menit | [C251] | Dari rencana awal |
| FR-13 | Jendela dikendalikan relay. Bukaan sebagian berbasis waktu jalan motor. Perlu jeda minimum antar gerakan dan perlindungan anti-jepit | Hardware | Konfirmasi |
| FR-14 | Alarm dan aksi jendela tidak bergantung internet | [C251] | Dari rencana awal |
| FR-15 | Data dikirim tiap 5 detik (rata-rata dan maksimum) dan langsung saat status berubah. Data 5 detik disimpan 7 hari, catatan peringatan dan aktuator disimpan lama. Data simulasi diberi label | [desain-data-dfd.md](../3-bukti/desain-data-dfd.md) | Konfirmasi |
| FR-16 | Mode simulasi untuk dua skenario (sumber CO dari dalam: CO turun saat jendela dibuka, sumber dari luar: CO naik), berlabel jelas | Tidak ada CO asli | Usulan |

### 3.2 Kebutuhan non-fungsional

| ID | Kebutuhan | Dasar | Status |
|---|---|---|---|
| NFR-01 | Keterlambatan total deteksi CO (filter, konfirmasi, respons sensor) tidak lebih dari 10–20% waktu menuju bahaya. Contoh: CO luar 200 ppm dengan jendela tertutup mencapai 35 ppm dalam sekitar 10 menit, jadi anggaran 60–120 detik | [C251 Tabel 10.6] (cek PDF) | Usulan |
| NFR-02 | Bunyi dalam ≤ 5 detik sejak status berubah. Jendela mulai bergerak dalam ≤ 10 detik sejak ambang terlewati | [C251 Tabel 6.2] | Dari rencana awal |
| NFR-03 | Jendela tidak membuka dan menutup lebih dari N kali per 10 menit pada berkendara normal (N diputuskan tim) | UX | Konfirmasi |
| NFR-04 | Alarm palsu pada data udara bersih: nol per jam | Tolok ukur uji | Usulan |
| NFR-05 | Nilai CO ditampilkan sebagai **estimasi indikatif**. Pesan: "kemungkinan CO atau gas lain" | Sensor tidak selektif [1] | Terbukti (sifat sensor) |
| NFR-06 | Kadar atau waktu yang diubah pada uji harus tercatat bersama alasannya | Bukti laporan | Usulan |

### 3.3 Parameter

| Parameter | Nilai sementara | Dasar | Status |
|---|---|---|---|
| Interval keputusan | 1 detik | Lonjakan CO terpendek yang relevan sekitar 10 detik [C251] | Usulan |
| Interval kirim data | 5 detik (rata-rata dan maksimum) | Ukuran data dan kuota | Usulan |
| Filter CO | SMA 4 sampai 6 pada Rs (jumlah genap) | [D]: meredam sekitar 76%. SMA 6: respons 5 detik dan lonjakan lolos 4,9%, lebih baik dari EMA 0,2 kode sekarang | Usulan |
| Filter CO2 | Tidak ada, hanya tolak data rusak | Sensor sudah lambat | Usulan |
| Konfirmasi CO2 | 3 bacaan valid | [D]: nol bacaan rusak dalam sekitar 7900 | Usulan |
| Konfirmasi CO | 30 detik | Lebih lama dari filter, jauh di bawah menit-an standar | Usulan |
| Lama uji arah | 30 detik (sementara) | Batas bawah: respons filter. Batas atas: tambahan paparan (sekitar 17 ppm untuk 30 detik, 33 ppm untuk 60 detik pada contoh luar 200 dan dalam 35 ppm) | Konfirmasi |
| Kriteria "naik lagi" | Sekitar 8% perubahan Rs setelah filter (tiga kali simpangan baku noise) | [D] | Konfirmasi |
| Pemulihan | 60 detik | Sekitar 6 kali konstanta waktu filter, dan sama dengan [C251] | Usulan |
| Ambang CO tingkat bahaya | 87 ppm (bunyi lebih keras, aturan jendela sama dengan 35 ppm) | [14] | Disepakati (25 Okt malam) |
| Pemanasan | MiCS 5 menit, CO2 3 menit | Pilihan kode, belum terbukti (baseline belum stabil) | Usulan |
| Kalibrasi otomatis CO2 | Dimatikan untuk mobil | Saran manual untuk ruang yang jarang kena udara luar [2] | Usulan |
| Waktu buka jendela | t = ln((C0 − Cluar) / (Ctarget − Cluar)) / N. N diukur per mobil dari log penurunan CO2. Cluar diukur saat uji | Metode peluruhan [21] | Konfirmasi (butuh uji mobil) |
| Jeda minimum antar gerakan jendela | Belum ada angka | Spesifikasi power window | Konfirmasi |

### 3.4 Alur rencana (pseudocode)

```
SETIAP 1 DETIK:
  1. Baca CO2 dari MH-Z19C. Baca tegangan MiCS dari ADS1115.

  2. Cek data:
       CO2 gagal atau checksum salah       -> data CO2 tidak valid
       tegangan mentok atau tidak masuk akal -> data CO tidak valid
       nilai 410 atau 500 setelah sensor mulai ulang -> dianggap pemanasan, bukan "aman"

  3. Hitung:
       Rs dari tegangan -> filter SMA genap (4 sampai 6) -> rasio Rs/R0 -> ppm CO (estimasi)
       CO2 = angka dari sensor (tanpa filter tambahan)

  4. Kalau ada data tidak valid -> status GANGGUAN, jendela tidak digerakkan otomatis.
  5. Kalau masih masa pemanasan -> tidak ada alarm.

  6. ATURAN CO (prioritas tertinggi):
       kalau CO >= 35 selama 30 detik, atau CO >= batas bahaya, dan aturan CO belum aktif:
            aktifkan aturan CO: bunyi, buka jendela, mulai waktu uji arah
       kalau aturan CO aktif dan waktu uji selesai:
            kalau CO naik lagi melebihi kriteria -> sumber luar: tutup jendela, kunci (tidak menguji ulang)
            kalau CO turun                       -> sumber dalam: jendela tetap terbuka
       kalau aturan CO aktif dan CO < 30 selama 60 detik berturut-turut:
            matikan aturan CO, bunyi berhenti, jendela kembali tertutup
       selama aturan CO aktif: aturan CO2 DIABAIKAN

  7. ATURAN CO2 (hanya kalau aturan CO tidak aktif):
       CO2 >= 2500 selama 3 bacaan valid -> bunyi singkat satu kali + peringatan di aplikasi
       CO2 >= 4000 selama 3 bacaan valid -> bunyi + buka jendela (bukaan sesuai mobil)
       CO2 <  2400 selama 60 detik berturut-turut -> tutup jendela, hentikan bunyi

  8. Tampilkan di layar. Kirim data tiap 5 detik, atau segera saat status berubah. Catat log.

  9. Tombol "Saya Tahu" mematikan bunyi. Bunyi juga mati sendiri setelah 5 menit.
```

### 3.5 Alur kode yang berjalan sekarang (pseudocode)

Tanda ⚠ menandai bagian yang berbeda dari rencana. Kode: [src/main.cpp](../../src/main.cpp), 353 baris, versi 23 Oktober 2026.

```
SAAT DINYALAKAN:
  buka serial 115200, mulai sensor CO2 (UART 9600), nyalakan I2C, cek LCD
  cek ADS1115; kalau tidak ada: tampilkan error dan BERHENTI SELAMANYA
  ambil R0 dari memori (bawaan 1730 kOhm)
  ⚠ kalibrasi otomatis CO2 aktif (DISABLE_ABC = false)

SETIAP 1 DETIK:
  1. Cek perintah keyboard: 'r' = ukur R0 (120 detik di udara bersih), 'd' = R0 kembali ke bawaan
  2. Baca CO2 (9 byte, tunggu maksimal 0,5 detik, cek header dan checksum)
  3. Baca tegangan MiCS: rata-rata 16 pembacaan, atur gain otomatis (1.024 / 2.048 / 4.096 V)
        ⚠ saat saturasi data detik itu dibuang, tidak dibaca ulang
  4. Rs = RL x (VCC - V) / V  (RL = 9970, VCC = 4,64)
        ⚠ Rs dihaluskan EMA 0,2 (belum diputuskan)
        rasio = Rs / R0; ppm = (3,7 / rasio) ^ (1 / 0,856), dan 0 bila rasio >= 0,5
        ⚠ angka 3,7 dan 0,856 hasil membaca grafik datasheet
  5. Status CO: kalibrasi / pemanasan 300 detik / alarm
        alarm nyala: ppm >= 35 selama 10 detik berturut-turut
        alarm mati : ppm < 25 selama 30 detik berturut-turut
        ⚠ buzzer tetap bunyi selama 30 detik pemulihan walau ppm 0
  6. Status CO2: < 1000 BAIK, < 2000 SEDANG, < 5000 TINGGI, >= 5000 BAHAYA
        ⚠ tidak ada tingkat 2500 dan 4000, dan CO2 tidak membunyikan buzzer
        ⚠ pemanasan CO2 dihitung dari boot, tidak diulang kalau sensor mati
  7. Buzzer hanya untuk alarm CO. Tampilkan di LCD. Cetak satu baris CSV ke serial.
  8. Tunggu sampai genap 1 detik.
```

Bagian yang belum ada sama sekali di kode: aturan prioritas, uji arah, penggerak jendela, tingkat CO2 2500 dan 4000, mode simulasi, filter SMA 4, penanganan gangguan sensor, Wi-Fi dan MQTT.

---

## 4. Implementasi

### 4.1 Yang sudah ada

| Hal | Keterangan |
|---|---|
| Firmware pembaca | Membaca MiCS (lewat ADS1115) dan MH-Z19C, LCD, buzzer, kalibrasi R0, alarm CO 35/25, keluaran CSV serial |
| Perekaman data | Log berjam ke file (`logs/`), tahan hingga baterai laptop habis |
| Analisis | `filter_compare.py` dan `noise_profile.py`, dengan data dan hasil di `analisis/` |
| Dokumentasi | Tabel validasi parameter, analisis filter, batasan sistem, perbandingan [C251], desain data, daftar pustaka, daftar tugas, skenario uji mobil, agenda pertemuan tim |
| Sumber terverifikasi dari teks asli | Satish (Methods), NIOSH dan OSHA CO, WHO CO, UL 2034 Tabel 3, NIOSH CO2, ASHRAE |

### 4.2 Perbedaan kode dan rencana (pekerjaan firmware, T8)

| # | Kode sekarang | Rencana |
|---|---|---|
| 1 | Status CO2 di 1000, 2000, 5000 | Tingkat 2500 dan 4000, tanpa penilaian di 1000 |
| 2 | CO2 tidak membunyikan buzzer | Bunyi singkat di 2500, bunyi di 4000 |
| 3 | Kalibrasi otomatis CO2 aktif | Dimatikan untuk mobil |
| 4 | Pemanasan dihitung dari boot | Dihitung ulang bila sensor mati sebentar |
| 5 | Saturasi: data dibuang | Baca ulang setelah ganti gain |
| 6 | Alarm CO 35 ppm selama 10 detik, buzzer menahan 30 detik | 30 detik konfirmasi, pemulihan 60 detik, uji arah |
| 7 | Filter EMA 0,2 | SMA 4 (usulan) |
| 8 | Satu tingkat alarm CO | Waspada dan bahaya |
| 9 | Tidak ada pesan "kemungkinan gas lain" | Pesan itu ada |
| 10 | Tidak ada aturan prioritas, uji arah, penggerak jendela | Semua ada |

### 4.3 Yang perlu dikonfirmasi

**Keputusan tim:**
- Lama uji arah dan kriteria "CO naik lagi" (FR-05).
- Jumlah maksimum siklus buka-tutup jendela per 10 menit (NFR-03).
- Cara menguji deteksi CO tanpa CO asli (T16).
- Satu ESP final dengan Wi-Fi yang sehat, dan format pesan MQTT (FR-15).
- Retensi data dan jeda minimum antar gerakan jendela (FR-13).
- Lokasi sensor di kabin (T18). Koreksi isi [C251] (T15, T17, T20) dicatat sebagai bahan C-501, karena C-251 tidak direvisi.

**Perlu data atau pengukuran:**
- Uji mobil berlog: laju naik dan turun CO2, laju pertukaran udara (N) per mobil, noise di mobil (T11).
- Simulasi sapuan waktu tunggu pada log, hasilnya berupa tabel (T9, T10).
- Pengukuran catu 5 V dan tegangan MiCS oleh teman hardware (T6).
- Baseline MiCS yang stabil. Belum tercapai.

**Perlu dibaca:**
- Permenaker 5/2018 dan Permenkes 48/2016, datasheet ADS1115, Scully, studi kabin, dan Persily (T3 yang tersisa).

### 4.4 Rencana pengujian target luaran

| Target | Cara uji | Bisa? |
|---|---|---|
| Deteksi CO2 melewati 2500 (4 dari 5 uji) | Napas ke kotak tertutup, lima pengulangan, catat log | Bisa |
| Deteksi CO (4 dari 5 uji) | Mode simulasi berlabel. Uji respons dengan gas pereduksi pengganti (butana dari korek), **bukan CO** | Sebagian |
| Bunyi ≤ 5 detik sejak status berubah | Bandingkan jam di log dengan video | Bisa |
| Jendela mulai bergerak ≤ 10 detik | Log dan video | Bisa |
| Buka dan tutup jendela (4 dari 5 uji) | Lima pengulangan | Bisa |
| Data tampil di aplikasi dalam waktu tertentu | Bandingkan jam log perangkat dengan jam di aplikasi | Butuh Wi-Fi dan MQTT |
| Anggaran ≤ Rp2.000.000 | Jumlahkan nota | Bisa |

---

## 5. Keterbatasan

- Nilai CO adalah **estimasi indikatif** dari kurva datasheet. Tidak ada kalibrasi dengan gas atau alat referensi.
- Tidak ada kompensasi suhu dan kelembapan. Data kami menunjukkan baseline MiCS bergeser lebih dari 50% dalam 4 jam.
- MiCS-5524 tidak selektif: alkohol, hidrogen, dan gas lain ikut terbaca.
- Waktu respons MiCS tidak diketahui dan tidak bisa diukur tanpa CO asli. Waktu untuk CO ditentukan dari model, standar, dan simulasi.
- Diuji di breadboard, daya dari USB laptop, di kamar. Uji mobil adalah uji tambahan dan satu malam.
- Alat ini bukan alat keselamatan bersertifikat dan **tidak memenuhi UL 2034**.
- Bukti dampak CO2 pada kadar umum belum konsisten antar studi [21].

---

## Istilah

| Istilah | Arti sederhana |
|---|---|
| ppm | Bagian per sejuta, satuan kadar gas |
| Rs, R0 | Hambatan sensor sekarang, dan hambatan di udara bersih (patokan) |
| TWA | Rata-rata selama waktu kerja |
| Ceiling (C) | Batas yang tidak boleh dilewati sama sekali |
| IDLH | Kadar yang langsung berbahaya bagi nyawa |
| T90 | Waktu sampai pembacaan mencapai 90% dari perubahan sebenarnya |
| SMA, EMA | Dua cara merata-ratakan data agar lebih halus |
| Histeresis | Batas nyala dan batas padam dibuat berbeda agar alarm tidak nyala-mati terus |
| Uji arah | Membuka jendela sebentar untuk melihat apakah CO naik (sumber luar) atau turun (sumber dalam) |
| Peluruhan (decay) | Cara mengukur pertukaran udara dari seberapa cepat kadar gas turun |
