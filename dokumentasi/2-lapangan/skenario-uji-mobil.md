# Uji Lapangan: Laporan dan Skenario

Terkait: [desain-peringatan.md](../3-bukti/desain-peringatan.md) (A6, B4, E, F), [daftar-tugas.md](../1-utama/daftar-tugas.md) (T11), analisis data: [ringkasan-temuan-2026-10-25.md](../analisis/ringkasan-temuan-2026-10-25.md) bagian 7 dan 8.

| Bagian | Isi |
|---|---|
| 1 | **Laporan uji 1**: mobil, 25 Oktober 2026 malam, firmware lama |
| 2 | **Laporan uji 2**: kamar, 26 Oktober 2026 pagi, firmware lama |
| 2B | **Catatan uji ruang pertemuan**: 26 Oktober 2026 sore, ESP baru |
| 3A | **Laporan uji 3**: mobil Avanza, 26 Oktober 2026 malam, firmware lama |
| 3 | **Skenario uji 3**: mobil, 26 Oktober 2026 malam |
| 4 | Firmware: lama atau baru? |
| 5 | Keselamatan, persiapan, setelah uji, batasan |
| 6 | Lembar catatan kosong untuk uji 3 |
| 7 | Perbandingan firmware lama dan baru (rencana) |

## 1. Laporan uji 1: mobil, 25 Oktober 2026 malam

### 1.1 Kondisi

| Hal | Isi |
|---|---|
| Mobil | Honda Civic EG6 tahun 1994 |
| Penumpang | 2 orang, kursi depan |
| Posisi alat | Di jok sebelah paha penumpang depan (dekat tubuh) |
| Jendela | Tidak pernah dibuka |
| Arah udara | Selalu sirkulasi dalam (tidak pernah udara luar) |
| Firmware | Lama (v0, 23 Okt, EMA 0,2). Checksum sama dengan `arsip-firmware/main-v0-2026-10-23.cpp` |
| Rangkaian | Breadboard, daya dan data dari USB laptop |
| Rute | Jalan ke SPBU lalu putar. "Ngebut" = jalan bagus dan ring road sepi. "Pelan" = jalan agak rusak, atau mengikuti arus yang lancar |
| Parfum / pewangi | Tidak ada, di tubuh maupun di mobil |

### 1.2 Garis waktu (dari catatan, jam 24 jam)

| Jam | Kejadian | Kecepatan / AC | Log |
|---|---|---|---|
| 21:37 | Alat menyala (tidak ada catatan; terlihat dari log) | | `...213732` |
| 21:41 | Alat mulai ulang, warm-up. Sirkulasi dalam (hanya kipas) | 20–40 km/jam, AC mati | `...214144` |
| 21:51 | AC (pendingin) menyala | | |
| 21:56 | AC mati, menuju SPBU | | |
| 21:58 | Isi bensin. **Alat dimatikan** (aturan keselamatan) | berhenti | |
| 22:00 | Keluar SPBU, alat menyala lagi. Hanya kipas, sirkulasi dalam | | `...220026` |
| 22:04 | Mobil ngebut | | |
| 22:07 | Lampu merah, mobil berhenti | berhenti | |
| 22:08 | Mobil ngebut sekitar 60 km/jam | 60 km/jam | |
| 22:08 (beda beberapa detik) | AC menyala | | |
| 22:14 | Mobil pelan | 20–30 km/jam | |
| 22:15 | Rekaman berakhir | | |

### 1.3 Berkas log

| Berkas di `logs/` | Waktu | Dipakai? |
|---|---|---|
| `device-monitor-261025-213732.log` | 21:37–21:41 (4 menit) | Tidak (terlalu pendek, alat mulai ulang) |
| `device-monitor-261025-214144.log` | 21:41–21:57 | **Ya** (sesi 1) |
| `device-monitor-261025-220026.log` | 22:00–22:15 | **Ya** (sesi 2) |

Analisis: `dokumentasi/analisis/analisis_mobil.py`. Hasil mentah: [hasil-uji-mobil-2026-10-25.txt](../analisis/hasil-uji-mobil-2026-10-25.txt).

### 1.4 Hasil ringkas

