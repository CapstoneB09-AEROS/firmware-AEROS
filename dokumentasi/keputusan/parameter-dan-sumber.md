# Parameter dan Sumber

Tujuan: setiap angka di firmware punya **sumber** (datasheet, standar, jurnal, atau data ukur sendiri), bukan keputusan subjektif. Daftar angka final dan nilai sementara ada di [algoritma-firmware.md](algoritma-firmware.md) bagian 2.1; alasan ambang di [peringatan-dan-ambang.md](peringatan-dan-ambang.md); daftar sumber di [daftar-pustaka.md](../referensi/daftar-pustaka.md).

Status yang dipakai:
- `Terbukti`: ada sumber yang sudah dibaca.
- `Sebagian`: ada sumber, tetapi belum cocok atau belum lengkap.
- `Belum`: belum ada sumber, masih pilihan sementara.

---

## Ringkasan dua sensor

### Perbandingan sensor

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

---

## A. Sensor CO (MiCS-5524)

| # | Parameter | Nilai di kode | Sumber | Alternatif | Alasan memilih | Kekurangan | Status |
|---|---|---|---|---|---|---|---|
| A1 | Koefisien kurva `A_COEF` | 3.46 (firmware baru); v0: 3.7 | Datasheet SGX rev 6, hlm. 1, grafik Rs/R0 terhadap ppm (garis tebal "CO"), tanpa persamaan. Pembacaan manual (lihat `kurva-co-mics5524.png`): Rs/R0 ≈ 3.6 pada 1 ppm | | | Hasil membaca grafik beresolusi rendah dengan mata (kira-kira ±10%), bukan nilai pabrikan. **Dicek 27 Okt 2026 (digitalisasi piksel, `analisis/skrip/digitasi_kurva_co.py`):** hasil ukur A=3.46, β=0.840 (A 3.35-3.58 bila sumbu meleset 1,5 piksel). Selisih rumus kode dengan hasil ukur <1,5% di 35-100 ppm (alarm), maks 7% di 1 ppm. **Diputuskan 27 Okt (diubah): firmware baru memakai hasil digitalisasi 3.46 dan 0.840** (satu paket, jangan diganti salah satu). v0 dan kode tim tetap 3.7 dan 0.856. Saat memutar ulang log v0 pada algoritma baru, ppm di bawah sekitar 10 ppm bergeser sampai 7% dan ambang alarm (rasio Rs/R0 untuk 35 ppm) bergeser sekitar 1% (0.1764 menjadi 0.1744). Ini hanya ketepatan membaca gambar, bukan kalibrasi gas. | Terbukti (pembacaan grafik); kalibrasi gas belum |
| A2 | Eksponen kurva `BETA` | 0.840 (firmware baru); v0: 0.856 | Sama seperti A1 (hasil digitalisasi piksel ada di catatan A1). Garis lurus dari sekitar 3.6 (1 ppm) ke 0.01 (1000 ppm) pada grafik log-log memberi kemiringan ≈ 0.85 | | | Garis lurus hanyalah pendekatan. Di bawah sekitar 5 ppm kurva sensor asli biasanya melengkung. Nilai pastinya perlu kalibrasi beberapa konsentrasi CO. | Terbukti (pembacaan grafik); kalibrasi gas belum |
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
| C1 | Jumlah pembacaan yang dirata-rata `N_SAMPEL` | 16 | Rekam data mentah, hitung simpangan baku, uji nilai lain di komputer. Hasil di [filter.md](../analisis/filter.md) | Hasil analisis 25 Okt 2026 (filter.md bagian 2–3) | Hanya sekitar seperdelapan detik, tidak meredam goyangan berperiode 2 detik. | Sebagian |
| C2 | Penghalusan EMA `EMA_ALPHA` | 0.2 | Konstanta waktu ≈ 4.5 detik (rumus di filter.md bagian 9). Bandingkan dengan response time sensor | Hasil analisis 25 Okt 2026: EMA 0.2 meredam 78%, EMA 0.1 meredam 81% (filter.md) | Lonjakan tunggal tetap masuk 20%. Menunda alarm. Diuji hanya di meja, udara bersih, sensor belum stabil. | Sebagian |
| C3 | Kecepatan sampling ADS1115 | bawaan | Datasheet TI ADS1115 (data rate) | | | Belum |
| C4 | Batas tegangan input ADS1115 | gain 1.024 / 2.048 / 4.096 V | Datasheet TI ADS1115 (nilai maksimum mutlak input) | | Log mencatat 3681 mV saat ADS1115 diberi daya 3.3 V. | Belum |
| C5 | Penanganan saturasi/ganti gain | satu tingkat per detik | Uji dengan lonjakan sinyal | | Log: `ADC_SATURASI` sesaat 5 kali. | Belum |
| C6 | Laju kirim data | 1 Hz | Sesuaikan dengan response time sensor | | | Belum |

---

## D. Alarm dan ambang

Angka standar di bawah ini disebut dari ingatan dan **belum diverifikasi**. Cek angka, satuan, dan masa paparannya di sumber aslinya sebelum dipakai.

| # | Parameter | Nilai di kode | Sumber yang perlu dicari | Sumber/data | Kekurangan | Status |
|---|---|---|---|---|---|---|
| D1 | Ambang CO nyala `ALARM_PPM` | 35 ppm | WHO (kualitas udara dalam ruang), NIOSH, OSHA, UL 2034 | NIOSH REL 35 ppm (rata-rata), plafon 200 ppm; OSHA PEL 50 ppm (rata-rata 8 jam); UL 2034 (alarm rumah). Rencana: [peringatan-dan-ambang.md](peringatan-dan-ambang.md) bagian B | Standar itu untuk paparan kerja dan alarm rumah, bukan khusus mobil. Pendekatan kadar dikali waktu belum diterapkan di kode. WHO belum terkonfirmasi dari dokumen utama | Sebagian |
| D2 | Ambang CO mati `CLEAR_PPM` | 25 ppm | Alasan histeresis | | | Belum |
| D3 | Konfirmasi nyala | 10 detik | Standar alarm CO: waktu paparan sebelum alarm | | Alarm bisa lebih lambat dari tuntutan standar. | Belum |
| D4 | Konfirmasi mati | 30 detik | | | Buzzer tetap bunyi walau ppm sudah 0. | Belum |
| D5 | Batas bawah estimasi | < ±10 ppm dianggap 0 | Rentang sensor 1–1000 ppm dan akurasi hasil ukur | | | Belum |
| D6 | Ambang CO2 | 1000 / 2000 / 5000 ppm | ASHRAE, aturan Kemenkes tentang kualitas udara dalam ruang | Rencana baru (1000 informasi, 2500 peringatan, 4000 tindakan): lihat [peringatan-dan-ambang.md](peringatan-dan-ambang.md) | Belum diuji. Laju naik dan laju turun CO2 di mobil belum terukur | Sebagian |
| D7 | Warm-up sebelum alarm aktif | 300 detik di kode; **usulan baru 180 detik** | Log 25 Okt: Rs kamar stabil dalam 1–2 menit; MiCS tidak punya angka di datasheet | | | Sementara sampai uji nyala dingin. Alasan: [algoritma-firmware.md](algoritma-firmware.md) bagian 2.7 | Sebagian |

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

## Catatan lain
- Keterbatasan yang ditulis di laporan: [batasan-sistem.md](batasan-sistem.md).
- Temuan dari log serial awal dan catatan percobaan baseline kamar: [pengujian/laporan/uji-0-baseline-kamar-2026-10-25.md](../pengujian/laporan/uji-0-baseline-kamar-2026-10-25.md).
