# Daftar Tugas dan Daftar Asumsi

Tujuan: menjaga pekerjaan tetap di jalur dan membedakan **fakta** dari **asumsi**. Diperbarui 25 Oktober 2026.

## Konteks proyek (dari pengguna, 25 Okt 2026)

- **C-251** (rencana awal, 14 Agustus 2026) **tidak akan direvisi**. Ia dipakai sebagai acuan dan dibandingkan dengan hasil.
- **C-501** adalah laporan implementasi dan hasil. **Tenggatnya setelah expo**. Artefak pengujian dikumpulkan sebelum expo dan menjadi bahan C-501.
- Expo dan demo sekitar 5 hari dari 25 Okt (menurut pengguna; tanggal pasti belum dicatat).
- Firmware lama (v0, 23 Okt) sengaja dipertahankan untuk **pembanding** dengan firmware baru: salinannya ada di `arsip-firmware/main-v0-2026-10-23.cpp` (di luar `src/`).

## Aturan kerja

1. Setiap angka di `src/main.cpp` punya status: `Terbukti`, `Sebagian`, atau `Asumsi`. Statusnya ada di [validasi-parameter.md](../3-bukti/validasi-parameter.md).
2. **Jangan mengubah angka di kode sebelum statusnya jelas** atau keputusannya dicatat beserta alasannya.
3. Temuan baru dicatat di file yang sesuai, bukan hanya di chat.
4. Sebelum pindah topik, cek daftar ini. Ide baru yang belum waktunya masuk ke bagian "Parkir", bukan dikerjakan langsung.
5. Hasil dari bacaan ringkasan (hasil pencarian, alphaxiv) dianggap **belum terverifikasi** sampai sumber aslinya dibuka.

---

## Jadwal menuju expo (30 Oktober 2026)

Tenggat expo dan demo: **30 Oktober**. PCB belum datang, jadi demo dirancang **berjalan di breadboard**. PCB hanya bonus.

| Hari | Fokus | Hasil yang diharapkan |
|---|---|---|
| Min 25 (malam) | Uji mobil dengan **firmware lama** (baseline) | Log dan lembar catatan jam |
| Sen 26 | **Pagi:** uji kamar firmware lama (nyala dingin, kipas/AC), **selesai**. **Malam:** uji mobil 2, firmware lama, dengan uji jendela ([skenario-uji-mobil.md](../2-lapangan/skenario-uji-mobil.md)). Siang: firmware baru (SMA 6, aturan CO dan CO2, mode simulasi) ditulis di folder terpisah. Putuskan ESP final dan kontrak data dengan tim. Draf naskah video dan isi banner | Firmware baru siap diunggah. ESP final ditetapkan |
| Sel 27 | Unggah ke ESP final. Uji di meja (napas ke kotak, simulasi CO). Ukur waktu gerak jendela. Mulai integrasi MQTT | Demo inti jalan di meja |
| Rab 28 | Uji gabungan sampai ke aplikasi. Uji mobil ketiga dengan firmware baru (bila sempat). Susun diorama | Alur lengkap sensor ke aplikasi |
| Kam 29 | Rekam video 3 menit, latihan demo. **Bekukan firmware pada siang hari**, tidak diubah lagi | Video, diorama, dan skenario demo siap, plus cadangan |
| Jum 30 | Expo | |

**Batas minimum demo (kalau waktu habis):** CO2 naik karena napas lalu bunyi dan jendela bergerak; kasus CO ditunjukkan lewat **mode simulasi berlabel**; data tampil di LCD, dan di aplikasi bila MQTT sempat jadi (bila tidak, tampilkan data rekaman).

**Dipotong dulu bila perlu:** PCB (bonus), tabel sensitivitas lengkap (cukup ringkas), sisa verifikasi sumber, uji mobil kedua, dan jendela Classy asli (cadangan: servo dengan panel mika seperti rencana C-251).

## Ringkasan status (25 Okt 2026, 19:06)

