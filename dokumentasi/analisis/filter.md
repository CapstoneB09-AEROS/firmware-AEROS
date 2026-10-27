# Analisis Filter Pembacaan MiCS-5524

Hasil analisis pemilihan filter pada rekaman baseline kamar. Skrip dan data ada di [skrip/](skrip/), [data/](data/), dan [hasil/](hasil/):
- `skrip/filter_compare.py`: skrip analisis (cara pakai ada di bagian atas skrip).
- `data/data-baseline-t3314-4313.csv`: data yang dianalisis (1000 baris).
- `hasil/hasil-filter-2026-10-25.txt`: keluaran skrip pada data itu; menjalankan ulang pada CSV memberi hasil yang sama.

Keputusan filter (SMA 6) ada di [keputusan.md](../keputusan/keputusan.md); profil noise dari rekaman 4 jam di [ringkasan-temuan.md](ringkasan-temuan.md).

---

## 1. Data yang dianalisis

| Item | Isi |
|---|---|
| Tanggal | 25 Oktober 2026 |
| Rentang | `t_s` 3314 sampai 4313 (sekitar 16,7 menit), sekitar 11:00–11:20 WIB |
| Kondisi | Meja di kamar, udara diasumsikan bersih, tanpa gas CO yang diketahui |
| Status | Semua baris `OK(<10ppm)`, tanpa celah waktu |
| Sinyal yang difilter | Rs mentah, dihitung dari `V_mV` dengan VCC = 4.64 V dan RL = 9970 Ω (sama dengan firmware). Sudah berupa rata-rata 16 pembacaan per detik di firmware |
| Rs | 1767–3114 kΩ, rata-rata 2045 kΩ |
| Sensor | Menyala sekitar 1,5 jam sebelum rentang ini dan **belum stabil** (Rs masih bergerak) |

## 2. Hasil

| Filter | Noise (%) | Turun | Korelasi lag-1 | Waktu naik 90% (detik) | Lonjakan +30% yang tersisa (%) |
|---|---|---|---|---|---|
| Mentah (tanpa filter) | 13.3 | 0% | -0.92 | 0 | 30.0 |
| SMA 5 | 3.7 | 72% | 0.02 | 4 | 6.4 |
| SMA 10 | 2.6 | 81% | 0.99 | 8 | 3.1 |
| SMA 30 | 2.4 | 82% | 0.99 | 26 | 1.1 |
| EMA 0.05 | 2.1 | 84% | 0.98 | 44 | 1.6 |
| EMA 0.1 | 2.5 | 81% | 0.90 | 21 | 3.1 |
| EMA 0.2 (firmware sekarang) | 2.9 | 78% | 0.55 | 10 | 6.2 |
| Median 5 | 13.0 | 2% | -0.93 | 2 | 6.2 |
| Median 5 lalu EMA 0.1 | 2.4 | 82% | 0.90 | 23 | 1.2 |

Arti kolom:
- **Noise (%)**: simpangan baku Rs di sekitar tren lambat (rata-rata bergerak 121 detik), relatif terhadap tren. Keterlambatan filter sudah dikoreksi dengan menerapkan filter yang sama pada tren.
- **Korelasi lag-1**: negatif besar berarti nilainya bergantian naik-turun tiap detik.
- **Waktu naik 90%**: simulasi. Rs turun mendadak 50%, lalu dihitung berapa detik sampai keluaran filter menempuh 90% dari perubahan itu.
- **Lonjakan +30%**: satu titik data nyata diganti nilainya jadi 130%, lalu dilihat berapa persen lonjakan yang masih lolos ke keluaran filter. Lonjakannya buatan.

## 3. Temuan

1. **Gangguan dominan bukan acak.** Tegangan MiCS bergantian tiap detik (contoh: 24.9 dan 23.7 mV) dengan korelasi lag-1 = -0.92.
2. **Besarnya goyangan naik-turun berulang** sekitar tiap 8 menit:

   | `t_s` mulai | Goyangan rata-rata (dari V) |
   |---|---|
   | 3314 | 2.7% |
   | 3414 | 9.5% |
   | 3514 | 19.6% |
   | 3614 | 10.1% |
   | 3714 | 1.9% |
   | 3814 | 2.6% |
   | 3914 | 9.9% |
   | 4014 | 20.1% |
   | 4114 | 8.3% |
   | 4214 | 2.0% |

