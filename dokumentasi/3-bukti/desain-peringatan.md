# Rencana Desain Peringatan (CO2 dan CO)

> **Catatan:** ini **catatan kerja yang rinci** (riwayat keputusan, hitungan, dan bukti). Dokumen utama yang ringkas dan berurutan (latar belakang, tinjauan, kebutuhan, implementasi) ada di [rencana-desain.md](../1-utama/rencana-desain.md).

Bagian D dari [validasi-parameter.md](validasi-parameter.md). Status: **rencana, belum diuji**. Angka bertanda "usulan" atau "belum ditentukan" belum punya dasar data. Batasan sensor dan batasan validasi ada di [batasan-sistem.md](batasan-sistem.md).

---

## A. CO2

### A1. Tingkat peringatan

| Tingkat | CO2 | Tindakan | Alasan |
|---|---|---|---|
| Tampilan angka | semua nilai | Hanya menampilkan angka ppm, tanpa penilaian dan tanpa bunyi | 1000 ppm tidak bisa dipakai sebagai ambang: di mobil, kadar itu sudah tercapai tidak lama setelah pengguna masuk, sehingga akan menjadi peringatan yang selalu muncul |
| Peringatan | sekitar 2500 ppm | Bunyi singkat satu kali, tidak berulang | Satish dkk. 2012 (22 peserta) melaporkan penurunan besar kemampuan mengambil keputusan di kadar ini. Tinjauan ASHRAE 2025 (**terverifikasi**) menyebut enam studi melaporkan hubungan dengan penurunan kognitif di sekitar 1000 ppm, satu studi meragukan (Scully 2019), dan studi lain tidak menemukan efek, sehingga bukti dinilai **tidak konsisten** dan belum cukup untuk mengubah standar. Dasar ini lemah, jadi peringatan di 2500 sengaja dibuat lembut |
| Tindakan | sekitar 4000 ppm | Pengguna membuka jendela | Margin di bawah batas sensor dan batas paparan kerja (lihat A2) |
| Selesai | (usulan) sekitar 2500 ppm atau lebih rendah | Tanda tindakan dihentikan | Belum ditentukan, tergantung seberapa cepat CO2 turun saat jendela dibuka |

Catatan untuk firmware: label status CO2 di kode saat ini (`BAIK` di bawah 1000, `SEDANG` 1000–2000, `TINGGI` 2000–5000, `BAHAYA` mulai 5000) tidak sesuai rencana ini dan perlu disesuaikan kemudian.

### A2. Dasar angka 4000 ppm

Aturan: **ambang tindakan = batas acuan dikurangi margin**.

