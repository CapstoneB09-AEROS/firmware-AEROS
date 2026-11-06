# Perbandingan 5 Uji Mobil Terakhir (Avanza, Civic, Ayla), 4 Nov 2026

Semua uji berisi **4 orang**. Angka dihitung ulang dengan satu cara yang sama dari kolom log yang ada di semua versi firmware (`t_s, V_mV, Rs, Rs/R0, CO, CO2`), memakai [skrip/bandingkan_mobil.py](skrip/bandingkan_mobil.py). Hasil lengkap per uji: [hasil/hasil-bandingkan-mobil-2026-11-04.txt](hasil/hasil-bandingkan-mobil-2026-11-04.txt). Salinan log: [data/uji-mobil-5-terakhir/](data/uji-mobil-5-terakhir/).

Status tiap angka: **Terukur** = dihitung langsung dari log. **Dugaan** = penjelasan yang masuk akal tetapi tidak dibuktikan oleh data ini.

## 1. Ringkasan

1. **Civic berbeda dari dua mobil lain, dan bedanya ada di CO2.** Di Civic (4 Nov) CO2 naik cepat sampai sekitar 3000, lalu melambat dan **mendatar di sekitar 3500–3700 ppm**. Dalam 40 menit CO2 tidak pernah mencapai 4000 dan jendela tidak pernah dibuka oleh sistem. Di Ayla dan Avanza, CO2 terus naik lewat 4000 dalam sekitar 9–11 menit setelah melewati 2500. Pola lambat yang sama muncul di Civic 30 Okt (15 menit dari 2500 ke 4000). Ini sesuai dugaan Anda bahwa Civic tidak kedap. Terukur.
2. **Ayla dan Avanza (4 Nov) hampir sama:** laju naik 2000–3000 ppm sekitar 155–200 ppm/menit di keduanya, dan siklus buka-tutup sekitar 18–20 menit. Terukur.
3. **Bahwa gas buang atau bensin masuk kabin Civic tidak bisa dibuktikan dari data ini.** Ada tanda yang cocok (Rs MiCS rendah, CO estimasi 10–27 ppm selama sekitar 30 menit pertama), tetapi ada penjelasan lain yang tidak bisa dipisahkan (bagian 5). Dugaan.
4. **Sinyal "bip sebelum tutup" (v2.5) belum pernah muncul di log mana pun.** Semua uji hari ini berjalan di v2.4, atau di v2.5 tetapi tidak ada kejadian tutup (Civic tidak mencapai 4000). Belum teruji di mobil.

## 2. Data yang dipakai

| # | Uji | Firmware | Waktu dipakai | Jumlah bacaan | Folder |
|---|---|---|---|---|---|
| 1 | Avanza 26 Okt | v0 | 19:59–20:26 (28 menit; 4 orang naik 19:53, dipakai mulai CO2 dasar 19:59) | 1675 | `1-avanza-2026-10-26/` |
| 2 | Civic EG6 1994, 30 Okt | v2.0 (CO belum aktif, tanpa Rs) | 18:34–19:10 (36 menit) | 2184 | `2-civic-2026-10-30/` |
| 3 | **Daihatsu Ayla 2023, 4 Nov sore** | v2.4 + casing 3D | 14:52–16:07 (76 menit) | 4200 | `3-ayla-2026-11-04/` |
| 4 | **Avanza, 4 Nov malam** | v2.4 + casing 3D | 18:39–19:42 (63 menit) | 3461 | `4-avanza-2026-11-04/` (3 berkas, monitor dimulai ulang tanpa alat mulai ulang) |
| 5 | **Civic EG6 1994, 4 Nov malam** | v2.4 + casing 3D | 20:09–20:53 (45 menit) | 2055 | `5-civic-2026-11-04/` (3 berkas, **alat mulai ulang 20:23 dan 20:52**) |