| Ukuran | Hasil | Status |
|---|---|---|
| Goyangan Rs 0,5 Hz di mobil | 9,4–9,9% mentah, 94–95% bergantian (kamar: 13%, 93–95%) | Terukur |
| Sisa noise setelah filter | SMA 4 / SMA 6: 0,9%. EMA 0,2 (kode lama): 1,3% | Terukur |
| Lompatan ppm 0 ↔ ~10 | SMA 6: 1–2 kali. EMA 0,2: 14–19 kali | Terukur |
| Rs/R0 di mobil | 0,30–0,67 (kamar: sekitar 1,0). ppm terbaca 0–19 terus, tidak ada detik ≥ 35 ppm | Terukur. ppm tetap estimasi |
| Pergeseran Rs | Sampai +15% dan −17% per menit | Terukur. Sebabnya belum dibuktikan |
| CO2 saat jalan pelan, AC mati | Naik 47–107 ppm/menit | Terukur |
| CO2 saat AC menyala | Naik hanya 19–24 ppm/menit | Terukur |
| CO2 saat ngebut | **Turun 90 ppm/menit** (22:04–22:07). Turun 51 ppm/menit saat 20–30 km/jam | Terukur |
| Laju pertukaran udara (N) | Hanya batas bawah, sekitar 1,3 per jam (luruhan 22:05–22:13, CO2 luar diasumsikan 420) | **Belum bisa dihitung** (jendela tidak dibuka) |
| USB / catu | Alat menyala 3 kali malam itu: 21:37 (awal), 21:41 (penyebab tidak tercatat), 22:00 (setelah SPBU, disengaja) | Perlu dicatat penyebabnya |
| Alarm palsu | Tidak ada (2 sesi, sekitar 30 menit) | Terukur |

Arti singkat: filter baru terbukti lebih baik di mobil; CO di mobil belum bisa dibaca dengan R0 kamar; CO2 bisa turun sendiri saat mobil melaju.

### 1.5 Yang kurang dari uji 1

- Tidak ada uji buka jendela, jadi N tidak bisa dihitung.
- Tidak ada pembanding udara luar (CO2 luar).
- Alat mati dan menyala lagi di tengah uji (21:41 tanpa catatan penyebab, 22:00 karena SPBU); sesi pertama hanya 16 menit.
- Alat dekat tubuh penumpang, belum diketahui seberapa besar pengaruhnya.
- Jam beberapa kejadian hanya sampai menit, tanpa suhu setelan AC.

---

---

## 2. Laporan uji 2: kamar, 26 Oktober 2026 pagi

Tujuan: menjawab empat hal sebelum uji mobil malam. (1) Apakah Rs menit ke-3 sudah dekat nilai stabil? (2) Apakah siklus Rs sekitar 7 menit muncul lagi? (3) Apakah siklus itu hilang bila kipas dimatikan? (4) Apakah siklus atau Rs berubah bila AC menyala?

### 2.1 Kondisi dan garis waktu (dari catatan, jam 24 jam)

| Fase | Jam | Kipas | AC | Pintu | Orang |
|---|---|---|---|---|---|
| P0 | 09:03:46 | Nyala | Mati | Terbuka | Alat dinyalakan (colok USB). Lima menit pertama dibuang |
| P1 | 09:08–09:45 | Nyala, mengarah ke alat | Mati | Terbuka | Pemilik tidak di kamar |
| P2 | 09:46–10:15 | **Mati** | Mati | Terbuka | Pemilik di kamar selama 15 menit terakhir, di sisi seberang alat |
| P3 | 10:16–10:47 | Mati | **Nyala** | **Tertutup** | Pemilik di kamar, di atas depan meja dan alat (dekat) |

Firmware: lama (v0, EMA 0,2), alat tidak berpindah dan tidak dicabut.

### 2.2 Berkas log

| Berkas di `logs/` | Waktu | Catatan |
|---|---|---|
| `device-monitor-261026-090343.log` | 09:03:46–10:47:33 (6226 detik) | Tanpa mulai ulang, tanpa celah |

Analisis: `dokumentasi/analisis/analisis_fase.py`. Hasil mentah: [hasil-uji-kamar-pagi-2026-10-26.txt](../analisis/hasil-uji-kamar-pagi-2026-10-26.txt).

### 2.3 Hasil ringkas

| Ukuran | P1 (kipas) | P2 (kipas mati) | P3 (AC, pintu tutup) | Status |
|---|---|---|---|---|
| Rs rata-rata (kOhm) | 1806 | 1561 | 1545 | Terukur |
| Goyangan Rs mentah | 13,0% | 15,2% | 15,6% | Terukur (uji mobil: 9–10%) |
| Bagian goyangan bergantian 0,5 Hz | 93% | 83% | 96% | Terukur |
| Sisa noise, **SMA 6** | **1,25%** | **1,82%** | **0,97%** | Terukur |
| Sisa noise, EMA 0,2 (kode lama) | 1,81% | 2,34% | 1,83% | Terukur |
| Siklus 7 menit (amplitudo pada periode tetap) | ±13,6% | ±15,4% | ±6,5% | Terukur |
| CO2 (ppm, setelah 64 detik) | 763–846 | 754–938 | 756–931 | Terukur |