- **Batas sensor**: menurut pengguna rentang MH-Z19C sekitar 500–5000 ppm (manual Winsen v1.2: 400–5000 untuk varian 5000, ada juga varian 2000 dan 10000). Batas atas 5000 berarti sensor tidak bisa melihat di atas itu. Cek stiker modul untuk memastikan (T2).
- **Batas paparan kerja (terverifikasi dari halaman NIOSH Pocket Guide CO2, ditempel pengguna 25 Okt 2026)**: NIOSH REL TWA 5000 ppm dan batas jangka pendek (ST) 30.000 ppm, OSHA PEL TWA 5000 ppm, IDLH 40.000 ppm. ASHRAE 2025 (terverifikasi) menyatakan CO2 dianggap tidak beracun sampai 5000 ppm dan menyebut OSHA sebagai batas regulasi (NIOSH bersifat anjuran). Halaman NIOSH hanya mencantumkan ST untuk REL NIOSH, bukan untuk OSHA.
- **Pedoman ISS dan kapal selam**: kadar dijaga 4000–5000 ppm untuk menurunkan kejadian sakit kepala (James dan Zalesak 2013, dikutip dalam dokumen ASHRAE, sumber aslinya belum dibaca). Ini mendukung 4000 ppm sebagai ambang tindakan.
- **Margin akibat kelemahan sensor**:
  - Akurasi ±(50 ppm + 5%): sekitar ±250 ppm di 4000 ppm ([manual Winsen](https://www.winsen-sensor.com/d/files/mh-z19c-pins%26terminal-type-co2-manual(ver1_2).pdf)).
  - Keterlambatan: T90 kurang dari 120 detik, konstanta waktu sekitar 52 detik. Jika CO2 naik 150–400 ppm per menit, pembacaan tertinggal sekitar 130–350 ppm (perkiraan dari rumus).
  - Total margin sekitar 400–600 ppm.

### A2b. Catatan dari dokumen ASHRAE (terverifikasi, 25 Okt 2026)

Sumber: ASHRAE Position Document on Indoor Carbon Dioxide (disetujui 12 Feb 2025, berlaku sampai 12 Feb 2028), teks ditempel pengguna. Rujukan tambahan di dalamnya (ASTM D6245, James dan Zalesak, Allen, dan lain-lain) belum dibaca langsung.

- **1000 ppm bukan batas kesehatan dan bukan batas ASHRAE.** ASHRAE Standard 62 edisi 1989 memuat batas 1000 ppm, lalu dihapus di edisi berikutnya karena sering disalahartikan. Angka 1000 terkait persepsi bau tubuh dan laju ventilasi sekitar 8 L/detik per orang. Standard 62.1 tidak memuat batas CO2 dalam ruang. Ini mendukung keputusan tidak memakai 1000 sebagai ambang.
- **CO2 adalah indikator ventilasi, bukan indikator kualitas udara menyeluruh.** Posisi ASHRAE: CO2 dalam ruang bukan indikator IAQ secara keseluruhan, tetapi dapat berguna jika keterbatasannya dipahami.
- **Bukti dampak langsung CO2 pada kadar umum dalam ruang dinilai tidak konsisten** dan belum cukup untuk mengubah standar.
- **Sensor, lokasi, dan kalibrasi sangat menentukan.** ASHRAE menyatakan kinerja sensor, lokasi, dan kalibrasi penting untuk menarik kesimpulan dari pengukuran CO2. Ini mendukung batasan sistem.
- **Metode peluruhan (decay) adalah cara baku mengukur laju pertukaran udara.** Dokumen menyebut metode peluruhan dan keadaan tunak menurut ASTM D6245. Asumsinya: konsentrasi seragam di ruang, CO2 luar konstan atau terukur, dan akurasi sensor menjadi faktor utama ketidakpastian. Mengukur sebelum keadaan tunak membuat laju ventilasi terlalu besar. Ini dasar untuk menghitung laju pertukaran udara (N) di mobil dari log penurunan CO2.
- **CO2 luar sekitar 426 ppm pada 2024** (NOAA, dikutip ASHRAE), dan di kawasan kota bisa sampai ratusan ppm lebih tinggi sesaat (mendekati atau melebihi 600). Halaman NIOSH yang menulis "sekitar 300 ppm" sudah usang. Untuk perhitungan penurunan, ukur CO2 luar saat uji (fase A di skenario mobil), jangan asumsikan 400.
- **Pedoman lama untuk ruang:** batas dalam ruang umumnya sekitar 1000 sampai 1500 ppm sebagai indikator ventilasi (Jepang 1000 ppm sejak 1970). CEN 16798-1: kategori I 550, II 800, III dan IV 1350 ppm di atas kadar luar.

### A3. Keputusan: tindakan di 4000, bukan di 2500

Alasan dari tim:
- Bertindak di 2500 membuat jendela sering dibuka sedikit-sedikit (siklus pendek).
- Bertindak di 4000 membuat siklus lebih jarang. Perkiraan tim: sekitar tiap 20 menit saat penuh (4 orang), lebih dari 30 menit saat 1–2 orang.
- Pengecekan kasar: dari sekitar 1000 ke 4000 ppm dengan laju naik 150–250 ppm per menit butuh sekitar 12–20 menit. Cocok dengan perkiraan tim. Laju naik itu masih perkiraan dari ingatan uji mobil, **bukan data terukur**.

### A4. Keputusan: tidak bergantung pada mode AC

- Tombol dan perilaku AC berbeda antar model dan tahun mobil, dan tidak mungkin dicek semuanya.
- Tindakan yang berlaku untuk semua mobil adalah membuka jendela.
- Catatan pendukung (hasil pencarian, belum dibuka sumbernya): mode udara luar dilaporkan menjaga CO2 sekitar 620–930 ppm, sedangkan sirkulasi dalam bisa 2500–4000 ppm. Mode AC memang berpengaruh dan sebaiknya dicatat saat uji.

### A5. Kelemahan CO2

- Di antara 2500 dan 4000, pengemudi tetap berada pada kadar yang pada studi Satish sudah menurunkan kemampuan mengambil keputusan. Peringatan di 2500 dimaksudkan agar pengguna bergerak sebelum 4000.
- Batas paparan kerja dibuat untuk pekerja, bukan khusus mobil.
- Laju naik, frekuensi buka jendela, dan batas "selesai" belum terukur.
- Dasar 2500 berasal dari satu studi kecil dan hasilnya tidak terulang secara konsisten pada studi lanjutan. Karena itu 2500 diperlakukan sebagai peringatan lembut, bukan batas kesehatan.

### A6. Yang harus dibuktikan dengan data

| # | Yang diukur | Cara |
|---|---|---|
| 1 | Laju naik CO2 untuk 1, 2, dan 4 orang | Rekam log saat berkendara dengan jendela dan AC tetap, catat mode AC |
| 2 | Laju turun CO2 saat jendela dibuka (lebar dan lama) | Rekam log saat jendela dibuka dengan lebar tertentu |
| 3 | Batas "selesai" | Dari laju turun (poin 2) |
| 4 | Frekuensi buka jendela | Dari poin 1 dan 2, lalu cocokkan dengan perkiraan tim |
| 5 | Varian sensor (0–5000 atau lainnya) | Cek stiker modul |
| 6 | Kenyamanan pengguna | Uji kecil 5–10 orang |

---

## B. CO

CO adalah soal keselamatan, jadi sifatnya berbeda dari CO2: tegas, tetapi dasarnya harus jelas. Semua angka CO di sini adalah **ppm estimasi** (lihat [batasan-sistem.md](batasan-sistem.md)).

### B1. Acuan angka (hasil pencarian, perlu dicek ke sumber aslinya)

| Acuan | Nilai | Catatan |
|---|---|---|
| OSHA PEL | 50 ppm (55 mg/m³), rata-rata 8 jam | Paparan kerja. **Terverifikasi** dari halaman OSHA yang ditempel pengguna (25 Okt 2026) |
| NIOSH REL | 35 ppm (40 mg/m³) rata-rata, plafon (C) 200 ppm (229 mg/m³) | Paparan kerja. **Terverifikasi** dari halaman NIOSH Pocket Guide dan OSHA. Halaman OSHA menulis REL "up to 10-hour TWA", jadi masa rata-ratanya **sampai 10 jam, bukan 8 jam**. C-251 menulis 8 jam dan menyebutnya OSHA di beberapa tempat, dan perlu dikoreksi |
| NIOSH IDLH | 1200 ppm | Langsung berbahaya bagi nyawa dan kesehatan. **Terverifikasi** |
| AIHA ERPG-1/2/3 | 200, 350, 500 ppm | Dicantumkan di halaman OSHA. Definisi tiap tingkat belum dibaca |
| Cal/OSHA | PEL-TWA 25 ppm, STEL 200 ppm | Dari halaman OSHA (negara bagian California). Letak kolom pada teks tempelan agak ambigu, cek di halaman aslinya |
| UL 2034 (alarm CO rumah) | 70 ppm dalam 60–240 menit, 150 ppm dalam 10–50 menit, 400 ppm dalam 4–15 menit | Alarm merespons gabungan kadar dan waktu, bukan satu angka. Satu sumber (University of Akron) menulis 60–189 menit untuk 70 ppm, sepertinya outlier. **Terverifikasi sebagian** dari teks "Sensitivity Test Analysis" laporan CPSC (ditempel pengguna 25 Okt 2026): 12 alarm per model diuji pada empat kondisi (kadar tetap dan satu uji kenaikan cepat), setiap alarm harus aktif dalam selang waktu tertentu, dan **aktif terlalu cepat dihitung sebagai kegagalan** (selang punya batas bawah dan atas). **Tabel 3 (hlm. 11) terverifikasi** (ditempel pengguna 25 Okt 2026): 70 ±5 ppm dalam 60–240 menit, 150 ±5 ppm dalam 10–50 menit, 400 ±10 ppm dalam 4–15 menit, kenaikan 16 ppm per menit sampai 480 ±15 ppm dalam 19–30 menit |
| WHO pedoman udara dalam ruang | 100 mg/m³ (15 menit), 35 mg/m³ (1 jam), 10 mg/m³ (8 jam), 7 mg/m³ (24 jam), setara sekitar 87, 30, 9, dan 6 ppm | **Terverifikasi** dari teks WHO yang ditempel pengguna (25 Okt 2026). Angka resmi WHO dalam mg/m³. ppm adalah hitungan dengan 1 ppm = 1,15 mg/m³ (faktor dari NIOSH): 87, 30,4, 8,7, dan 6,1 ppm. Dasar: kadar COHb tidak melebihi 2% (model Coburn-Forster-Kane). Asumsi: 15 menit dan 1 jam dengan aktivitas ringan dan tidak lebih dari sekali sehari, 8 jam rata-rata dengan aktivitas ringan sampai sedang, 24 jam rata-rata dengan orang terjaga dan tidak berolahraga. Untuk paparan di dalam ruang, bukan tempat kerja |
| Permenaker 5/2018 (NAB) | CO 25 ppm | Pekerja. Dari lampiran, **perlu dicek pada tabel resminya** |
| Permenkes 48/2016 (perkantoran) | CO 10 ppm (8 jam) | Lingkungan perkantoran, bukan pekerja secara umum. Dari lampiran, **belum diverifikasi** |

Sumber: [NIOSH IDLH karbon monoksida](https://www.cdc.gov/niosh/idlh/630080.html), [ATSDR](https://www.atsdr.cdc.gov/ToxProfiles/tp201-c8.pdf), [UMEM](https://em.umaryland.edu/educational_pearls/2924/), [BRK](https://www.brkelectronics.com/faqs/diy/what_levels_of_co_cause_an_alarm). Semuanya ringkasan hasil pencarian, belum dibuka satu per satu.

Catatan: standar di atas untuk paparan kerja dan alarm rumah, **bukan khusus kabin mobil**. Dipakai sebagai acuan, bukan sebagai tuntutan hukum.

### B1b. Membandingkan rencana kita dengan selang UL 2034

UL 2034 memberi **selang** waktu aktivasi alarm rumah. Batas bawahnya mencegah alarm terlalu cepat (gangguan), batas atasnya mencegah alarm terlambat (Tabel 3, terverifikasi).

| Kadar CO | Selang UL 2034 | Alarm kita (rencana sementara) | Perbandingan |
|---|---|---|---|
| 70 ppm | 60–240 menit | Waspada di ≥ 35 ppm setelah konfirmasi sekitar 30 detik | **Jauh lebih cepat** dari batas bawah UL. Menurut kriteria UL ini akan dihitung "aktif terlalu cepat" |
| 150 ppm | 10–50 menit | Sama (sudah di atas 35 ppm) | Jauh lebih cepat dari batas bawah |
| 400 ppm | 4–15 menit | Tingkat bahaya, hampir langsung | Jauh lebih cepat dari batas bawah |

Artinya: alat ini **tidak boleh diklaim memenuhi UL 2034**, dan penguji bisa bertanya mengapa jauh lebih sensitif. Alasan yang bisa dipertimbangkan (harus diputuskan tim dan ditulis jelas):
- UL 2034 dibuat untuk alarm rumah yang menyala berjam-jam, sedangkan satu perjalanan mobil biasanya sekitar 30–60 menit. Batas bawah 60 menit pada 70 ppm hampir membuat alarm tidak berguna untuk satu perjalanan.
- **Biaya tindakan keliru kecil**: tindakan yang dilakukan adalah membuka jendela, bukan evakuasi. Alarm palsu lebih murah daripada alarm terlambat. Tetap harus diakui: alarm palsu mengganggu pengguna (UX), dan sensor tidak selektif.
- WHO 2010 (terverifikasi) memberi 30 ppm untuk rata-rata 1 jam dan 87 ppm untuk 15 menit. Itu mendukung kewaspadaan di sekitar 30–35 ppm, tetapi **bukan** alasan untuk alarm dalam 30 detik. Untuk itu butuh argumen biaya tindakan di atas.
- Struktur "kadar dan waktu" milik UL bisa dipinjam sebagai bentuk, bukan angkanya: kadar lebih tinggi, waktu lebih pendek.

Dalam laporan, jelaskan bahwa UL 2034 dipakai sebagai **referensi bentuk** (alarm adalah fungsi kadar dan waktu), bukan sebagai syarat yang dipenuhi.

### B2. Rencana tingkat (usulan)

| Tingkat | CO (estimasi) | Tindakan | Dasar |
|---|---|---|---|
| Peringatan | sekitar 35 ppm bertahan | Tampilan dan bunyi lembut | NIOSH REL 35 ppm. Waktu bertahan **belum ditentukan** |
| Bahaya | sekitar 200 ppm | Bunyi tegas dan terus-menerus | Plafon NIOSH 200 ppm, dan UL 2034 menuntut respons 10–50 menit di 150 ppm |
| Di atas rentang | lebih dari 1000 ppm | "Di atas rentang sensor", bunyi tegas | Rentang sensor 1–1000 ppm (datasheet) |

Yang harus diputuskan dengan alasan:
- **Waktu bertahan** untuk tingkat peringatan. Kode saat ini 10 detik pada 35 ppm. Jauh lebih cepat dari UL 2034 (yang mengizinkan sampai beberapa jam pada 70 ppm), dan di mobil mudah memicu alarm palsu akibat gas lain (pengharum, uap bensin, asap rokok). Perlu ditimbang dengan keterlambatan sensor (response time MiCS belum diketahui) dan filter.
- **Pendekatan kadar dikali waktu** seperti UL 2034, bukan satu angka sesaat. Itu lebih sesuai dengan cara standar bekerja.
- **Batas selesai** (kode saat ini 25 ppm selama 30 detik).

### B3. Aturan pendukung

- **Tidak ada alarm saat warm-up.** Kode saat ini 5 menit. Lamanya belum terbukti (datasheet tidak memuat). Setelah sensor mati sebentar (misalnya sambungan USB putus), warm-up harus dihitung ulang.
- **Kerusakan sensor tidak boleh tampil sebagai "OK".** `ADC_ERR` dan `ADC_SATURASI` ditampilkan sebagai gangguan.
- **Sensor tidak bisa membedakan gas.** Pesan sebaiknya "kemungkinan CO atau gas lain", bukan "CO terdeteksi" (lihat batasan di batasan-sistem.md).

### B4. Yang harus dibuktikan

| # | Yang diukur | Cara |
|---|---|---|
| 1 | Berapa detik/menit sensor dan filter butuh untuk mencapai ambang saat ada gas | Tidak bisa diukur dengan CO asli. Cukup dinyatakan sebagai batasan |
| 2 | Seberapa sering alarm palsu di mobil | Rekam log di mobil dengan berbagai kondisi (pengharum, AC, dan lain-lain) |
| 3 | Waktu warm-up yang cukup | Analisis log baseline |

---

## C. Alur kode saat ini (pseudocode)

Ini gambaran [src/main.cpp](../../src/main.cpp) **versi sekarang** (353 baris, terakhir diubah 23 Oktober 2026). Tanda `⚠` menandai bagian yang **berbeda dari rencana** di bagian A dan B. Perbedaannya dirangkum di bagian D.

### C1. Saat dinyalakan (`setup`, [baris 239](../../src/main.cpp#L239))
```
buka Serial 115200, tunggu 1 detik
matikan buzzer
buka jalur sensor CO2 (9600)
   kalau DISABLE_ABC = true -> matikan kalibrasi otomatis       ⚠ sekarang false (ABC aktif)
nyalakan I2C, cek LCD, tampilkan "CO + CO2 Monitor"
cek ADS1115 di 0x48
   kalau tidak ada -> tampilkan error di LCD, BERHENTI SELAMANYA
atur gain ADS1115 ke tingkat paling sensitif (1.024 V)
ambil R0 dari memori (bawaan 1730 kOhm kalau belum pernah disimpan)
cetak petunjuk dan judul kolom CSV
```

### C2. Setiap 1 detik (`loop`, [baris 278](../../src/main.cpp#L278))
```
1. cek perintah keyboard: 'r' = mulai kalibrasi R0, 'd' = R0 kembali ke bawaan

2. CO2:
     kirim pertanyaan ke MH-Z19C, tunggu jawaban maksimal 0,5 detik
     valid kalau 9 byte, header benar, checksum cocok
     ppm CO2 = byte3 x 256 + byte4
     kalau tidak valid -> CO2 dianggap gagal ("n/a")

3. MiCS (tegangan):
     rata-ratakan 16 pembacaan ADS1115
     kalau mentok di batas alat ukur -> SATURASI
     atur gain otomatis: naik satu tingkat per detik kalau sinyal hampir penuh,
                         turun satu tingkat kalau sinyal kecil
        ⚠ saat SATURASI pembacaan detik itu dibuang, tidak dibaca ulang (T8)

4. MiCS (hitungan):
     Rs = RL x (VCC - V) / V           (RL = 9970, VCC = 4.64)
     kalau SATURASI           -> status "ADC_SATURASI", ppm CO tidak dihitung
     kalau Rs tidak valid     -> status "ADC_ERR", ppm CO tidak dihitung
     kalau valid:
        kalau sedang kalibrasi -> catat Rs (lihat C3)
        Rs halus = EMA (20% data baru + 80% yang lama)      ⚠ filter belum diputuskan (T9)
        rasio = Rs halus / R0
        kalau rasio >= 0,5 -> ppm CO = 0
        kalau tidak        -> ppm CO = (3,7 / rasio) ^ (1 / 0,856)    ⚠ A dan BETA asumsi (S2)

5. Status dan alarm CO:
     kalau sedang kalibrasi        -> "KALIBRASI_R0"
     kalau menyala < 300 detik     -> "WARMUP"       ⚠ 5 menit belum terbukti (S4)
                                                      ⚠ tidak dihitung ulang kalau sensor mati sebentar
     kalau tidak:
        alarm belum aktif:  ppm >= 35 selama 10 detik berturut-turut -> ALARM AKTIF    ⚠ waktu belum diputuskan (T10)
        alarm aktif:        ppm <  25 selama 30 detik berturut-turut -> ALARM MATI     ⚠ buzzer tetap bunyi walau ppm 0 di 30 detik ini
        status: ALARM(est) / DI_ATAS_RENTANG (> 1000 ppm) / OK(<10ppm) / OK

6. Buzzer: bunyi kalau alarm CO aktif, diam kalau tidak
     ⚠ buzzer hanya untuk CO. CO2 belum punya bunyi sama sekali

7. Status CO2:
     gagal dibaca                  -> "CO2_ERR"
     menyala < 180 detik           -> "WARMUP"       ⚠ tidak dihitung ulang kalau sensor CO2 mati
     < 1000   -> "BAIK"
     < 2000   -> "SEDANG(ventilasi)"     ⚠ tidak sesuai rencana (A1: tanpa penilaian di 1000)
     < 5000   -> "TINGGI"                ⚠ tidak ada tingkat 2500 dan 4000
     >= 5000  -> "BAHAYA"                ⚠ sensor mentok di 5000, tidak akan melihat lebih dari itu

8. LCD: baris 1 "CO: xxxx ppm [kode]", baris 2 "CO2: xxxx ppm [kode]"
        (LCD 4 baris: dua baris tambahan berisi status lengkap)

9. Serial: satu baris CSV:  t_s, V_mV, Rs_kohm, Rs_per_R0, CO_ppm_est, CO2_ppm, status_CO, status_CO2

10. tunggu sampai genap 1 detik sejak awal loop, lalu ulangi
```

### C3. Kalibrasi R0 (perintah `r`, [baris 195](../../src/main.cpp#L195))
```
mulai hitung 120 detik, kosongkan catatan, matikan alarm
tiap detik selama 120 detik: catat Rs (jumlah, terkecil, terbesar)
setelah 120 detik:
   data < 60 titik                       -> GAGAL
   selisih (terbesar - terkecil) / rata-rata > 10%  -> DITOLAK, R0 tidak berubah
   selain itu                            -> R0 = rata-rata, simpan ke memori ESP32
```

## D. Perbedaan kode sekarang dan rencana

| # | Kode sekarang | Rencana | Tugas |
|---|---|---|---|
| 1 | Status CO2 memakai batas 1000, 2000, 5000 | Tampilan angka saja, peringatan 2500, tindakan 4000 | T8 |
| 2 | CO2 tidak punya bunyi | Bunyi singkat satu kali di 2500 | T8, T11 |
| 3 | `DISABLE_ABC = false` (ABC aktif) | Dimatikan untuk versi mobil (usulan) | T8 |
| 4 | Warm-up dihitung dari boot ESP32 | Dihitung ulang kalau sensor mati sebentar | T8 |
| 5 | Gain naik satu tingkat per detik, data saturasi dibuang | Baca ulang setelah ganti gain | T8 |
| 6 | Alarm CO: 35 ppm selama 10 detik, buzzer tetap bunyi 30 detik walau ppm 0 | Waktu dan batas selesai ditentukan dengan alasan | T10 |
| 7 | Filter EMA 0.2 | Belum diputuskan (kandidat EMA 0.1 atau SMA 10) | T9 |
| 8 | Alarm CO satu tingkat | Tiga tingkat (peringatan, bahaya, di atas rentang) | T10 |
| 9 | Tidak ada pesan "kemungkinan gas lain" | Pesan memuat kemungkinan gas pereduksi lain | T8 |

Aturan: bagian ini diperbarui setiap kali `main.cpp` berubah, dan perbedaan yang sudah teratasi dihapus.

## E. Aturan prioritas dan cara menentukan waktu

Berdasarkan diagram alur rancangan awal C-251 (Gambar 8.11). Status: **usulan, belum disetujui tim**.

### E1. Aturan prioritas (yang tertinggi menang)

| Prioritas | Kondisi | Tindakan |
|---|---|---|
| 1 | Sensor rusak atau data tidak valid | Tampilkan gangguan. Jangan melakukan tindakan jendela otomatis berdasarkan data yang tidak valid |
| 2 | CO tinggi (estimasi ≥ 35 ppm, setelah konfirmasi) | Bunyi dan **buka jendela** (uji sumber). Setelah waktu uji: bila CO naik lagi, sumber dari luar, jendela **ditutup** dan tetap tertutup sampai CO turun. Bila CO turun, jendela tetap terbuka sampai CO di bawah batas selesai. **Aktuator mengikuti aturan CO, aturan CO2 tidak dipakai** selama prioritas ini aktif. Pesan: "kemungkinan CO atau gas lain" |
| 3 | CO2 ≥ 4000 ppm dan prioritas 2 tidak aktif | Bunyi dan buka jendela. Besar bukaan dihitung per mobil |
| 4 | CO2 ≥ 2500 ppm | Bunyi singkat satu kali dan peringatan di aplikasi mobile |
| 5 | Selain itu | Normal |

Prioritas 2 selesai bila CO di bawah batas selesai selama waktu pemulihan. Setelah itu aturan CO2 berlaku kembali.

Dasar prioritas 2 (keputusan tim, 25 Okt 2026): sensor tidak bisa membedakan CO dari luar (misalnya knalpot truk) dan dari dalam kabin (C-251 Bab 7.4). Maka jendela dibuka **sebagai uji arah**, lalu diamati:
- Model C-251 (Persamaan 4.3) menyatakan konsentrasi kabin bergerak menuju konsentrasi luar. Jika CO **turun** setelah jendela dibuka, sumber ada di dalam dan ventilasi membantu. Jika CO **naik**, sumber di luar, sehingga jendela ditutup.
- Keputusan arah memakai **perubahan relatif**, bukan angka ppm mutlak, sehingga tidak bergantung pada kalibrasi referensi.
- Biaya uji: dengan laju pertukaran udara jendela terbuka N ≈ 13,3 per jam (angka tabel C-251 yang terbaca sebagian, **[cek PDF]**), konstanta waktu sekitar 270 detik. Uji 30 detik menaikkan CO kabin sekitar 10% dari selisih konsentrasi luar dan dalam, dan uji 60 detik sekitar 20%. Contoh: luar 200 ppm, kabin 35 ppm menghasilkan sekitar +17 ppm (30 detik) atau +33 ppm (60 detik). Perkiraan dari model, belum terukur.
- Risiko: lamanya uji harus lebih panjang dari keterlambatan sensor dan filter. Respons MiCS-5524 tidak ada di datasheet, dan filter kandidat butuh sekitar 8–21 detik. Selama waktu uji, penghuni terpapar CO luar.
- Catatan keselamatan: menutup jendela otomatis pada power window perlu dibahas risiko terjepit (anti-jepit), dan dicatat di batasan.
- Saran AC (recirculation atau udara luar) **tidak dipakai dulu**. Literatur memang membahas perbedaan mode, tetapi belum diketahui apakah berlaku untuk AC mobil sekarang.

### E2. Celah di diagram alur rancangan awal

1. **Kondisi WASPADA tidak mengevaluasi ulang CO.** Di diagram, begitu status WASPADA, alur hanya mengecek pemulihan. Jika WASPADA dipicu CO2 (jendela terbuka) lalu CO naik karena truk di depan, jendela tetap terbuka. Prioritas 2 di atas perlu dievaluasi **setiap siklus, apa pun statusnya**.
2. **Cabang saat CO dan CO2 sama-sama tinggi tidak digambarkan.** Prioritas di E1 menjawabnya (CO menang), tetapi perlu diputuskan tim apa yang terjadi bila CO2 terus naik sampai batas sensor saat jendela dikunci (lihat bagian E4).
3. **Pemulihan memakai nilai sesaat.** Data kita menunjukkan goyangan Rs sekitar ±10% per detik, yang bisa membuat estimasi ppm di sekitar 30 ppm bolak-balik. Nilai sesaat berisiko membuat pemulihan gagal berulang. Pertimbangkan nilai yang difilter ringan (keterlambatan 10–20 detik masih jauh di bawah waktu pemulihan 60 detik).

### E3. Dari mana waktu ditentukan

| Parameter waktu | Sumber keputusan | Data yang sudah ada | Status |
|---|---|---|---|
| Interval keputusan (rancangan awal 5 detik, kode 1 detik) | Cukup sering untuk menangkap lonjakan terpendek yang relevan. Rancangan awal menyebut lonjakan CO 10 detik di Auckland | Log 1 detik | Usulan: baca tiap 1 detik, keputusan boleh per beberapa detik |
| Panjang filter CO | Dua syarat: noise yang harus diredam (filtering.md) dan anggaran keterlambatan | Analisis 1000 baris, dua sesi | Kandidat EMA 0.1 (sekitar 21 detik) atau SMA 10 (sekitar 8 detik) |
| Filter CO2 | Sensor sudah lambat (T90 kurang dari 120 detik) | Manual Winsen | Usulan: tanpa filter tambahan |
| Konfirmasi sebelum WASPADA CO | Alarm palsu vs keterlambatan. Standar alarm rumah (UL 2034) menuntut respons dalam menit pada 70–400 ppm. Plafon NIOSH 200 ppm dihitung sebagai rata-rata 15 menit (belum diverifikasi) | Belum ada data mobil | Usulan sementara 30 detik. **Tentukan dengan simulasi pada log mobil** |
| Waktu pemulihan (rancangan awal 60 detik) | C-251 Bab 4.4.3 menyatakan parameter ini "ditetapkan secara empiris" dan belum ada justifikasi baku | Belum | Tentukan dengan simulasi: jalankan mesin status pada log dengan beberapa waktu pemulihan, pilih yang terpendek yang tidak membuat status bolak-balik |
| Durasi jendela terbuka | Laju pertukaran udara N terukur: t = ln((C0 − Cluar) / (Ctarget − Cluar)) / N | Belum terukur di mobil | Butuh pengukuran (T11) |
| Buzzer berhenti sendiri setelah 5 menit (C-251 Bab 8.1) | Keputusan desain: hemat daya dan hindari gangguan pendengaran | Tidak ada | Pertahankan |
| Warm-up | Log baseline | Sedang direkam | Menunggu T1 |

### E4. Yang masih harus diputuskan tim

Sudah diputuskan tim (25 Okt 2026):
- Bila CO tinggi dan CO2 juga tinggi, jendela **tetap mengikuti aturan CO** (tertutup bila sumber luar) sampai CO turun. Aturan CO2 tidak diikuti.
- Saran mode AC ditunda.

Masih harus diputuskan:
- **Lama uji arah** setelah jendela dibuka (usulan sementara 60 detik) dan **kriteria "naik lagi"**. Kriteria harus lebih besar dari noise. Data kita: simpangan baku Rs setelah filter sekitar 2,5%, sehingga usulan awal 3 kali simpangan baku (sekitar 8% perubahan Rs). Perlu ditentukan dengan simulasi dan, bila memungkinkan, uji respons sensor memakai stimulus gas pereduksi.
- **Besar bukaan jendela per mobil**: dihitung dari laju pertukaran udara N yang diukur di tiap mobil (Daihatsu Classy, Honda Civic).
- **Pola bunyi**: CO dan CO2 4000 sama-sama "bunyi dan buka jendela". Usulan: pola bunyi dan pesan di layar dibedakan agar pengemudi tahu gas mana yang memicu.
- Uji logika tanpa CO asli: mode simulasi yang memutar kurva model C-251 untuk dua skenario (sumber dalam: CO turun saat jendela dibuka, sumber luar: CO naik). Harus diberi label "simulasi".

## F. Prinsip menentukan waktu tunggu (agar bisa dipertahankan di sidang)

Kritik yang pernah muncul: waktu tunggu menyangkut keselamatan dan UX, dan C-251 menyebut nilainya "ditetapkan secara empiris". Pembelaan yang kuat membutuhkan alasan terukur untuk tiap angka. Status: **usulan metode, angka belum final**.

### F1. Empat prinsip

1. **Asimetris: cepat memberi alarm, lambat membatalkan.** Alarm palsu lebih aman daripada alarm terlambat, jadi penundaan sebelum alarm dibuat sekecil mungkin dan penundaan sebelum membatalkan lebih panjang.
2. **Bertingkat menurut tingkat bahaya.** Kadar sangat tinggi (misalnya plafon CO 200 ppm) tidak menunggu konfirmasi panjang. Penundaan konfirmasi hanya berlaku pada tingkat rendah.
3. **Pita histeresis dipilih dari noise terukur, bukan dari waktu.** Jika pita antara batas nyala dan batas selesai cukup lebar dibanding noise, noise tidak akan membuat status bolak-balik, dan waktu tunggu tidak perlu panjang hanya untuk meredam noise.
4. **Anggaran keterlambatan dari waktu menuju bahaya.** Keterlambatan total (filter + konfirmasi + respons sensor) dibatasi sebagian kecil dari waktu yang dibutuhkan kadar untuk mencapai tingkat berbahaya.

### F2. Apa yang bisa dihitung dari data sekarang

| Hal | Perhitungan | Hasil sementara |
|---|---|---|
| Noise pada ppm | Simpangan baku Rs setelah filter 2,5–2,9% (dua sesi baseline). ppm bergantung pada Rs^(-1/0,856), jadi noise ppm sekitar 1,17 kali noise Rs | Sekitar 3% pada udara bersih |
| Pita histeresis CO (35 nyala, 30 selesai) | 5 ppm sekitar 14% dari 35 ppm, sekitar 4,5 kali simpangan baku noise | Noise saja tidak cukup untuk membuat status bolak-balik. Syarat: berlaku pada udara bersih, noise saat ada gas belum diukur |
| Konstanta waktu EMA 0,1 | τ = −1 / ln(0,9) ≈ 9,5 detik | Waktu pemulihan sebaiknya beberapa kali τ agar nilai yang diperiksa sudah menetap: 3τ sekitar 28 detik, 6τ sekitar 57 detik. Itu dasar yang masuk akal untuk 60 detik |
| Waktu menuju bahaya, CO dari luar 200 ppm, jendela tertutup | C-251 Tabel 10.6: sekitar 10 menit ke 35 ppm **[cek PDF]** | Anggaran keterlambatan 10–20% sekitar 60–120 detik |
| Waktu menuju bahaya, jendela terbuka (N ≈ 13,3 per jam) | t = −τ ln(1 − (35 − 5) / (200 − 5)) dengan τ sekitar 271 detik | Sekitar 45 detik. Jendela terbuka mempercepat paparan bila sumber di luar |
| Lama maksimum uji arah | Batasi tambahan paparan ΔC. t ≤ −τ ln(1 − ΔC / (Cluar − C0)). Contoh ΔC = 20 ppm | Sekitar 35 detik. Sementara filter butuh sekitar 21 detik untuk t90 (EMA 0,1), jadi jendelanya sempit |
| Waktu menuju 2500 ppm CO2 (4 penumpang Avanza) | C-251 Tabel 10.3 sekitar 4,6 menit **[cek PDF]** | Penundaan puluhan detik masih aman. Keterlambatan sensor CO2 sudah diperhitungkan di margin 4000 ppm |

Catatan: semua angka dari model C-251 memakai asumsi tabelnya dan terbaca sebagian dari PDF. Pembelaan di sidang harus memakai angka yang sudah dicek.

### F3. Ketegangan yang harus diakui

Uji arah (jendela dibuka untuk melihat apakah CO naik) butuh waktu lebih panjang dari keterlambatan sensor, tetapi makin lama dibuka, makin besar paparan bila sumber di luar. Pilihan untuk meredakannya: filter yang lebih cepat selama masa uji (SMA 5 punya t90 sekitar 4 detik dengan noise 3,7%), atau menerima tambahan paparan tertentu yang dinyatakan terbuka di laporan. Pilihan ini harus diputuskan tim dan dicatat sebagai trade-off.

### F4. Bukti yang harus disiapkan

| Bukti | Cara |
|---|---|
| Tabel sensitivitas: waktu alarm vs jumlah alarm palsu vs jumlah status bolak-balik, untuk beberapa nilai konfirmasi dan waktu pemulihan | Jalankan mesin status pada log (baseline dan mobil) dan pada skenario simulasi model C-251. Pilih titik di mana perbaikan mulai kecil |
| Kriteria penerimaan UX tertulis | Contoh: "tidak lebih dari satu siklus buka-tutup jendela per sepuluh menit pada pengemudian normal". Angka batasnya harus diputuskan tim, lalu diuji |
| Batas dari aktuator | Jeda minimum antar gerakan power window (cek spesifikasi mobil atau motor) |
| Pernyataan keterbatasan | Waktu untuk CO tidak bisa divalidasi dengan CO asli. Dasarnya model, standar, dan simulasi |

### F5. Waktu tunggu per keputusan (usulan sementara, bukan satu angka untuk semua)

Metode penentuan: simulasi ulang pada log dengan sapuan parameter (lihat F4). Nilai di bawah adalah titik awal sebelum sapuan dijalankan.

| Keputusan | Waktu tunggu (usulan) | Dasar |
|---|---|---|
| CO ≥ 200 ppm (tingkat bahaya) | Hampir langsung, hanya keterlambatan filter | Prinsip 2: kadar sangat tinggi tidak menunggu |
| CO ≥ 35 ppm, memberi alarm dan membuka jendela | 30 detik konfirmasi | Prinsip 1 dan 4. Lebih panjang dari keterlambatan filter, jauh di bawah waktu menuju bahaya |
| Uji arah setelah jendela dibuka | 30–60 detik | Batas bawah: filter butuh sekitar 21 detik. Batas atas: batas tambahan paparan (sekitar 35 detik untuk ΔC = 20 ppm). Harus diputuskan tim (F3) |
| Setelah jendela ditutup karena sumber luar: boleh menguji lagi? | Tidak, sampai CO turun di bawah batas selesai selama waktu pemulihan | Mencegah uji arah berulang dan paparan berulang |
| Pemulihan CO (status selesai) | 60 detik di bawah 30 ppm | Sekitar 6 kali konstanta waktu filter EMA 0,1 (sekitar 9,5 detik) |
| CO2 ≥ 2500 (bunyi singkat) | Beberapa detik saja | Sensor CO2 sudah lambat (T90 kurang dari 120 detik), dan tindakannya lembut |
| CO2 ≥ 4000 (buka jendela) | Beberapa detik saja | Sama. Keterlambatan sensor sudah masuk margin 4000 ppm |
| CO2 selesai | 60 detik di bawah 2400 ppm | Sama dengan C-251, diuji pada sapuan |
| Jeda minimum antar gerakan jendela | **Belum ada angka** | Dari spesifikasi atau uji power window mobil (Classy, Civic) |

## G. Langkah membandingkan hasil simulasi dengan rencana desain

Tujuan: memastikan angka di F5 diganti atau dipertahankan berdasarkan hasil, bukan selera.

1. **Tulis tolok ukur penerimaan lebih dulu, sebelum melihat hasil.** Contoh (angkanya harus diputuskan tim):
   - Waktu alarm setelah kejadian ≤ 10–20% dari waktu menuju bahaya (F2).
   - Alarm palsu pada udara bersih: nol per jam.
   - Status bolak-balik: tidak lebih dari satu perpindahan per kejadian.
   - Siklus buka-tutup jendela: tidak lebih dari N per 10 menit (kriteria UX).
2. **Jalankan sapuan** (konfirmasi, pemulihan, filter) pada tiga jenis data: log udara bersih, log mobil (bila ada), dan kejadian buatan dari model C-251 di atas noise asli.
3. **Uji ketahanan.** Ulangi dengan respons sensor lambat yang berbeda (10, 30, 60 detik) dan noise 1 kali dan 2 kali. Pilihan yang baik tidak berubah banyak di rentang itu.
4. **Isi tabel perbandingan** untuk tiap parameter:

   | Parameter | Nilai di rencana (F5) | Nilai hasil sapuan | Memenuhi tolok ukur? | Tindakan |
   |---|---|---|---|---|
   | (contoh) konfirmasi CO | 30 detik | (isi) | (ya atau tidak) | (pertahankan, ubah, atau perpanjang uji) |

5. **Aturan keputusan:** pilih nilai **terkecil yang masih memenuhi semua tolok ukur**. Bila nilai rencana gagal tolok ukur, ganti dan catat alasannya. Bila jauh lebih konservatif dari yang dibutuhkan, boleh dipertahankan dengan alasan keselamatan yang ditulis jelas.
6. **Perbarui F5 dan firmware**, lalu konfirmasi dengan uji nyata di kotak (napas untuk CO2, lima pengulangan) dan, untuk CO, lewat mode simulasi.
7. **Catat apa yang tidak bisa dibuktikan** (waktu CO tanpa CO asli) sebagai batasan.

## H. Cara menentukan "beberapa detik" untuk CO2

Untuk aksi CO2 2500 (bunyi) dan 4000 (buka jendela), konfirmasi hanya perlu menolak **bacaan satu kali yang salah**. Noise tidak jadi masalah karena jaraknya ke ambang sangat jauh.

Data dari log (sesi 25 Okt 2026, sekitar 7.900 pembacaan setelah warm-up, kamar tertutup):

| Ukuran | Hasil |
|---|---|
| Simpangan baku CO2 di sekitar tren lokal | sekitar 3–4 ppm |
| Perubahan terbesar dalam 1 detik | 14 ppm |
| Lompatan ≥ 30 ppm dalam 1 detik | tidak ada |
| Bacaan gagal (n/a) setelah warm-up | tidak ada |
| Nilai sama berturut-turut | rata-rata sekitar 1,3 detik (sensor memperbarui nilainya kira-kira tiap 1–2 detik) |

Penalaran:
- Noise sekitar 4 ppm, sedangkan ambang 2500 dan 4000 berjarak ratusan sampai ribuan ppm dari kondisi normal. Noise tidak mungkin memicu aksi.
- Satu-satunya risiko adalah satu bacaan rusak (misalnya akibat gangguan catu daya). Konfirmasi **N bacaan valid berturut-turut** cukup untuk menolaknya. Dengan nol bacaan rusak di sekitar 7.900 bacaan, N = 3 (sekitar 3 detik) adalah usulan sementara, dan menambah N hanya menambah keterlambatan tanpa manfaat terukur.
- Batas atas: target C-251 menuntut aktuator bergerak ≤ 10 detik sejak ambang terlewati, jadi konfirmasi harus jauh di bawah itu.
- **Aturan aman gagal:** bacaan `n/a`, atau nilai 410 dan 500 menempel setelah sensor mulai ulang, **bukan tanda udara aman**. Aksi yang sudah aktif tidak boleh dibatalkan oleh bacaan seperti itu.
- Batasan: data ini dari kamar yang diam. Di mobil (getaran, catu daya, suhu) perlu diulang, dan N bisa berubah bila ditemukan bacaan rusak.
