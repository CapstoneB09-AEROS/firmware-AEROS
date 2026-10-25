# Batasan Sistem

Dua jenis batasan:
- **A. Batasan operasi sensor**: kondisi yang tidak boleh dilanggar (dari pabrikan).
- **B. Batasan validasi**: hal yang tidak dilakukan dalam penelitian ini beserta alasannya, dan cara menuliskannya.

Terkait: [validasi-parameter.md](validasi-parameter.md), [desain-peringatan.md](desain-peringatan.md).

---

## A. Batasan operasi sensor

### MiCS-5524 (CO)

Sumber: datasheet SGX Sensortech MiCS-5524 rev 6 (sudah dibaca).

| Batasan | Isi | Implikasi |
|---|---|---|
| Zat perusak lapisan sensor | Tidak boleh terpapar konsentrasi tinggi pelarut organik, uap silikon, atau asap rokok | Dapat merusak lapisan sensor secara **permanen**. Di mobil: asap rokok, pembersih berbasis pelarut, dan produk silikon (misalnya semir dasbor) dihindari |
| Tegangan pemanas | Tegangan pemanas di atas batas maksimum merusak sensor. Catu 4.9–5.1 V | Catu harus stabil. Kode mencatat 4.64 V, di bawah rentang |
| Resistor beban | RLOAD minimal 820 Ω | Rangkaian sekarang 9970 Ω, aman |
| Pelindung | Sensor harus dipasang dalam kemasan berfilter yang melindungi dari cipratan air dan debu | Perlu dipertimbangkan pada desain housing |
| Pengaruh listrik statis | Direkomendasikan memakai perlindungan ESD saat menangani | Berlaku saat perakitan |
| Suhu dan kelembapan operasi | −30 sampai 85 °C, 5 sampai 95% RH | Kabin mobil perlu dicek terhadap rentang ini |
| Kondisi acuan kurva | 25 °C dan 50% RH (kurva Rs/R0) | Di luar kondisi ini, pembacaan bergeser dan tidak dikompensasi |
| Gas lain | Ikut bereaksi terhadap etanol, hidrogen, amonia, metana, dan lain-lain | Tidak bisa membedakan CO dari gas lain |

### MH-Z19C (CO2)

Sumber: manual Winsen MH-Z19C v1.2 (sudah dibaca).

| Batasan | Isi | Implikasi |
|---|---|---|
| Catu daya | Tabel spesifikasi: 5.0 ±0.1 V. Bagian catatan: 4.5 sampai 5.5 V dan arus tidak kurang dari 150 mA. Di luar rentang, keluaran bisa rendah atau sensor tidak bekerja | Manual tidak konsisten. Pakai rentang yang lebih ketat sebagai target |
| Suhu dan kelembapan | −10 sampai 50 °C, 0 sampai 95% RH tanpa kondensasi | Kabin yang diparkir di bawah matahari perlu diperiksa terhadap batas 50 °C |
| Panas dan sinar matahari | Jauhkan dari panas dan sinar matahari langsung | Penempatan di mobil: hindari dasbor yang terkena matahari |
| Debu | Jangan dipakai lama di lingkungan sangat berdebu | Pertimbangkan housing |
| Tekanan mekanis | Hindari tekanan pada ruang plastik berlapis emas dari arah mana pun | Perhatikan pemasangan |
| Ruang kecil | Bila ditempatkan di ruang sempit, harus berventilasi baik terutama di jendela difusi | Housing harus memberi aliran udara ke sensor |
| Kalibrasi otomatis (ABC) | Aktif bawaan pabrik, siklus 24 jam, titik nol 400 ppm. Tidak cocok untuk rumah kaca, peternakan, lemari es, atau ruang yang jarang kena udara luar | Untuk mobil, pertimbangkan dimatikan |
| Kalibrasi berkala | Disarankan paling lama tiap 6 bulan | Tidak dilakukan dalam penelitian ini (lihat B) |
| Kalibrasi titik nol manual | Sensor harus berada di gas stabil 400 ppm lebih dari 30 menit | Tidak tersedia pada penelitian ini |
| Rentang | 400–5000 ppm (varian lain 400–2000 dan 400–10000) | Pembacaan "mentok" di batas rentang tidak berarti angka sebenarnya |
| Preheat | 1 menit (manual) | Kode memakai 3 menit |

---

## B. Batasan validasi (cara menuliskannya)

### B1. Prinsip penulisan

Penguji lebih mudah menerima batasan yang **dinyatakan sendiri, jelas, dan beralasan** daripada batasan yang baru ketahuan saat ditanya. Karena itu bahasa yang tepat bukan "menyembunyikan", tetapi:
- **Pakai istilah yang tepat**: *estimasi*, *indikatif*, *berdasarkan karakteristik pabrikan*, *relatif*. Hindari: *akurat*, *terkalibrasi*, *tervalidasi* (kecuali memang dilakukan).
- **Pisahkan tiga hal**: ruang lingkup (apa yang sengaja dikerjakan), keterbatasan (apa yang tidak bisa dikerjakan dan alasannya), pengembangan lanjutan (apa yang direkomendasikan berikutnya).
- **Nyatakan dampaknya**, bukan hanya fakta bahwa tidak dilakukan.
- **Jangan melebih-lebihkan sistem**: sebut "indikator" atau "peringatan dini", bukan "alat ukur keselamatan".

