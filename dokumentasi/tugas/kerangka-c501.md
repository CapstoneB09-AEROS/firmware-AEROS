# Kerangka Laporan C-501 (Usulan)

Versi 27 Oktober 2026, **Bab 1-3 dirinci 10 November 2026** (bagian 3b). C-501 = laporan implementasi dan hasil, tenggat setelah expo. Kerangka ini mengikuti **template C-501 lengkap** yang kamu kirim (7 bab). Aturan template (batas kata, apa yang harus ada) dan isi untuk AEROS ada di bagian 3. **Rincian per subbab Bab 1-3 ada di bagian 3b**; Bab 4-7 masih tingkat bab. Isi tiap bab adalah usulanku.

## 1. Prinsip memilih apa yang ditampilkan
Kamu tidak perlu menjelaskan semua temuan. Tapi ada satu aturan: **apa pun yang mempengaruhi kesimpulan atau klaim laporan harus ada di badan laporan**, walau singkat. Yang tidak mempengaruhi cukup di lampiran atau cukup disiapkan jawabannya.

| Pertanyaan ke tiap temuan | Bila ya | Bila tidak |
|---|---|---|
| Apakah temuan ini mengubah arti klaim kita (akurasi, alarm, keselamatan)? | **Badan laporan**, 1-3 kalimat | lanjut |
| Apakah penguji bisa memeriksa angka kita lalu mendapatinya tidak konsisten tanpa temuan ini? | **Badan laporan**, singkat | lanjut |
| Apakah ini rincian cara kita menemukan sesuatu (analisis, debug, proses)? | **Lampiran** | lanjut |
| Apakah ini urusan internal (salah paham, perbaikan, diskusi tim)? | tidak dilaporkan | |

Alasan praktis: temuan yang kelihatan dari data kita sendiri (log, tabel) lebih merugikan kalau ditemukan penguji daripada kalau kita sebut sendiri sebagai batasan. Satu kalimat jujur lebih murah daripada pertanyaan yang tidak bisa dijawab.

## 2. Temuan yang kamu khawatirkan: cara memperlakukannya
| Temuan | Perlakuan | Dasar |
|---|---|---|
| **Siklus Rs sekitar 7-12 menit (+/-13-17%), penyebab tidak diketahui** | **Badan, 2 kalimat** di **4.2 Batasan Masalah** dan **5.1**; rincian (periode per ESP, korelasi) di lampiran | Di dekat ambang 35 ppm, +/-15% Rs setara sekitar +/-5-7 ppm, jadi menyentuh klaim alarm. Contoh kalimat: "Hambatan sensor berfluktuasi sekitar +/-15% dengan periode 7-12 menit yang penyebabnya belum diketahui; efeknya diredam dengan konfirmasi 30 detik dan tidak ditemukan alarm palsu pada sekitar 30 menit data mobil dan 4 jam data kamar." |
| Pola goyangan 0,5 Hz | **Badan**, karena itu dasar pemilihan SMA 6 (hasil utama). Penyebab: satu kalimat "diduga dari catu, belum terbukti" | |
| R0 tidak konstan, R0 di atas batas datasheet | Badan, 1-2 kalimat, bagian keputusan R0 tetap berlabel estimasi | mempengaruhi klaim ppm |
| Sensor tidak selektif (uji parfum) | **Badan**, 1 tabel kecil | klaim "CO" harus dibedakan dari "gas pereduksi" |
| Catu 5 V di bawah 4,9 V sebelum buck | Lampiran (rincian), badan hanya bila PCB/buck tidak selesai | |
| Model C-251 konservatif, N dan P terukur | **Badan** (validasi model) | hasil positif, nilai tambah |
| Analisis kode tim, tebakan ESP, masalah kompilasi | tidak masuk (bagian teman backend) | |
| 3,7/0,856 lawan 3,46/0,840 | Badan (4.3): nilai akhir dan cara (digitalisasi grafik), satu kalimat | |
| Anti-jepit tidak dibangun, tanpa CO nyata, tanpa kompensasi suhu | **Badan**, bagian 4.2 Batasan Masalah | sudah akui di C-251 |

## 3. Kerangka bab (mengikuti template C-501 lengkap)
Kolom "Aturan template" merangkum petunjuk di template. "Sumber" menunjuk berkas dokumentasi kita. Template berbentuk LaTeX: data dokumen diisi di `Data Capstone.tex` (judul, judul Inggris, nomor dokumen yaitu kode tim, nomor revisi, mahasiswa, dosen pembimbing, tempat), catatan revisi di `Revisi 00.tex` dan seterusnya, bukti bebas plagiasi sebagai `Bukti Bebas Plagiasi.pdf` di folder `fig`, sitasi angka dalam kurung siku (IEEE).

