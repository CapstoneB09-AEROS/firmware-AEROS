# Keputusan yang Belum Ada (UX, Angka, Hardware, Data)

Versi 27 Oktober 2026. Satu daftar untuk dibawa ke pertemuan tim. Menggabungkan bagian 5 dan 6 [pseudocode-baru.md](pseudocode-baru.md) (yang ditulis 25 Okt) dengan temuan 26 sampai 27 Okt. Kolom **Usulan** adalah usulan saya sebagai dasar diskusi, bukan keputusan. Kolom **Status** memakai istilah yang sama dengan [validasi-parameter.md](../3-bukti/validasi-parameter.md).

Tenggat: firmware dibekukan **Kamis 29 Okt siang**, expo Jumat 30 Okt.

## 0. Yang harus selesai sebelum Kamis siang (urut penting)

| # | Keputusan | Siapa | Kenapa mendesak |
|---|---|---|---|
| 1 | Waktu gerak motor jendela setengah (`WAKTU_SETENGAH`) di mobil demo | hardware (ukur), kamu (catat) | Tanpa ini logika jendela tidak bisa diuji |
| 2 | Pin buzzer dan pin jendela di PCB | hardware | Firmware butuh pin pasti. GPIO14 sudah dipakai tombol Wi-Fi |
| 3 | Pesan data: v3 (diputuskan, sisa: teman backend mengerjakan worker) | teman backend | Menentukan apa yang boleh dikirim firmware |
| 4 | Pola bunyi dan tombol "Saya Tahu" (B15) | kamu dan tim | Mudah, tapi harus ada sebelum kode ditulis |
| 5 | Teks LCD (B18) | kamu | Sama |
| 6 | Strategi R0 di mobil (B1) | kamu | Menentukan apakah ppm di demo masuk akal |
| 7 | Rencana cadangan demo (bila jaringan atau jendela bermasalah) | tim | Expo tidak boleh bergantung pada satu hal |

## 1. UX: bunyi, tombol, tampilan

| Kode | Yang belum diputuskan | Usulan | Status |
|---|---|---|---|
| B15a | Bunyi **WASPADA** (CO ≥ 35 ppm atau CO2 ≥ 2500) | **3 bip pendek (sekitar 2 detik), sekali saat status masuk level ini** | Diubah 27 Okt: 10 detik dinilai mengganggu |
| B15b | Bunyi **BAHAYA** (CO ≥ 87 ppm, CO2 ≥ 4000, atau CO dari luar) | **1 bip panjang (sekitar 3 detik), sekali saat status masuk level ini** | Diubah 27 Okt |
| B15c | Pengulangan bunyi | **CO2: tidak diulang** (siklus sekitar 15 menit, jadi cukup dua bunyi per siklus: saat 2500 dan saat 4000). **CO: diulang tiap 60 detik sampai "Saya Tahu" atau kondisi turun, maksimum 5 menit**, karena CO menyangkut keselamatan. Naik ke level lebih tinggi selalu berbunyi | Usulan (perlu persetujuan) (**disetujui 27 Okt**) |
| B15d | Arti "Saya Tahu" | mematikan **bunyi saja**. Alarm dan jendela tetap jalan sesuai aturan. Bunyi muncul lagi bila naik ke tingkat bahaya. Bunyi mati sendiri setelah 5 menit | Usulan |
| B15e | Apakah ada tombol fisik "Saya Tahu" di perangkat, atau hanya lewat aplikasi | **belum ada info**: tanya teman hardware. GPIO14 dipakai tombol portal Wi-Fi, jadi tombol ini butuh pin lain | Belum |
| B15f | Volume "lebih keras" untuk bahaya | tergantung jenis buzzer (aktif atau pasif). Kalau aktif, volume tetap, pembeda hanya pola | Belum |
| B18a | Angka di LCD 16x2 | **Tetap seperti v0** (`CO: 12ppm`, `CO2: 850ppm`). Disetujui 27 Okt | Diputuskan |
| B18b | Status (disederhanakan jadi 5) | `PEMANASAN`, `NORMAL`, `WASPADA`, `BAHAYA`, `GANGGUAN`. Jenis gas ditulis di baris LCD (`WASPADA CO`, `BAHAYA CO2`, `BAHAYA CO LUAR`). Di database tetap 3 nilai (`normal`, `waspada`, `bahaya`) plus penanda pemanasan atau gangguan | Usulan pengguna 27 Okt |
| B18c | Teks di aplikasi | wajib memuat: ppm CO "**estimasi, kemungkinan CO atau gas lain**"; "perangkat offline **bukan** berarti aman"; waktu data terakhir | Usulan |
| B18d | Apa yang ditampilkan saat CO masih pemanasan | `PEMANASAN`, bukan angka ppm (sudah di pseudocode, alasan: 20 detik pertama terbaca 3000-4120 ppm palsu) | Diputuskan |

