# Skenario Uji Mobil (malam, rute SPBU)

Rencana uji: 25 Oktober 2026, malam. Rute: sekitar 2–3 km dari rumah ke SPBU, dengan antrean. Terkait: [desain-peringatan.md](../3-bukti/desain-peringatan.md) (A6, B4, E, F), [daftar-tugas.md](../1-utama/daftar-tugas.md) (T11).

## 1. Tujuan: yang ingin dipelajari

| # | Pertanyaan | Hasil yang dicari |
|---|---|---|
| 1 | Seberapa cepat CO2 naik tiap jumlah orang? | Laju naik (ppm per menit) untuk jumlah orang yang ada |
| 2 | Seberapa cepat CO2 turun saat jendela dibuka? | Laju turun untuk beberapa lebar bukaan dan lama |
| 3 | Seberapa besar noise sensor di mobil (getaran, catu) dibanding di meja? | Jalankan `noise_profile.py` pada log mobil |
| 4 | Apakah sambungan USB dan catu stabil saat berkendara? | Jumlah putus dan mulai ulang |
| 5 | Bagaimana pembacaan MiCS (Rs) saat antre di belakang kendaraan lain? | Perubahan **relatif** Rs, bukan ppm |
| 6 | Seberapa sering alarm palsu muncul (dengan logika simulasi pada log)? | Dihitung setelah uji pada log |

**Yang tidak bisa disimpulkan:** ppm CO yang akurat. Tidak ada CO asli atau alat referensi. Pembacaan MiCS di SPBU dan antrean ikut dipengaruhi uap bensin dan gas lain (sensor tidak selektif), jadi tulis sebagai "respons terhadap gas pereduksi".

## 2. Keselamatan (baca dulu)

- **Pengemudi tidak boleh menyentuh laptop atau sensor.** Penumpang yang mengoperasikan laptop dan mencatat.
- **SPBU:** uap bensin mudah terbakar, dan pemanas sensor serta rangkaian terbuka (breadboard, ESP32, USB, laptop) bukan perangkat aman di area pompa. **Matikan dan simpan perangkat sebelum memasuki area SPBU** sesuai aturan SPBU. Lakukan bagian antrean di jalan umum atau di luar area SPBU (antrean di jalan, lalu lintas macet), bukan di dalam area pompa.
- Jangan menyalakan korek di dalam mobil. Jangan merokok, menyemprot parfum, atau memakai hand sanitizer di kabin selama uji.
- Kabel dan laptop terpasang aman (tidak menghalangi pedal, setir, atau tuas).
- Jangan menguji bukaan jendela saat mobil bergerak kencang. Lakukan saat berhenti atau pelan.
- Jangan membuat CO sendiri.

## 3. Persiapan sebelum berangkat

- [ ] Baterai laptop terisi, `caffeinate` aktif (`caffeinate -im -t 7200`).
- [ ] Kabel USB sensor dilekatkan (selotip) dan konektor masuk penuh. Ingat dua kali USB putus tadi siang.
- [ ] Jalankan perekam: `cd /Users/maritzavania/Downloads/aeros-sensor` lalu `~/.platformio/penv/bin/pio device monitor -f time -f log2file`.
- [ ] Siapkan **berkas catatan kejadian** (ponsel atau teks) dengan jam sesuai jam laptop.
- [ ] Cek jam laptop dan ponsel sama.
- [ ] Siapkan penghitung waktu dan lembar catatan (tabel di bagian 5).
- [ ] Posisi sensor ditetapkan dan **dicatat** (misalnya di konsol tengah). Gunakan posisi yang sama sepanjang uji.
- [ ] Catat versi firmware: `main.cpp` per 23 Okt 2026 (belum diperbaiki), filter EMA 0,2.

## 4. Urutan fase

Durasi adalah usulan. Sesuaikan dengan kondisi. Catat jam mulai dan selesai tiap fase.