Pembacaan utama:
- **Filter:** SMA 6 lebih halus dari EMA 0,2 di ketiga fase (31%, 22%, dan 47% lebih kecil). Pola bergantian 0,5 Hz sama seperti di kamar 4 jam dan di mobil.
- **Siklus Rs sekitar 7 menit muncul lagi.** Periodenya **7,01 menit**, sama dengan log 4 jam kemarin (7,01 menit), dua hari berbeda.
- **Siklus tidak hilang bila kipas dimatikan** (P2: ±15,4%), dan tidak hilang oleh pintu terbuka atau orang di kamar (jauh dari alat).
- **Siklus mengecil bila AC menyala dan pintu ditutup.** Dilihat per jendela 14 menit, amplitudonya ±12,6% sampai ±17,0% dari 09:08 sampai sekitar 10:25, lalu turun menjadi ±4–7% setelah sekitar 10:18. Pada saat yang sama goyangan 0,5 Hz tidak mengecil (goyangan mentah 13,0% di P1 menjadi 15,6% di P3).
- **Tiga hal berubah serentak pada 10:15** (AC menyala, pintu ditutup, pemilik duduk dekat alat), jadi belum diketahui yang mana penyebab mengecilnya siklus.

Pemanasan nyala dingin (alat mati sejak semalam):

| Umur alat | 30 dtk | 60 dtk | 120 dtk | 180 dtk | 300 dtk | 600 dtk |
|---|---|---|---|---|---|---|
| Rs (kOhm) | 892 | 1300 | 1626 | 1730 | 1852 | 1759 |

Rata-rata Rs menit ke-7 sampai 30 adalah 1849 kOhm. Pada 180 detik Rs berada 6% di bawah rata-rata itu, masih di dalam rentang siklus 7 menit (±15%). Pada 60 detik −30%, pada 120 detik −12%.

CO2: nilai nyata pertama muncul pada detik ke-64 (1021 ppm), lalu turun pelan 953 → 804 ppm dalam 10 menit. Di kamar dengan pintu terbuka itu bisa penurunan nyata. Selisih antara 180 detik (857) dan 600 detik (804) adalah 53 ppm, di dalam akurasi sensor (±50 ppm + 5%).

Pergeseran Rs dalam 30 detik (tanpa gas): turun lebih dari 8% terjadi pada 13% waktu; lebih dari 15% pada 2,6% waktu (7,1% pada P2); lebih dari 25% tidak pernah terjadi dalam sekitar 28.000 detik data kamar dan mobil (maksimum −21,4%).

### 2.4 Jawaban dari empat pertanyaan

| # | Pertanyaan | Jawaban |
|---|---|---|
| 1 | Pemanasan 3 menit cukup? | **Ya untuk satu kali nyala dingin.** Rs menit ke-3 sudah di dalam rentang siklus. Pemanasan CO 3 menit tetap, dengan catatan satu pengukuran |
| 2 | Siklus 7 menit muncul lagi? | **Ya**, periode 7,01 menit, ±13–17% |
| 3 | Hilang bila kipas dimatikan? | **Tidak.** Kipas bukan penyebabnya |
| 4 | Berubah bila AC menyala? | **Ya, mengecil menjadi ±4–7%.** Penyebab (AC, pintu, atau orang dekat) belum terpisah |

### 2.5 Tentang sumber siklus: dugaan, belum bukti

Petunjuk bahwa siklus dan goyangan 0,5 Hz berasal dari sumber yang sama:
- Periode 7,01 menit, sama pada dua hari.
- Jarak antara dua pembalikan tanda goyangan bergantian: median 420 detik, sama dengan periode siklus (7,00 menit).
- Korelasi 0,90 (pagi) dan 0,92 (4 jam) antara siklus dan kuadrat amplitudo goyangan bergantian.

Petunjuk yang melawan: setelah AC menyala siklus mengecil menjadi sepertiga, sementara goyangan bergantian tidak. Jadi sumbernya mungkin sama, tetapi besarnya ikut dipengaruhi kondisi udara.

Uji yang membedakan (belum dilakukan): mengganti interval siklus firmware dari 1,0 detik menjadi misalnya 1,25 detik pada firmware baru. Bila siklus 7 menit itu muncul akibat sampling terhadap sumber 2 detik, periodenya akan **berubah**; bila berasal dari lingkungan, periodenya tetap 7 menit.

