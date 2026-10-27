# Model C-251 (Simulasi) Lawan Hasil Uji

Versi 27 Oktober 2026. Membandingkan asumsi dan keluaran **model Bab 4 C-251** (skrip [pemodelan_bab4_simulasi.py](skrip/pemodelan_bab4_simulasi.py)) dengan **hasil uji lapangan** (Avanza 26 Okt, Civic 25 Okt; perhitungan N di [skrip/analisis_n.py](skrip/analisis_n.py)). Model: dC/dt = P - N(C - C_ext), dengan P = n x G x 1e6 / V.

Batasan: satu mobil per angka (Avanza dan Civic sangat berbeda), jam jendela hanya sampai menit, V kabin di model adalah placeholder (2750 dan 2150 L), CO luar dan jeda sensor diasumsikan. Hasil CO tidak bisa dibandingkan karena tidak ada CO nyata.

## 1. Parameter: asumsi model lawan terukur
| Parameter | Model C-251 | Terukur | Selisih |
|---|---|---|---|
| Produksi CO2 per orang, G (L/jam) | 19,6 (rentang 15-25) | Avanza: **sekitar 10,5** (P efektif 15.340 ppm/jam, V = 2750 L, 4 orang) | nyata sekitar **54%** dari model; V dan G tidak bisa dipisah, yang berarti P efektifnya |
| P Avanza 4 orang (ppm/menit) | 475 | **256** | sekitar 0,54 kali |
| N jendela tertutup (per jam) | 0,5 (tabel), 1-3 (simulasi, tengah 2,0) | Avanza 20-40 km/jam: **0,5-2** (terbaik 1,0) | **cocok** |
| N jendela tertutup, mobil melaju | sama | Civic (kasar): **6,6-11** | **6-20 kali** model; Civic 1994 jauh lebih bocor |
| N dua jendela depan setengah terbuka (per jam) | 13,3-26,1 (tengah 19,7); pemulihan 20 km/jam 3,5; diam 1,0 | Avanza 20-40 km/jam: **27-28** (hitungan kasar tanpa jeda sensor) sampai **46-79** (dengan jeda sensor tau 30-70 detik dan produksi napas; terbaik sekitar 60) | dari **sedikit di atas batas atas model** sampai sekitar 3 kali; 3,5 dan 1,0 jauh di bawah |
| CO2 luar (ppm) | 400 | 420 (asumsi; belum diukur di tempat) | kecil |

## 2. Keluaran model lawan uji (Avanza, 4 orang, 20-40 km/jam)
Titik awal uji 19:59 (jendela baru ditutup, CO2 1839 ppm). Model dihitung dengan P dan N dari model (kolom 2 dan 3) dan dengan P dan N terukur (kolom 4).

| Ukuran | Model, N = 0,5 | Model, N = 2,0 | Model dengan P dan N terukur | **Uji** |
|---|---|---|---|---|
| Laju naik CO2 pada 2000-3000 ppm (ppm/menit) | 454-462 | 389-422 | 213-229 | **207-218** |
| Waktu 1839 ke 2500 ppm (menit) | 1,4 | 1,6 | 2,9 | **sekitar 3,1** |
| Waktu 2500 ke 4000 ppm (menit) | 3,3 | 3,9 | 7,2 | **sekitar 7,3** |
| Waktu 1839 ke 4000 ppm (menit) | 4,8 | 5,5 | 10,1 | **sekitar 10,4** |
| Waktu dari kosong ke 2500 ppm, Tabel 4.2 (menit) | 4,5 | - | - | tidak diuji (mulai dari kabin berisi) |
| Siklus buka-tutup jendela (ambang 4000) | - | - | sekitar 10 + 5 = 15 | **15,6 menit** |

Model bawaan C-251 menaikkan CO2 sekitar **2,1 kali lebih cepat** dari kenyataan, jadi model itu **konservatif** (peringatan datang lebih awal dari yang sebenarnya). Dengan P dan N terukur, model menirukan uji (kolom 4 lawan 5), tetapi itu sebagian karena P dan N dicocokkan dari data yang sama.

Laju naik Avanza 3 orang: model 356 ppm/menit (tanpa pertukaran), **uji +156**. Civic 2 orang: model 304 (N = 0) atau 251 (N = 2 pada 2000 ppm), **uji +47 sampai +107** saat jalan pelan; **turun 51-91** saat melaju (model tidak bisa menirunya tanpa N 6-11).

