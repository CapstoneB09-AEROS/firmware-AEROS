# Ringkasan Temuan Analisis Rekaman Baseline (25 Oktober 2026)

Data: `logs/device-monitor-261025-115335.log`, sensor MiCS-5524 dan MH-Z19C di kamar, rekaman 11:53 sampai 16:05 WIB (`t_s` 3 sampai 15071, sekitar 4 jam 11 menit, tanpa mulai ulang). Pewangi dicopot sebelum rekaman. Skrip: `skrip/filter_compare.py` dan `noise_profile.py` (folder ini). Hasil mentah: `hasil-noise-2026-10-25.txt`.

Status: **temuan dari satu sesi di kamar yang diam, belum diuji di mobil atau pada rangkaian akhir.** Penyebab tidak dibuktikan.

---

## 1. Ringkasan satu paragraf

Goyangan Rs MiCS terbaca sekitar 13% per detik, dan sekitar **95% dari goyangan itu adalah satu komponen: bergantian naik-turun tiap detik (0,5 Hz)** dengan periode sumber mendekati 2 detik. Goyangan itu **proporsional terhadap sinyal** (bukan noise ADC yang tetap), stabil selama empat jam, dan bisa dibuang dengan rata-rata bergerak jumlah genap pendek (SMA 2 sampai 4). Sisa gangguan sekitar 3% adalah gerakan lambat, yang tidak berkurang walau filter diperpanjang. Selain itu, Rs bergeser lebih dari 50% dalam empat jam, sehingga R0 tidak konstan.

## 2. Temuan

| # | Temuan | Data |
|---|---|---|
| 1 | Hampir semua goyangan adalah satu komponen bergantian tiap detik | Bagian bergantian 93–96% dari ragam goyangan di semua 17 blok 15 menit |
| 2 | Goyangan **proporsional terhadap sinyal**, bukan noise ADC | Noise V terhadap V rata-rata konstan sekitar 11–13% (V naik dari 23 mV ke 50 mV, noise ikut naik dari 2,6 ke 6,4 mV). Korelasi antar blok: V rata-rata vs noise V = +0,99. Noise ADC akan tetap dalam mV |
| 3 | Noise Rs relatif hampir tetap | 12,7–14,7% pada semua blok |
| 4 | Sumber periodik yang stabil, **sedikit berbeda dari 2,000 detik** | Amplitudo bergantian berganti tanda tiap 406–441 detik (median 430). Itu memberi periode sumber sekitar **1,9954 atau 2,0047 detik** (dua kemungkinan). Loop firmware tepat 1,000 detik, jadi sumbernya osilator lain |
| 5 | Sebaran noise dua-tingkat | Kemiringan +0,07, kurtosis −0,53 (lebih datar dari normal). Persentil 50/90/99 dari |noise|: 5,1%, 22,4%, 27,7% |
| 6 | Filter jumlah **genap** meredam, jumlah ganjil kurang | Noise Rs: mentah 13,9%, SMA 2 3,33%, SMA 3 5,59%, SMA 4 3,33%, SMA 5 4,28%, SMA 10 3,30%, EMA 0,2 3,58%, EMA 0,1 3,14% |
| 7 | **Memperpanjang filter tidak membuang sisa noise** | SMA 2 sama baiknya dengan SMA 10. Sisa sekitar 3,3% adalah gerakan lambat (puluhan detik ke atas) |
| 8 | Noise CO2 kecil | Simpangan baku 3,4 ppm, perubahan terbesar 10 ppm per detik, 26% detik tanpa perubahan |
| 9 | **R0 tidak konstan** | Rs rata-rata turun dari sekitar 2045 kΩ ke sekitar 900–1000 kΩ dalam sekitar 4 jam di kamar tanpa gas yang diketahui. Penurunan terjadi saat pengguna tidak di kamar. Penyebab belum diketahui (kelembapan, suhu, atau drift) |
| 10 | Ada dua kejadian celah 1 detik, tanpa mulai ulang | `t_s` 1220→1222 dan 4807→4809, dan beberapa lainnya |

## 3. Arti untuk keputusan filter