### 2.6 Yang berlaku untuk firmware baru
- SMA 6 tetap dipilih. Ia tidak menghilangkan siklus 7 menit (itu gerakan lambat), hanya goyangan per detik.
- Kriteria uji arah (B6) dinaikkan ke **25%**: 8% dan 15% terlampaui oleh gerakan alami Rs tanpa gas.
- Pemanasan 3 menit untuk keduanya tidak berubah.

### 2.7 Yang kurang dari uji 2
- Hanya satu kali nyala dingin.
- Tiga hal berubah bersamaan di P3 (AC, pintu, orang dekat), jadi pengaruh masing-masing belum terpisah.
- Tidak ada pembanding suhu dan kelembapan (tidak ada sensornya).

---

## 2B. Catatan uji ruang pertemuan, 26 Oktober 2026 sore (ESP baru)

### Kondisi ruangan (dari catatan)

| Hal | Isi |
|---|---|
| Ukuran | 4,6 m × 6,7 m, tinggi paling 2,5 m |
| Volume | sekitar **77 m³** (4,6 × 6,7 × 2,5 = 77,05 m³) |
| Penghuni | **13 orang** (sekitar 5,9 m³ per orang) |
| AC | 2 unit |
| Pintu | Semua tertutup |
| Perangkat | ESP baru (CH9102), firmware lama (v0, EMA 0,2), kode terunggah 26 Okt 17:08 |

Dari log: mulai **17:15:16**, berkas `device-monitor-261026-171515.log`, masih merekam pukul 17:31 (CO2 sejauh ini 1290–1549 ppm). Rekaman dipakai sampai sekitar 18:01. Hasil (ringkasan-temuan bagian 9): siklus Rs yang di ESP lama 7,0 menit menjadi sekitar 11,9 menit di ESP baru, dengan amplitudo sama; CO2 hanya 1116–1549 ppm. Di mobil, ESP baru memberi 7,6 menit (bagian 3A), jadi periode tidak hanya ditentukan ESP.

Belum diisi (lengkapi dari ingatan): Wi-Fi mati atau menyala ____, posisi alat dan jaraknya dari AC dan orang ____, setelan AC (suhu, arah angin) ____, nama berkas log ____, apakah ada pintu yang dibuka di tengah acara dan jamnya ____.

### Catatan membaca hasilnya
- **Ini bukan kamar udara bersih.** 13 orang menambah CO2, uap air, dan bau napas, jadi Rs dan siklus 7 menit **tidak boleh dibandingkan langsung** dengan log kamar kemarin. Yang dibandingkan hanya noise dan perilaku ESP baru.
- **CO2 bisa naik cepat.** Perkiraan kasar (bukan pengukuran): satu orang duduk menghasilkan sekitar 0,005 L CO2 per detik, jadi 13 orang di 77 m³ tanpa pertukaran udara menaikkan CO2 sekitar 50 ppm per menit. Pertukaran udara sebenarnya (AC, celah pintu) tidak diketahui. Angka sebenarnya diambil dari log.
- **Batas aman:** bila CO2 mendekati 4000, buka pintu. Ruangan penuh orang, bukan ruang uji.
- **Data yang berguna:** laju naik CO2 untuk 13 orang di ruang tertutup (satu kondisi lagi untuk model well-mixed), dan kemampuan sensor membaca CO2 tinggi di ruang nyata.

---

## 3A. Laporan uji 3: mobil Avanza, 26 Oktober 2026 malam

### 3A.1 Kondisi dan garis waktu (dari catatan)

Mobil Toyota Avanza. Penumpang awal 3 orang, lalu 4 orang mulai 19:53. Kecepatan di jalan biasa 20–40 km/jam. Firmware lama (v0). Berkas: `device-monitor-261026-193817.log` (19:38–20:26, tanpa mulai ulang atau celah).

| Jam | Kejadian |
|---|---|
| 19:38–19:48 | Mobil diam, alat memanas |
| 19:48 | Mobil jalan |
| 19:53 | Satu orang naik, pintu terbuka. CO naik, lalu langsung turun |
| 19:56 | Dua jendela depan dibuka sekitar setengah |
| 19:57 | Jendela ditutup. CO2 sekitar 2400 saat ditutup, lalu masih turun setelahnya |
| 20:11:40 | Dua jendela depan dibuka sekitar setengah |
| 20:13 | Jendela ditutup. CO2 sekitar 2100 saat ditutup, lalu masih turun setelahnya |
| 20:22:27 | Kecepatan naik ke 60–80 km/jam |
| 20:23:21 | Melambat |
| 20:25:42 | Kecepatan naik |
| 20:26 | Kecepatan lebih dari 100 km/jam |