### B2. Kalimat contoh (silakan disesuaikan)

**Tanpa kalibrasi dengan instrumen referensi:**
> Nilai konsentrasi CO yang ditampilkan merupakan estimasi indikatif yang dihitung dari kurva karakteristik yang disediakan pabrikan (Rs/R0 terhadap konsentrasi pada 25 °C dan 50% RH) dan nilai R0 hasil pengukuran pada udara sekitar yang diasumsikan bersih. Verifikasi terhadap instrumen referensi terkalibrasi atau gas standar berkonsentrasi diketahui tidak dilakukan karena keterbatasan akses terhadap peralatan tersebut. Oleh karena itu, nilai absolut yang ditampilkan tidak dapat dijamin akurasinya, dan sistem ini diposisikan sebagai peringatan dini, bukan alat ukur terkalibrasi.

**Tanpa kompensasi suhu dan kelembapan:**
> Pengaruh suhu dan kelembapan terhadap respons sensor MOX telah dilaporkan dalam literatur (Abdullah dkk., 2022). Dalam penelitian ini, kompensasi terhadap kedua variabel tersebut tidak diimplementasikan karena penentuan koefisien koreksi yang valid memerlukan data pembanding dan pengukuran pada berbagai kondisi lingkungan yang berada di luar cakupan waktu dan sumber daya penelitian. Pengaruhnya diidentifikasi sebagai salah satu sumber ketidakpastian pengukuran dan direkomendasikan sebagai pengembangan lanjutan.

**Tanpa pengujian dengan gas CO nyata:**
> Karena tidak tersedia sumber CO berkonsentrasi diketahui, waktu respons dan waktu pemulihan sensor terhadap CO tidak dapat diukur dalam penelitian ini. Nilai yang digunakan pada parameter penyaringan dan penundaan alarm ditentukan berdasarkan data pembacaan pada udara sekitar dan spesifikasi pabrikan, bukan dari uji respons terhadap gas target.

**Sensor tidak selektif:**
> Sensor MiCS-5524 responsif terhadap beberapa gas pereduksi selain CO (antara lain etanol, hidrogen, dan amonia). Oleh karena itu, peringatan yang dihasilkan menunjukkan kemungkinan keberadaan gas pereduksi, dan tidak secara spesifik membuktikan keberadaan CO.

**Diuji pada breadboard dan di meja:**
> Pengujian dilakukan pada rangkaian prototipe (breadboard) tanpa housing dan terutama pada kondisi meja di ruangan. Karakteristik pada rangkaian akhir dan pada kondisi kabin kendaraan (suhu, getaran, catu daya, aliran udara) perlu diverifikasi lebih lanjut.

### B3. Apa yang tetap bisa Anda klaim (dan buktikan)

| Klaim | Bukti |
|---|---|
| Parameter firmware punya dasar sumber atau data | Tabel di validasi-parameter.md |
| Pembacaan di udara bersih konsisten dan stabil setelah waktu tertentu | Log baseline (menunggu data) |
| Pemilihan filter berbasis data, bukan tebakan | filtering.md dan skrip analisis |
| CO2 sesuai spesifikasi pabrikan | Spesifikasi dan manual (perbandingan dengan CO2 meter lain bila ada) |
| Ambang peringatan punya alasan | desain-peringatan.md |

### B4. Kemungkinan pertanyaan penguji

| Pertanyaan | Jawaban jujur yang bisa disiapkan |
|---|---|
| Kenapa tidak dikalibrasi? | Tidak ada akses ke instrumen referensi atau gas standar. Hasil dinyatakan sebagai estimasi indikatif, dan kalibrasi direkomendasikan sebagai pengembangan lanjutan |
| Kenapa tanpa sensor suhu dan kelembapan? | Koefisien koreksi yang valid butuh data pembanding dan variasi kondisi yang melampaui waktu penelitian. Pengaruhnya diakui sebagai sumber ketidakpastian |
| Seberapa akurat alatnya? | Akurasi absolut tidak diklaim. Yang diklaim: konsistensi baseline dan dasar parameter. Akurasi CO2 mengacu pada spesifikasi pabrikan |
| Bagaimana tahu alarm berbunyi pada saat yang tepat? | Ambang diturunkan dari standar paparan dan alarm yang dikutip. Waktu respons sensor terhadap CO nyata tidak terukur dan dinyatakan sebagai batasan |
| Bagaimana kalau alarm palsu karena gas lain? | Itu batasan sensor (tidak selektif). Pesan peringatan dirancang menyebut kemungkinan gas pereduksi |