- Rata-rata bergerak jumlah genap pendek (SMA 2 sampai 4, keterlambatan sekitar 1–3 detik) membuang sekitar 76% goyangan. Kandidat EMA 0,1 yang tadinya dipertimbangkan (waktu respons sekitar 21 detik) hanya memperbaiki sekitar 0,2 poin persentase lagi, dengan keterlambatan 10 kali lebih besar.
- Pilihan yang cenderung lebih baik: **SMA 4** (meredam 0,5 Hz dan 0,25 Hz, keterlambatan kecil). Ini **usulan**, belum keputusan.
- Syarat penting: filter ini bergantung pada goyangan yang tetap berada di sekitar 0,5 Hz. Jika sumbernya berubah (PCB, MH-Z19C dicabut, catu daya berbeda), pola bisa hilang atau bergeser. Ulangi analisis ini pada rangkaian akhir.
- Sisa noise sekitar 3,3% pada Rs setara sekitar 3,9% pada ppm (ppm bergantung pada Rs^(-1/0,856)). Pita histeresis 35 dan 30 ppm (sekitar 14%) masih sekitar 3,6 kali noise tersebut pada udara bersih.

- Uji ulang `skrip/filter_compare.py` pada 13.000 baris (sekitar 3,6 jam, 12:29–16:05, hasil di `hasil-filter-3jam-2026-10-25.txt`) searah dengan uji 1000 baris: mentah 13,9%, SMA 5 turun 69%, SMA 10 76%, EMA 0,1 77%, EMA 0,2 (firmware sekarang) 74%, EMA 0,05 81% (paling lambat, sekitar 44 detik), median 5 hanya 2%. Setelah SMA jumlah genap ditambahkan ke `skrip/filter_compare.py` (hasil diperbarui): SMA 2, 4, 6, 8, dan 10 semuanya turun 76% (noise Rs 3,3%), sedangkan SMA 3 hanya 60% dan SMA 5 69%. Pembedanya kecepatan dan lonjakan: SMA 4 (respons 3 detik, lonjakan buatan lolos 7,4%), SMA 6 (5 detik, 4,9%), SMA 8 (7 detik, 3,7%). SMA 6 dan SMA 8 lebih baik dari EMA 0,2 kode sekarang (respons 10 detik, lolos 5,9%, turun 74%) pada ketiga ukuran.

## 4. Dugaan penyebab (belum terbukti)

- Sumber bergantian dengan periode sekitar 2 detik yang tidak sinkron dengan loop 1 detik, dan memodulasi Rs secara proporsional, cocok dengan gangguan pada **catu pemanas** (tegangan 5 V yang naik-turun akibat beban berdenyut), bukan dengan noise pembacaan ADC.
- MH-Z19C adalah kandidat (arus puncak 125 mA di manualnya), tetapi **belum dibuktikan**. Cara membuktikan: uji cabut MH-Z19C (tugas T7). Periode siklus pengukuran MH-Z19C tidak tertulis di bagian manual yang saya baca.

## 5. Batasan

- Satu sesi, kamar diam, breadboard, daya dari USB laptop.
- Kondisi lain (mobil, getaran, catu mobil, PCB) belum diuji.
- Noise saat ada gas belum diukur. Respons sensor terhadap gas belum diukur.
- Kejadian `t_s` 3 sampai 300 (warm-up) tidak dipakai.

## 6. Yang perlu dilakukan berikutnya

1. Uji cabut MH-Z19C **tidak dilakukan** (pengguna khawatir merusak rangkaian). Alternatif yang tidak menyentuh perangkat keras: ubah firmware sementara agar CO2 dibaca lebih jarang (misalnya tiap 10 detik) atau berhenti, rekam 15 menit, lalu jalankan `noise_profile.py`. Jika goyangan berubah, MH-Z19C terlibat. Jika tidak, dugaan itu lemah. Uji ini menunjukkan keterlibatan, belum membuktikan penyebab pasti.
2. Ulangi analisis pada rangkaian akhir (PCB dan housing) dan di mobil.
3. Putuskan filter (T9) dengan memakai temuan 6 dan 7.

---

## 7. Temuan lintas uji (26-27 Oktober)

Hasil per uji ada di [pengujian/laporan/](../pengujian/laporan/). Di sini hanya kesimpulan yang melintasi beberapa uji.