## 3. Pemulihan CO2 saat jendela dibuka (Avanza, dari sekitar 4437 ke 2500 ppm)
| Sumber | N (per jam) | Waktu (detik) | Catatan |
|---|---|---|---|
| Model, pemulihan idle (Tabel 4.4) | 1,0 | sekitar 2350 | 4437 ke 2500 dihitung dari rumus (C_ext 420); Tabel 4.4 sendiri dari 2500 ke 2400 (176 detik) |
| Model, pemulihan 20 km/jam (Tabel 4.4) | 3,5 | 677 | |
| Model, jendela terbuka, batas bawah | 13,3 | 178 | |
| Model, jendela terbuka, tengah | 19,7 | 120 | |
| Model, jendela terbuka, batas atas | 26,1 | 91 | |
| **Uji, jendela 1 dan 2** | - | **85-105** | bacaan sensor (jeda sensor membuat waktu sebenarnya lebih pendek) |

Waktu terbaca di sensor jatuh di sekitar **batas atas** model jendela terbuka (N 26 per jam). Karena sensor lambat (T90 hingga 120 detik), N sebenarnya lebih tinggi, dan hitungan dengan jeda sensor memberi 46-79 per jam. Pemulihan "idle" dan "20 km/jam" di Tabel 4.4 (N 1,0 dan 3,5) **jauh lebih lambat** dari yang teramati dengan dua jendela terbuka saat mobil melaju; kedua nilai itu hanya cocok untuk jendela tertutup.

## 4. Parameter desain di simulasi lawan keputusan firmware sekarang
| Hal | Simulasi C-251 | Firmware sekarang (keputusan 27 Okt) |
|---|---|---|
| Interval baca | 5 detik | 1 detik |
| Penghalusan | rata-rata 120 detik (CO2) dan 150 detik (CO) | CO: SMA 6 (6 detik); CO2: tanpa filter |
| Keadaan | 2 (AMAN, WASPADA) dengan sub CO2 atau CO | 5 status: PEMANASAN, NORMAL, WASPADA, BAHAYA, GANGGUAN |
| Ambang CO2 | 2500 memicu aksi jendela | 2500 peringatan (bunyi), **4000 tindakan** (jendela) |
| CO2 selesai | < 2400 selama 60 detik | **< 2500 selama 10 detik**, jendela terbuka minimal 20 detik |
| Aksi saat CO tinggi | jendela ditutup (servo 0) | jendela **dibuka dulu 30 detik (uji arah)**, tutup bila Rs turun > 25% atau tidak jelas |
| CO selesai | < 30 ppm selama 60 detik | sama |
| Jendela | servo 0 atau 90 derajat | setengah terbuka lewat waktu motor, maks. 180 detik, jeda tertutup minimal 5 menit |
| Pemanasan sensor | tidak dimodelkan | 180 detik, angka tidak tampil |
| Bunyi | tidak dimodelkan | waspada 3 bip pendek, bahaya 1 bip panjang |

## 5. Yang tidak bisa dibandingkan
| Hal | Alasan |
|---|---|
| Tabel 4.5 (waktu CO mencapai 35 ppm) dan Tabel 4.6 (pemulihan CO) | tidak ada CO nyata; uji arah baru dibuat di firmware |
| Profil CO luar di simulasi (macet ringan 30 ppm, ekstrem 200 ppm) | tidak pernah teramati; di uji mobil Rs/R0 0,30-0,69 tanpa alarm CO |
| Simulasi 1 penumpang | tidak ada uji 1 penumpang |
| Respons sensor MiCS terhadap CO | tidak ada di datasheet dan tidak bisa diukur tanpa CO (uji parfum hanya menunjukkan sensor tidak selektif) |

## 6. Kesimpulan
1. **N jendela tertutup di model cukup wajar untuk Avanza** (0,5-2), tetapi tidak berlaku untuk Civic yang melaju (6-11).
2. **N jendela terbuka di model (13-26) pada sisi rendah** untuk mobil yang bergerak dengan dua jendela setengah terbuka (27 sampai 79).
3. **Produksi CO2 nyata sekitar setengah model** (P efektif 54%). Waktu menuju ambang di model lebih cepat sekitar 2 kali, jadi model C-251 bersifat konservatif.
4. Untuk firmware, semua perbedaan ini berada di sisi aman: jendela cukup dibuka 20-180 detik, dan siklus buka-tutup sekitar 15 menit (4 orang, ambang 4000) lebih lambat dari yang dikhawatirkan.
5. Bila model dipakai di C-501, laporkan **dua versi**: asumsi C-251 (konservatif) dan parameter terukur (`--terukur`), dengan catatan bahwa angka terukur berasal dari satu mobil.
