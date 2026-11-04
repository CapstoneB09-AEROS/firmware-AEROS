# Pembagian Tugas: Database dan Pencatatan Peringatan MVP

Versi 3 November 2026. Rancangan lengkap, SQL, dan hasil uji: [rancangan-database-mvp.md](../keputusan/rancangan-database-mvp.md). Diagram: [diagram-8-hubungan-tabel-mvp.png](../keputusan/diagram/diagram-8-hubungan-tabel-mvp.png). Rancangan worker: [rancangan-worker-mvp.md](../keputusan/rancangan-worker-mvp.md). Berkas ini hanya membagi pekerjaan; isi teknisnya ada di dua rancangan itu.

## Ringkas

MVP: CO dan CO2 dibaca, ada waspada dan bahaya, tiap peringatan direkam beserta gas penyebabnya, tanpa mode offline, tanpa "Saya Tahu". Tabel `actuator_logs` dibuang. Gas dicatat lewat `co_level` dan `co2_level` per bacaan dan `event_id` yang menunjuk ke peringatan; ringkasan per peringatan ada di view `v_alerts`. Ambang CO2 dan CO diganti setelah pengembangan selesai, dan itu tidak mengubah database atau aplikasi karena tingkat dihitung di ESP.

## Urutan kerja

1. Database bagian 4a (tambahan, tidak merusak apa pun).
2. Worker baru (menerima `r3` dan `r4`, peringatan dibuat sebelum bacaan).
3. Database bagian 4b, dengan ESP dimatikan sebentar (4b merusak worker lama).
4. ESP versi 4: kirim `co_level` dan `co2_level`.
5. Aplikasi: pindah ke `v_alerts`, buang "Saya Tahu".
6. Bersih-bersih: buang `alert_type`, penerimaan `r3`, dan jadwalkan hapus bacaan lama.

Urutan ini penting: menjalankan 4b sebelum worker baru membuat worker lama gagal menyimpan bacaan. Rinciannya di [rancangan-worker-mvp.md](../keputusan/rancangan-worker-mvp.md) bagian 7.

## Teman database

Catatan: worker (Node) **dikerjakan pengguna**; baris W di tabel ini adalah daftar pekerjaannya, bukan tugas teman database. Teman database mengerjakan baris D saja.

| # | Tugas | Selesai bila |
|---|---|---|
| D1 | Buat salinan atau cabang database sebelum apa pun diubah | ada cadangan yang bisa dipulihkan |
| D2 | Cek versi PostgreSQL di Supabase. Kunci tamu gabungan dengan `ON DELETE SET NULL (event_id)` butuh versi 15 atau lebih | versi tercatat; bila di bawah 15, tulis alternatifnya |
| D3 | Jalankan SQL 4a dan 4b di salinan, bandingkan dengan skema asli (skema uji adalah perkiraan). Periksa batasan `status`, kebijakan RLS, dan fungsi yang memakai kolom yang dibuang | SQL jalan tanpa galat dan aplikasi lama masih bisa membaca `status` |
| D4 | Beri izin baca pada `v_alerts` dan `v_alert_gas` untuk peran yang dipakai aplikasi, dan pastikan `device_state` tetap bisa dipakai untuk realtime | aplikasi bisa `select` dari `v_alerts` |
| D5 | Tutup dua peringatan lama (`7b1b3c7d`, `d6dc1da2`), dan putuskan data uji: data `AEROS_DEMO_01` dan peringatan dari uji ambang 700/800 dihapus atau ditandai | tidak ada peringatan terbuka yang tidak sebenarnya aktif |
| D6a | Jalankan SQL 4a di database asli (utuh, sekali) | kolom baru dan view ada; worker lama masih jalan |
| D6b | Setelah worker baru berjalan: matikan ESP, jalankan SQL 4b, ubah `WRITE_STATUS_COLUMN=false`, nyalakan ESP | `status` bertipe turunan, `actuator_logs` hilang, data tetap masuk |
| D7 | Jadwalkan hapus bacaan lebih dari 7 hari yang `event_id`-nya kosong, **setelah** D6b | tugas terjadwal berjalan dan peringatan tetap utuh |
| W1 | Worker: terima pesan versi 3 dan versi 4 (kontrak dan contoh uji di rancangan worker bagian 2). Versi 4 menandatangani `r4\|device_id\|nonce\|timestamp\|time_valid\|co_ppm\|co2_ppm\|co_peak_ppm\|co2_peak_ppm\|co_peak_second\|co2_peak_second\|co_level\|co2_level\|buzzer_state\|window_status\|event_id\|demo` (`status` tidak dikirim lagi) | pesan v3 dan v4 lolos pemeriksaan tanda tangan |
| W2 | Worker: saat ada `event_id`, **buat baris `alert_logs` dulu, baru simpan bacaan**. Tulis `co_level`, `co2_level`, `buzzer_state`, `event_id` | bacaan tersimpan dengan `event_id` yang menunjuk peringatan |
| W3 | Worker: `device_state.status` = tingkat tertinggi dari kedua gas; `alert_logs.alert_type` diisi tingkat tertinggi episode (sementara, demi aplikasi lama) dan naik ke `bahaya` bila status naik | peringatan yang naik dari waspada ke bahaya tercatat `bahaya` |
| W5 | Worker: variabel `WRITE_STATUS_COLUMN` (bawaan benar) supaya masih menulis `status` sebelum D6b | worker jalan di database sebelum dan sesudah D6b |
| W4 | Worker: buang "Saya Tahu": `actuatorService.js`, `realtimeAckService.js`, langganan `cmd/ack` dan `command/ack`, pengecekan 15 detik, dan semua tulisan ke `ack_driver`, `ack_at` | `npm test` lulus dan worker tidak lagi menyentuh `actuator_logs` |

