# Uji Lapangan: Laporan Uji 1 dan Skenario Uji 2

Terkait: [desain-peringatan.md](../3-bukti/desain-peringatan.md) (A6, B4, E, F), [daftar-tugas.md](../1-utama/daftar-tugas.md) (T11), analisis data: [ringkasan-temuan-2026-10-25.md](../analisis/ringkasan-temuan-2026-10-25.md) bagian 7.

| Bagian | Isi |
|---|---|
| 1 | **Laporan uji 1**: mobil, 25 Oktober 2026 malam, firmware lama |
| 2 | **Skenario uji 2**: 26 Oktober, pagi di kamar dan malam di mobil |
| 3 | Firmware besok: lama atau baru? |
| 4 | Keselamatan, persiapan, setelah uji, batasan |
| 5 | Lembar catatan kosong untuk uji 2 |
| 6 | Perbandingan firmware lama dan baru (rencana) |

---

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

Penyebab mulai ulang jam 21:41 tidak tercatat. Isi bila ingat: ____________

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

## 2. Skenario uji 2: 26 Oktober 2026

Tujuan satu kalimat: menjawab dua hal yang belum diketahui, yaitu **dari mana pergeseran Rs berasal** dan **berapa laju pertukaran udara (N) Civic**.

### 2.1 Pagi: uji kamar (firmware lama), sekitar 75 menit

**Pertanyaan yang dijawab**

| # | Pertanyaan | Dari mana jawabannya |
|---|---|---|
| 1 | Setelah alat dinyalakan dingin, Rs menit ke-3 sudah dekat menit ke-10? (menentukan pemanasan CO 3 menit, S4) | Rs per menit pada P1 |
| 2 | Siklus Rs sekitar 7 menit muncul lagi pada kondisi sama seperti log 4 jam? | P1, minimal 4 siklus (30 menit) |
| 3 | Siklus itu hilang bila kipas dimatikan? | P2 |
| 4 | Siklus atau Rs bergeser bila AC kamar menyala? | P3 |

**Persiapan**
- Alat **mati lebih dari 1 jam** sebelum dinyalakan (misalnya sejak semalam).
- Letakkan alat di tempat yang sama seperti rekaman 4 jam (11:53–16:05), dengan kipas mengarah seperti waktu itu.
- Pintu dan jendela kamar tertutup. Jangan bernapas dekat alat. Orang boleh di kamar, tetapi duduk diam dan **catat**.
- Jangan cabut MH-Z19C.
- Perekam: `~/.platformio/penv/bin/pio device monitor -f time -f log2file` (nama berkas akan dicatat dalam lembar).

**Urutan** (jam dicatat tepat, satu variabel berubah tiap fase)

| Fase | Kegiatan | Durasi | Catat |
|---|---|---|---|
| P0 | Nyalakan alat (colok USB). Mulai rekam. Kipas menyala seperti log 4 jam | 5 menit pertama dibuang | Jam colok |
| P1 | Tidak diapa-apakan. Kipas menyala, AC mati | 30 menit | Jam mulai, apakah kipas berayun |
| P2 | **Kipas dimatikan**. AC tetap mati | 20 menit | Jam kipas mati |
| P3 | **AC menyala** (kipas tetap mati). Catat suhu setelan dan arah angin | 20 menit | Jam AC nyala, suhu setelan, arah angin |

Total sekitar 75 menit. Bila tidak ada waktu: P1 (30 menit) dan P2 (20 menit) sudah menjawab pertanyaan 1–3.

**Cara membaca hasil**
- Pertanyaan 1: bandingkan Rs rata-rata menit ke-3 dengan menit ke-10 pada P1 (selisih dalam persen).
- Pertanyaan 2–4: jalankan `analisis_mobil.py` pada tiap fase; lihat bagian siklus lambat (6) per fase.
- Bila siklus hilang saat kipas mati: penyebabnya kipas (aliran udara). Bila tetap ada: sensor atau rangkaian, bahas dengan teman hardware.

### 2.2 Malam: uji mobil (firmware lama)

**Pertanyaan yang dijawab**

| # | Pertanyaan |
|---|---|
| 1 | Berapa N (laju pertukaran udara) Civic saat jendela dibuka, untuk lebar dan lama tertentu? |
| 2 | Berapa laju naik CO2 saat mobil **diam** dengan 2 orang (tanpa pengaruh kecepatan)? |
| 3 | Berapa CO2 udara luar? |
| 4 | Apakah Rs di mobil stabil bila alat tidak mulai ulang? |

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

## 3. Firmware besok: lama atau baru?

**Rekomendasi: firmware lama, untuk uji pagi dan uji malam.** Firmware baru dipakai mulai uji berikutnya.