### Bagian awal
| Bagian | Aturan template | Isi untuk AEROS |
|---|---|---|
| Halaman Pengesahan, Bukti Bebas Plagiasi, Catatan Revisi | dari `Data Capstone.tex`; similarity report halaman utama; revisi V.x.y (x mayor, y minor), `Revisi 00` wajib. **Urutan di contoh kelompok lain**: Pengesahan, Bukti Bebas Plagiasi, Daftar Isi, Daftar Gambar, Daftar Tabel, Catatan Revisi, Intisari, Ringkasan Eksekutif, lalu Bab 1 | administrasi |
| **Intisari** | **maksimal 300 kata, satu paragraf**, untuk pembaca teknis, entitas lengkap. Komponen: masalah di C-251 (1-2 kalimat), analisis masalah (1-2), rencana solusi C-251 (1-2), proses di C-501 (2-4), analisis dan kesimpulan (2-3) | ditulis terakhir |
| **Ringkasan Eksekutif** | **500-1000 kata**, untuk **pembaca awam** (masyarakat, manajer, investor, dosen departemen lain), lebih panjang dari intisari, jelaskan apa yang menarik | ditulis terakhir; pakai kalimat aman di [komunikasi.md](../keputusan/komunikasi.md) bagian 8 |
| Daftar Gambar dan Tabel | otomatis | gambar: diagram 1-6, hasil analisis; tabel: uji, spesifikasi |

### Bab
| Bab | Aturan template | Isi untuk AEROS | Sumber | Tampil |
|---|---|---|---|---|
| **1 Pengantar** | ringkas, **maksimal 1200 kata (2 halaman)**: topik, motivasi, alur dokumen. 1.1: bagian yang tidak berubah dari C-251 boleh dipindahkan, yang berubah harus disesuaikan. Dugaan awal bahwa 1.2 dan 1.3 template hanya petunjuk LaTeX **dikoreksi oleh contoh kelompok lain** (1.2 Kendala, 1.3 Mata Kuliah); cek template | **rinci di bagian 3b, Bab 1** | | Badan |
| **2 Dasar Teori Pendukung** | terstruktur, tanpa pengulangan definisi; **ditulis sendiri, dilarang copy-paste, bebas plagiasi**; menyunting boleh dengan referensi tepat | **rinci di bagian 3b, Bab 2** | | Badan |
| **3 Analisis Studi Pustaka Kunci dan Pemilihan Metode** | **minimal 3 pustaka** paling berkaitan, analisis mendalam (disimulasikan bila perlu), heading per metode; **Pemilihan Metode** (di sini 3.7): kelebihan dan kekurangan lalu memilih; bila berbeda dari C-251, **jelaskan perubahan dan justifikasinya** | **rinci di bagian 3b, Bab 3** | | Badan |
| **4 Detail Implementasi** | **4.1** luaran yang dijanjikan (sinkron dengan lembar luaran; minimal satu jenis luaran) dan **spesifikasi** dengan besaran, satuan, standar keteknikan (tabel: No, Spesifikasi, Satuan, Standar, Keterangan). **4.2** batasan masalah: spesifikasi fungsional, fitur yang tidak disediakan, alasan. **4.3** detail rancangan **sampai level yang dapat diimplementasikan** | 4.1 jenis luaran: **firmware di development board**, **prototipe sistem**, **simulasi lengkap dengan Python** ([pemodelan_bab4_simulasi.py](../analisis/skrip/pemodelan_bab4_simulasi.py), bukan perangkat lunak jadi), sistem informasi (backend dan aplikasi); spesifikasi: target C-251 lawan status (bagian 4). 4.2 batasan sensor dan validasi. 4.3 arsitektur, hardware dan pin, algoritma, status dan bunyi, pesan v3, database | [batasan-sistem.md](../keputusan/batasan-sistem.md), [algoritma-firmware.md](../keputusan/algoritma-firmware.md), [komunikasi.md](../keputusan/komunikasi.md), [data-dan-database.md](../keputusan/data-dan-database.md), diagram 1-6 | Badan |
| **5 Pengujian dan Pembahasan** | tiap skenario: **tujuan**, **bagian yang diuji**, **skenario**, **analisis yang dikaitkan dengan ilmu dasar** (matematika, fisika, engineering science: kenapa fenomena terjadi) dan memastikan **spesifikasi atau kriteria sukses** terpenuhi. **5.2 Improvement**: jelaskan **logis dan kronologis** kenapa perlu tambahan atau revisi rancangan | 5.1.1 baseline kamar, noise, filter (uji 0 dan 2); 5.1.2 Civic (uji 1); 5.1.3 ruang pertemuan (uji 3); 5.1.4 Avanza: laju naik CO2, jendela, N (uji 4); 5.1.5 parfum, sensor tidak selektif (uji 5); 5.1.6 model lawan uji; 5.1.7 komunikasi (mode online, tanpa antrean offline); 5.1.8 demo gabungan; 5.2 bagian 6 di bawah | [rencana-uji.md](../pengujian/rencana-uji.md), [laporan uji 0-5](../pengujian/laporan/uji-1-mobil-civic-2026-10-25.md), [ringkasan-temuan.md](../analisis/ringkasan-temuan.md), [model-vs-uji.md](../analisis/model-vs-uji.md) | Badan |
| **6 Analisis Pengaruh Solusi Engineering Design** | dampak dalam konteks **global, ekonomis, lingkungan, sosial**; prediksi bila diadopsi luas | global: CO dan CO2 kabin, pedoman WHO, tidak ada aturan kabin di Indonesia; ekonomis: anggaran di bawah Rp2.000.000 lawan alat komersial; lingkungan: limbah elektronik, penggunaan AC dan ventilasi; sosial: keselamatan pengemudi, kelelahan akibat alarm palsu, privasi data lokasi dan waktu | [batasan-sistem.md](../keputusan/batasan-sistem.md), anggaran | Badan |
| **7 Kesimpulan dan Saran** | 7.1 ringkasan proses desain dan hasil uji; 7.2 saran perbaikan | jawab tiap tujuan dan spesifikasi; saran: kalibrasi dengan gas CO, sensor suhu dan kelembapan, uji lebih banyak mobil, anti-jepit, PCB dan catu stabil | | Badan |
| **Referensi** | IEEE bernomor, sitasi `[1]`, `[1, 2]`, `[1-4]` | | [daftar-pustaka.md](../referensi/daftar-pustaka.md) | |