3. **Median 5 tidak berguna untuk pola ini** (turun 2%). Median menolak lonjakan tunggal, bukan pola bolak-balik.
4. **Moving average bekerja.** SMA 10 (jumlah genap) meredam pola bolak-balik dengan baik (81%). SMA 5 (jumlah ganjil) menyisakan lebih banyak (72%).
5. **Filter yang meredam semua (SMA 10, SMA 30, EMA 0.05, EMA 0.1, median lalu EMA 0.1) hanya berbeda 2.1–2.6%.** Perbedaan itu kecil dan tidak bermakna, karena angka tersebut masih memuat gerakan lambat sensor yang belum stabil. Yang membedakan adalah kecepatan responsnya.
6. **Rata-rata saja tidak membuang lonjakan tunggal.** SMA 5 dan EMA 0.2 masih meloloskan sekitar 6%. Median lalu EMA 0.1 meloloskan 1.2% tetapi respons 23 detik.

## 4. Dugaan penyebab (belum terbukti)

Pola bergantian dengan amplitudo naik-turun tiap sekitar 8 menit mirip interaksi dua siklus yang periodenya hampir sama, misalnya siklus pengukuran MH-Z19C (manual menyebut arus puncak 125 mA) dan loop 1 detik firmware.

Cara membuktikan: jalankan 10–15 menit tanpa MH-Z19C (cabut catu 5 V-nya) lalu lihat apakah goyangan hilang. Kalau hilang, penyebabnya ketemu.

## 4. Batasan analisis

- Hanya 16,7 menit di satu kondisi, dan sensor belum stabil.
- Lonjakan dan perubahan mendadak berupa simulasi, bukan kejadian gas nyata, jadi tabel tidak menjawab "alarm bereaksi berapa detik".
- Diuji di meja. Di mobil akan ada gangguan tambahan (lihat bagian 7).
- Pola bolak-balik kemungkinan berasal dari papan sendiri, bukan lingkungan. Penyebabnya belum dikonfirmasi.

## 5. Rumus keterlambatan

Rumus dari alphaxiv, sudah saya periksa kebenaran matematisnya. Tulis jelas jenis "delay" yang dipakai.

**Moving average kausal N sampel:**

    y[n] = (1/N) * jumlah dari k=0 sampai N-1 dari x[n-k]

Group delay: tau_g = (N - 1) / 2 sampel, atau t_g = ((N - 1) / 2) * Ts, dengan Ts periode sampling. Contoh: SMA 5 punya delay efektif 2 sampel. Rumus ini untuk MA simetris. Untuk jendela yang hanya melihat ke belakang, perhatikan apakah keluaran diberi cap waktu di sampel terbaru atau di pusat jendela.

**EMA dengan 0 < alpha <= 1:**

    y[n] = alpha * x[n] + (1 - alpha) * y[n-1]

- Group delay pada frekuensi mendekati nol: tau_g(0) = (1 - alpha) / alpha sampel. Untuk alpha = 0.2 ini 4 sampel.
- Respons step dari kondisi awal nol: y[n] = 1 - (1 - alpha)^(n+1).
- Waktu mencapai sekitar 63,2% dari nilai akhir: t_63 = -Ts / ln(1 - alpha). Untuk alpha = 0.2 dan Ts = 1 detik, sekitar 4.5 detik.
- Waktu mencapai 90%: t_90 = ln(0.1) / ln(1 - alpha). Untuk alpha = 0.2 sekitar 10.3 detik, cocok dengan tabel di bagian 2.

**Median:** filter nonlinear, jadi group delay klasik tidak berlaku. Kalau yang penting adalah keterlambatan deteksi kenaikan CO, ukur dengan uji step: catat waktu perubahan gas dan waktu keluaran melewati ambang. Median cocok untuk lonjakan sesaat, tetapi bisa menunda transien nyata kalau jendelanya terlalu lebar.

Catatan: kolom "Waktu naik 90%" di bagian 2 adalah t_90 hasil simulasi, **bukan** group delay dan bukan t_63. Sebutkan itu di laporan.