### 3A.2 Hasil

| Ukuran | Hasil | Status |
|---|---|---|
| Laju naik CO2, jendela tertutup | **3 orang: +156 ppm/menit. 4 orang: +207 sampai +218 ppm/menit** (jalan 20–40 km/jam). Kecepatan >100 km/jam: +164 ppm/menit | Terukur |
| CO2 puncak | 4444 ppm (19:56:14) dan 4453 ppm (20:11:52). Tidak sampai 5000 | Terukur |
| Jendela 1 | Dibuka sekitar 19:56:20, CO2 4437 → 2384 saat ditutup (±95 detik) → turun lagi ke 1831 setelah ditutup | Terukur |
| Jendela 2 | Dibuka 20:11:40, CO2 4447 → 2121 saat ditutup (±110 detik) → turun lagi ke 1660 setelah ditutup | Terukur |
| **N saat dua jendela depan setengah terbuka** | **sekitar 30–32 per jam** (luruhan, CO2 luar diasumsikan 400–450). Batas bawah: penumpang masih bernapas dan sensor punya jeda | Perkiraan |
| Siklus buka-tutup | Puncak ke puncak 15,6 menit (19:56 dan 20:11). Naik dari 1831 ke sekitar 4100 butuh sekitar 10 menit | Terukur |
| Rs dan CO | Rs/R0 0,40–0,69, ppm estimasi 0–13, tidak ada alarm CO sama sekali | Terukur |
| Pintu dibuka 19:53 | Rs turun 1121 → 861 kΩ (−23%) dalam 15 detik, lalu pulih sebagian (950). Cocok dengan "CO naik, lalu turun" | Terukur |
| Jendela dibuka 19:56 dan 20:11 | Rs justru naik sedikit (+4% sampai +8%), tidak ada lonjakan CO dari luar | Terukur |
| Goyangan Rs mentah | 7,3% (87% bergantian) | Terukur |
| Siklus Rs lambat | periode 7,6 menit, ±8% (ESP baru) | Terukur |

Catatan bacaan:
- CO2 **masih turun setelah jendela ditutup** (selisih 550 ppm dan 460 ppm). Penyebabnya jeda sensor MH-Z19C (T90 sampai 120 detik) dan pencampuran udara. Akibatnya N dari luruhan agak diremehkan, dan angka 30–32 per jam adalah batas bawah.
- Sekitar dua kali lebih besar daripada N yang diasumsikan di perhitungan awal uji arah (sekitar 13 per jam), jadi paparan tambahan saat uji arah 30–60 detik bisa lebih kecil dari perkiraan awal, dan jendela setengah terbuka cukup efektif.
- Dengan 4 orang CO2 naik dari 2500 ke 4000 dalam sekitar 7 menit. Siklus buka-tutup per 15–16 menit lebih sering daripada perkiraan tim ("sekitar 20 menit saat penuh").

### 3A.3 Filter
- **Seluruh log:** sisa noise SMA 6 1,71%, EMA 0,2 1,63%, SMA 8 1,64%, EMA 0,1 1,43%. Lompatan ppm 0 ↔ 10: 9 kali (SMA 6) lawan 27 kali (EMA 0,2).
- **Per fase:** fase A (mobil jalan, orang naik, jendela pertama): SMA 6 3,04% lawan EMA 0,2 2,65% (bagian bergantian hanya 79%, banyak guncangan jalan). Fase B dan C (bagian bergantian 92%): SMA 6 0,72 dan 0,75% lawan EMA 0,2 1,04 dan 1,05%.
- Kesimpulan: SMA 6 menang bila goyangan didominasi pola bergantian; saat jalan bergelombang, filter yang lebih panjang (EMA 0,1 atau SMA 8) sedikit lebih halus. Pilihan SMA 6 dipertahankan dan SMA 8 tetap cadangan bila ada alarm palsu dari guncangan.

### 3A.4 Yang kurang
- Jam buka dan tutup jendela hanya sampai menit, bukan detik. N dihitung dari titik CO2 ketika jendela ditutup (±5 detik).
- Posisi alat belum dicatat. ESP: baru (dikonfirmasi). Jam jendela hanya sampai menit, tidak ada catatan lebih rinci.
- Satu mobil, satu malam, dua bukaan jendela dengan lebar sama; lebar lain belum diuji.

---

## 3. Skenario uji 3: mobil, 26 Oktober 2026 malam (firmware lama)

Uji kamar pagi (bagian 2) sudah selesai. Tujuan uji malam: **laju pertukaran udara (N) Civic** dan perilaku Rs di mobil tanpa alat mulai ulang.