| Kelompok | Isi |
|---|---|
| **Sudah** | Analisis data kamar 4 jam, noise, dan pemilihan filter (SMA 6). Sumber standar CO dan CO2 terverifikasi (NIOSH, OSHA, WHO, UL 2034, ASHRAE, Satish). Rencana desain, pseudocode baru dan 4 diagram alur, rancangan data dan 3 DFD, evaluasi skema dan fungsi database tim. Skenario uji mobil, agenda pertemuan tim, README dan penataan folder. Keputusan: ambang CO memakai ppm estimasi (B2), ambang bahaya 87 ppm (B4), aturan bila satu sensor gagal (B10) |
| **Belum dikerjakan** | **Firmware** (`src/main.cpp` belum diubah sama sekali sejak 23 Okt). **Uji mobil** (belum ada log baru sejak 16:05). Mode simulasi. Skrip tabel sensitivitas waktu tunggu. Bahan untuk C-501 (T15–T17, T20: koreksi dari C-251 dicatat, **C-251 tidak direvisi**) dan keputusan cara uji CO (T16). Naskah expo, skrip video, banner, diorama. Hitungan bukaan jendela per mobil |
| **Menunggu tim** | ESP final yang Wi-Fi-nya sehat. Kontrak data (7 butir) dan perbaikan skema database (cascade, `created_at`). MQTT dan aplikasi. Pengendalian power window dan jeda minimum. B14–B18 |
| **Menunggu data** | Baseline MiCS yang stabil (B1, B11), laju naik dan turun CO2 di mobil (B8, B9) |
| **Ditunda atau dibatalkan** | Verifikasi sisa sumber (T3 sisa, T4). Uji cabut MH-Z19C (T7). Sensor suhu dan kelembapan |

**Risiko terbesar saat ini:** dokumentasi sudah jauh lebih maju daripada alat. Jalur kritis menuju expo adalah **firmware yang bekerja, data uji mobil, dan bahan expo**.

## A. Tugas aktif (urut prioritas)

Status: `Berjalan`, `Belum`, `Menunggu` (butuh tugas lain atau data), `Selesai`.