Tidak dipakai: Civic 25 Okt (hanya 2 penumpang), log pendek `261104-144140` (2 menit, alat dimulai ulang), dan seluruh log meja.

Jendela dibuka dan ditutup **manual** (2 jendela depan, bukaan setengah) sesuai bunyi. **Jam buka dan tutup tidak tercatat di log**, jadi siklus dibaca dari bentuk kurva CO2. Bacaan CO2 = 500 (nilai pengisi saat pemanasan setelah alat nyala) dibuang.

## 3. CO2: kecepatan naik dan turun

**Laju naik** (median ppm/menit, jendela tertutup, 120 detik pertama setelah dasar dibuang karena jeda sensor dan pencampuran udara). Terukur.

| Pita CO2 | Avanza 26 Okt | Civic 30 Okt | Ayla 4 Nov | Avanza 4 Nov | **Civic 4 Nov** |
|---|---|---|---|---|---|
| 2000–2500 | 199 | 206 | 190 | 189 | 150 |
| 2500–3000 | 205 | 110 | 184 | 156 | 101 |
| 3000–3500 | 162 | 102 | 177 | 142 | **72** |
| 3500–4000 | 196 | **66** | 142 | 120 | **−6 (datar)** |

**Waktu dari melewati 2500 sampai melewati 4000** (jendela tertutup). Terukur.

| Uji | Waktu | Jumlah siklus |
|---|---|---|
| Avanza 26 Okt | 7,4 menit | 1 |
| Civic 30 Okt | 15,2 menit | 1 |
| Ayla 4 Nov | 8,6–9,5 menit | 4 |
| Avanza 4 Nov | 9,9–11,5 menit | 3 |
| Civic 4 Nov | **tidak tercapai** sampai data habis (maks 3725 ppm, lebih dari 40 menit di atas 2500) | 0 |

**Waktu turun** dari puncak sampai di bawah 2500 setelah jendela dibuka. Terukur, tetapi mengandung jeda penguji membuka jendela (manual):

| Uji | Detik |
|---|---|
| Avanza 26 Okt | 97 |
| Civic 30 Okt | 67 |
| Ayla 4 Nov | 58–74 |
| Avanza 4 Nov | 65–67 |
| Civic 4 Nov | tidak ada pembukaan (CO2 tidak mencapai 4000) |

Titik terendah CO2 setelah jendela dibuka (1161–1465 ppm pada uji 2–4) **tidak dibandingkan**, karena ditentukan kapan jendela ditutup secara manual dan CO2 masih turun beberapa menit setelah ditutup (jeda sensor).

### Avanza yang sama, dua kali (26 Okt dan 4 Nov)

Laju naik 3000–4000 ppm turun dari sekitar 211 (26 Okt) ke sekitar 130 ppm/menit (4 Nov). Untuk 2000–3000 selisihnya kecil (207 lawan 175–184). Penyebabnya **tidak bisa dipisahkan** dari data ini: casing 3D, firmware, kecepatan mobil, AC, posisi alat, dan isi mobil tidak dicatat sama persis. Dugaan.

## 4. Sensor gas (MiCS) hari ini: Ayla, Avanza, Civic

Hanya tiga uji 4 Nov yang bisa dibandingkan di sini: alat, firmware, dan R0 sama (1878 kΩ, hasil kalibrasi di Ayla). Rs antar-tanggal tidak sebanding: Rs Avanza 26 Okt (925 kΩ) lawan 4 Nov (2021 kΩ) berbeda dua kali lipat di mobil yang sama, sesuai catatan bahwa R0 tidak konstan di [ringkasan-temuan.md](ringkasan-temuan.md). Terukur.

| | Ayla | Avanza | **Civic** |
|---|---|---|---|
| Rs median (persentil 5–95), kΩ | 1530 (1257–2105) | 2021 (1860–2205) | **801 (517–1196)** |
| Rs/R0 median | 0,78 | 1,08 | **0,43** |
| CO estimasi: median / maks, ppm | 0 / 17 | 0 / 0 | **12 / 27** |
| Waktu dengan CO estimasi ≥ 10 ppm | 16% | 0% | **68%** |
| CO estimasi ≥ 35 ppm (waspada) | 0% | 0% | 0% |

