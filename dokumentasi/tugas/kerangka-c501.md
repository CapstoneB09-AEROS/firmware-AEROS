# Kerangka Laporan C-501 (Usulan)

Versi 27 Oktober 2026. C-501 = laporan implementasi dan hasil, tenggat setelah expo. Kerangka ini mengikuti **template C-501 lengkap** yang kamu kirim (7 bab). Aturan template (batas kata, apa yang harus ada) dan isi untuk AEROS ada di bagian 3. Isi tiap bab adalah usulanku.

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
| Halaman Pengesahan, Bukti Bebas Plagiasi, Catatan Revisi | dari `Data Capstone.tex`; similarity report halaman utama; revisi V.x.y (x mayor, y minor), `Revisi 00` wajib | administrasi |
| **Intisari** | **maksimal 300 kata, satu paragraf**, untuk pembaca teknis, entitas lengkap. Komponen: masalah di C-251 (1-2 kalimat), analisis masalah (1-2), rencana solusi C-251 (1-2), proses di C-501 (2-4), analisis dan kesimpulan (2-3) | ditulis terakhir |
| **Ringkasan Eksekutif** | **500-1000 kata**, untuk **pembaca awam** (masyarakat, manajer, investor, dosen departemen lain), lebih panjang dari intisari, jelaskan apa yang menarik | ditulis terakhir; pakai kalimat aman di [komunikasi.md](../keputusan/komunikasi.md) bagian 8 |
| Daftar Gambar dan Tabel | otomatis | gambar: diagram 1-6, hasil analisis; tabel: uji, spesifikasi |