## 2. Angka yang masih sementara

| Kode | Parameter | Nilai sekarang | Dasar | Status | Cara menentukan |
|---|---|---|---|---|---|
| B12 | Panjang filter CO | SMA 6 (cadangan 4 atau 8) | data kamar dan mobil, 0,9-1,4% sisa noise | Usulan | uji ulang di PCB dan jalan bergelombang |
| B3 | Konfirmasi CO | 30 detik | sementara | Usulan | tabel sensitivitas |
| B5 | Lama uji arah | 30 detik | pengamatan informal (korek) | Usulan | uji dengan sumber nyata bila ada |
| B6 | Kriteria "CO dari luar" | Rs turun >25% | tanpa gas tidak pernah lewat 25% di ±28.000 detik, satu lonjakan nyata -54% | Usulan | uji ulang dengan data baru |
| B7 | Batas selesai CO | 30 ppm, 60 detik | sementara | Usulan | tabel sensitivitas |
| B8 | CO2: konfirmasi, batas selesai | 3 bacaan, <2500, 10 detik | data Avanza | Usulan | uji mobil lain |
| B9a | Lama jendela terbuka | min 20 detik, maks 180 detik | satu mobil (Avanza) | Usulan | uji di mobil demo |
| B9b | Jeda tertutup minimum | 5 menit | siklus alami 15,6 menit | Usulan | uji di mobil demo |
| B9c | `WAKTU_SETENGAH` | belum ada angka | harus diukur per mobil (Classy, Civic, Avanza) | **Belum** | ukur dengan stopwatch |
| B11 | Pemanasan CO | 180 detik | datasheet tidak memuat; data kamar | Usulan | uji nyala dingin 10 menit |
| B16 | Kalibrasi otomatis CO2 | dimatikan | konfirmasi tim | Belum dikonfirmasi | tanya tim |
| Telemetri | Interval kirim | 5 detik (kode tim 10 detik) | rancangan data | Belum | keputusan tim |
| Antrean | Kapasitas di flash | 360 (dugaan sebenarnya ~200) | dugaan littlefs | **Belum diuji** | tes Wi-Fi mati |
| Buzzer | Berhenti sendiri | 5 menit | | Usulan | |

## 3. Hardware dan kalibrasi

| Yang belum diputuskan | Catatan | Siapa |
|---|---|---|
| **R0 di mobil (B1)** | **Diputuskan 27 Okt:** satu nilai tetap 1730 kΩ dengan label estimasi, tanpa ukur ulang tiap berangkat. Ukur ulang sekali (perintah `r`, udara bersih) setelah buck terpasang | kamu |
| **R0 melewati batas datasheet** | Datasheet rev 8: R0 100-1500 kΩ. Kita 1730 kΩ. Dugaan: catu 4,64 V. Ukur ulang setelah buck | hardware |
| VCC di kode (4,64 V) | Ubah sekali setelah buck terpasang, lalu ukur R0 ulang. Catat VCC di tiap log | kamu dan hardware |
| Pengukuran 5 V dengan Min/Max 15 menit (ESP, pin MiCS, pin MH-Z19C) | Belum dilakukan dengan Min/Max | hardware |
| Pin buzzer dan jendela di PCB | GPIO14 sudah dipakai | hardware |
| Relay jendela: arus, jenis, perilaku saat daya jatuh | belum ada informasi | hardware |
| **Anti-jepit** | Tidak dibangun. Ditulis sebagai batasan. Tanya apakah jendela Classy punya anti-jepit pabrik | hardware |
| Cara mendeteksi sensor mati sebentar tanpa ESP mulai ulang (B11 sisa) | | kamu |
| Pengaruh Wi-Fi menyala terhadap Rs dan catu | uji T22 setelah firmware gabungan | kamu |
| Siklus Rs ±13-17% (penyebab belum diketahui) | kandidat: catu, regulator, kondisi laptop | hardware |