| # | Tugas | Status | Bergantung pada | Hasil / bukti yang diperlukan | File terkait |
|---|---|---|---|---|---|
| T1 | Rekam baseline MiCS di udara kamar tanpa gangguan, lalu analisis: kapan Rs stabil, nilai R0, kecukupan warm-up | **Selesai, dihentikan 16:05** (baterai). Sesi `logs/device-monitor-261025-115335.log`: sekitar 4 jam 11 menit tanpa mulai ulang. Baseline **tidak stabil** (Rs turun lebih dari 50%), jadi R0 tidak ditetapkan dari data ini | Kabel tidak tersenggol, laptop tidak mati | Kriteria "stabil" ditulis dulu (misalnya perubahan Rs < 2% per jam), lalu dihitung | A4, A5, D7 |
| T2 | Cek stiker modul MH-Z19C untuk memastikan varian rentang. Keterangan pengguna: sekitar 500–5000 ppm (MH-Z19B 0–5000 sudah tidak diproduksi, **belum diverifikasi**). Manual Winsen v1.2: 400–5000 (ada juga varian 2000 dan 10000). Deskripsi penjual: 400–5000 | Menunggu (sebagian terjawab dari deskripsi penjual, yang lebih lemah daripada stiker) | T1 selesai, karena modul tidak boleh dicabut saat rekaman berjalan | Foto atau catatan stiker | desain-peringatan.md A2 |
| T3 | Buka dan baca sumber asli angka standar: OSHA, NIOSH (CO dan CO2), UL 2034, WHO 2010, Satish 2012. Lampiran alphaxiv (25 Okt 2026) sudah memuat angka dan halaman, tetapi **belum saya verifikasi sendiri** (lihat [daftar-pustaka.md](../3-bukti/daftar-pustaka.md) bagian B dan C) | **Berjalan** (25 Okt 2026 sore). Terverifikasi dari teks asli: Satish (Methods), NIOSH CO, OSHA CO, WHO CO, UL 2034 (Tabel 3), NIOSH CO2, dokumen ASHRAE. Belum: Scully, halaman OSHA CO2 sendiri, Permenaker dan Permenkes, Persily, ADS1115, studi kabin | Tidak ada | Angka, satuan, masa paparan, dan halaman dicatat | desain-peringatan.md, D1–D6 |
| T4 | Buka dan baca sumber filter: Smith bab 15 dan sumber lain | **Ditunda** (dikerjakan nanti atas keputusan pengguna) | Tidak ada | Rumus yang dikutip sudah dicek | filtering.md bagian 8–9 |
| T5 | Sesuaikan skrip analisis agar bisa membaca log berjam (`11:40:13.564 > ...`) | **Selesai** (25 Okt 2026, diuji pada format lama dan log berjam) | Tidak ada | Skrip berjalan di file `logs/` | analisis/filter_compare.py |
| T6 | Sampaikan ke rekan hardware: tegangan MiCS 3.68 V di ADS1115 (batas sekitar 3.6 V), catu 4.64 V (datasheet 4.9–5.1 V), MH-Z19C sempat mati, konektor USB longgar | Belum | Tidak ada | Tanggapan atau perbaikan dari rekan | batasan-sistem.md |
| T7 | Uji cabut MH-Z19C 10–15 menit untuk membuktikan dugaan goyangan. **Tidak dilakukan** (pengguna khawatir merusak rangkaian, 25 Okt 2026). Alternatif tanpa menyentuh perangkat keras: ubah firmware agar membaca CO2 lebih jarang atau berhenti sementara, lalu lihat apakah goyangan berubah | Dibatalkan, alternatif perangkat lunak menunggu T8 | T1 selesai (jangan mengganggu rekaman) | Goyangan hilang atau tidak | filtering.md bagian 4 |
| T8 | Perbaikan firmware: baca ulang setelah ganti gain, tampilan alarm yang menahan saat ppm 0, hitung ulang warm-up CO2 setelah sensor mati, label status CO2 sesuai rencana | Menunggu | Desain peringatan disepakati (T3) | Versi firmware baru dan uji ulang | main.cpp |
| T9 | Putuskan filter, lalu isi bagian 5 filtering.md | Menunggu | T3, T4, T7 | Keputusan, alasan, kekurangan | filtering.md |
| T10 | Tentukan waktu bertahan alarm CO dan batas "selesai" | Menunggu | T3 | Angka dengan alasan | desain-peringatan.md B2 |
| T11 | Uji mobil dengan log: laju naik CO2 (1, 2, 4 orang), laju turun saat jendela dibuka, batas "selesai", alarm palsu | Belum | Kabel stabil, catu mobil, T8 sebaiknya sudah selesai | Data log, bukan ingatan | desain-peringatan.md A6, B4. Skenario malam 25 Okt: [skenario-uji-mobil.md](../2-lapangan/skenario-uji-mobil.md) |
| T12 | Isi kolom alternatif, alasan, dan kekurangan di semua tabel | Belum | T1, T3 | Tabel lengkap | validasi-parameter.md |
| T13 | Uji pengguna kecil (5–10 orang) untuk cara peringatan | Belum | T8, T11 | Hasil umpan balik | desain-peringatan.md A6 |
| T14 | Setelah PCB dan housing: ulangi uji singkat (baseline, noise, respons) dan kunci angka akhir | Menunggu | Perangkat final | Uji ulang | semua |
| T15 | **Diubah:** C-251 **tidak akan direvisi**. Koreksi spesifikasi (sensor, akurasi dan rentang CO2, kalimat kalibrasi) dicatat sebagai bahan **C-501** | Dialihkan ke C-501 | T2 | Daftar revisi yang disepakati tim | [perbandingan-c251.md](../3-bukti/perbandingan-c251.md) |
| T16 | Putuskan cara menguji deteksi CO tanpa sumber CO (atau ubah spesifikasi "4 dari 5 uji"). Jangan membuat CO sendiri tanpa protokol keselamatan | Belum | Diskusi tim dan dosen | Keputusan tertulis | perbandingan-c251.md bagian 4 |
| T17 | **Diubah:** inkonsistensi internal C-251 (jumlah status, ambang CO2 di Bab 11, bukaan servo, bunyi buzzer, salah ketik C-501, jadwal) dicatat sebagai bahan **C-501**, tidak merevisi C-251. **Cek langsung di PDF** | Dialihkan ke C-501 | Tidak ada | Daftar yang sudah diverifikasi | perbandingan-c251.md bagian 4 |
| T18 | Tinjau lokasi sensor di kabin dan alasannya | Belum | Tidak ada | Keputusan lokasi dan dasar | perbandingan-c251.md bagian 4 |
| T19 | Bandingkan model Bab 10 dengan data uji mobil berlog | Menunggu | T11 | Perbandingan angka | perbandingan-c251.md bagian 5 |
| T20 | Perbarui daftar komponen dan anggaran (MiCS-5524, ADS1115, LCD I2C) **untuk C-501** | Dialihkan ke C-501 | Tidak ada | Anggaran baru di bawah Rp2.000.000 dan komponen tunggal ≤ Rp500.000 | perbandingan-c251.md |
| T21 | Pertemuan dengan tim hardware, backend komunikasi, dan software memakai [agenda-pertemuan-tim.md](../2-lapangan/agenda-pertemuan-tim.md) | Belum | Tidak ada | Keputusan dan hasil pengukuran dicatat | agenda-pertemuan-tim.md |
| T22 | **Setelah ganti ke ESP final:** ukur ulang tegangan 5V di pin modul MiCS (saat Wi-Fi aktif), perbarui `VCC` di kode bila berbeda dari 4,64 V, lalu ulangi uji kamar 30 menit (noise, siklus Rs, nyala dingin) dengan Wi-Fi menyala. Bandingkan dengan log ESP lama | Menunggu | Keputusan ESP final (T21) | Periode siklus Rs di ESP baru (lama: 7,01 menit), noise, VCC terukur | [skenario-uji-mobil.md](../2-lapangan/skenario-uji-mobil.md) bagian 2 |

