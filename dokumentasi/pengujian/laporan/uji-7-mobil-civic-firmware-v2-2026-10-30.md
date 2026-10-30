# Laporan Uji 7: Mobil Honda Civic, firmware v2.1 (ambang 2500/4000), 30 Oktober 2026 petang

Firmware v2.1 dengan ambang CO2 2500 (waspada) dan 4000 (bahaya) sementara, lewat Wi-Fi hotspot, HiveMQ, worker di Railway dan Supabase. Berkas: `logs/device-monitor-261030-183128.log` (18:31:29 sampai 19:10:23). Jam di log adalah jam laptop (WIB); jam di database UTC (WIB = UTC+7), sudah dicocokkan.

## 7.1 Kondisi dan garis waktu

Mobil Honda Civic, 4 orang. Jam alat tidak dicatat ulang oleh pengguna; jam di bawah dibaca dari log.

| Jam | Kejadian | Sumber |
|---|---|---|
| 18:31:29 | Log mulai (ESP menyala, pemanasan 3 menit) | log |
| 18:34:25 | Pemanasan selesai, CO2 sudah 2881 | log |
| sekitar 18:34:40 | CO2 turun drastis 2881 → 1289 (jendela depan dibuka, dugaan dari catatan pengguna) | log + catatan |
| 18:45 | Lampu merah, lalu jalan lagi saat hijau | catatan |
| 18:55 | Lampu merah | catatan |
| sekitar 18:57:40 | CO2 turun drastis lagi 3651 → 1342 (dua jendela depan dibuka, dugaan) | log + catatan |
| 19:10:23 | Log berhenti, CO2 3245 | log |

## 7.2 Hasil

| Ukuran | Hasil | Status |
|---|---|---|
| Waspada (>= 2500, 3 bacaan) | 18:34:27 (CO2 2864), 18:42:07 (2509), 19:04:23 (2522) | Terukur |
| Bahaya (>= 4000, 3 bacaan) | 18:57:19 (CO2 4025), puncak 4025 | Terukur |
| Selesai (< 2500 selama 10 detik) | 18:35:01 (2219) dan 18:58:34 (2210) | Terukur |
| Buzzer | waspada: 3 bip pendek sekali; bahaya: 1 bip panjang 3 detik | Terukur |
| GPIO26 turun (buka) | HIGH 18:57:19 selama **1689 ms** (diset 1500) | Terukur |
| GPIO26 naik (tutup) | HIGH 18:58:34 selama **5690 ms** (diset 5000) | Terukur |
| Laju naik CO2, 4 orang, jendela tertutup | +213 sampai +268 ppm/menit (1300 → 2500), melambat ke sekitar 50 sampai 120 ppm/menit di 2700 sampai 3500 | Terukur |
| Waktu dari jendela tertutup ke bahaya | sekitar 21 menit (18:36 sampai 18:57) | Terukur |
| Penurunan setelah jendela dibuka | 2881 → 1289 dalam sekitar 80 detik; 3651 → 1342 dalam sekitar 100 detik | Terukur |
| Lantai CO2 setelah turun | sekitar 1290 sampai 1340, lalu naik lagi | Terukur |
| Kehilangan data | tidak ada: 431 ACK untuk sekitar 431 kiriman (18:34:25 sampai 19:10:23), tidak ada lompatan waktu di log | Terukur |
| Database | 451 baris sesi ini, jeda simpan (received_at − measured_at) median 1,45 s, p95 1,68 s, maks 2,68 s; puncak CO2 di DB 4025 sama dengan log | Terukur |
| `alert_logs` | 3 peringatan (id 6ffb76b9, 16a55aef, 9347442f) cocok dengan 3 event di log; 2 pertama sudah `resolved_at` | Terukur |
| `window_status` di DB | 0 saat atas, 50 saat bawah (14 baris), null saat bergerak (3 baris) | Terukur |

## 7.3 Temuan

| # | Temuan | Dampak |
|---|---|---|
| 1 | `alert_type` tetap `waspada` untuk peringatan 16a55aef walau CO2 mencapai bahaya 18:57:19. Bahaya hanya terlihat di `sensor_readings.status` dan `device_state.status` | aplikasi tidak boleh bergantung pada `alert_type` untuk tingkat bahaya |
| 2 | ESP offline setelah 19:10:34, tetapi `device_state` masih `status = waspada`, `buzzer_state = on`, `active_alert_id` = 9347442f, `last_co2_ppm = 3278`. `connection_status = offline` sudah benar | aplikasi harus menampilkan "perangkat offline" bila `connection_status` offline atau `updated_at` lebih dari 30 detik; peringatan 9347442f tetap terbuka sampai ESP menyala lagi dan mengirim data normal (worker menutupnya otomatis lewat `telemetryStateService.js`, tidak perlu SQL manual) |
| 3 | Lama sinyal GPIO26 melebihi nilai set: +189 ms (turun) dan +690 ms (naik). Di log lama: 1501 dan 5000 (29 Okt), 1614 (30 Okt 15:12) | selisih 0 sampai sekitar 0,7 detik; penyebab belum diperiksa |
| 4 | Tombol "Saya Tahu" tidak diuji: `acknowledged_at` kosong di ketiga peringatan | fitur ini di luar MVP (keputusan pengguna 30 Okt), tidak perlu diuji sekarang |
| 5 | Lantai CO2 sekitar 1300 setelah jendela dibuka. Pada uji 4 (Avanza) CO2 juga masih turun setelah jendela ditutup karena jeda sensor (T90 sampai 120 detik) | belum bisa dibedakan antara jendela sudah ditutup dan sensor naik; perlu pembacaan di udara terbuka |

## 7.4 Yang belum diketahui

- Jam jendela ditutup dan alasan lonjakan CO2 18:56 (3400 → 3945 dalam 30 detik), tidak ada di catatan.
- Pengaruh lampu merah 18:45 dan 18:55 pada CO2: di 18:45 CO2 datar sekitar 2770 selama 1 menit; di 18:55 turun 3612 → 3400 lalu naik tajam. Satu pengamatan, belum cukup untuk kesimpulan.