### Bab
| Bab | Aturan template | Isi untuk AEROS | Sumber | Tampil |
|---|---|---|---|---|
| **1 Pengantar** | ringkas, **maksimal 1200 kata (2 halaman)**: topik, motivasi, alur dokumen. 1.1: bagian yang tidak berubah dari C-251 boleh dipindahkan, yang berubah harus disesuaikan. Bagian 1.2 dan 1.3 template adalah petunjuk pemakaian LaTeX (tanyakan apakah diganti isi sendiri) | konteks masalah, tujuan, hubungan dengan C-251 (tidak direvisi), alur dokumen | [keputusan.md](../keputusan/keputusan.md) bagian 1 | Badan |
| **2 Dasar Teori Pendukung** | terstruktur, tanpa pengulangan definisi; **ditulis sendiri, dilarang copy-paste, bebas plagiasi**; menyunting boleh dengan referensi tepat | cara kerja sensor MOX dan NDIR; model kesetimbangan massa (Pers. 4.1-4.4); sampling dan filter SMA/EMA (mengapa jumlah genap menghapus pola bergantian); komunikasi (MQTT, TLS, HMAC); Supabase dan Flutter secara ringkas | C-251 Bab 2 dan 4, [daftar-pustaka.md](../referensi/daftar-pustaka.md) | Badan |
| **3 Analisis Studi Pustaka Kunci dan Pemilihan Metode** | **minimal 3 pustaka** paling berkaitan, analisis mendalam (disimulasikan bila perlu), heading per metode; **3.4 Pemilihan Metode**: kelebihan dan kekurangan lalu memilih; bila berbeda dari C-251, **jelaskan perubahan dan justifikasinya** | 3.1 sensor CO (MQ-7, MiCS-5524); 3.2 penghalusan sinyal (EMA, SMA, median); 3.3 strategi keputusan CO (ambang mutlak, perubahan relatif, **uji arah**); 3.4 pemilihan metode (tabel pilihan dan alasan; jendela servo atau relay berbasis waktu; komunikasi) | [peringatan-dan-ambang.md](../keputusan/peringatan-dan-ambang.md), [filter.md](../analisis/filter.md), [perbandingan-c251.md](../analisis/perbandingan-c251.md), [keputusan.md](../keputusan/keputusan.md) | Badan |
| **4 Detail Implementasi** | **4.1** luaran yang dijanjikan (sinkron dengan lembar luaran; minimal satu jenis luaran) dan **spesifikasi** dengan besaran, satuan, standar keteknikan (tabel: No, Spesifikasi, Satuan, Standar, Keterangan). **4.2** batasan masalah: spesifikasi fungsional, fitur yang tidak disediakan, alasan. **4.3** detail rancangan **sampai level yang dapat diimplementasikan** | 4.1 jenis luaran: **firmware di development board**, **prototipe sistem**, **simulasi lengkap dengan Python** ([pemodelan_bab4_simulasi.py](../analisis/skrip/pemodelan_bab4_simulasi.py), bukan perangkat lunak jadi), sistem informasi (backend dan aplikasi); spesifikasi: target C-251 lawan status (bagian 4). 4.2 batasan sensor dan validasi. 4.3 arsitektur, hardware dan pin, algoritma, status dan bunyi, pesan v3, database | [batasan-sistem.md](../keputusan/batasan-sistem.md), [algoritma-firmware.md](../keputusan/algoritma-firmware.md), [komunikasi.md](../keputusan/komunikasi.md), [data-dan-database.md](../keputusan/data-dan-database.md), diagram 1-6 | Badan |
| **5 Pengujian dan Pembahasan** | tiap skenario: **tujuan**, **bagian yang diuji**, **skenario**, **analisis yang dikaitkan dengan ilmu dasar** (matematika, fisika, engineering science: kenapa fenomena terjadi) dan memastikan **spesifikasi atau kriteria sukses** terpenuhi. **5.2 Improvement**: jelaskan **logis dan kronologis** kenapa perlu tambahan atau revisi rancangan | 5.1.1 baseline kamar, noise, filter (uji 0 dan 2); 5.1.2 Civic (uji 1); 5.1.3 ruang pertemuan (uji 3); 5.1.4 Avanza: laju naik CO2, jendela, N (uji 4); 5.1.5 parfum, sensor tidak selektif (uji 5); 5.1.6 model lawan uji; 5.1.7 komunikasi dan offline first; 5.1.8 demo gabungan; 5.2 bagian 6 di bawah | [rencana-uji.md](../pengujian/rencana-uji.md), [laporan uji 0-5](../pengujian/laporan/uji-1-mobil-civic-2026-10-25.md), [ringkasan-temuan.md](../analisis/ringkasan-temuan.md), [model-vs-uji.md](../analisis/model-vs-uji.md) | Badan |
| **6 Analisis Pengaruh Solusi Engineering Design** | dampak dalam konteks **global, ekonomis, lingkungan, sosial**; prediksi bila diadopsi luas | global: CO dan CO2 kabin, pedoman WHO, tidak ada aturan kabin di Indonesia; ekonomis: anggaran di bawah Rp2.000.000 lawan alat komersial; lingkungan: limbah elektronik, penggunaan AC dan ventilasi; sosial: keselamatan pengemudi, kelelahan akibat alarm palsu, privasi data lokasi dan waktu | [batasan-sistem.md](../keputusan/batasan-sistem.md), anggaran | Badan |
| **7 Kesimpulan dan Saran** | 7.1 ringkasan proses desain dan hasil uji; 7.2 saran perbaikan | jawab tiap tujuan dan spesifikasi; saran: kalibrasi dengan gas CO, sensor suhu dan kelembapan, uji lebih banyak mobil, anti-jepit, PCB dan catu stabil | | Badan |
| **Referensi** | IEEE bernomor, sitasi `[1]`, `[1, 2]`, `[1-4]` | | [daftar-pustaka.md](../referensi/daftar-pustaka.md) | |

Template **tidak memiliki bab lampiran**. Parameter dan sumbernya, kontrak pesan, catatan teknis (periode siklus Rs, korelasi, catu 5 V, R0), serta log dan skrip bisa dimasukkan ke dalam 4.3 dan 5.1, atau disimpan di repositori dan disebut di teks; tanyakan ke dosen apakah lampiran boleh.

### Aturan penulisan template
- Judul gambar di **bawah** gambar, judul tabel di **atas** tabel; acuan "Gambar 1.1", "Tabel 1.4", "Persamaan (1.1)".
- Gambar dan tabel diletakkan di bagian atas atau bawah halaman; tabel panjang memakai `longtable`.
- Sitasi hanya nomor, jangan "Ref. [4]" kecuali di awal kalimat.
- Dasar teori dan semua teks **ditulis sendiri**; kutipan harus bertanda dan tepat; dokumen diperiksa kemiripannya.

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
| Kalau internet mati? | Alarm dan jendela jalan di ESP32; data ditulis ke flash dan dikirim setelah tersambung, dihapus hanya setelah database mengonfirmasi |
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