## A2. Urutan pengerjaan (berat dulu, ringan belakangan)

Dibuat 25 Okt 2026 siang. Kolom "Siapa" menunjukkan beban utama. Kerjakan **satu hal saja** pada satu waktu.

| Urutan | Pekerjaan | Tugas | Perkiraan beban | Siapa |
|---|---|---|---|---|
| 1 | Verifikasi jurnal dan standar, lengkapi daftar pustaka | T3, T4 | Berat (baca banyak, sekitar 3–4 jam) | Pengguna, saya bantu mengecek |
| 2 | Uji mobil berlog dan ukur bukaan jendela (Classy, Civic) | T11 | Berat (butuh mobil dan kabel stabil, sekitar setengah hari) | Pengguna dan tim |
| 3 | Catat koreksi dan pertentangan C-251 sebagai bahan C-501 (C-251 tidak direvisi), putuskan cara uji CO, lokasi sensor, anggaran | T15–T18, T20 | Sedang (diskusi tim, sekitar 1–2 jam) | Tim |
| 4 | Naskah expo, skrip video 3 menit, isi banner, konsep diorama | (baru) | Sedang-berat (menulis) | Saya buat draf, pengguna mengubah |
| 5 | DFD revisi dan format pesan MQTT. **Draf selesai 25 Okt** ([rancangan-data.md](rancangan-data.md)), tinggal dicocokkan dengan tim | (baru) | Sedang | Saya buat draf, tim backend dan software mencocokkan |
| 6 | Firmware: perbaikan, mode simulasi, aturan prioritas, nilai sementara, dan skrip simulasi sapuan waktu tunggu | T8, T9, T10 | Sedang bagi pengguna (cukup meninjau dan mengunggah) | Saya |
| 7 | Isi kolom alternatif, alasan, kekurangan di tabel validasi | T12 | Sedang | Pengguna dan saya |
| 8 | Analisis baseline setelah rekaman selesai | T1 | Ringan bagi pengguna | Saya |
| 9 | Cek stiker modul, uji cabut MH-Z19C 15 menit, sampaikan temuan ke rekan hardware | T2, T7, T6 | Ringan | Pengguna |
| 10 | Menjaga rekaman dan pengisian daya laptop | T1 | Ringan | Pengguna |

## B. Selesai

| Pekerjaan | Hasil |
|---|---|
| Cek `c_cpp_properties.json` dan bereskan workspace | Selesai (dua peringatan sisa berasal dari paket framework, tidak berpengaruh) |
| Telaah log serial awal | Temuan tercatat di validasi-parameter.md bagian F |
| Pseudocode algoritma `main.cpp` | Diberikan di chat |
| Tabel validasi parameter A–H | [validasi-parameter.md](../3-bukti/validasi-parameter.md) |
| Analisis filter pada 1000 baris | [filtering.md](../3-bukti/filtering.md), skrip dan data di [analisis/](../analisis/) |
| Rencana desain peringatan CO2 dan CO | [desain-peringatan.md](../3-bukti/desain-peringatan.md) |
| Batasan sistem dan kalimat contoh | [batasan-sistem.md](../3-bukti/batasan-sistem.md) |
| Cara merekam log ke file | Berfungsi, tercatat di bagian I validasi-parameter.md |
| Pencatatan dua kali USB putus (11:53:17 dan 11:53:34) | validasi-parameter.md bagian I |