**Pertanyaan yang dijawab**

| # | Pertanyaan |
|---|---|
| 1 | Berapa N (laju pertukaran udara) Civic saat jendela dibuka, untuk lebar dan lama tertentu? |
| 2 | Berapa laju naik CO2 saat mobil **diam** dengan 2 orang (tanpa pengaruh kecepatan)? |
| 3 | Berapa CO2 udara luar? |
| 4 | Apakah Rs di mobil stabil bila alat tidak mulai ulang? |

**Bila memakai mobil lain:** boleh dan aman, dengan aturan keselamatan yang sama. Tulis jenis dan tahun mobil di lembar. Angka N hanya berlaku untuk mobil itu (tiap mobil punya kebocoran dan ruang berbeda), jadi tidak dibandingkan dengan Civic. Ia justru berguna sebagai data mobil kedua untuk perhitungan bukaan jendela. Rs dan CO tidak dibandingkan antar mobil karena kabin dan bahannya berbeda.

**Aturan penting:** alat **tidak boleh mulai ulang**. Jangan melewati SPBU (alat harus mati di area pompa dan itu memulai ulang pemanasan). Gunakan rute lain: ring road dan jalan biasa.

**Persiapan tambahan dibanding uji 1**
- Nyalakan alat dan mulai rekam **10 menit sebelum** masuk mobil (alat di mobil, di tempat yang akan dipakai).
- Posisi alat: **di konsol tengah atau dasbor**, jauh dari tubuh. Sama sepanjang uji. Catat posisi.
- Catat jumlah orang (usahakan sama: 2 orang di kursi depan).
- Siapkan cara mencatat jam sampai detik (ponsel dengan jam sama dengan laptop).

**Urutan**

| Fase | Kegiatan | Durasi | Catat |
|---|---|---|---|
| A | **Udara luar.** Mobil parkir di tempat terbuka, mesin mati, semua jendela terbuka, belum ada orang di mobil. Alat sudah menyala sejak 10 menit sebelumnya | 5–10 menit | Jam mulai. Angka CO2 dianggap CO2 luar |
| B | **Diam, tertutup.** Dua orang masuk, tutup semua jendela, sirkulasi dalam, **AC mati**, mesin mati (atau hidup bila perlu, dicatat). Mobil parkir di tempat terbuka. Duduk diam | 10 menit (atau sampai CO2 sekitar 3000) | Jam tutup. Mesin, AC. Laju naik CO2 (ppm/menit) diukur dari sini |
| C | **Berkendara** ring road dan jalan biasa, sirkulasi dalam, jendela tertutup. Sampai CO2 ≥ 2500 | 10–15 menit | Jam, kecepatan kasar, jenis jalan, AC |
| D | **Uji jendela 1.** Berhenti di tempat aman (mobil diam, mesin boleh hidup). Saat CO2 ≥ 2500: buka **jendela depan sisi penumpang setengah** selama **60 detik**, lalu tutup | 5 menit setelah dibuka | Jam buka dan tutup **sampai detik**, lebar |
| E | **Uji jendela 2.** Setelah CO2 naik lagi (diam, tertutup), buka jendela yang sama **penuh** selama 60 detik, lalu tutup | 5 menit setelah dibuka | Sama |
| F | **Uji jendela 3** (bila sempat). Dua jendela depan setengah, 60 detik | 5 menit setelah dibuka | Sama |
| G | **AC** (opsional): AC menyala sirkulasi dalam, lalu mode udara luar, mobil diam, 5 menit tiap mode | 10 menit | Jam ganti mode |

Jendela hanya dibuka saat mobil **diam atau sangat pelan**, supaya N tidak bercampur dengan efek kecepatan.

**Aturan berhenti:** bila CO2 mencapai **4000**, buka jendela segera dan hentikan fase. Jangan sampai 5000 (sensor mentok).

**Cara membaca hasil**
- Laju naik CO2 saat diam (fase B) memberi gambaran pembentukan CO2 dua orang di kabin.
- Pertukaran udara dari fase D–F: laju turun CO2 setelah jendela dibuka, dibandingkan CO2 luar (fase A). Dari model luruhan dihitung N per bukaan.
- Bandingkan Rs sebelum dan sesudah jendela dibuka: bila Rs berubah jauh, ada pengaruh udara luar pada CO (data untuk B6 dan uji arah).
- Tidak ada CO nyata, jadi ppm CO tetap estimasi.

---

---

## 4. Firmware: lama atau baru?