Template **tidak memiliki bab lampiran**. Parameter dan sumbernya, kontrak pesan, catatan teknis (periode siklus Rs, korelasi, catu 5 V, R0), serta log dan skrip bisa dimasukkan ke dalam 4.3 dan 5.1, atau disimpan di repositori dan disebut di teks; tanyakan ke dosen apakah lampiran boleh.

### Aturan penulisan template
- Judul gambar di **bawah** gambar, judul tabel di **atas** tabel; acuan "Gambar 1.1", "Tabel 1.4", "Persamaan (1.1)".
- Gambar dan tabel diletakkan di bagian atas atau bawah halaman; tabel panjang memakai `longtable`.
- Sitasi hanya nomor, jangan "Ref. [4]" kecuali di awal kalimat.
- Dasar teori dan semua teks **ditulis sendiri**; kutipan harus bertanda dan tepat; dokumen diperiksa kemiripannya.

## 3b. Bab 1-3 terperinci (per subbab)

Cara baca: kolom "Membahas" = isi subbab itu, bukan judul saja. "Jangan" = hal yang sengaja **tidak** ditaruh di situ, supaya tidak tumpang tindih dengan bab lain. Panjang adalah usulan; hanya Bab 1 yang dibatasi template (1200 kata).

**Satu hal yang harus kamu putuskan dulu** (memengaruhi 3.1, 3.2, dan 3.7): sensor CO apa yang dilaporkan sebagai sistem akhir? Fakta: C-251 = MQ-7; kelima uji mobil (26 Okt-4 Nov) = MiCS-5524 + ADS1115; firmware v3.1 (6 Nov, setelah alat utama short) = MQ-7 lagi, tanpa ADS, CO2 nonaktif. Usulan kerangka di bawah: **MiCS-5524 = sistem yang diuji dan dilaporkan** (semua data ada di sini), **MQ-7 = rancangan C-251 dan jalur cadangan v3.1**. Bila kamu memilih lain, hanya bagian bertanda (S) di 3.1, 3.2, dan 3.7 yang berubah.

### Bab 1. Pengantar (maks. 1200 kata, sekitar 2 halaman)

Mengikuti contoh kelompok lain: **tiga subbab** (Latar Belakang, Kendala, Mata Kuliah). Kerangka versi pertama mengira 1.2 dan 1.3 template hanya petunjuk LaTeX dan mengisinya dengan "tujuan" dan "perubahan dari C-251"; contoh menunjukkan keduanya sebenarnya **Kendala** dan **Mata Kuliah**. Cek ke berkas template Bab 1 untuk memastikan. Perubahan dari C-251 sengaja tidak jadi subbab di sini; tempatnya di 3.7 dan 5.2.

