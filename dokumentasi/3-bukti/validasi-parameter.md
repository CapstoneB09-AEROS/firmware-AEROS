# Daftar Validasi Parameter Firmware (Capstone)

Tujuan: setiap angka di `src/main.cpp` punya **sumber** (datasheet, standar, jurnal, atau data ukur sendiri), bukan keputusan subjektif.

## Cara memakai dokumen ini
1. Untuk setiap baris, isi kolom **Sumber**, **Alternatif**, **Alasan memilih**, dan **Kekurangan**.
2. Ubah **Status** menjadi `Terbukti` hanya jika sumbernya sudah dibaca dan dicatat (judul, halaman/bagian, tanggal akses).
3. Kalau datasheet tidak punya angkanya, ukur sendiri dan simpan data mentahnya (lihat bagian "Percobaan").
4. Kalau angkanya belum bisa dibuktikan, tulis di bagian "Keterbatasan" laporan.

Status yang dipakai:
- `Terbukti`: ada sumber yang sudah dibaca.
- `Sebagian`: ada sumber, tetapi belum cocok atau belum lengkap.
- `Belum`: belum ada sumber, masih pilihan sementara.

---

## A. Sensor CO (MiCS-5524)

| # | Parameter | Nilai di kode | Sumber | Alternatif | Alasan memilih | Kekurangan | Status |
|---|---|---|---|---|---|---|---|
| A1 | Koefisien kurva `A_COEF` | 3.7 | Datasheet SGX rev 6, hlm. 1, grafik Rs/R0 terhadap ppm (garis tebal "CO"), tanpa persamaan. Pembacaan manual (lihat `kurva-co-mics5524.png`): Rs/R0 ≈ 3.6 pada 1 ppm | | | Hasil membaca grafik beresolusi rendah dengan mata (kira-kira ±10%), bukan nilai pabrikan. **Dicek 27 Okt 2026 (digitalisasi piksel, `analisis/digitasi_kurva_co.py`):** hasil ukur A=3.46, β=0.840 (A 3.35-3.58 bila sumbu meleset 1,5 piksel). Selisih rumus kode dengan hasil ukur <1,5% di 35-100 ppm (alarm), maks 7% di 1 ppm. **Diputuskan tetap 3.7 dan 0.856** (satu paket, jangan diganti salah satu). Ini hanya ketepatan membaca gambar, bukan kalibrasi gas. | Terbukti (pembacaan grafik); kalibrasi gas belum |
| A2 | Eksponen kurva `BETA` | 0.856 | Sama seperti A1. Garis lurus dari sekitar 3.6 (1 ppm) ke 0.01 (1000 ppm) pada grafik log-log memberi kemiringan ≈ 0.85 | | | Garis lurus hanyalah pendekatan. Di bawah sekitar 5 ppm kurva sensor asli biasanya melengkung. Nilai pastinya perlu kalibrasi beberapa konsentrasi CO. **Dicek 27 Okt 2026 (digitalisasi piksel, `analisis/digitasi_kurva_co.py`):** hasil ukur A=3.46, β=0.840 (A 3.35-3.58 bila sumbu meleset 1,5 piksel). Selisih rumus kode dengan hasil ukur <1,5% di 35-100 ppm (alarm), maks 7% di 1 ppm. **Diputuskan tetap 3.7 dan 0.856** (satu paket, jangan diganti salah satu). Ini hanya ketepatan membaca gambar, bukan kalibrasi gas. | Terbukti (pembacaan grafik); kalibrasi gas belum |
| A3 | Arti R0 pada grafik datasheet | (di kode: Rs di udara bersih) | Datasheet SGX rev 6, hlm. 2, catatan 1: R0 = hambatan sensor di udara sintetis, 23 ±5 °C, 50 ±10% RH. Grafik memakai Rs/R0 | | | Jika R0 adalah Rs di udara, kurva CO pada 1 ppm seharusnya mendekati 1. Rumus di kode memberi 3.7. Rs/R0 = 1 setara sekitar 4.6 ppm. Ini perlu dicek ulang pada grafik. | Terbukti (definisi) |
| A4 | Nilai R0 | 1730 kΩ (sementara) | Datasheet SGX rev 6, hlm. 2: 100–1500 kΩ | | | Itu rentang spesifikasi, bukan satu nilai untuk semua sensor. Log: Rs masih naik sampai 2296 kΩ. | Terbukti (rentang) |
| A5 | Waktu pemanasan/stabil | 300 detik | Adafruit (halaman overview): tunggu 1 detik setelah heater menyala. Saran aging 24 jam dari SGX **belum saya verifikasi** | | | 1 detik hanya agar pemanas panas, bukan agar baseline stabil. Datasheet resmi tidak memuat angka stabilisasi. | Sebagian |
| A6 | Response time | belum ada di kode | Tidak ada di datasheet resmi maupun Adafruit | | | Harus diukur sendiri. | Belum |
| A7 | Recovery time (pemulihan setelah gas hilang) | belum ada di kode | Tidak ada di datasheet resmi | | | Harus diukur sendiri. | Belum |
| A8 | Kompensasi suhu dan kelembapan | tidak ada | Abdullah dkk., Sensors 2022, 22(9):3301 (DOI 10.3390/s22093301): meneliti MiCS-5524 dan membuat model regresi koreksi suhu dan kelembapan per sensor | | | Koefisien dari studi itu tidak otomatis cocok untuk sensor Anda. Kurva datasheet hanya pada 25 °C dan 50% RH. | Sebagian |
| A9 | Tegangan pemanas/catu | `VCC = 4.64` | Datasheet SGX rev 6, hlm. 3: pemanas tipikal 2.4 V, catu 4.9–5.1 V | | | Kode memakai 4.64 V (hasil ukur), di bawah rentang datasheet. Pemanas kurang panas bisa mengubah Rs dan sensitivitas. **Ukur 26 Okt 2026 (ESP baru, USB laptop, sebelum buck, multimeter, ±3 detik, belum Min/Max):** pin 5V ESP maks 4,86 V; pin MH-Z19C 4,69–4,83 V; pin MiCS 4,64–4,79 V. Semua di bawah 4,9 V. VCC kode tetap 4,64 sampai buck terpasang (pilihan B). **Datasheet rev 8:** R0 di udara sintetis 100-1500 kOhm, sedangkan R0 kita 1730 kOhm (di atas batas); dugaan: catu 4,64 V membuat pemanas kurang panas (belum diuji). Ukur ulang R0 setelah buck. | Terbukti (spesifikasi) |
| A10 | Resistor beban `RL_OHM` | 9970 Ω | Datasheet SGX rev 6, hlm. 3: RLOAD minimal 820 Ω | | | Itu batas minimum, bukan nilai wajib. | Terbukti (batas minimum) |
| A11 | Gas lain yang ikut terbaca | tidak ditangani | Datasheet SGX: grafik untuk CO, etanol, hidrogen, amonia, metana, propana, isobutana. Adafruit: sensor tidak bisa membedakan gas penyebab | | | Alkohol, H2, amonia, dll. ikut mengubah Rs. | Terbukti |
| A12 | Pembanding CO asli | tidak ada | Adafruit (halaman overview): semua sensor gas perlu kalibrasi. Detail metode (aliran 0.5 L/menit, flowhood) **belum saya verifikasi** | | | Tanpa alat terkalibrasi, ppm hanya estimasi. | Sebagian |