Rs di Civic naik terus dari rendah setiap alat mulai: sekitar 500 kΩ pukul 20:09 jadi 870 kΩ pukul 20:20; setelah mulai ulang 20:23 jadi 429 kΩ lalu naik ke 1220 kΩ pukul 20:52. CO estimasi turun ke 0 mulai sekitar 20:42, saat Rs melewati sekitar 1000 kΩ. Di Avanza, Rs tetap sekitar 2000–2100 kΩ sejak alat nyala sampai selesai; di Ayla tidak naik terus (2066 → 1458 → 1541 kΩ pada tiga titik uji). Terukur.

## 5. Yang bisa dan belum bisa disimpulkan tentang Civic

**Didukung data (Terukur):** udara kabin Civic bertukar dengan luar jauh lebih banyak daripada Ayla dan Avanza. Buktinya CO2 mendatar di 3500–3700 dengan 4 orang (di titik itu produksi CO2 penumpang seimbang dengan kebocoran). Ini terjadi di dua hari berbeda (30 Okt dan 4 Nov).

**Belum bisa dibedakan (Dugaan):** apakah Rs rendah di Civic berasal dari
1. gas yang benar-benar masuk kabin (gas buang, bau bensin yang Anda catat), atau
2. sensor yang masih menstabil setelah nyala (alat mulai ulang dua kali dan Rs naik terus tiap kali), atau
3. kondisi lain (suhu dan kelembapan, uap bensin atau alkohol; MiCS-5524 tidak membedakan CO dari gas pereduksi lain).

Di Ayla dan Avanza Rs tidak naik terus setelah alat nyala, jadi poin 2 saja kurang menjelaskan. Tapi R0 hasil kalibrasi di Ayla dipakai di Civic tanpa kalibrasi ulang, dan sensor belum diuji dengan gas CO referensi, sehingga "CO 10–27 ppm" di Civic **tidak boleh ditulis sebagai CO yang terukur**.

## 6. Temuan yang relevan untuk produk

- Ambang tindakan 4000 ppm **tidak pernah tercapai di Civic** walau CO2 bertahan 3300–3700 ppm lebih dari 30 menit. Sistem hanya berada di WASPADA (3 bip pendek sekali, jendela tidak dibuka). Ini fakta untuk dibahas di laporan: ambang tetap 4000 tidak bereaksi di mobil yang tidak kedap.
- Fitur bip sebelum jendela naik (v2.5) belum teramati di log.
- Alat mulai ulang dua kali di Civic (20:23 dan 20:52, `t_s` kembali ke 3). Penyebab tidak diketahui (dugaan awal: USB mobil atau kabel, sesuai peringatan di [rencana-uji.md](../pengujian/rencana-uji.md) bagian 2.0).

## 7. Keterbatasan

- Satu uji per mobil per hari, 28–76 menit. Posisi alat, kecepatan, dan AC tidak dicatat sama.
- Jam buka dan tutup jendela tidak tercatat, jadi laju turun dan titik dasar tidak bisa dibandingkan teliti.
- N (laju pertukaran udara) tidak dihitung: regresi sederhana hanya bermakna untuk Ayla (N ≈ 2,0/jam, r −0,54) dan Avanza 4 Nov (≈ 2,4/jam, r −0,75). Untuk uji lain korelasi terlalu kecil (r −0,12 sampai −0,15) atau tidak ada siklus (Civic 4 Nov). Pakai [model-vs-uji.md](model-vs-uji.md) untuk N yang sudah ada.
- Firmware beda antara uji (v0, v2.0, v2.4), dan hanya tiga uji terakhir memakai casing 3D.
