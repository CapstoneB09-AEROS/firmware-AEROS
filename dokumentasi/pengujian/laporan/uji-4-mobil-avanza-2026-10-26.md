# Laporan Uji 4: Mobil Toyota Avanza, 26 Oktober 2026 malam

ESP baru, firmware lama (v0). Hasil mentah: [hasil-uji-mobil-2026-10-26.txt](../../analisis/hasil/hasil-uji-mobil-2026-10-26.txt).

## 3A.1 Kondisi dan garis waktu (dari catatan)

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

## 3A.2 Hasil

| Ukuran | Hasil | Status |
|---|---|---|
| Laju naik CO2, jendela tertutup | **3 orang: +156 ppm/menit. 4 orang: +207 sampai +218 ppm/menit** (jalan 20–40 km/jam). Kecepatan >100 km/jam: +164 ppm/menit | Terukur |
| CO2 puncak | 4444 ppm (19:56:14) dan 4453 ppm (20:11:52). Tidak sampai 5000 | Terukur |
| Jendela 1 | Dibuka sekitar 19:56:20, CO2 4437 → 2384 saat ditutup (±95 detik) → turun lagi ke 1831 setelah ditutup | Terukur |
| Jendela 2 | Dibuka 20:11:40, CO2 4447 → 2121 saat ditutup (±110 detik) → turun lagi ke 1660 setelah ditutup | Terukur |
| **N saat dua jendela depan setengah terbuka** | **sekitar 30–32 per jam** (perkiraan kasar dari luruhan; batas bawah karena penumpang masih bernapas dan sensor punya jeda). **Dihitung ulang dengan model dan jeda sensor: N = 46–79 per jam, terbaik sekitar 60**; N tertutup 0,5–2 per jam ([analisis/ringkasan-temuan.md](../../analisis/ringkasan-temuan.md) baris 13) | Perkiraan |
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

## 3A.3 Filter
- **Seluruh log:** sisa noise SMA 6 1,71%, EMA 0,2 1,63%, SMA 8 1,64%, EMA 0,1 1,43%. Lompatan ppm 0 ↔ 10: 9 kali (SMA 6) lawan 27 kali (EMA 0,2).
- **Per fase:** fase A (mobil jalan, orang naik, jendela pertama): SMA 6 3,04% lawan EMA 0,2 2,65% (bagian bergantian hanya 79%, banyak guncangan jalan). Fase B dan C (bagian bergantian 92%): SMA 6 0,72 dan 0,75% lawan EMA 0,2 1,04 dan 1,05%.
- Kesimpulan: SMA 6 menang bila goyangan didominasi pola bergantian; saat jalan bergelombang, filter yang lebih panjang (EMA 0,1 atau SMA 8) sedikit lebih halus. Pilihan SMA 6 dipertahankan dan SMA 8 tetap cadangan bila ada alarm palsu dari guncangan.

## 3A.4 Yang kurang
- Jam buka dan tutup jendela hanya sampai menit, bukan detik. N dihitung dari titik CO2 ketika jendela ditutup (±5 detik).
- Posisi alat belum dicatat. ESP: baru (dikonfirmasi). Jam jendela hanya sampai menit, tidak ada catatan lebih rinci.
- Satu mobil, satu malam, dua bukaan jendela dengan lebar sama; lebar lain belum diuji.