Fakta dari datasheet SGX MiCS-5524 rev 6 (sudah dibaca):
- R0 di udara: 100–1500 kΩ. Faktor sensitivitas Rs(udara)/Rs(60 ppm CO): 1.2–50 (nilai indikatif).
- Pemanas: 76 mW, 2.4 V, 32 mA. Catu daya yang diminta 4.9–5.1 V.
- Rentang CO yang umum: 1–1000 ppm, kurva pada 25 °C, 50% RH.
- Hindari pelarut organik, uap silikon, dan asap rokok (merusak lapisan sensor).
- Response time, preheat time, dan recovery time **tidak tertulis**.

Catatan verifikasi:
- Halaman dan isi datasheet di atas saya baca dari **rev 6**. Rev 8 (tautan SGX) sebagian besar berupa gambar sehingga teksnya tidak terbaca. Rujukan "hlm." untuk rev 8 perlu dicek manual.
- Saran "aging 24 jam" dan metode kalibrasi aliran 0.5 L/menit berasal dari rangkuman pihak ketiga. Halaman Adafruit yang saya buka tidak memuatnya. Baca sendiri bagian aslinya sebelum mengutip.
- Arti `Terbukti`: sumber sudah dibaca dan sesuai dengan klaimnya. Tidak berarti nilai di kode sudah benar.