| Fase | Kegiatan | Durasi | Catat |
|---|---|---|---|
| A | **Pemanasan dan pembanding udara luar.** Mobil parkir di tempat terbuka, mesin mati, semua jendela terbuka, sensor menyala. | 10–15 menit | Jam mulai. Warm-up sensor (CO2 3 menit, MiCS belum stabil) |
| B | **Kabin tertutup, parkir.** Jendela tertutup, AC pada kondisi yang **dicatat** (mati, sirkulasi dalam, atau udara luar), jumlah orang tetap. Mesin hidup hanya bila perlu AC dan mobil di tempat terbuka. | 10 menit atau sampai CO2 mencapai 3000 (batas aman 4000, hentikan sebelum 4000) | Jumlah orang, mode AC, suhu AC, jam |
| C | **Berkendara ke SPBU** (2–3 km). Kondisi kabin sama seperti fase B. | Sesuai rute | Jumlah orang, mode AC, kecepatan kasar, jam, kejadian (lampu merah, jalan rusak) |
| D | **Antre di jalan menuju SPBU** (berhenti dan jalan, mesin hidup). Catat apa yang ada di depan: truk, mobil diesel, motor. | Sesuai antrean | Jam masuk dan keluar antrean, jenis kendaraan di depan, mesin dan AC, jendela tertutup |
| E | **Uji buka jendela** (di tempat aman, mobil berhenti atau sangat pelan). Saat CO2 sekitar 2000–3000: buka jendela depan dengan lebar tertentu selama waktu tertentu, lalu tutup. Ulangi dengan lebar atau lama berbeda bila waktu cukup. | 3–5 menit per percobaan | Jam buka dan tutup **tepat**, lebar (seperempat, setengah, penuh), jendela mana saja, mobil berhenti atau jalan |
| F | **Pulang** (opsional): ubah mode AC (misalnya dari sirkulasi dalam ke udara luar) dan lihat selisihnya. | Sesuai rute | Mode AC, jam perubahan |

**Aturan berhenti:** jika CO2 mencapai **4000**, buka jendela segera (sesuai aturan desain), jangan menunggu sampai 5000. Sensor mentok di 5000, dan di atas itu tidak terbaca.

## 5. Lembar catatan kejadian (isi dengan jam)

| Jam | Fase | Kejadian | Jumlah orang | Mode AC | Jendela | Keterangan |
|---|---|---|---|---|---|---|
| | | | | | | |

Catat juga hal yang bisa memengaruhi sensor: parfum atau semprotan, makanan, napas dekat sensor, jendela atau pintu dibuka, putusnya kabel, lampu merah lama.

### Contoh pengisian (angka dan jam hanya contoh, bukan data)

| Jam | Fase | Kejadian | Jumlah orang | Mode AC | Jendela | Keterangan |
|---|---|---|---|---|---|---|
| 19:42 | A | Mulai rekam, mobil parkir di depan rumah, mesin mati | 0 | mati | semua terbuka | Layar menunjukkan CO2 sekitar 480. Cuaca cerah. Catat angka CO2 ini sebagai CO2 udara luar |
| 19:57 | B | Masuk mobil, jendela ditutup, AC dinyalakan | 4 | sirkulasi dalam, 24 °C | semua tertutup | Mesin hidup. Mulai hitung naiknya CO2 |
| 20:07 | B | CO2 terbaca sekitar 3000, hentikan fase B | 4 | sirkulasi dalam | semua tertutup | Dicatat 10 menit dari 19:57 |
| 20:10 | C | Berangkat menuju SPBU | 4 | sirkulasi dalam | tertutup | Jalan sedang, tidak macet |
| 20:18 | D | Masuk antrean di jalan menuju SPBU, di belakang truk diesel | 4 | sirkulasi dalam | tertutup | Mesin hidup, berhenti dan jalan |
| 20:30 | E | Buka jendela depan kanan setengah, mulai hitung | 4 | sirkulasi dalam | depan kanan setengah | Mobil berhenti. CO2 saat dibuka sekitar 3200 |
| 20:31 | E | Tutup jendela | 4 | sirkulasi dalam | tertutup | Lama dibuka 60 detik. CO2 setelahnya sekitar 2900 |

