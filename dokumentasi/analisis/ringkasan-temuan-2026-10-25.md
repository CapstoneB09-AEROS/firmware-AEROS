# Ringkasan Temuan Analisis Rekaman Baseline (25 Oktober 2026)

Data: `logs/device-monitor-261025-115335.log`, sensor MiCS-5524 dan MH-Z19C di kamar, rekaman 11:53 sampai 16:05 WIB (`t_s` 3 sampai 15071, sekitar 4 jam 11 menit, tanpa mulai ulang). Pewangi dicopot sebelum rekaman. Skrip: `filter_compare.py` dan `noise_profile.py` (folder ini). Hasil mentah: `hasil-noise-2026-10-25.txt`.

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

- Uji ulang `filter_compare.py` pada 13.000 baris (sekitar 3,6 jam, 12:29–16:05, hasil di `hasil-filter-3jam-2026-10-25.txt`) searah dengan uji 1000 baris: mentah 13,9%, SMA 5 turun 69%, SMA 10 76%, EMA 0,1 77%, EMA 0,2 (firmware sekarang) 74%, EMA 0,05 81% (paling lambat, sekitar 44 detik), median 5 hanya 2%. Setelah SMA jumlah genap ditambahkan ke `filter_compare.py` (hasil diperbarui): SMA 2, 4, 6, 8, dan 10 semuanya turun 76% (noise Rs 3,3%), sedangkan SMA 3 hanya 60% dan SMA 5 69%. Pembedanya kecepatan dan lonjakan: SMA 4 (respons 3 detik, lonjakan buatan lolos 7,4%), SMA 6 (5 detik, 4,9%), SMA 8 (7 detik, 3,7%). SMA 6 dan SMA 8 lebih baik dari EMA 0,2 kode sekarang (respons 10 detik, lolos 5,9%, turun 74%) pada ketiga ukuran.

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

## 7. Tambahan: uji mobil malam 25 Oktober (firmware lama v0)

Data: `logs/device-monitor-261025-214144.log` (21:41 sampai 21:57) dan `...220026.log` (22:00 sampai 22:15). Log `...213732.log` hanya 4 menit (mulai ulang), tidak dipakai. Skrip: `analisis_mobil.py`. Hasil mentah: `hasil-uji-mobil-2026-10-25.txt`. Catatan lapangan: `2-lapangan/skenario-uji-mobil.md` bagian 1.

Status: **dua sesi pendek, tanpa gas CO acuan.** Sebab perubahan Rs tidak dibuktikan.

| # | Temuan | Bukti |
|---|--------|-------|
| 1 | Goyangan 0,5 Hz **sama di mobil** (9,4–9,9% mentah, 94–95% bergantian; kamar 13%, 93–95%) | `analisis_mobil.py` |
| 2 | SMA genap tetap lebih halus dari EMA 0,2 di mobil: sisa noise 0,9% (SMA 4 dan 6) lawan 1,3% (EMA 0,2). Lompatan 0 ↔ 10 ppm: 1–2 kali (SMA 6) lawan 14–19 kali (EMA 0,2) | `analisis_mobil.py` bagian 2 dan 3 |
| 3 | Rs/R0 di mobil **0,30–0,67**, bukan sekitar 1,0 seperti di kamar. Akibatnya ppm estimasi terbaca 0–19 terus-menerus, tanpa alarm (tidak ada detik ≥ 35 ppm) | R0 1730 kOhm dari kamar |
| 4 | Rs bergeser jauh lebih besar dari noise: sampai +15% dan −17% **per menit**, rentang 570–1078 kOhm dalam 15 menit | bagian 4 |
| 5 | **Di kamar yang diam pun** Rs naik-turun dengan periode **sekitar 7,0 menit, ±14–15%**, stabil selama 4 jam (seperempat 1–4: 14,3 / 15,3 / 14,1 / 15,0%). Di kamar **tidak ada AC**, hanya kipas yang mengarah ke tempat duduk, jadi AC bukan penjelasannya. Belum diketahui sumbernya | bagian 6, log 11:53–16:05 |
| 6 | Setelah dihidupkan di mobil, Rs terus bergeser sekitar 9–10 menit (480 → 1078 kOhm di sesi 22:00, 620 → 997 di sesi 21:41). **Di kamar Rs sudah stabil dalam 1–2 menit setelah dihidupkan** (menit ke-0 sampai 4: 1492, 1878, 1968, 1973, 1994 kOhm). Jadi pemanasan sensor sendiri cukup singkat, dan pergeseran di mobil lebih mungkin berasal dari kondisi kabin. Warm-up 5 menit di firmware **tidak perlu diperpanjang** | log 11:40 dan 11:53 (kamar) lawan bagian 4 |
| 7 | AC dinyalakan 21:51: Rs turun 1034 → 808 dalam 90 detik. AC dinyalakan sekitar 22:08: tidak ada penurunan setajam itu. **Belum konsisten** | per-30-detik di sekitar jam kejadian |
| 8 | 21:56–21:57 (menuju SPBU, AC mati): Rs turun 17% dalam semenit (686 → 567). Cocok dengan uap bensin atau gas buang, tetapi tidak dibuktikan | bagian 4 |
| 9 | MH-Z19C mengeluarkan nilai 410/500 palsu sekitar 60 detik pertama setelah menyala, lalu nilai nyata (1788 dan 2449 ppm) | log setelah boot |
| 10 | CO2 (Civic EG6 1994, 2 orang di kursi depan, jendela tidak pernah dibuka, selalu mode sirkulasi dalam): naik 47–107 ppm/menit saat jalan pelan, **turun 90 ppm/menit** saat ngebut (22:04–22:07) dan turun 51 ppm/menit saat 20–30 km/jam (22:10–22:14). Saat AC menyala naik hanya 19–24 ppm/menit | kemiringan per fase |
| 11 | Warm-up CO2: sensor mengeluarkan 410/500 palsu sampai t=64 detik (4 dari 5 kali nyala) atau t=128 detik (1 kali, nyala dingin pertama malam itu). Di kamar nilainya datar 996–999 ppm mulai t=64 sampai t=300. Akurasinya tanpa gas acuan tidak bisa dipastikan | log 11:40, 11:53, 21:37, 21:41, 22:00 |
| 12 | Drift alami Rs (SMA 6) tanpa gas: perubahan lebih dari −8% dalam 30 detik terjadi pada 12% waktu (mobil sesi 1), 8% (sesi 2), 13% (kamar 4 jam). Persentil ke-5 perubahan 30 detik: −11,7 / −9,0 / −13,4%. Kriteria uji arah 8% (B6) tidak aman | hitung dari log yang sama |