| Subbab | Membahas | Sumber | Kata |
|---|---|---|---|
| **1.1 Latar Belakang** | 2-3 paragraf. Kabin mobil tertutup menjebak CO2 dari napas dan bisa kemasukan CO dari kendaraan lain; pengemudi tidak merasakannya sampai terlambat. Data lapangan: studi Hong Kong 51 mobil ber-AC, 96% melewati 1000 ppm, 16% di atas 5000 ppm, rata-rata saat jalan 3413 ppm. Dampak CO2 pada keputusan (Satish). Tidak ada pedoman kadar gas di kabin. Celah: alat yang ada belum memadukan peringatan dan tindakan otomatis (jendela). Paragraf penutup (2-3 kalimat): C-251 merencanakan sistem AEROS, C-501 melaporkan implementasi dan hasilnya; satu kalimat alur dokumen. **Jangan** masuk: hasil uji kita (Bab 5), daftar perubahan C-251 (3.7) | [27], [19], [11], [14], C-251 Bab 1 | 350-450 |
| **1.2 Kendala-Kendala yang Perlu Dipertimbangkan** | Tiga aspek seperti contoh, daftar bernomor, tiap butir 3-5 kalimat. **Teknis**: sensor gas semikonduktor tidak selektif dan bergeser (drift), tanpa gas CO acuan sehingga ppm hanya estimasi, resolusi ADC untuk sinyal puluhan mV, Wi-Fi tidak stabil di mobil, getaran dan suhu kabin, catu mobil. **Ekonomi**: anggaran <= Rp2.000.000. **Keselamatan dan keamanan**: tidak membuat gas CO sendiri tanpa protokol, anti-jepit jendela tidak dibangun, kelistrikan mobil, keamanan data (HMAC, TLS) dan privasi lokasi dan waktu. **Jangan** rinci spesifikasi (itu 4.2) | [batasan-sistem.md](../keputusan/batasan-sistem.md), [perbandingan-c251.md](../analisis/perbandingan-c251.md) T16, [hasil-dan-pengujian.md](hasil-dan-pengujian.md) bagian 1b | 250-300 |
| **1.3 Mata Kuliah dan Kemampuan yang Mendukung** | Daftar bernomor: nama mata kuliah + 2-3 kalimat kaitannya dengan bagian proyek. **Isi hanya mata kuliah yang benar-benar kamu ambil.** Pemetaan usulan (ganti nama sesuai transkrip): Sensor dan Transduser (MOX, NDIR), Sistem Mikroprosesor (ESP32), Teknik Pengolahan Isyarat Digital (SMA, EMA, Nyquist), Pengukuran dan Instrumentasi (kalibrasi R0, akurasi, resolusi ADC), Jaringan Komunikasi dan Data (MQTT, TLS), Pemrograman Dasar, Teknologi Basis Data (ERD, normalisasi 3NF), Pengalaman Pengguna (LCD, status, bunyi), Statistika (analisis noise, korelasi, persentil), Matematika (persamaan diferensial model CO2). Batasi 8-10 butir supaya Bab 1 tetap <= 1200 kata | transkrip kamu | 350-450 |

### Bab 2. Dasar Teori Pendukung (usulan 10-12 halaman)

Pola contoh: **tiap teknologi atau komponen yang dipakai punya subbab sendiri** (apa itu, cara kerja dasar, spesifikasi pokok), diakhiri kalimat "digunakan pada Capstone Project ini", dan komponen fisik diberi **gambar + "Sumber dari [n]"**. Aturan kita: ditulis sendiri, tiap definisi sekali saja, tanpa angka hasil kita. Definisi **filter, ADC, UART, I2C, dan metode keputusan** tidak di sini, tetapi di Bab 3 (contoh juga begitu: Bab 2 = apa komponennya, Bab 3 = metode mana yang dibandingkan).

| Subbab | Membahas | Sumber | Halaman |
|---|---|---|---|
| **2.1 Kualitas Udara Kabin dan Batas Paparan** | Setara "Indoor Health and Comfort" di contoh. CO: sumber, efek, ppm lawan mg/m3. CO2: sumber, efek pada kewaspadaan. Satu tabel batas: CO (NIOSH REL 35 ppm sampai 10 jam, plafon 200, IDLH 1200; OSHA 50; WHO 100 mg/m3 per 15 menit = 87 ppm, 35 per jam, 10 per 8 jam); CO2 (NIOSH dan OSHA 5000; ASHRAE: 1000 ppm bukan batas). Peraturan Indonesia | [11]-[14], [16], [19], [21], [25], [26] | 1,5 |
| **2.2 Model Kesetimbangan Massa CO2 Kabin** | dC/dt = P - N(C - C_luar), P = n x G x 1e6 / V; arti tiap suku; penyelesaian naik dan turun; laju pertukaran udara N. Asumsi well-mixed. Dipakai di 4.1, divalidasi di 5.1.6 | C-251 Bab 4 (Pers. 4.1-4.4), [pemodelan_bab4_simulasi.py](../analisis/skrip/pemodelan_bab4_simulasi.py) | 1,5 |
| **2.3 Internet of Things** | **2.3.1 MQTT**: publish/subscribe, broker, QoS 0/1/2, keep alive, last will; TLS dan tanda tangan HMAC-SHA256 dengan nonce. **2.3.2 HTTP dan REST**: dipakai untuk portal Wi-Fi ESP32 dan akses Supabase. Kerjakan bersama teman backend | dokumentasi teman, [komunikasi.md](../keputusan/komunikasi.md) | 1,5 |
| **2.4 Development Board: ESP32** | Mikrokontroler, Wi-Fi, ADC 12-bit, UART, I2C, GPIO; versi DevKitC V4. Gambar papan | datasheet Espressif (**belum di daftar pustaka**) | 1 |
| **2.5 Sensor** | **2.5.1 Sensor gas semikonduktor (MOX)**: prinsip Rs turun oleh gas pereduksi, pembagi tegangan dengan RL, rasio Rs/R0, hubungan pangkat ppm = A (Rs/R0)^B, pemanas, tidak selektif, drift, suhu dan kelembapan; MQ-7 dan MiCS-5524 masing-masing satu paragraf dan gambar. **2.5.2 Sensor CO2 NDIR**: penyerapan inframerah, UART, T90, pemanasan, ABC; MH-Z19B dan MH-Z19C. **Jangan** bandingkan di sini (itu 3.1) | [1], [2], [4], [6], [7] | 2,5 |
| **2.6 Komponen Antarmuka dan Aktuator** | **2.6.1 ADS1115** (ADC eksternal 16-bit I2C; hanya fungsi, perbandingan di 3.2). **2.6.2 LCD I2C 16x2 dan buzzer aktif**. **2.6.3 Relay dan penggerak jendela**: relay sebagai saklar, pulsa turun dan naik, waktu motor. Tiap komponen satu gambar | [3] (belum dibaca langsung), datasheet modul | 1,5 |
| **2.7 Sumber Energi DC** | Catu mobil 12 V, buck converter ke 5 V, adaptor USB; mengapa catu 5 V stabil penting untuk sensor MOX | [hardware-wiring.md](../keputusan/hardware-wiring.md), [1] | 0,5-1 |
| **2.8 Sistem Informasi** | Supabase (PostgreSQL, REST), worker MQTT, aplikasi Flutter; peran tiap bagian. Ditulis teman backend dan software | dokumentasi teman, [data-dan-database.md](../keputusan/data-dan-database.md) | 1 |
| **2.9 Bahasa Pemrograman** | C/C++ (firmware ESP32 lewat Arduino framework dan PlatformIO), JavaScript (worker Node.js), Dart (Flutter, **cek dengan teman software**). Satu paragraf per bahasa: asal, ciri, alasan dipakai | buku atau standar bahasa (**cari**) | 1 |

