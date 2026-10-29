# Rencana Uji

Versi 27 Oktober 2026. Rencana, templat, dan lembar catatan untuk uji lapangan dan uji bangku. Hasil tiap uji ada di [laporan/](laporan/). Analisis datanya di [analisis/](../analisis/ringkasan-temuan.md). Keputusan yang bergantung pada uji ada di [belum-diputuskan.md](../keputusan/belum-diputuskan.md).

## 1. Uji yang sudah dilakukan
| Uji | Tanggal | Firmware | Laporan |
|---|---|---|---|
| 0. Baseline kamar 4 jam | 25 Okt | v0 | [uji-0](laporan/uji-0-baseline-kamar-2026-10-25.md) |
| 1. Mobil Civic EG6 | 25 Okt malam | v0 | [uji-1](laporan/uji-1-mobil-civic-2026-10-25.md) |
| 2. Kamar pagi (nyala dingin, kipas, AC) | 26 Okt pagi | v0 | [uji-2](laporan/uji-2-kamar-pagi-2026-10-26.md) |
| 3. Ruang pertemuan 13 orang (ESP baru) | 26 Okt sore | v0 | [uji-3](laporan/uji-3-ruang-rapat-2026-10-26.md) |
| 4. Mobil Avanza (jendela) | 26 Okt malam | v0 | [uji-4](laporan/uji-4-mobil-avanza-2026-10-26.md) |
| 5. Parfum di ruangan | 27 Okt | v0 | [uji-5](laporan/uji-5-parfum-2026-10-27.md) |
| 6. Firmware v1 di meja (CO2, jendela) | 28 Okt sore | v1 | [uji-6](laporan/uji-6-firmware-v1-2026-10-28.md) |

Semua uji memakai firmware lama sebagai pembanding dasar. Algoritma baru dibandingkan dengan **memutar ulang log yang sama** (bagian 6), bukan dengan mengulang uji.

## 2. Uji berikutnya
| Uji | Cara singkat | Lulus bila |
|---|---|---|
| Parfum di mobil | di akhir sesi; jendela tertutup; **satu** semprotan 30-50 cm ke arah dashboard; rekam 5 menit; buka jendela sesudahnya | dicatat apakah melewati 35 ppm lebih dari 30 detik atau mencapai 87 ppm (sensor tidak boleh terpapar pelarut berulang) |
| Jendela mobil lain (Civic atau Classy) | templat bagian 3 | N dan waktu motor tercatat |
| Wi-Fi bersama sensor (T22), setelah firmware gabungan | tahap A Wi-Fi mati 30 menit; B1 tersambung diam 15 menit; B2 kirim 15 menit; lalu putus-sambung Wi-Fi 2 menit | `t_s` tidak melompat; jumlah baris di database sama dengan yang dikirim; tidak ada data dobel atau hilang; alarm tetap bunyi tanpa internet; Rs tidak berubah dibanding log ESP lama; kapan antrean penuh tercatat |
| Pengukuran 5 V dengan Min/Max 15 menit | multimeter di pin ESP, MiCS, MH-Z19C; laptop baterai dan charger | nilai minimum dan maksimum tercatat; ulangi setelah buck |
| Firmware gabungan di meja | napas ke kotak (CO2 sampai 2500 dan 4000), mode simulasi CO, ukur waktu gerak jendela | aturan CO dan CO2 bekerja sesuai [algoritma-firmware.md](../keputusan/algoritma-firmware.md) |
| Nyala dingin (opsional) | mati lebih dari 1 jam, rekam 10 menit di kamar | Rs menit ke-3 dekat menit ke-10 (satu uji bersih sudah ada) |
| Relay jendela di meja, tanpa sensor | bagian 2.1; firmware kecil di `alat-uji/uji-relay-jendela/` | relay klik, jendela turun, ESP tidak reset, waktu turun per ms tercatat |

### 2.1 Uji relay jendela di meja (tanpa sensor)

Tujuan: memastikan rangkaian ESP → transistor → relay → motor bekerja, dan **mengukur berapa jauh jendela turun per milidetik** (mengisi `PULSA_BUKA_MS`, lihat [belum-diputuskan.md](../keputusan/belum-diputuskan.md) butir 1b). Sensor, LCD, dan buzzer tidak dipasang. Firmware: [alat-uji/uji-relay-jendela/src/main.cpp](../../alat-uji/uji-relay-jendela/src/main.cpp) (terpisah dari `src/main.cpp`). Rangkaiannya ada di [algoritma-firmware.md](../keputusan/algoritma-firmware.md) bagian 5.1.

Perintah di serial monitor (+ Enter): `o` (2000 ms), `o<ms>` (maks 5000), `x` (stop), `s` (status), `n` (nolkan total), `h` (bantuan).