Kondisi uji: mobil Honda Civic EG6 1994, 2 orang di kursi depan, alat di jok sebelah paha penumpang, jendela tidak pernah dibuka, udara selalu sirkulasi dalam. Jalan ngebut = jalan bagus dan ring road sepi. Jalan pelan = jalan agak rusak atau mengikuti arus.

Batasan tambahan: tidak ada jendela dibuka, jadi N dari pembukaan jendela belum bisa dihitung. Dari luruhan 22:05–22:13 hanya didapat N tampak sekitar 1,3 per jam (batas bawah: penumpang masih bernapas, CO2 luar diasumsikan 420 ppm). Alat di dekat paha penumpang, jadi pembacaan bisa terpengaruh napas dan panas tubuh. Posisi alat di PCB/housing perlu dipikirkan.

---

## 8. Tambahan: uji kamar pagi 26 Oktober (firmware lama)

Data: `logs/device-monitor-261026-090343.log` (09:03–10:47, 6226 detik, tanpa mulai ulang). Kipas menyala sampai sekitar 09:45 (pintu terbuka, pemilik di luar), kipas mati sampai sekitar 10:15 (pintu terbuka), lalu AC menyala dan pintu ditutup (pemilik dekat alat). Skrip: `analisis_fase.py`. Hasil mentah: `hasil-uji-kamar-pagi-2026-10-26.txt`. Laporan: `2-lapangan/skenario-uji-mobil.md` bagian 2.

| # | Temuan | Bukti |
|---|--------|-------|
| 1 | SMA 6 lebih halus dari EMA 0,2 di ketiga fase: sisa noise 1,25 / 1,82 / 0,97% lawan 1,81 / 2,34 / 1,83% | `analisis_fase.py` |
| 2 | Goyangan mentah 13,0 / 15,2 / 15,6%; bagian bergantian 93 / 83 / 96% | sama |
| 3 | **Siklus Rs 7,01 menit muncul lagi**, sama dengan log 4 jam kemarin (7,01 menit). Amplitudo ±13,6% (kipas), ±15,4% (kipas mati), ±6,5% (AC + pintu tutup) | sama |
| 4 | Kipas bukan penyebab siklus; pintu terbuka dan orang di kamar (jauh dari alat) juga bukan | P2 |
| 5 | Setelah AC menyala (dan pintu ditutup, orang dekat alat), siklus mengecil dari ±17% menjadi ±4–7% dalam sekitar 10 menit, sementara goyangan 0,5 Hz tidak mengecil | jendela 14 menit |
| 6 | Siklus berkaitan dengan goyangan 0,5 Hz: periode sama (420 detik = jarak balik tanda goyangan bergantian), korelasi 0,90 dan 0,92. Tetapi amplitudo siklus turun saat AC menyala sedangkan goyangan tidak. **Sumbernya belum diketahui** | `analisis_fase.py` |
| 7 | Nyala dingin: Rs 60 detik −30%, 120 detik −12%, 180 detik −6% dari rata-rata menit 7–30. Pemanasan 3 menit cukup untuk satu kali nyala dingin | per 30 detik umur alat |
| 8 | CO2 nyata muncul detik ke-64 (1021 ppm), lalu 953 → 804 dalam 10 menit (pintu terbuka) | log |
| 9 | Pergeseran Rs 30 detik tanpa gas: turun > 25% tidak pernah dalam sekitar 28.000 detik (maks −21,4%); > 15% terjadi 1,6–2,6% waktu | semua log kamar dan mobil |

