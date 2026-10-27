# Laporan Uji 1: Mobil Honda Civic EG6, 25 Oktober 2026 malam

Firmware lama (v0). Analisis lintas uji: [analisis/ringkasan-temuan.md](../../analisis/ringkasan-temuan.md).

## 1.1 Kondisi

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

## 1.2 Garis waktu (dari catatan, jam 24 jam)

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

## 1.3 Berkas log

| Berkas di `logs/` | Waktu | Dipakai? |
|---|---|---|
| `device-monitor-261025-213732.log` | 21:37–21:41 (4 menit) | Tidak (terlalu pendek, alat mulai ulang) |
| `device-monitor-261025-214144.log` | 21:41–21:57 | **Ya** (sesi 1) |
| `device-monitor-261025-220026.log` | 22:00–22:15 | **Ya** (sesi 2) |

Analisis: `analisis/skrip/analisis_mobil.py`. Hasil mentah: [hasil-uji-mobil-2026-10-25.txt](../../analisis/hasil/hasil-uji-mobil-2026-10-25.txt).

## 1.4 Hasil ringkas

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

## 1.5 Yang kurang dari uji 1

- Tidak ada uji buka jendela, jadi N tidak bisa dihitung.
- Tidak ada pembanding udara luar (CO2 luar).
- Alat mati dan menyala lagi di tengah uji (21:41 tanpa catatan penyebab, 22:00 karena SPBU); sesi pertama hanya 16 menit.
- Alat dekat tubuh penumpang, belum diketahui seberapa besar pengaruhnya.
- Jam beberapa kejadian hanya sampai menit, tanpa suhu setelan AC.