## C. Daftar asumsi aktif

Semua yang di bawah ini **belum terbukti**. Hapus dari daftar hanya setelah ada bukti.

| # | Asumsi | Dari mana | Cara membuktikan | Tugas |
|---|---|---|---|---|
| S1 | Udara kamar bersih (CO mendekati nol) | Perkiraan pengguna | Tidak bisa dibuktikan tanpa alat. Nyatakan sebagai asumsi | T1 |
| S2 | `A_COEF = 3.7` dan `BETA = 0.856` benar | Dibaca dari grafik datasheet dengan mata (±10%) | Kalibrasi multi-konsentrasi (tidak ada akses). Nyatakan sebagai batasan | T12 |
| S3 | R0 default 1730 kΩ | Nilai sementara di kode | Hasil T1 | T1 |
| S4 | Warm-up MiCS 3 menit cukup (kode sekarang 5 menit) | Nyala dingin 26 Okt: Rs 180 detik −6% dari rata-rata, di dalam siklus ±15% (satu kali uji) | Uji nyala dingin: mati > 1 jam, rekam 10 menit, bandingkan Rs menit ke-3 dan ke-10 | T1 |
| S5 | Warm-up CO2 3 menit cukup | Manual: 1 menit. Log: nilai palsu sampai detik 64 (4 dari 5) dan 128 (1 dari 5) | Final bila tidak ada kasus > 128 detik | T1 |
| S6 | Goyangan Rs berasal dari siklus MH-Z19C | Dugaan | Uji cabut MH-Z19C | T7 |
| S7 | USB putus karena konektor longgar | Dugaan | Ganti kabel atau perbaiki sambungan | T6 |
| S8 | Laju naik CO2 di mobil 150–400 ppm per menit | Ingatan uji mobil | T11 | T11 |
| S9 | Jendela dibuka tiap sekitar 20 menit (4 orang), lebih dari 30 menit (1–2 orang) | Perkiraan tim | T11 | T11 |
| S10 | Jendela dibuka 10 detik menurunkan CO2 100–300 ppm | Pengamatan lisan, dan sensor lambat sehingga mungkin lebih kecil dari kenyataan | T11 | T11 |
| S11 | Rentang MH-Z19C berbatas atas 5000 ppm (bawah sekitar 400–500) | Cerita "mentok di 5000", keterangan pengguna, dan deskripsi penjual (400–5000). Manual: 400–5000 untuk varian 5000. Stiker belum dicek | T2 | T2 |
| S12 | Angka standar CO dan CO2 (OSHA, NIOSH, UL, WHO, Satish) | Ringkasan hasil pencarian | T3 | T3 |
| S13 | Rumus margin lag dan akurasi untuk 4000 ppm | Perhitungan dari spesifikasi dan laju S8 | T11 | T11 |
| S14 | Filter kandidat EMA 0.1 atau SMA 10 cukup | Analisis 16 menit di meja, sensor belum stabil | T9, T14 | T9 |
| S15 | Hasil tidak berubah di PCB dan housing | Belum diuji | T14 | T14 |
| S16 | Mode AC tidak diandalkan sebagai tindakan | Keputusan desain berdasarkan variasi antar mobil | Tidak perlu dibuktikan, tetapi dicatat sebagai keputusan | desain-peringatan.md A4 |

## D. Parkir (ditunda, jangan dikerjakan dulu)

| Ide | Kenapa ditunda |
|---|---|
| Sensor suhu dan kelembapan dengan kompensasi | Diputuskan tidak dikerjakan (waktu dan pengetahuan). Tercatat sebagai batasan |
| Kalibrasi dengan lab kampus atau gas standar | Tidak ada akses saat ini. Bisa jadi pengembangan lanjutan |
| Buzzer untuk CO2 | Mengikuti hasil T11 dan T13 |
| Pendekatan alarm CO berbasis kadar dikali waktu | Menunggu T3 dan T10 |
| Penyaring lonjakan tunggal (median lalu EMA) | Menunggu T9 |