Tips mengisi: cukup satu baris tiap **kejadian**, bukan tiap menit. Yang paling penting adalah jam buka dan tutup jendela (sampai ke detik bila bisa), karena dari situ laju turun CO2 dihitung. Jam yang dipakai harus sama dengan jam laptop.

## 6. Setelah uji

1. Simpan folder `logs/` dan lembar catatan **sebelum** melakukan hal lain.
2. Kirim nama berkas log dan catatan. Saya akan:
   - Menghitung laju naik CO2 per fase dan per jumlah orang.
   - Menghitung laju turun saat jendela dibuka dan memperkirakan laju pertukaran udara (N).
   - Menjalankan `noise_profile.py` dan `filter_compare.py` pada log mobil.
   - Mencari putus-putus USB dan mulai ulang.
   - Menjalankan simulasi waktu tunggu pada log.
3. Bandingkan dengan model C-251 Bab 10 (T19).

## 7. Batasan uji ini

- Satu malam, satu mobil, satu rute.
- Jumlah orang tergantung yang ikut.
- Tidak ada CO asli dan tidak ada alat referensi.
- Sensor MiCS masih punya baseline yang bergeser (Rs turun lebih dari 50% dalam 4 jam di kamar), jadi nilai absolut CO tidak dipakai.
- Rangkaian masih di breadboard dan daya dari laptop.
- Pengujian di kendaraan nyata dinyatakan di luar cakupan di C-251 Bab 7.6, jadi ini dilaporkan sebagai **uji eksplorasi tambahan**.

## 8. Perbandingan firmware lama dan baru

Sebelum firmware baru difinalkan, perilakunya dibandingkan dengan firmware lama.

| Hal | Rencana |
|---|---|
| Firmware lama (v0) | `src/main.cpp` per 23 Okt 2026 (filter EMA 0,2). **Salinan cadangan:** `arsip-firmware/main-v0-2026-10-23.cpp` (checksum sama dengan `src/main.cpp`) |
| Uji malam ini | Memakai firmware **lama** sebagai pembanding dasar (baseline) |
| Memutar ulang di komputer | Log 1 detik dari uji malam ini berisi tegangan, Rs, dan CO2. Algoritma baru (SMA 6, aturan prioritas, uji arah) bisa **dijalankan ulang pada data yang sama**. Ini perbandingan yang paling adil karena inputnya identik, dan tidak perlu menunggu mobil lagi |
| Uji kedua | Memakai firmware **baru**, dengan rute, jam, dan jumlah orang semirip mungkin. Kondisi tidak akan identik, jadi hasilnya dipakai sebagai konfirmasi, bukan angka mutlak |

Yang dibandingkan:

| Ukuran | Cara menghitung |
|---|---|
| Noise Rs (%) | `noise_profile.py` dan `filter_compare.py` |
| Waktu alarm sesudah kejadian (jendela dibuka, antrean) | Dari jam di log dan lembar catatan |
| Jumlah alarm dan perpindahan status per 10 menit | Dihitung dari log |
| Jumlah gerakan jendela per 10 menit (hanya firmware baru) | Dihitung dari log kejadian |
| Alarm palsu | Dari log dan catatan |
| Mulai ulang atau USB putus | Dari log |

Catatan:
- Firmware lama **tidak punya aktuasi jendela**. Pada uji malam ini jendela dibuka manual (lembar catatan), jadi yang dibandingkan adalah **filter dan logika alarm**, bukan gerakan jendela.
- Laju turun CO2 setelah jendela dibuka adalah sifat mobil, bukan firmware. Nilainya seharusnya mirip di kedua uji.
- Tuliskan **versi firmware** di nama berkas log dan di lembar catatan setiap sesi, supaya data tidak tertukar.