| # | Temuan | Uji | Arti |
|---|---|---|---|
| 1 | Goyangan Rs mentah 7-16%, 83-97% berupa pola bergantian 0,5 Hz di kamar, mobil, dan ruang rapat | 0-4 | Filter jumlah genap bekerja di semua tempat |
| 2 | SMA 6 lebih halus dari EMA 0,2: sisa noise 0,7-1,8% lawan 1,0-2,3%; saat jalan bergelombang EMA sedikit lebih halus | 1-4 | SMA 6 dipertahankan; SMA 8 cadangan |
| 3 | Rs/R0 di mobil 0,30-0,69 dengan R0 kamar; ppm estimasi terbaca 0-19 tanpa alarm | 1, 4 | R0 tetap dengan label estimasi |
| 4 | Siklus Rs lambat: 7,01 menit (+/-13-17%, ESP lama, dua hari), 11,9 menit (ESP baru, ruang rapat), 7,6 menit (+/-8%, ESP baru, Avanza); mengecil ke +/-4-7% setelah AC dan pintu tertutup | 2-4 | Periode tidak hanya ditentukan ESP; sumber belum diketahui |
| 5 | Nyala dingin: Rs 156 -> sekitar 1650 kOhm dalam 3 menit (6% di bawah rata-rata menit 7-30); MH-Z19C nilai palsu 410/500 sampai detik 64 (4 dari 5) dan 128 (1) | 2 | Pemanasan 180 detik |
| 6 | Pergeseran Rs 30 detik tanpa gas: turun > 25% tidak pernah dalam sekitar 28.000 detik (maks -21,4%), kecuali pintu dibuka (-23%); > 15% pada 1,6-2,6% waktu | 1-4 | Kriteria uji arah 25% |
| 7 | CO2 Civic (2 orang, tertutup): naik 47-107 ppm/menit saat jalan pelan, turun 51-90 ppm/menit saat melaju (mobil tidak kedap), naik 19-24 saat AC | 1 | Pemulihan CO2 dinilai dari bacaan, bukan anggapan jendela terbuka |
| 8 | CO2 Avanza: +156 (3 orang), +207-218 (4 orang) ppm/menit; dua jendela depan setengah: 4437 -> 2384 dalam sekitar 95 detik dan 4447 -> 2121 dalam sekitar 110 detik; N sekitar 30-32 per jam (perkiraan kasar, batas bawah; dihitung ulang di baris 13); siklus buka-tutup 15,6 menit; CO2 terus turun 460-550 ppm setelah jendela ditutup | 4 | Tutup saat < 2500; angka jendela dari satu mobil |
| 9 | Ruang rapat 13 orang, 77 m3: CO2 1116-1549 ppm selama 45 menit | 3 | Tidak mendekati 2500 |
| 10 | Parfum 30 cm ke sensor: Rs turun 92% dalam 13 detik, estimasi 72-83 ppm, di atas 35 ppm selama 14 detik, pulih sekitar 5,5 menit; 10 cm ke samping: estimasi 11 ppm | 5 | Sensor tidak selektif; konfirmasi 30 detik menolak lonjakan ini di ruang besar; kabin belum diuji |
| 11 | Digitalisasi kurva CO: A = 3,46 dan beta = 0,840, selisih < 1,5% dari 3,7 dan 0,856 di 35-100 ppm | - | Firmware baru memakai 3,46 dan 0,840; v0 tetap 3,7 dan 0,856 |
| 12 | Catu sebelum buck: pin 5 V ESP maks 4,86 V; MH-Z19C 4,69-4,83 V; MiCS 4,64-4,79 V (semuanya di bawah 4,9 V datasheet); R0 1730 kOhm di atas batas datasheet 1500 kOhm | - | Ukur ulang R0 setelah buck |

| 13 | **Laju pertukaran udara N** dengan model yang sama seperti simulasi C-251 (dC/dt = P - N(C - Cext)) dan jeda sensor tau 52 detik. Avanza, jendela tertutup, 4 orang, 20-40 km/jam: **N = 0,5-2 per jam (terbaik 1,0)**, kenaikan produksi efektif P = 15.340 ppm/jam (G efektif sekitar 10,5 L/jam/orang, sekitar 54% dari 19,6 di model). Avanza, dua jendela depan setengah terbuka: **N = 46-79 per jam (terbaik sekitar 60; tergantung tau 30-70 detik)**. Civic, tertutup, melaju (perkiraan kasar, P diasumsikan): **N = 6,6-11 per jam** | 1, 4 | Model C-251 memakai N tertutup 0,5-3 dan N jendela terbuka 13,3-26,1: N tertutup cocok untuk Avanza tetapi Civic yang melaju jauh lebih bocor; N jendela terbuka 27-28 (kasar) sampai 46-79 (dengan jeda sensor), dari sedikit di atas batas atas model sampai sekitar 3 kali; produksi CO2 nyata lebih kecil dari model, jadi model C-251 konservatif. Perbandingan lengkap: [model-vs-uji.md](model-vs-uji.md) |

Skrip dan keluaran mentah: [skrip/](skrip/) dan [hasil/](hasil/). Perhitungan N: [skrip/analisis_n.py](skrip/analisis_n.py), [hasil Avanza](hasil/hasil-n-2026-10-27.txt), [hasil Civic](hasil/hasil-n-civic-2026-10-27.txt).