**Rekomendasi: firmware lama, untuk uji pagi (sudah dijalankan) dan uji malam.** Firmware baru dipakai mulai uji berikutnya.

| Alasan | Penjelasan |
|---|---|
| Satu variabel berubah | Yang diuji malam ini adalah sensor dan mobilnya (nyala dingin, siklus Rs, N Civic). Dengan firmware yang sama seperti uji 1, selisih hasil berasal dari kondisi, bukan dari kode. Dibandingkan dengan log 4 jam dan uji 1 |
| Log lama sudah cukup | Log mencatat tegangan mentah per detik. Filter baru (SMA 6) dan aturan baru bisa **diputar ulang pada log yang sama** tanpa menyalakan firmware baru. Perbandingan lama lawan baru paling adil di cara ini (bagian 6) |
| Firmware baru belum ditulis | Menurut jadwal ([daftar-tugas.md](../1-utama/daftar-tugas.md)), firmware baru ditulis 26 Okt dan diunggah ke ESP final 27 Okt. Menunggunya berarti uji malam bisa terlambat atau bercampur dengan perbaikan bug |
| Risiko | Firmware baru yang belum dicoba di meja bisa mulai ulang atau berhenti di tengah uji mobil, dan itu mengulang kesalahan uji 1 |

Urutan yang disarankan:

| Hari | Uji | Firmware |
|---|---|---|
| 26 Okt pagi | Kamar: nyala dingin, kipas, AC (bagian 2) **selesai** | Lama |
| 26 Okt malam | Mobil: jendela dan N (bagian 3) | Lama |
| 27 Okt | Meja: napas ke kotak, simulasi CO, ukur gerak jendela | **Baru** (bila sudah ada dan Anda setuju) |
| 28 Okt | Mobil ke-3 dan integrasi (bila sempat) | **Baru** |
| 29 Okt siang | Bekukan | |

Firmware baru ditulis di cabang `firmware-baru` (git), bukan menimpa `src/main.cpp`, dan hanya setelah ada izin eksplisit dari Anda.

---

---

## 5. Keselamatan, persiapan, setelah uji, batasan

### Keselamatan
- **Pengemudi tidak boleh menyentuh laptop atau sensor.** Penumpang yang mengoperasikan laptop dan mencatat.
- **SPBU:** uap bensin mudah terbakar, dan pemanas sensor serta rangkaian terbuka (breadboard, ESP32, USB, laptop) bukan perangkat aman di area pompa. Matikan dan simpan perangkat sebelum memasuki area SPBU. Uji 3 tidak melewati SPBU.
- Jangan menyalakan korek di dalam mobil. Jangan merokok, menyemprot parfum, atau memakai hand sanitizer di kabin selama uji.
- Kabel dan laptop terpasang aman (tidak menghalangi pedal, setir, atau tuas).
- Jangan menguji bukaan jendela saat mobil bergerak kencang. Lakukan saat berhenti atau pelan.
- Jangan membuat CO sendiri.

### Persiapan (centang)
- [ ] Baterai laptop terisi, `caffeinate` aktif (`caffeinate -im -t 7200`).
- [ ] Kabel USB dilekatkan (selotip), konektor masuk penuh. Jangan dicabut di tengah uji.
- [ ] Perekam jalan: `cd /Users/maritzavania/Downloads/aeros-sensor` lalu `~/.platformio/penv/bin/pio device monitor -f time -f log2file`.
- [ ] Jam laptop dan ponsel sama.
- [ ] Lembar catatan (bagian 6) siap, atau berkas teks di ponsel.
- [ ] Posisi alat ditetapkan dan dicatat.
- [ ] Versi firmware ditulis di lembar (lama v0, EMA 0,2).

### Setelah uji
1. Simpan folder `logs/` dan lembar catatan **sebelum** melakukan hal lain.
2. Kirim nama berkas log dan catatan. Yang akan dihitung:
      - Laju naik CO2 saat diam (B) dan per jenis jalan (C).
   - Laju turun CO2 dan N per bukaan jendela (D–F).
   - Noise dan filter (`analisis_mobil.py`).
   - Putus-putus USB dan mulai ulang.
3. Bandingkan dengan model C-251 Bab 10 (T19).

### Batasan uji ini
- Dua uji, satu mobil, satu rute.
- Jumlah orang tergantung yang ikut.
- Tidak ada CO asli dan tidak ada alat referensi.
- Sensor MiCS masih punya baseline yang bergeser (Rs turun lebih dari 50% dalam 4 jam di kamar), jadi nilai absolut CO tidak dipakai.
- Rangkaian masih di breadboard dan daya dari laptop.
- Pengujian di kendaraan nyata dinyatakan di luar cakupan di C-251 Bab 7.6, jadi ini dilaporkan sebagai **uji eksplorasi tambahan**.