Batasan: satu kali nyala dingin; AC, pintu, dan orang dekat berubah bersamaan di P3.

---

## 9. Tambahan: uji ruang pertemuan dengan ESP baru (26 Oktober sore)

Data: `logs/device-monitor-261026-171515.log` (17:15–18:01, 2746 detik, tanpa mulai ulang). Ruangan 4,6 × 6,7 × 2,5 m, 13 orang, 2 AC, pintu tertutup. ESP baru (CH9102), firmware lama (v0), sensor yang sama dengan sebelumnya, Wi-Fi tidak dipakai. Skrip: `analisis_fase.py`. Hasil mentah: `hasil-uji-ruang-2026-10-26.txt`. Catatan kondisi: `2-lapangan/skenario-uji-mobil.md` bagian 2B.

| # | Temuan | Bukti |
|---|--------|-------|
| 1 | **Periode siklus Rs berbeda antara ESP lama dan ESP baru di ruangan.** ESP lama: 7,0 menit (dua hari berbeda). ESP baru di ruangan: sekitar 11,9 menit; amplitudo pada 7,0 menit hanya ±1,4%. (Koreksi: di mobil ESP baru memberi 7,6 menit, lihat bagian 10) | `analisis_fase.py` |
| 2 | Amplitudo siklus pada ESP baru sama besar (sekitar ±12,6%) | sama |
| 3 | Korelasi siklus dengan kuadrat amplitudo goyangan bergantian tetap tinggi (0,94), jarak balik tanda median 705 detik | sama |
| 4 | Goyangan Rs mentah 9,7% (17:20–17:39) dan 12,7% (17:40–18:00); bagian bergantian 92% dan 97% | sama |
| 5 | SMA 6 tetap lebih halus dari EMA 0,2: sisa noise 1,08 / 0,87% lawan 1,32 / 1,46% | sama |
| 6 | Interval baca rata-rata: ESP lama 1,00034 detik, ESP baru 1,00007 detik | jam laptop |
| 7 | CO2 1116–1549 ppm selama 45 menit, tidak mendekati 2500 walau 13 orang | log |

Arti (dikoreksi setelah uji mobil): periode tidak ditentukan oleh ESP saja. ESP baru memberi 11,9 menit di ruangan dan 7,6 menit di mobil, sedangkan ESP lama memberi 7,0 menit dua kali di kamar. Periode bergantung pada kombinasi ESP, catu (USB laptop pada baterai atau charger belum dicatat), dan kondisi tempat. Sumber tepatnya belum diketahui. Dugaan sampling murni (sumber 2 detik dibaca tiap 1 detik) belum cocok secara hitungan dengan perubahan interval baca di atas, jadi sumber tepatnya belum terbukti.

Batasan: hanya sekitar 4 siklus (45 menit), periode ±1 menit; kondisi ruangan berbeda dari kamar; Wi-Fi tidak aktif.

---

## 10. Tambahan: uji mobil Avanza, 26 Oktober malam (firmware lama)

Data: `logs/device-monitor-261026-193817.log` (19:38–20:26). Hasil mentah dari semua skrip: `hasil-uji-mobil-2026-10-26.txt`. Laporan lengkap: `2-lapangan/skenario-uji-mobil.md` bagian 3A.

| # | Temuan | Bukti |
|---|--------|-------|
| 1 | Laju naik CO2 tertutup: 3 orang +156, 4 orang +207 sampai +218 ppm/menit (20–40 km/jam); >100 km/jam +164 ppm/menit | kemiringan per fase |
| 2 | Dua jendela depan setengah terbuka: CO2 4437 → 2384 dalam ±95 detik dan 4447 → 2121 dalam ±110 detik. N sekitar 30–32 per jam (batas bawah) | luruhan eksponensial |
| 3 | CO2 terus turun 460–550 ppm setelah jendela ditutup (jeda sensor dan pencampuran) | log |
| 4 | Siklus buka-tutup 15,6 menit dengan 4 orang; CO2 naik dari ~1830 ke ~4100 dalam ~10 menit | log |
| 5 | Pintu dibuka 19:53: Rs −23% dalam 15 detik, lalu pulih sebagian. Jendela dibuka: Rs naik +4% sampai +8% | per 15 detik |
| 6 | Perubahan Rs 30 detik tanpa gas: turun > 25% terjadi 0,27% waktu (kejadian pintu terbuka), > 15% 1,07% | semua log mobil dan kamar |
| 7 | Siklus Rs lambat 7,6 menit ±8%, dengan **ESP baru** (dikonfirmasi). Di ruangan ESP baru memberi 11,9 menit, jadi periode tidak hanya ditentukan ESP | `analisis_mobil.py` bagian 6 | `analisis_mobil.py` bagian 6 |
| 8 | SMA 6 menang bila goyangan didominasi pola bergantian (fase B, C); saat jalan bergelombang (fase A) EMA 0,2 sedikit lebih halus | `analisis_fase.py` |

Batasan: satu mobil, satu malam, jam jendela sampai menit, tidak ada CO nyata.