## 4. Data, jaringan, backend

| Yang belum diputuskan | Usulan | Siapa |
|---|---|---|
| Isi pesan versi 3 atau tetap v2 | **Diputuskan 27 Okt:** worker dan komunikasi mengikuti kebutuhan firmware dan data (v3 jadi acuan). v2 hanya jalan mundur bila worker belum siap sebelum 29 Okt. Tinggal teman backend menyetujui dan mengerjakan | teman backend |
| Worker menulis `alert_logs` dengan `id = event_id` | **disetujui dari sisi kita** (2.8.8), menunggu pemilik worker | teman backend |
| Format kolom `alert_logs` (gas, nilai, ambang, sumber) | cocokkan dengan [rancangan-data.md](rancangan-data.md) 4.3 | teman backend |
| Kebijakan antrean penuh | buang telemetri tertua, lindungi kejadian | teman backend |
| Tabel partisi ESP | `huge_app.csv` (kode tim tidak muat dengan bawaan) | teman backend |
| Akun HiveMQ, kunci HMAC, sertifikat | diisi lokal, tidak masuk git | teman backend |
| Hotspot 2,4 GHz untuk uji | | tim |
| Retensi data | | teman backend |
| Bagaimana notifikasi di aplikasi sekarang dibuat | tanya langsung | teman software |
| Aturan akses (ACL) HiveMQ | satu topik `aeros/data` untuk semua perangkat: disengaja? | teman backend |

## 5. Laporan dan demo

| Yang belum diputuskan | Catatan |
|---|---|
| Rencana cadangan demo | contoh: jendela diganti diorama atau servo (C-251) bila mobil tidak aman; mode simulasi bila jaringan mati |
| Pembagian C-501 (laporan hasil) | setelah expo |
| Cara menyebut ppm CO di laporan | selalu "estimasi dari kurva datasheet (±10% pembacaan grafik), belum dikalibrasi gas referensi" |
| Batasan yang ditulis jujur | anti-jepit, kalibrasi CO, satu mobil untuk angka jendela, offline bukan berarti aman |
| Uji jendela Civic | belum dilakukan |

## 6. Yang sudah diputuskan (supaya tidak dibahas ulang)

Ambang CO 35 ppm dan 87 ppm (estimasi); CO2 2500 dan 4000 (bukan 4500, lihat desain-peringatan.md A2 dan A3); pemanasan 180 detik untuk keduanya; SMA 6 dan CO2 tanpa filter; sensor sehat tetap bekerja saat sensor lain gagal; A=3,7 dan β=0,856 dipertahankan (digitalisasi piksel selisih <1,5% di 35-100 ppm); VCC tetap 4,64 V sampai buck terpasang; jendela setengah lewat waktu motor; worker menulis `alert_logs`; uji arah 30 detik untuk membedakan CO dalam dan luar (27 Okt); status disederhanakan jadi 5 (`PEMANASAN`, `NORMAL`, `WASPADA`, `BAHAYA`, `GANGGUAN`); bunyi waspada 3 bip pendek dan bahaya 1 bip panjang, CO2 tidak diulang (B15a-b). Uji parfum ruangan selesai ([laporan](../2-lapangan/laporan-uji-parfum-2026-10-27.md)); uji di mobil masih diperlukan.

## 7. Usulan tambahan ringan (belum disetujui)

Lihat [pseudocode-baru.md](pseudocode-baru.md) bagian 2.11. Sembilan hal dari kode tim dimasukkan sebagai rancangan. Lima tambahan ringan menunggu persetujuanmu: T1 uji mandiri saat menyala, T2 watchdog dan alasan reset, T3 "data terakhir X detik lalu" di aplikasi, T4 `fw`, `r0_kohm`, `rst` di pesan `ONLINE`, T5 daftar periksa demo dan rekaman cadangan.