---

## B. Sensor CO2 (MH-Z19C)

| # | Parameter | Nilai di kode | Sumber | Alternatif | Alasan memilih | Kekurangan | Status |
|---|---|---|---|---|---|---|---|
| B1 | Waktu preheat | 180 detik | Manual Winsen v1.2: 1 menit | | | Log: nilai 500/410 menempel sampai t=64 detik pada 4 dari 5 kali menyala (25 Okt), dan sampai t=128 pada satu kali menyala dingin pertama malam itu. Sebelumnya terlihat sampai t=175. Jadi 1 menit kadang kurang; 180 detik di kode masih menutup semua kasus. | Sebagian |
| B2 | Response time | tidak ada | Manual Winsen: T90 < 120 detik | | | Perubahan CO2 terbaca lambat. | Terbukti |
| B3 | Kalibrasi otomatis (ABC) | aktif (`DISABLE_ABC = false`) | Manual Winsen: tiap 24 jam, titik nol 400 ppm | | | Tidak cocok untuk ruang yang tidak pernah kena udara luar. | Terbukti |
| B4 | Akurasi | tidak dicek | Manual Winsen: ±(50 ppm + 5% pembacaan) | | | Bandingkan dengan CO2 meter lain. | Terbukti |
| B5 | Deteksi sensor mulai ulang | tidak ada | | | | Log: sensor sempat `n/a` lalu kembali 410/500 di t=115. | Belum |

Fakta dari manual Winsen MH-Z19C v1.2 (sudah dibaca):
- UART 9600 8N1, level 3.3 V. Perintah baca `FF 01 86 00 00 00 00 00 79`. Checksum = `0xFF - jumlah(Byte1..7) + 1`.
- Catu 5.0 ±0.1 V, arus rata-rata < 40 mA, puncak 125 mA.
- Rentang 400–5000 ppm (varian lain 400–2000 dan 400–10000).
- Preheat 1 menit, T90 < 120 detik.

---

## C. Filter dan pembacaan

| # | Parameter | Nilai di kode | Cara membuktikan | Sumber/data | Kekurangan | Status |
|---|---|---|---|---|---|---|
| C1 | Jumlah pembacaan yang dirata-rata `N_SAMPEL` | 16 | Rekam data mentah, hitung simpangan baku, uji nilai lain di komputer. Hasil di [filtering.md](filtering.md) | Hasil analisis 25 Okt 2026 (filtering.md bagian 2–3) | Hanya sekitar seperdelapan detik, tidak meredam goyangan berperiode 2 detik. | Sebagian |
| C2 | Penghalusan EMA `EMA_ALPHA` | 0.2 | Konstanta waktu ≈ 4.5 detik (rumus di filtering.md bagian 9). Bandingkan dengan response time sensor | Hasil analisis 25 Okt 2026: EMA 0.2 meredam 78%, EMA 0.1 meredam 81% (filtering.md) | Lonjakan tunggal tetap masuk 20%. Menunda alarm. Diuji hanya di meja, udara bersih, sensor belum stabil. | Sebagian |
| C3 | Kecepatan sampling ADS1115 | bawaan | Datasheet TI ADS1115 (data rate) | | | Belum |
| C4 | Batas tegangan input ADS1115 | gain 1.024 / 2.048 / 4.096 V | Datasheet TI ADS1115 (nilai maksimum mutlak input) | | Log mencatat 3681 mV saat ADS1115 diberi daya 3.3 V. | Belum |
| C5 | Penanganan saturasi/ganti gain | satu tingkat per detik | Uji dengan lonjakan sinyal | | Log: `ADC_SATURASI` sesaat 5 kali. | Belum |
| C6 | Laju kirim data | 1 Hz | Sesuaikan dengan response time sensor | | | Belum |

---

## D. Alarm dan ambang

Angka standar di bawah ini disebut dari ingatan dan **belum diverifikasi**. Cek angka, satuan, dan masa paparannya di sumber aslinya sebelum dipakai.