| Alasan | Penjelasan |
|---|---|
| Satu variabel berubah | Yang diuji besok adalah sensor dan mobilnya (nyala dingin, siklus Rs, N Civic). Dengan firmware yang sama seperti uji 1, selisih hasil berasal dari kondisi, bukan dari kode. Dibandingkan dengan log 4 jam dan uji 1 |
| Log lama sudah cukup | Log mencatat tegangan mentah per detik. Filter baru (SMA 6) dan aturan baru bisa **diputar ulang pada log yang sama** tanpa menyalakan firmware baru. Perbandingan lama lawan baru paling adil di cara ini (bagian 6) |
| Firmware baru belum ditulis | Menurut jadwal ([daftar-tugas.md](../1-utama/daftar-tugas.md)), firmware baru ditulis 26 Okt dan diunggah ke ESP final 27 Okt. Menunggunya berarti uji besok bisa terlambat atau bercampur dengan perbaikan bug |
| Risiko | Firmware baru yang belum dicoba di meja bisa mulai ulang atau berhenti di tengah uji mobil, dan itu mengulang kesalahan uji 1 |

**Uji pagi** memang tempat yang cocok untuk firmware baru **setelah ia ada**: di kamar, udara bersih, tanpa risiko. Itu bisa dilakukan 27 Okt (uji meja), bukan besok pagi.

Urutan yang disarankan:

| Hari | Uji | Firmware |
|---|---|---|
| 26 Okt pagi | Kamar: nyala dingin, kipas, AC (2.1) | Lama |
| 26 Okt malam | Mobil: jendela dan N (2.2) | Lama |
| 27 Okt | Meja: napas ke kotak, simulasi CO, ukur gerak jendela | **Baru** (bila sudah ada dan Anda setuju) |
| 28 Okt | Mobil ke-3 dan integrasi (bila sempat) | **Baru** |
| 29 Okt siang | Bekukan | |

Firmware baru ditulis di cabang `firmware-baru` (git), bukan menimpa `src/main.cpp`, dan hanya setelah ada izin eksplisit dari Anda.

---

## 4. Keselamatan, persiapan, setelah uji, batasan

### Keselamatan
- **Pengemudi tidak boleh menyentuh laptop atau sensor.** Penumpang yang mengoperasikan laptop dan mencatat.
- **SPBU:** uap bensin mudah terbakar, dan pemanas sensor serta rangkaian terbuka (breadboard, ESP32, USB, laptop) bukan perangkat aman di area pompa. Matikan dan simpan perangkat sebelum memasuki area SPBU. Uji 2 tidak melewati SPBU.
- Jangan menyalakan korek di dalam mobil. Jangan merokok, menyemprot parfum, atau memakai hand sanitizer di kabin selama uji.
- Kabel dan laptop terpasang aman (tidak menghalangi pedal, setir, atau tuas).
- Jangan menguji bukaan jendela saat mobil bergerak kencang. Lakukan saat berhenti atau pelan.
- Jangan membuat CO sendiri.

### Persiapan (centang)
- [ ] Baterai laptop terisi, `caffeinate` aktif (`caffeinate -im -t 7200`).
- [ ] Kabel USB dilekatkan (selotip), konektor masuk penuh. Jangan dicabut di tengah uji.
- [ ] Perekam jalan: `cd /Users/maritzavania/Downloads/aeros-sensor` lalu `~/.platformio/penv/bin/pio device monitor -f time -f log2file`.
- [ ] Jam laptop dan ponsel sama.
- [ ] Lembar catatan (bagian 5) siap, atau berkas teks di ponsel.
- [ ] Posisi alat ditetapkan dan dicatat.
- [ ] Versi firmware ditulis di lembar (lama v0, EMA 0,2).

### Setelah uji
1. Simpan folder `logs/` dan lembar catatan **sebelum** melakukan hal lain.
2. Kirim nama berkas log dan catatan. Yang akan dihitung:
   - Rs menit ke-3 lawan menit ke-10 (P1), dan siklus lambat per fase (P1–P3).
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

## 5. Lembar catatan kosong, uji 2 (26 Oktober)

Cukup satu baris tiap **kejadian**, bukan tiap menit. Yang paling penting: jam buka dan tutup jendela sampai detik. Jam harus sama dengan jam laptop.

**Pagi, kamar**

| Jam (hh:mm:ss) | Fase | Kejadian | Kipas | AC | Keterangan |
|---|---|---|---|---|---|
| | P0 | Colok USB, mulai rekam | | | Nama log: |
| | P1 | Mulai | | | |
| | P2 | Kipas mati | | | |
| | P3 | AC nyala | | | Suhu setelan: |
| | | Selesai | | | |

**Malam, mobil**

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

## 6. Perbandingan firmware lama dan baru

Sebelum firmware baru difinalkan, perilakunya dibandingkan dengan firmware lama.

| Hal | Rencana |
|---|---|
| Firmware lama (v0) | `src/main.cpp` per 23 Okt 2026 (filter EMA 0,2). **Salinan cadangan:** `arsip-firmware/main-v0-2026-10-23.cpp` (checksum sama dengan `src/main.cpp`) |
| Uji 1 dan uji 2 | Memakai firmware **lama** sebagai pembanding dasar (baseline) |
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