---

---

## 6. Lembar catatan kosong, uji 3 (26 Oktober malam)

Cukup satu baris tiap **kejadian**, bukan tiap menit. Yang paling penting: jam buka dan tutup jendela sampai detik. Jam harus sama dengan jam laptop.

Posisi alat: ____________  Jumlah orang: ____  Mobil: ____________  Firmware: ____________

| Jam (hh:mm:ss) | Fase | Kejadian | Mesin | AC | Jendela | Keterangan |
|---|---|---|---|---|---|---|
| | A | Mulai rekam, jendela terbuka | | | | CO2 di layar: |
| | B | Dua orang masuk, jendela tertutup | | | | |
| | C | Mulai berkendara | | | | Jalan/kecepatan: |
| | D | Jendela dibuka (lebar: ) | | | | CO2 saat dibuka: |
| | D | Jendela ditutup | | | | CO2 saat ditutup: |
| | E | Jendela dibuka (lebar: ) | | | | CO2 saat dibuka: |
| | E | Jendela ditutup | | | | CO2 saat ditutup: |
| | F | Jendela dibuka (lebar: ) | | | | |
| | F | Jendela ditutup | | | | |
| | | Alat mulai ulang? penyebab: | | | | |

Catat juga hal yang bisa memengaruhi sensor: parfum atau semprotan, makanan, napas dekat sensor, pintu dibuka, putusnya kabel, lampu merah lama.

### Contoh pengisian (angka dan jam hanya contoh, bukan data)

| Jam | Fase | Kejadian | Mesin | AC | Jendela | Keterangan |
|---|---|---|---|---|---|---|
| 19:42:00 | A | Mulai rekam, mobil parkir, belum ada orang | mati | mati | semua terbuka | CO2 sekitar 480 |
| 19:52:30 | B | Dua orang masuk, jendela ditutup | mati | mati | tertutup | Mulai hitung naiknya CO2 |
| 20:02:30 | B | CO2 sekitar 3000, hentikan | mati | mati | tertutup | |
| 20:30:10 | D | Buka jendela depan kiri setengah | hidup | mati | depan kiri setengah | CO2 sekitar 3200 |
| 20:31:10 | D | Tutup jendela | hidup | mati | tertutup | Dibuka 60 detik. CO2 setelahnya sekitar 2900 |

---

---

## 7. Perbandingan firmware lama dan baru

Sebelum firmware baru difinalkan, perilakunya dibandingkan dengan firmware lama.

| Hal | Rencana |
|---|---|
| Firmware lama (v0) | `src/main.cpp` per 23 Okt 2026 (filter EMA 0,2). **Salinan cadangan:** `arsip-firmware/main-v0-2026-10-23.cpp` (checksum sama dengan `src/main.cpp`) |
| Uji 1, 2, dan 3 | Memakai firmware **lama** sebagai pembanding dasar (baseline) |
| Memutar ulang di komputer | Log 1 detik berisi tegangan, Rs, dan CO2. Algoritma baru (SMA 6, aturan prioritas, uji arah) bisa **dijalankan ulang pada data yang sama**. Ini perbandingan yang paling adil karena inputnya identik |
| Uji dengan firmware baru | Rute, jam, dan jumlah orang semirip mungkin. Kondisi tidak akan identik, jadi hasilnya dipakai sebagai konfirmasi, bukan angka mutlak |

Yang dibandingkan:

| Ukuran | Cara menghitung |
|---|---|
| Noise Rs (%) | `analisis_mobil.py` dan `filter_compare.py` |
| Waktu alarm sesudah kejadian (jendela dibuka, antrean) | Dari jam di log dan lembar catatan |
| Jumlah alarm dan perpindahan status per 10 menit | Dihitung dari log |
| Jumlah gerakan jendela per 10 menit (hanya firmware baru) | Dihitung dari log kejadian |
| Alarm palsu | Dari log dan catatan |
| Mulai ulang atau USB putus | Dari log |

Catatan:
- Firmware lama **tidak punya aktuasi jendela**. Jendela dibuka manual (lembar catatan), jadi yang dibandingkan adalah **filter dan logika alarm**, bukan gerakan jendela.
- Laju turun CO2 setelah jendela dibuka adalah sifat mobil, bukan firmware. Nilainya seharusnya mirip di kedua uji.
- Tuliskan **versi firmware** di nama berkas log dan di lembar catatan setiap sesi, supaya data tidak tertukar.