| # | Parameter | Nilai di kode | Sumber yang perlu dicari | Sumber/data | Kekurangan | Status |
|---|---|---|---|---|---|---|
| D1 | Ambang CO nyala `ALARM_PPM` | 35 ppm | WHO (kualitas udara dalam ruang), NIOSH, OSHA, UL 2034 | NIOSH REL 35 ppm (rata-rata), plafon 200 ppm; OSHA PEL 50 ppm (rata-rata 8 jam); UL 2034 (alarm rumah). Rencana: [desain-peringatan.md](desain-peringatan.md) bagian B | Standar itu untuk paparan kerja dan alarm rumah, bukan khusus mobil. Pendekatan kadar dikali waktu belum diterapkan di kode. WHO belum terkonfirmasi dari dokumen utama | Sebagian |
| D2 | Ambang CO mati `CLEAR_PPM` | 25 ppm | Alasan histeresis | | | Belum |
| D3 | Konfirmasi nyala | 10 detik | Standar alarm CO: waktu paparan sebelum alarm | | Alarm bisa lebih lambat dari tuntutan standar. | Belum |
| D4 | Konfirmasi mati | 30 detik | | | Buzzer tetap bunyi walau ppm sudah 0. | Belum |
| D5 | Batas bawah estimasi | < ±10 ppm dianggap 0 | Rentang sensor 1–1000 ppm dan akurasi hasil ukur | | | Belum |
| D6 | Ambang CO2 | 1000 / 2000 / 5000 ppm | ASHRAE, aturan Kemenkes tentang kualitas udara dalam ruang | Rencana baru (1000 informasi, 2500 peringatan, 4000 tindakan): lihat [desain-peringatan.md](desain-peringatan.md) | Belum diuji. Laju naik dan laju turun CO2 di mobil belum terukur | Sebagian |
| D7 | Warm-up sebelum alarm aktif | 300 detik di kode; **usulan baru 180 detik** | Log 25 Okt: Rs kamar stabil dalam 1–2 menit; MiCS tidak punya angka di datasheet | | | Sementara sampai uji nyala dingin. Alasan: [pseudocode-baru.md](../1-utama/pseudocode-baru.md) bagian 2.7 | Sebagian |

---

## E. Percobaan yang bisa dilakukan sendiri

Simpan data mentah (CSV) dan catat tanggal, suhu, kelembapan, dan kondisi ruangan.

| # | Percobaan | Menjawab | Cara |
|---|---|---|---|
| E1 | Uji nyalakan dingin | A4, A5, D7 | Nyalakan sensor, rekam Rs sampai stabil. Tulis kriteria "stabil" di awal, misalnya perubahan < 2% per jam. |
| E2 | Uji udara bersih beberapa hari | A3, A4 | Rekam Rs di udara bersih, lihat seberapa R0 bergeser antar hari. |
| E3 | Uji paparan terkontrol | A6, A7, D3 | Paparkan sumber gas yang aman, catat waktu naik dan waktu turun. |
| E4 | Uji filter | C1, C2 | Simpan data mentah, coba nilai filter lain di Excel/Python, bandingkan noise dan keterlambatan. |
| E5 | Uji CO2 mulai dingin | B1 | Catat kapan angka CO2 berhenti menempel di 410/500. |
| E6 | Pembandingan | A1, A2, A12, B4 | Bandingkan dengan alat ukur terkalibrasi. |
| E7 | Uji tegangan | A9, C4 | Ukur VCC modul dan tegangan keluaran MiCS saat ada gas (dengan bantuan rekan hardware). |

---

## F. Temuan dari log serial awal (`.vscode/readme.md`)

Ringkasan, untuk dibuktikan lagi dengan data baru:
- Tegangan MiCS mencapai 3681 mV saat gas kuat (t=369). Itu melewati sekitar 3.6 V, batas input ADS1115 jika diberi daya 3.3 V.
- `ADC_SATURASI` sesaat di t=367, 368, 377, 384, 386 akibat penggantian gain otomatis.
- Alarm menyala di t=395 dan mati di t=431. Selama 30 detik terakhir buzzer tetap bunyi walau ppm sudah 0.
- Sensor CO2 sempat `n/a` di t=115 lalu kembali 410 dan 500 (kemungkinan mulai ulang).
- Rs naik dari 512 kΩ sampai 2296 kΩ dalam sekitar 8 menit (belum stabil).
- Tegangan MiCS bergoyang bolak-balik tiap detik (72 dan 59 mV) pada awal log.
- Ada beberapa detik data hilang dan baris teks terpotong di t≈268–274 dan t≈366–387.

---

## G. Keterbatasan yang perlu ditulis di laporan