| Tahap | Cara | Lulus bila |
|---|---|---|
| 0. GPIO26 tanpa beban | firmware `alat-uji/uji-gpio26` (paksa HIGH terus; `h` dan `l` mengganti level); lepas 470 Ω dan PN2222A, ukur GPIO26 terhadap GND ESP | sekitar 3,3 V (3,2-3,35 V); LED ESP ikut menyala |
| 1. Motor dan relay saja (tanpa ESP) | 12 V langsung ke koil relay (pin 85/86), jendela bebas | relay klik, jendela turun |
| 2. Transistor dan relay | 3,3 V dari pin 3V3 ke ujung resistor 470 Ω | relay klik |
| 3. ESP penuh | unggah firmware uji, ketik `o` | LED ESP menyala 2 detik, relay klik, jendela turun, `alasan reset` tidak berubah (tidak reset saat relay menyala) |
| 4. Ukur jarak per waktu | naikkan jendela manual ke atas, ketik `n`, lalu `o500`, ukur jarak turun; naikkan lagi, ulangi dengan `o1000`, `o2000` | tabel ms → cm tercatat |

Tegangan yang perlu dicatat saat tahap 3 (probe di titik ukur sebelum Enter):

| Titik | Diam | Aktif |
|---|---|---|
| GPIO26 terhadap GND ESP | sekitar 0 V | sekitar 3,3 V |
| Koil relay (85-86) | 0 V | sekitar 12 V |
| 5 V pada pin VIN atau 5V ESP | stabil | tidak turun di bawah 4,7 V |

Bila ESP reset saat relay menyala, bacaan `alasan reset` di baris pembuka akan menunjukkan penyebabnya (BROWNOUT = catu tidak kuat). Itu berguna untuk memeriksa dugaan masalah catu dan ground (lihat [ringkasan-temuan.md](../analisis/ringkasan-temuan.md)).

Lembar catatan (isi saat uji):

| Pulsa (ms) | Jarak turun (cm) | Jendela | Mobil/rig | ESP reset? | Catatan |
|---|---|---|---|---|---|
| 500 | | | | | |
| 1000 | | | | | |
| 2000 | | | | | |

## 3. Skenario uji mobil (templat untuk mobil berikutnya)

Tujuan: **laju pertukaran udara (N)** mobil yang diuji dan perilaku Rs di mobil tanpa alat mulai ulang. Uji Avanza 26 Okt memakai templat ini sebagian ([laporan uji 4](laporan/uji-4-mobil-avanza-2026-10-26.md)).

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

## 4. Keselamatan, persiapan, setelah uji, batasan

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
- [ ] Lembar catatan (bagian 5) siap, atau berkas teks di ponsel.
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

## 5. Lembar catatan kosong

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

## 6. Perbandingan firmware lama dan baru

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
| Noise Rs (%) | `analisis_mobil.py` dan `skrip/filter_compare.py` |
| Waktu alarm sesudah kejadian (jendela dibuka, antrean) | Dari jam di log dan lembar catatan |
| Jumlah alarm dan perpindahan status per 10 menit | Dihitung dari log |
| Jumlah gerakan jendela per 10 menit (hanya firmware baru) | Dihitung dari log kejadian |
| Alarm palsu | Dari log dan catatan |
| Mulai ulang atau USB putus | Dari log |

Catatan:
- Firmware lama **tidak punya aktuasi jendela**. Jendela dibuka manual (lembar catatan), jadi yang dibandingkan adalah **filter dan logika alarm**, bukan gerakan jendela.
- Laju turun CO2 setelah jendela dibuka adalah sifat mobil, bukan firmware. Nilainya seharusnya mirip di kedua uji.
- Tuliskan **versi firmware** di nama berkas log dan di lembar catatan setiap sesi, supaya data tidak tertukar.

## 7. Rencana pengujian target luaran

| Target | Cara uji | Bisa? |
|---|---|---|
| Deteksi CO2 melewati 2500 (4 dari 5 uji) | Napas ke kotak tertutup, lima pengulangan, catat log | Bisa |
| Deteksi CO (4 dari 5 uji) | Mode simulasi berlabel. Uji respons dengan gas pereduksi pengganti (butana dari korek), **bukan CO** | Sebagian |
| Bunyi ≤ 5 detik sejak status berubah | Bandingkan jam di log dengan video | Bisa |
| Jendela mulai bergerak ≤ 10 detik | Log dan video | Bisa |
| Buka dan tutup jendela (4 dari 5 uji) | Lima pengulangan | Bisa |
| Data tampil di aplikasi dalam waktu tertentu | Bandingkan jam log perangkat dengan jam di aplikasi | Butuh Wi-Fi dan MQTT |
| Anggaran ≤ Rp2.000.000 | Jumlahkan nota | Bisa |