### Bab 3. Analisis Studi Pustaka Kunci dan Pemilihan Metode (usulan 10-12 halaman)

Pola contoh: **dikelompokkan per kategori metode** (konversi sinyal, komunikasi data, filtering, ...), tiap metode satu heading, ada subbab "Perbandingan". Aturan template: **minimal 3 pustaka kunci**, analisis mendalam (boleh simulasi), dan **setiap perbedaan dari C-251 dijelaskan dan dibenarkan**. Contoh tidak menampakkan judul "Pemilihan Metode" di daftar isinya; saya tetap menaruhnya sebagai subbab terakhir (3.7) karena aturan template meminta keputusan metode, nomornya boleh kamu sesuaikan. Pola tiap subbab: *apa yang dikatakan pustaka -> kelebihan dan kekurangan -> artinya untuk AEROS -> analisis kita sendiri*.

**Pustaka kunci yang dipakai** (lebih dari 3 supaya ada cadangan bila ada yang gagal dibaca):

| Pustaka | Dipakai di | Status baca (dari [daftar-pustaka.md](../referensi/daftar-pustaka.md)) | Yang harus dibereskan |
|---|---|---|---|
| Datasheet MiCS-5524 [1] | 3.1 | dibaca langsung | tidak ada |
| Datasheet MQ-7 | 3.1 | **belum ada di daftar pustaka** | cari, baca, tambahkan |
| ADS1115 [3] dan dokumentasi ADC ESP32 | 3.2 | [3] belum dibaca langsung; ESP32 belum ada | baca dan tambahkan |
| Smith, bab 15 rata-rata bergerak [8] | 3.4 | dari ringkasan | baca langsung, catat halaman |
| Spesifikasi MQTT (OASIS) atau sumber setara | 3.3 | **belum ada di daftar pustaka** | tambahkan |
| Dokumentasi PostgreSQL atau Supabase, dan buku basis data untuk normalisasi 3NF | 3.6 | **belum ada di daftar pustaka** | tambahkan bersama teman backend |
| Barnes dkk., kabin Hong Kong [27] | 3.5 | dibaca langsung | tidak ada |
| Satish dkk. [19] dan ASHRAE [21] | 3.5 | Satish: hanya Methods; ASHRAE dibaca langsung | baca Results Satish |
| Dirks dkk., CO di kabin [28] | 3.5 | hanya abstrak | baca teks penuh (server menolak, coba jalur lain) |
| CPSC, uji alarm CO UL 2034 [15] | 3.5 | Tabel 3 dibaca | tahun dan nomor laporan |