## Teman software (aplikasi)

| # | Tugas | Selesai bila |
|---|---|---|
| S1 | Buang tombol dan halaman "Saya Tahu", dan kode yang membaca `actuator_logs`, `ack_driver`, `ack_at`, `acknowledged_at` | tidak ada lagi tombol atau pembacaan itu di aplikasi |
| S2 | Riwayat peringatan dibaca dari `v_alerts`: `tingkat`, `gas` (larik), `created_at`, `resolved_at` | satu peringatan tampil dengan tingkat tertinggi dan gasnya |
| S3 | Notifikasi menampilkan tingkat dan gas, mis. "BAHAYA: CO2 4025 ppm". Sampai ESP versi 4 terpasang, tampilkan nilai `last_co_ppm` dan `last_co2_ppm` bersama tingkat | notifikasi memuat tingkat dan gas |
| S4 | Jangan menulis ambang tetap di aplikasi. Tingkat berasal dari ESP; ambang akan diganti setelah pengembangan | tidak ada angka ambang di kode aplikasi |
| S5 | Keadaan sekarang dari `device_state`. Anggap offline bila `connection_status` = `offline` atau `updated_at` lebih dari 30 detik; jangan menampilkan "aman" saat offline | perangkat mati tidak tampil aman |
| S6 | Tampilkan "CO: estimasi, bisa berasal dari gas lain" dan "perangkat offline bukan berarti aman" | teks ada di layar yang relevan |
| S7 | Setelah D6b dan W3 selesai, pindah dari `alert_type` ke `tingkat` dan kabari agar kolom `alert_type` bisa dibuang | aplikasi tidak lagi membaca `alert_type` |

## Pengguna (ESP)

| # | Tugas | Catatan |
|---|---|---|
| E1 | `SensorSnapshot` ditambah `coLevel`; telemetri versi 4 mengirim `co_level` dan `co2_level` dan membuang `status` | mengubah `main.cpp` dan `sensorBridge.cpp`: perlu izin eksplisit |
| E2 | Perbaiki: CO waspada kini terkirim sebagai `bahaya` karena `coAlarm` menyala untuk waspada juga | ikut E1 |
| E3 | Putuskan status CO `LUAR` dipetakan ke waspada (usulan) | keputusan |
| E4 | Unggah dan uji dengan worker baru: satu peringatan CO2 dan satu CO muncul benar di `v_alerts` | setelah D6b dan W1 sampai W3; buktikan juga contoh tanda tangan r4 di rancangan worker bagian 2 |
| E5 | Commit firmware v2.2 dan v2.2.1, dan `firmware-v2-c3/` | belum di-commit |

## Keputusan yang masih perlu disepakati

| Keputusan | Pilihan |
|---|---|
| Siapa memegang worker | **diputuskan: pengguna** |
| Data uji | dihapus atau ditandai |
| Waktu membuang `alert_type` | setelah aplikasi pindah ke `v_alerts` |
| Peringatan saat offline | diterima tidak tercatat (mode online-only), atau antrean peringatan di ESP |
| Ambang final (2500 dan 4000 untuk CO2) | setelah pengembangan selesai |
