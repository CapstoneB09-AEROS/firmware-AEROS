# Perubahan Database dan Data AEROS untuk Aplikasi

Versi 29 Oktober 2026. Untuk teman software: apa yang berubah di database dan di data yang dikirim ESP, dari apa ke apa, supaya aplikasi bisa menyesuaikan. Sumber: firmware v2.0 (`firmware-v2/`), worker v3 (`worker/`), dan pemeriksaan database langsung. Alur dan kontrak pesan: [komunikasi.md](../keputusan/komunikasi.md).

## Ringkas (yang paling penting)
1. Perangkat sekarang **`AEROS_01`** (sebelumnya data uji `AEROS_DEMO_01`).
2. Data nyata masuk **tiap 5 detik**, tersimpan sekitar 1 detik setelah diukur.
3. Hanya **CO2** yang dipakai. Nilai CO selalu 0 (jalur CO dimatikan untuk MVP).
4. `window_status` sekarang berisi angka: **0** (atas), **50** (bawah, perkiraan dari timer), **null** (sedang bergerak).
5. Tidak ada antrean offline: kalau ESP putus, tidak ada data baru. Aplikasi harus menampilkan "data terakhir X detik lalu", bukan "aman".

## Perubahan struktur database
| Tabel | Sebelum | Sesudah | Dampak ke aplikasi |
|---|---|---|---|
| `sensor_readings` | tanpa nilai puncak | **+ `co_peak_ppm`, `co2_peak_ppm`, `co_peak_second`, `co2_peak_second`** (integer; puncak dalam jendela 5 detik, detik ke-1 sampai 5) | opsional untuk grafik; lonjakan singkat tidak hilang |
| `device_state` | tanpa nilai terakhir | **+ `last_co_ppm`, `last_co2_ppm`** (integer) | **pakai `last_co2_ppm` untuk angka CO2 terkini** |
| `actuator_logs` | tanpa penanda diterima | **+ `received_at`** (timestamptz, boleh kosong) | diisi worker saat perintah dikirim ke ESP |
| `devices` | hanya `AEROS_DEMO_01` | **+ `AEROS_01`** (`is_active = true`) | `AEROS_DEMO_01` dan 156 data ujinya masih ada |
| Hak akses `service_role` | tidak punya akses ke `devices` | diberi akses ke semua tabel `public` | hanya untuk worker; aplikasi tidak terpengaruh |

Yang **belum** berubah (jangan diasumsikan): kolom tambahan di rencana (`sim`, `st_co2`, `fase_*`, dst.), perbaikan cascade, indeks, penghapusan 7 hari, dan perubahan RLS.

## Perubahan isi data
| Hal | Sebelum | Sesudah |
|---|---|---|
| `device_id` | `AEROS_DEMO_01` | **`AEROS_01`** |
| `co_ppm`, `co_peak_ppm` | data uji | **selalu 0** (CO tidak dipakai); tampilkan "CO: tidak dipakai di MVP" |
| `co2_ppm` | data uji | nilai nyata dari MH-Z19C |
| `status` | label uji | **`normal` / `waspada` / `bahaya` dari CO2**. Saat ini mode pengembangan: waspada di 700 ppm, bahaya di 800 ppm (angka final 2500 dan 4000, akan diganti sebelum demo akhir) |
| `window_status` | null | **0 / 50 / null** (lihat ringkas; 50 adalah perkiraan, bukan sensor posisi) |
| `buzzer_state` | `off` | `on` selama ada alarm yang belum dibungkam |
| `event_id` dan `alert_logs.id` | acak | **sama persis** (UUID dibuat ESP saat status naik dari normal; satu episode memakai satu ID dari waspada sampai normal) |
| `measured_at` | waktu simpan | **waktu ukur ESP (UTC)**; tampilkan di aplikasi dengan zona waktu lokal (WIB = UTC+7) |
| `received_at` | - | waktu worker menyimpan; sekarang sekitar 1 detik setelah `measured_at` |
| Pemanasan | - | **3 menit pertama setelah ESP menyala tidak ada data**; perangkat bisa `online` tetapi `device_state` belum berubah |

## Cara membaca keadaan terkini
| Mau tahu | Pakai |
|---|---|
| CO2 dan status sekarang | `device_state`: `last_co2_ppm`, `status`, `buzzer_state`, `window_status` |
| Peringatan aktif | `device_state.active_alert_id` (kosong = tidak ada) dan baris `alert_logs` dengan `id` yang sama |
| Data masih segar? | **`device_state.updated_at`** (diperbarui tiap 5 detik). Anggap offline bila lebih dari 30 detik |
| Perangkat tersambung? | `connection_status` (`online` / `offline`, dari status MQTT ESP). `last_seen_at` hanya berubah saat ESP tersambung, **jangan dipakai** untuk kesegaran data |
| Riwayat | `sensor_readings` urut `measured_at`, satu baris tiap 5 detik (sekitar 17.000 baris per hari) |

## Catatan untuk peringatan
- `alert_logs.alert_type` terisi **sekali** saat peringatan dibuat (biasanya `waspada`) dan **tidak naik ke `bahaya`**. Tingkat tertinggi episode ada di `sensor_readings.status` dan di `device_state.status` (terkini).
- `alert_logs.resolved_at` diisi worker saat status kembali normal. Dua peringatan uji lama (sebelum 12:30 UTC) belum selesai karena `device_state` belum berfungsi waktu itu. Pembersihan (opsional):
```sql
UPDATE public.alert_logs SET resolved_at = now()
WHERE device_id = 'AEROS_01' AND resolved_at IS NULL AND created_at < '2026-10-29 12:30:00+00';
```

## "Saya Tahu" (perintah dari aplikasi): belum diuji ujung ke ujung
Alur rancangan: aplikasi menambah baris di `actuator_logs` (`device_id`, `alert_id` = `alert_logs.id`, `buzzer_state`, `window_action`, `trigger_source`, `execution_status = 'pending'`) → worker membaca baris `pending` tiap beberapa detik → mengirim ke ESP → ESP membalas → worker mengisi `received_at`, `execution_status`, `alert_logs.acknowledged_at`, `device_state.ack_driver` dan `ack_at`. Yang perlu diperiksa: aplikasi punya izin menambah baris di `actuator_logs`, `trigger_source` terisi (bawaan tabel kosong tetapi batasannya hanya `auto` atau `manual`), dan `alert_id` memakai `event_id` yang sedang aktif.