| Subbab | Membahas | Analisis kita sendiri (bukti) | Sumber data |
|---|---|---|---|
| **3.1 Analisis Pustaka Sensor Gas** | **3.1.1 Sensor CO**: MQ-7 (C-251: pemanas bersiklus 5 V dan 1,4 V) lawan MiCS-5524 (pemanas tanpa siklus, modul I2C lewat ADS1115); satu tabel kelebihan dan kekurangan; tidak selektif pada keduanya. **3.1.2 Sensor CO2**: MH-Z19B (0-5000 ppm, +/-50 ppm) lawan MH-Z19C (400-5000 ppm, +/-(50 ppm + 5%)); akibat akurasi lebih longgar pada margin ambang 4000 | Digitalisasi kurva datasheet MiCS-5524: A = 3,46 dan beta = 0,840, selisih < 1,5% dari pembacaan mata di 35-100 ppm. R0 terukur di atas batas datasheet. Uji parfum: Rs turun 92%. (S) bila MQ-7: kurva ppm = 99,042 x (Rs/R0)^-1,518, catu 5 V tetap berarti **menyimpang dari siklus pemanas datasheet**, tulis sebagai batasan | [parameter-dan-sumber.md](../keputusan/parameter-dan-sumber.md) A1, [digitasi_kurva_co.py](../analisis/skrip/digitasi_kurva_co.py), [analisis_parfum.py](../analisis/skrip/analisis_parfum.py), [firmware-v3.1/README.md](../../firmware-v3.1/README.md) |
| **3.2 Analisis Pustaka Konversi Sinyal** | **3.2.1 ADC**: sampling, kuantisasi, Nyquist (definisi sekali di sini). Perbandingan ADC internal ESP32 (12-bit, tak linier di ujung rentang, saturasi) lawan ADS1115 (16-bit, I2C, penguat terprogram). DAC tidak dipakai, tidak dibahas | Tegangan keluaran MiCS pada udara bersih hanya puluhan mV (23-50 mV pada rekaman 25 Okt), sehingga resolusi ADC menentukan kualitas Rs: hitung langkah (LSB) ESP32 lawan ADS1115 pada rentang itu. (S) bila MQ-7 lewat pembagi 10k/20k ke GPIO34: batas atas dan saturasi ADC ESP32 | [ringkasan-temuan.md](../analisis/ringkasan-temuan.md) temuan 2, [firmware-v3.1/README.md](../../firmware-v3.1/README.md) |
| **3.3 Perbandingan Metode Komunikasi Data** | **3.3.1 Sensor ke ESP32**: analog, UART (MH-Z19C), I2C (ADS1115, LCD), SPI sebagai pembanding; kecepatan, jumlah pin, jarak. **3.3.2 ESP32 ke server**: MQTT lawan HTTP (overhead, push lawan pull, QoS, last will) dan keamanan TLS + HMAC. Ditulis bersama teman backend | Alasan MQTT; hasil uji komunikasi bukan di sini (5.1.7) | [komunikasi.md](../keputusan/komunikasi.md) |
| **3.4 Analisis Pustaka Metode Filtering** | Satu heading per metode, sambil menautkan ke istilah contoh: **3.4.1 Moving average** (SMA ganjil lawan genap, itu FIR), **3.4.2 EMA** (IIR, setara LPF orde satu), **3.4.3 Median** (nonlinier, tahan lonjakan). Respons frekuensi: SMA jumlah genap punya nol di 0,5 Hz. Kompromi kehalusan lawan keterlambatan. Pustaka kunci Smith [8] | Simulasi pada rekaman 4 jam: 95% goyangan Rs adalah pola bergantian tiap detik; SMA genap meredam sekitar 76% (SMA 3 hanya 60%, SMA 5 69%); median 5 hanya 2%; SMA 6 lawan EMA 0,2 (v0): sisa noise 0,7-1,8% lawan 1,0-2,3%, lonjakan lolos 4,9% lawan 5,9%. Syarat: pola harus tetap di 0,5 Hz (ulang bila rangkaian berubah). Penyebabnya tulis "diduga dari catu, belum terbukti" | [filter.md](../analisis/filter.md), [ringkasan-temuan.md](../analisis/ringkasan-temuan.md), [filter_compare.py](../analisis/skrip/filter_compare.py), [noise_profile.py](../analisis/skrip/noise_profile.py) |
| **3.5 Analisis Pustaka Strategi Keputusan Peringatan** | **3.5.1 Ambang CO2**: Satish (bukti lemah, jadi 2500 hanya peringatan), ASHRAE (tidak ada batas), NIOSH dan OSHA (5000), Barnes (kabin nyata 3413). **3.5.2 Ambang CO**: NIOSH 35, WHO 87 per 15 menit, UL 2034 (70 ppm 60-240 menit, 150 ppm 10-50 menit, 400 ppm 4-15 menit). **3.5.3 Pemicu**: ambang mutlak, perubahan relatif, konfirmasi waktu, histeresis, mesin status. **3.5.4 Sumber dalam atau luar**: uji arah, dengan Dirks [28] (sirkulasi dalam paling efektif menghindari lonjakan CO) | Ambang perubahan relatif ditolak: kriteria 8% dan 15% terlampaui gerakan alami Rs, 25% tidak terlampaui dalam sekitar 28.000 detik tanpa gas. 4000, bukan 2500 atau 5000: akurasi sensor +/-250 ppm, jeda sensor, batas 5000, siklus jendela 15,6 menit. Konfirmasi 30 detik jauh lebih cepat dari batas respons UL 2034. **Siklus Rs 7-12 menit (+/-15%) sebut jujur di sini** | [peringatan-dan-ambang.md](../keputusan/peringatan-dan-ambang.md), [ringkasan-temuan.md](../analisis/ringkasan-temuan.md), [analisis_fase.py](../analisis/skrip/analisis_fase.py) |
| **3.6 Analisis Pustaka Sistem Informasi (pemantauan dan kontrol IoT)** | Setara "website pemantauan dan kontrol IoT" di contoh. **3.6.1 Aliran data**: ESP32 langsung ke database lawan lewat broker + worker (worker memeriksa HMAC, nonce, jendela waktu, lalu mengirim ACK bertanda tangan setelah data tersimpan). **3.6.2 Basis data**: relasional (PostgreSQL di Supabase) lawan alternatif lain (dokumen, deret waktu); normalisasi sampai 3NF; langganan realtime. **3.6.3 Aplikasi pemantauan**: Flutter (ponsel) lawan web; tampilan status, riwayat peringatan, notifikasi. Ditulis teman backend dan software; kamu cek konsistensi dengan firmware | Mengapa tiap bacaan membawa `co_level` dan `co2_level` per gas (bukan kolom gas bertulisan "CO,CO2": melanggar 1NF; `max()` pada teks salah urut); `status` dibuat kolom turunan agar tidak ada ketergantungan transitif; `device_state` pengecualian sengaja (cache realtime). Worker: 36 uji lulus. Latensi bacaan sampai database 1,45 detik (median, uji 8) | [rancangan-database-mvp.md](../keputusan/rancangan-database-mvp.md), [rancangan-worker-mvp.md](../keputusan/rancangan-worker-mvp.md), [data-dan-database.md](../keputusan/data-dan-database.md), [komunikasi.md](../keputusan/komunikasi.md), [uji 8](../pengujian/laporan/uji-8-meja-wifi-mqtt-firmware-v2.3-2026-11-03.md) |
| **3.7 Pemilihan Metode** | Satu tabel besar: Aspek / Pilihan C-251 / Alternatif / **Dipilih** / Alasan (satu kalimat) / Dibuktikan di bagian. Baris: sensor CO (S), sensor CO2, ADC, siklus baca, filter, ambang CO2 peringatan, ambang CO2 tindakan, ambang CO, pemicu (rata-rata lawan nilai langsung dengan konfirmasi), syarat selesai, aktuator jendela (servo lawan relay dan waktu motor, bukaan penuh lawan setengah), komunikasi (antrean offline lawan mode online dengan penyangga kecil). **Sisi software**: aliran data (langsung lawan broker + worker), format pesan (v2 ke v4, nilai level per gas), basis data (tabel gas dan normalisasi 3NF, tabel `actuator_logs` dibuang), platform aplikasi (tidak berubah dari C-251: Flutter). Baris sisi software diisi bersama teman backend dan software. Di bawah tabel: paragraf **pengakuan** bagian C-251 yang tidak berlaku lagi (ambang bertentangan antar bab, atribusi 35 ppm dan ASHRAE) | | [keputusan.md](../keputusan/keputusan.md), bagian 6 file ini (bahan 5.2), [perbandingan-c251.md](../analisis/perbandingan-c251.md) bagian 3 dan 4 |