Versi lengkap beserta kalimat contoh dan batasan operasi sensor ada di [batasan-sistem.md](batasan-sistem.md). Ringkasnya:
- Nilai ppm CO adalah **estimasi** dari kurva datasheet, belum dikalibrasi dengan gas CO standar.
- Tidak ada kompensasi suhu dan kelembapan.
- MiCS-5524 juga bereaksi terhadap gas lain (alkohol, H2, amonia, dll.).
- Alat ini bukan alat keselamatan. Datasheet maupun pembuat breakout tidak menyatakan sensor cocok untuk keselamatan jiwa.

## H. Daftar sumber (isi sambil jalan)

| Sumber | Dipakai untuk | Tanggal akses |
|---|---|---|
| SGX Sensortech, MiCS-5524 datasheet rev 6 | A1–A12 | |
| Winsen, MH-Z19C manual v1.2 | B1–B5 | |
| Adafruit, MiCS5524 Gas Sensor Breakout (halaman overview) | A5, A11, A12 | |
| Abdullah dkk., Sensors 2022, 22(9):3301, DOI 10.3390/s22093301 | A8 | |
| TI, ADS1115 datasheet | C3, C4 | |
| (isi: standar alarm CO) | D1–D5 | |
| (isi: standar kualitas udara CO2) | D6 | |
| (isi: jurnal tentang MiCS-5524) | A1, A2, A5–A8 | |

---

## I. Catatan percobaan baseline (udara kamar)

Untuk menjawab A4, A5, D7 (percobaan E1 dan E2).

| Catatan | Isi |
|---|---|
| Tanggal | 25 Oktober 2026 |
| Penanda waktu | Pada `t_s = 3700` jam di komputer menunjukkan sekitar 11:00 WIB (pembacaan dari pengguna) |
| Perkiraan waktu nyala (`t_s = 0`) | sekitar 09:58 WIB (11:00 dikurangi 3700 detik) |
| Kecocokan | Log serial awal (`.vscode/readme.md`) berakhir di `t_s = 517`, sekitar 10:07 WIB, sama dengan waktu terakhir file itu disimpan |
| Lokasi | Kamar, diasumsikan udara bersih (belum dibuktikan dengan alat ukur) |
| Suhu dan kelembapan | Tidak diukur. Diputuskan tidak dikompensasi karena keterbatasan waktu dan pengetahuan. Ini keterbatasan. |
| Kriteria "stabil" | (isi sebelum menganalisis, misalnya perubahan Rs < 2% per jam) |
| Catatan kejadian (parfum, pintu/jendela, orang di kamar, dll.) | (isi sambil jalan) |

Peringatan: `t_s` kembali ke 0 setiap ESP32 mulai ulang (dicabut, ditekan EN, atau port serial dibuka). Catat jam setiap kali itu terjadi.

### Kondisi ruangan, run kedua (mulai dingin, log ke file)

Dicatat oleh pengguna sebelum mencolok sensor, 25 Oktober 2026 (jam mulai: isi saat dicolok).

