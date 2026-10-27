# Laporan Uji 2: Kamar, 26 Oktober 2026 pagi

Firmware lama (v0). Analisis lintas uji: [analisis/ringkasan-temuan.md](../../analisis/ringkasan-temuan.md).

Tujuan: menjawab empat hal sebelum uji mobil malam. (1) Apakah Rs menit ke-3 sudah dekat nilai stabil? (2) Apakah siklus Rs sekitar 7 menit muncul lagi? (3) Apakah siklus itu hilang bila kipas dimatikan? (4) Apakah siklus atau Rs berubah bila AC menyala?

## 2.1 Kondisi dan garis waktu (dari catatan, jam 24 jam)

| Fase | Jam | Kipas | AC | Pintu | Orang |
|---|---|---|---|---|---|
| P0 | 09:03:46 | Nyala | Mati | Terbuka | Alat dinyalakan (colok USB). Lima menit pertama dibuang |
| P1 | 09:08–09:45 | Nyala, mengarah ke alat | Mati | Terbuka | Pemilik tidak di kamar |
| P2 | 09:46–10:15 | **Mati** | Mati | Terbuka | Pemilik di kamar selama 15 menit terakhir, di sisi seberang alat |
| P3 | 10:16–10:47 | Mati | **Nyala** | **Tertutup** | Pemilik di kamar, di atas depan meja dan alat (dekat) |

Firmware: lama (v0, EMA 0,2), alat tidak berpindah dan tidak dicabut.

## 2.2 Berkas log

| Berkas di `logs/` | Waktu | Catatan |
|---|---|---|
| `device-monitor-261026-090343.log` | 09:03:46–10:47:33 (6226 detik) | Tanpa mulai ulang, tanpa celah |

Analisis: `analisis/skrip/analisis_fase.py`. Hasil mentah: [hasil-uji-kamar-pagi-2026-10-26.txt](../../analisis/hasil/hasil-uji-kamar-pagi-2026-10-26.txt).

## 2.3 Hasil ringkas

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

## 2.4 Jawaban dari empat pertanyaan

| # | Pertanyaan | Jawaban |
|---|---|---|
| 1 | Pemanasan 3 menit cukup? | **Ya untuk satu kali nyala dingin.** Rs menit ke-3 sudah di dalam rentang siklus. Pemanasan CO 3 menit tetap, dengan catatan satu pengukuran |
| 2 | Siklus 7 menit muncul lagi? | **Ya**, periode 7,01 menit, ±13–17% |
| 3 | Hilang bila kipas dimatikan? | **Tidak.** Kipas bukan penyebabnya |
| 4 | Berubah bila AC menyala? | **Ya, mengecil menjadi ±4–7%.** Penyebab (AC, pintu, atau orang dekat) belum terpisah |

## 2.5 Tentang sumber siklus: dugaan, belum bukti

Petunjuk bahwa siklus dan goyangan 0,5 Hz berasal dari sumber yang sama:
- Periode 7,01 menit, sama pada dua hari.
- Jarak antara dua pembalikan tanda goyangan bergantian: median 420 detik, sama dengan periode siklus (7,00 menit).
- Korelasi 0,90 (pagi) dan 0,92 (4 jam) antara siklus dan kuadrat amplitudo goyangan bergantian.

Petunjuk yang melawan: setelah AC menyala siklus mengecil menjadi sepertiga, sementara goyangan bergantian tidak. Jadi sumbernya mungkin sama, tetapi besarnya ikut dipengaruhi kondisi udara.

Uji yang membedakan (belum dilakukan): mengganti interval siklus firmware dari 1,0 detik menjadi misalnya 1,25 detik pada firmware baru. Bila siklus 7 menit itu muncul akibat sampling terhadap sumber 2 detik, periodenya akan **berubah**; bila berasal dari lingkungan, periodenya tetap 7 menit.

## 2.6 Yang berlaku untuk firmware baru
- SMA 6 tetap dipilih. Ia tidak menghilangkan siklus 7 menit (itu gerakan lambat), hanya goyangan per detik.
- Kriteria uji arah (B6) dinaikkan ke **25%**: 8% dan 15% terlampaui oleh gerakan alami Rs tanpa gas.
- Pemanasan 3 menit untuk keduanya tidak berubah.

## 2.7 Yang kurang dari uji 2
- Hanya satu kali nyala dingin.
- Tiga hal berubah bersamaan di P3 (AC, pintu, orang dekat), jadi pengaruh masing-masing belum terpisah.
- Tidak ada pembanding suhu dan kelembapan (tidak ada sensornya).