### Pembagian isi Bab 1-3 dan 4-5 (agar tidak ganda)
- **Bab 3 menjawab "kenapa metode ini"** (pustaka dan analisis data untuk memilih). **Bab 4 menjawab "apa tepatnya yang dibangun"** (nilai akhir, pin, pseudocode). **Bab 5 menjawab "apakah berhasil"** (uji dan angka hasil). Angka final hanya di Bab 4, Bab 3 menyebut alasan.
- Bagian 6 file ini (Improvement) menjadi bahan **5.2**, dan baris-barisnya harus cocok dengan tabel 3.7.

### Cek sebelum menulis (dari daftar pustaka; belum terverifikasi)
1. Satish: baca Results sebelum menulis "6 dari 9 indikator pada 1000 ppm dan 7 pada 2500 ppm" (klaim C-251).
2. Dirks [28]: **jangan** pakai "171 ppm dalam 10 detik" dan "pulih lebih dari 11 menit"; abstrak hanya mendukung puncak sekitar 170 ppm dan sirkulasi dalam paling baik menghindari lonjakan.
3. Barnes [27]: rata-rata 3413 ppm adalah pendekatan (4 mobil melewati batas alat 8888 ppm).
4. Atribusi: 35 ppm adalah **NIOSH REL** (sampai 10 jam), bukan OSHA 8 jam; 1000 ppm bukan batas ASHRAE.
5. Belum diverifikasi: hemoglobin 240 kali, "belum ada standar kualitas udara kabin di Indonesia", angka tabel Permenaker 5/2018 dan Permenkes 48/2016.
6. Lengkapi data kepustakaan [6], [7], [22]-[24] atau jangan kutip.
7. Tanda "[cek PDF]" di [perbandingan-c251.md](../analisis/perbandingan-c251.md): lihat langsung di PDF C-251 sebelum menyalin angka Tabel 6.2.

---

## 4. Data yang dibutuhkan lawan yang sudah ada
Tiap klaim di laporan sebaiknya punya data. Yang kosong adalah yang perlu dikerjakan sebelum atau sesudah expo.