| Item | Kondisi |
|---|---|
| Sensor sebelumnya | Dicabut sekitar 20 menit supaya dingin |
| Kipas | Menyala, dengan pewangi ruangan (aroma dahlia) terpasang. **Potensi gangguan**: pewangi melepas senyawa yang bisa ikut terbaca MiCS (sensor bereaksi ke banyak gas, bukan hanya CO) |
| Orang | Pengguna sendirian di kamar |
| Jendela dan pintu | Jendela tertutup, pintu kamar terbuka (tersambung ke ruang tengah) |
| Posisi sensor | Di atas meja, di sebelah siku pengguna saat mengetik. Dekat tubuh dan napas pengguna, sehingga CO2 bisa naik |
| Catatan | Run ini tidak bisa dianggap "udara bersih murni" bila pewangi dan kipas tetap menyala. Bandingkan dengan run tanpa pewangi bila ada waktu |
| Jam sensor dicolok (`t_s = 0`) | sekitar 11:39:53 WIB (dihitung dari `t_s = 20` pada 11:40:13) |
| File log | `logs/device-monitor-261025-114013.log`, tiap baris diawali jam. Rekaman mulai di `t_s = 20`, jadi 20 detik pertama tidak terekam |
| Gangguan 1 | 11:53:17 WIB: log sistem macOS mencatat perangkat USB CP2102 terlepas (`Removed`) lalu tersambung lagi 11:53:18. ESP32 mulai ulang (`t_s` kembali ke 0). File log baru: `device-monitor-261025-115319.log`. Run pertama berakhir di `t_s = 803` |
| Gangguan 2 | 11:53:34 WIB: terulang. Terlepas 11:53:34, tersambung 11:53:35. File log baru: `device-monitor-261025-115335.log`. Pengguna tidak menyentuh perangkat |
| Dugaan penyebab | Sambungan USB atau catu daya terputus sesaat (kabel/konektor, breadboard, atau tegangan turun). Belum terbukti. Perlu dicek oleh rekan hardware |
| Dampak | Warm-up MiCS dan MH-Z19C mulai dari awal setiap kejadian. Data sebelum dan sesudah gangguan berada di file berbeda dan tidak boleh disambung sebagai satu run |
| Koreksi kondisi | Pewangi dahlia **dicopot sebelum rekaman dimulai** (keterangan pengguna, 25 Okt 2026). Status kipas belum dicatat |
| Kehadiran pengguna | Tidak di kamar sekitar 12:46–13:00. Di kamar lagi sejak sekitar 13:36. Pada rentang itu CO2 terendah 924 ppm (12:52) dan tertinggi 1116 ppm (13:40) |
| Pengamatan Rs (14:02) | Rs rata-rata turun dari sekitar 2040 kΩ ke sekitar 1460–1540 kΩ dalam sekitar 2 jam. Lereng 60 menit terakhir sekitar −29% per jam dan 30 menit terakhir sekitar −17% per jam, jauh dari kriteria stabil (di bawah 2% per jam). Penurunan tajam sekitar 13:16–13:36 (1792 ke 1491 kΩ) **belum dapat dijelaskan**: pengguna menyatakan tidak ada perubahan di kamar. Pewangi sudah disingkirkan, jadi penyebab yang tersisa adalah suhu atau kelembapan kamar, drift sensor, atau sebab lain. Tidak ada sensor suhu dan kelembapan untuk memisahkannya |
| Akhir rekaman | Dihentikan sekitar 16:05 WIB karena baterai laptop 9%. Sesi `115335`: `t_s` 3 sampai 15071 (sekitar 4 jam 11 menit), 15.064 baris, tanpa mulai ulang, lima celah masing-masing sekitar 1 detik |
| Pengamatan Rs sampai akhir | Rs rata-rata per 15 menit: sekitar 2045 kΩ (11:53), 1508 (13:53), 1466 (14:53), 1332 (15:08), 1111 (15:23), 1014 (15:38), 907 (15:53). Pada 16:04 Rs 832 kΩ, rasio 0,48, ppm CO estimasi 11 ("OK", bukan "OK(<10ppm)"). Penurunan **mempercepat sejak sekitar 15:00** (lereng 60 menit terakhir sekitar −50% per jam). Tidak ada baseline stabil. Penyebab **belum diketahui**: gas pereduksi di kamar (VOC, alkohol, dan lain-lain), suhu atau kelembapan, atau drift. Data ini **tidak boleh dipakai untuk menetapkan R0** |
| Kegiatan pengguna (keterangan 16:07) | Pengguna mandi tanpa pewangi tambahan dan keluar kamar. CO2 di bawah 800 ppm dari 15:18:52 sampai 15:48:25 (minimum 766 ppm), cocok dengan pengguna tidak di kamar. Pada rentang itu Rs turun paling cepat (rata-rata 10 menit: 1395 kΩ pada 15:05, 1244, 1070, 1075, 963, lalu 918 kΩ pada 15:55 setelah pengguna kembali) |
| Tafsir (hipotesis, belum terbukti) | Penurunan Rs terjadi saat **tidak ada orang di kamar**, jadi bukan akibat kehadiran atau pewangi pengguna. Kandidat: kelembapan (uap mandi masuk ke kamar), suhu, atau drift. Tanpa sensor suhu dan kelembapan tidak bisa dibuktikan. Temuan yang aman dituliskan: pada kamar tanpa gas yang diketahui, Rs bergeser lebih dari 50% (sekitar 2045 ke sekitar 900–1000 kΩ) dalam sekitar 4 jam, sehingga **R0 tidak konstan** dan kalibrasi R0 harus diulang pada kondisi yang dicatat |