| Klaim atau spesifikasi (C-251) | Data yang ada | Kekurangan |
|---|---|---|
| Deteksi CO2 melewati 2500 (4 dari 5 uji) | 3 kali melewati 2500 di mobil dan satu kali di ruang rapat tidak (laporan uji 1, 3, 4) | belum ada 5 pengulangan terkontrol; firmware baru belum dipakai |
| Deteksi CO | uji parfum (respons sensor), mode simulasi nanti | tanpa CO nyata; tulis di 4.2 sebagai batasan |
| Bunyi <= 5 detik, jendela <= 10 detik sejak ambang | firmware baru belum ada | ukur dengan log dan video di meja |
| Buka dan tutup jendela (4 dari 5 uji) | jendela dibuka manual di Avanza; `WAKTU_SETENGAH` belum diukur | uji dengan penggerak jendela |
| Data tampil di aplikasi dalam waktu tertentu | belum | uji latensi dengan tim backend dan software |
| Alarm palsu nol per jam pada udara bersih | sekitar 30 menit mobil dan sekitar 4 jam kamar, tanpa alarm | uji dengan firmware baru |
| Model Bab 4 sesuai kenyataan | [model-vs-uji.md](../analisis/model-vs-uji.md) | satu mobil per angka |
| Anggaran <= Rp2.000.000 | belum dihitung ulang | jumlahkan nota (komponen berubah) |

## 5. Pertanyaan yang mungkin ditanyakan, dan jawaban singkat
| Pertanyaan | Jawaban (dengan bukti) |
|---|---|
| Seberapa akurat CO? | Tidak diklaim akurat; estimasi dari kurva datasheet (digitalisasi grafik, selisih < 1,5% di 35-100 ppm), belum dikalibrasi gas. Bukti: parameter-dan-sumber.md A1 |
| Kenapa baseline sensor naik-turun? | Fluktuasi sekitar +/-15% (7-12 menit), penyebab belum diketahui; kandidat catu. Diredam konfirmasi 30 detik; tidak ada alarm palsu pada data yang ada |
| Bagaimana kalau gas lain (parfum)? | Terbukti terbaca sebagai CO (Rs -92%, estimasi 72-83 ppm selama 14 detik); konfirmasi 30 detik menolaknya di ruang besar, kabin belum diuji; pesan "kemungkinan CO atau gas lain" |
| Kenapa SMA 6, bukan EMA? | 95% goyangan berupa pola bergantian per detik; jumlah genap menghapusnya; sisa noise 0,7-1,8% lawan 1,0-2,3% |
| Kenapa 4000 ppm, bukan 2500 atau 5000? | Akurasi sensor +/-250 ppm, jeda sensor, batas paparan kerja 5000, pedoman ISS 4000-5000; siklus buka-tutup 15,6 menit |
| Kenapa model C-251 beda dari uji? | Strukturnya cocok; parameter literatur konservatif (produksi nyata sekitar 54%, N berbeda per mobil) |
| Kalau internet mati? | Alarm dan jendela jalan di ESP32. Mode online (keputusan 29 Okt): tanpa antrean offline di flash; penyangga RAM menahan 4 data terbaru sampai ACK, data lebih tua dari 30 detik dibuang. Data selama putus tidak dikirim ulang |
| Kalau jendela menjepit? | Anti-jepit tidak dibangun; dicatat sebagai batasan; tanya hardware apakah jendela Classy punya anti-jepit pabrik |

## 6. Bahan untuk 5.2 Improvement
Perubahan dari iterasi pertama ke hasil akhir, semuanya dengan data:

| Dari | Ke | Alasan (data) |
|---|---|---|
| Filter EMA 0,2 | SMA 6 | sisa noise 0,7-1,8% lawan 1,0-2,3%; lompatan 0-10 ppm 1-2 kali lawan 14-19 |
| Kriteria uji arah 8% | 25% | gerakan alami Rs melewati 8% pada 8-13% waktu |
| Pemanasan CO 5 menit | 3 menit | nyala dingin 26 Okt: Rs stabil dalam 3 menit |
| Ambang CO2 tindakan 2500 | 4000 (2500 hanya peringatan) | akurasi sensor, jeda, batas paparan; siklus jendela 15,6 menit |
| CO2 selesai < 2400 selama 60 detik | < 2500 selama 10 detik | data Avanza: CO2 terus turun sesudah jendela ditutup |
| Jendela dibuka penuh | setengah lewat waktu motor | saran teman elektro; N terukur tinggi |
| A=3,7 dan beta=0,856 (baca mata) | 3,46 dan 0,840 (digitalisasi piksel) | hasil bisa diulang |
| Kode demo acak (versi komunikasi awal) | data sensor nyata lewat tugas terpisah | siklus 1 detik tidak tertahan jaringan |
| Pesan v2 | v3 (nilai puncak, `null` untuk yang tidak diketahui) | kebutuhan firmware |

## 7. Langkah berikutnya
1. Cek ke dosen aspek yang diminta di Bab 6 dan apakah lampiran boleh ditaruh setelah Referensi.
2. Kumpulkan data yang kosong di bagian 4 (setelah firmware baru dan uji meja).
3. Mulai dari **Bab 4 dan Bab 5**: isinya paling banyak sudah ada di dokumentasi, tinggal dirapikan. Intisari (maks. 300 kata) dan Ringkasan Eksekutif (500-1000 kata, bahasa awam) ditulis paling akhir.
4. Pembagian penulisan: komunikasi dan aplikasi oleh teman backend dan software (bagian 3.5, 4.3, dan 5.1.7), sisanya kamu.
