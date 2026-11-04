# Rancangan Worker untuk Database MVP

Versi 3 November 2026. Menyesuaikan worker (`worker/`, Node.js, HiveMQ ke Supabase) dengan [rancangan-database-mvp.md](rancangan-database-mvp.md). Berisi rancangan dan rencana uji. **Status 3 November 2026: langkah kode 1 sampai 6 bagian 10 sudah dikerjakan di `worker/`** (36 uji lulus; urutan tulis juga dicoba pada PostgreSQL 17 lokal sebelum dan sesudah SQL 4b). Belum dilakukan: langkah 7 (uji dengan ESP pada salinan database) dan 8 (rilis), karena menunggu database 4a/4b dan aplikasi selesai. Pengerja: pengguna. Semua keputusan terbuka sudah diputuskan (bagian 9). Dasar: kode worker yang ada (`mqtt-worker.js`, `sensorDataHandler.js`, `telemetryStateService.js`, `securityService.js`, `stateService.js`, `actuatorService.js`) dan empat berkas uji di `worker/test/`.

## 1. Yang berubah dan yang tidak

| Berubah | Tidak berubah |
|---|---|
| Format pesan telemetri: versi 4 membawa `co_level` dan `co2_level`, tidak lagi `status` | Koneksi HiveMQ TLS, langganan `aeros/+/telemetry` dan `aeros/+/status` |
| Urutan tulis: peringatan dulu, bacaan kemudian | Pemeriksaan HMAC, `nonce`, `device_id`, jendela waktu, dan batas nilai |
| Tabel yang ditulis: `sensor_readings` (kolom baru), `alert_logs`, `device_state` | ACK bertanda tangan setelah bacaan benar-benar tersimpan |
| `alert_type` dinaikkan ke `bahaya` saat tingkat naik (sementara) | Penutupan peringatan lama saat episode baru atau kembali normal |
| Dibuang: semua kode "Saya Tahu" | Pemetaan kehadiran (`ONLINE` dan `OFFLINE`) ke `device_state` |

## 2. Kontrak pesan versi 4

Dikirim ESP ke `aeros/<device_id>/telemetry` tiap 5 detik. Versi 3 diterima selama masa transisi (bagian 6).

| Field | Aturan |
|---|---|
| `version` | `4` |
| `device_id`, `nonce`, `timestamp`, `time_valid`, `demo` | sama dengan versi 3 |
| `co_ppm`, `co2_ppm` | bilangan bulat 0 sampai 100000 |
| `co_peak_ppm`, `co2_peak_ppm`, `co_peak_second`, `co2_peak_second` | sama dengan versi 3 (puncak tidak kurang dari nilai sekarang; detik 1 sampai 5) |
| `co_level`, `co2_level` | **baru:** bilangan bulat 0 (normal), 1 (waspada), 2 (bahaya) |
| `status` | **dibuang** dari pesan; worker menghitung `status` = nama tingkat tertinggi dari kedua gas |
| `buzzer_state`, `window_status`, `event_id` | sama dengan versi 3 |
| `signature` | HMAC-SHA256 hex dari string kanonik di bawah |

String kanonik (tiap bagian dipisah `|`):

```
r4|device_id|nonce|timestamp|time_valid|co_ppm|co2_ppm|co_peak_ppm|co2_peak_ppm|co_peak_second|co2_peak_second|co_level|co2_level|buzzer_state|window_status|event_id|demo
```

`time_valid` dan `demo` ditulis 1 atau 0; `window_status` null ditulis `-`; `event_id` null ditulis `-`. Ini sama dengan `r3`, tetapi `co_level|co2_level` menggantikan `status`.

Aturan keselarasan (diperiksa setelah `status` dihitung): `status` bukan `normal` wajib punya `event_id`; `status` normal tidak boleh punya `event_id`; `buzzer_state` = `on` wajib `status` bukan `normal`.

**Contoh uji kontrak** (rahasia uji 34 byte `uji-HMAC-secret-uji-HMAC-secret-01`, bukan rahasia asli):

```
r4|AEROS_01|0123456789abcdef0123456789abcdef|1793000000|1|12|950|15|962|2|4|0|1|on|0|216b0b86-d596-4c56-9ae0-53394d389025|0
HMAC = 02fc8cb02d9ccde1854f18fd7ba33df4b36db52fbc56ee4bf5df1e8bf18c2418
```

ESP dan worker harus menghasilkan string dan tanda tangan yang sama untuk contoh ini; ESP boleh membuktikannya dengan potongan kode kecil sebelum diunggah.

## 3. Alur satu pesan

```
terima pesan telemetri
  verifikasi: versi, bentuk, HMAC, jendela waktu, aturan keselarasan      -> gagal: buang, tanpa ACK
  p.status = nama tingkat tertinggi (co_level, co2_level)
  periksa perangkat aktif                                                  -> gagal: buang
  bila event_id ada:  pastikan_peringatan(p)                               -> gagal: berhenti, tanpa ACK
  simpan bacaan (sensor_readings, termasuk event_id dan tingkat)           -> gagal: berhenti, tanpa ACK
  salin keadaan (device_state, alert_type, tutup peringatan lama)          -> gagal: catat saja, tetap ACK
  kirim ACK bertanda tangan
```

`pastikan_peringatan(p)`: sisipkan baris `alert_logs` (`id` = `event_id`, `device_id`, `alert_type` = tingkat saat ini, `created_at` tidak diisi: database mengisinya dengan jam worker, `now()`). Bila `id` sudah ada, itu pesan ulang yang sah, bukan galat; bila milik perangkat lain, tolak.

Urutan ini wajib karena kunci tamu gabungan `(event_id, device_id)` di `sensor_readings` menuntut peringatan sudah ada saat bacaan disimpan.

### Kegagalan dan akibatnya

| Kejadian | Akibat | Pemulihan |
|---|---|---|
| Menyimpan peringatan gagal | bacaan tidak disimpan, tidak ada ACK | ESP mengirim ulang (penyangga 4 data, umur maksimum 30 detik) |
| Menyimpan bacaan gagal | tidak ada ACK | sama |
| Pesan ganda (`nonce` sama) | dibuktikan ada di database, lalu di-ACK | tidak ada tulisan ganda |
| Menyalin keadaan gagal | bacaan sudah tersimpan, ACK tetap dikirim | pesan berikutnya dengan `event_id` yang sama memperbaikinya |
| `event_id` milik perangkat lain | ditolak, tanpa ACK | dicatat di log |
| Wi-Fi putus lebih dari 30 detik | peringatan di periode itu tidak tercatat | **batasan yang diterima** (tanpa mode offline) |

## 4. Perubahan per berkas

| Berkas | Perubahan |
|---|---|
| `src/services/securityService.js` | `verifyReading` menerima **hanya versi 3 dan 4** (versi 2 dibuang); versi 4 memeriksa `co_level` dan `co2_level` dan menghitung `status`; versi 3 ditolak bila `ACCEPT_V3=false`; `canonicalReading` menambah `r4` dan membuang cabang `r2`. Buang `signedCommand`, `signedWindowCommand`, `verifyCommandAck`. **`signedDataAck` (`dataack2`) tidak diubah.** |
| `src/handlers/sensorDataHandler.js` | tambah `pastikanPeringatan` sebelum `persistReading`; `persistReading` menulis `co_level`, `co2_level`, `buzzer_state`, `event_id`; `status` hanya ditulis bila `WRITE_STATUS_COLUMN=true` (bagian 7); ACK selalu ke `/telemetry/ack` (cabang `/data/ack` dibuang). |
| `src/services/telemetryStateService.js` | `device_state.status` dari tingkat tertinggi; naikkan `alert_logs.alert_type` ke `bahaya` (`update ... where id = ? and alert_type <> 'bahaya'`) bila ada tingkat 2; **hentikan** penulisan `ack_driver` dan `ack_at`; buang pembuatan peringatan dari sini (pindah ke `pastikanPeringatan`). |
| `mqtt-worker.js` | buang impor dan pemakaian `actuatorService`, `realtimeAckService`; buang langganan `aeros/data`, `aeros/+/command/ack`, dan `aeros/+/cmd/ack` serta penangannya; buang pengecekan 15 detik. Tinggal `aeros/+/telemetry` dan `aeros/+/status`. |
| `src/services/actuatorService.js`, `src/services/realtimeAckService.js` | **dihapus** |
| `src/services/stateService.js`, `deviceRegistry.js`, `config/*` | tidak berubah |
| `cek-database.js` | periksa kolom baru (`co_level`, `co2_level`, `buzzer_state`, `event_id`), bacaan `v_alerts`; buang pemeriksaan `actuator_logs` |
| `test-publish.js` | kirim pesan versi 4 |
| `test/security.test.js`, `test/sensor-handler.test.js` | pindahkan pesan uji dari versi 2 ke versi 3 dan 4 |
| `sql/` | tambah dua berkas yang isinya sama dengan bagian 4a dan 4b rancangan database (satu sumber: salinan, bukan versi baru) |

Bacaan versi 2 dan topik `aeros/data` dibuang: firmware di repo ini mengirim bacaan versi 3 (`main.cpp`), jadi tidak ada pengirim versi 2. **Jangan** menyentuh ACK data bertanda `dataack2` (juga bernomor versi 2): ESP masih mengharapkannya.

### Pengaturan lewat variabel lingkungan

| Variabel | Bawaan | Fungsi |
|---|---|---|
| `WRITE_STATUS_COLUMN` | `false` (diubah 3 Nov setelah galat di Railway) | `true` membuat worker menulis kolom `status`; hanya perlu untuk database sebelum SQL 4b. Nilai dibaca tanpa peka huruf dan spasi. |
| `ACCEPT_V3` | `true` | menerima pesan versi 3. Jadi `false` di langkah terakhir, setelah ESP versi 4 terpasang. |

## 5. Aturan tingkat dan `alert_type`

- Tingkat peringatan = angka terbesar yang pernah muncul di `co_level` atau `co2_level` untuk `event_id` itu. Aplikasi membacanya dari `v_alerts`.
- `alert_logs.alert_type` hanya ada demi aplikasi lama: diisi saat peringatan dibuat, dan dinaikkan satu arah (waspada ke bahaya), tidak pernah turun. Dibuang setelah aplikasi memakai `v_alerts.tingkat`.
- `device_state.status` selalu nama tingkat tertinggi saat ini, bukan tingkat tertinggi episode.

## 6. Pesan versi 3 selama transisi

Versi 3 tidak membawa jenis gas. Pemetaan sementara: `co2_level` = tingkat dari `status`, `co_level` = 0. Ini **bisa salah** bila peringatan sebenarnya dari CO (firmware v2.2 sampai v2.3 masih mengirim versi 3, dan di sana CO waspada terkirim sebagai bahaya). Jadi pemetaan hanya untuk masa transisi singkat: setelah ESP versi 4 terpasang dan terbukti, `ACCEPT_V3` diubah menjadi `false` sehingga pesan versi 3 ditolak dan dicatat di log (diputuskan).

## 7. Urutan rilis

| Langkah | Tindakan | Catatan |
|---|---|---|
| 1 | Database bagian 4a | tidak merusak worker lama |
| 2 | Pasang worker baru dengan `WRITE_STATUS_COLUMN=true` | hanya untuk database yang belum 4b: `status` masih kolom biasa; menerima versi 3 dan 4 |
| 3 | Uji dengan ESP lama: satu peringatan lewat versi 3 muncul di `v_alerts` | |
| 4 | **Matikan ESP**, jalankan database bagian 4b, jadikan `WRITE_STATUS_COLUMN=false` (atau hapus variabelnya: bawaan), nyalakan ESP | 4b merusak worker lama: setelahnya menulis `status` ditolak ("cannot insert a non-DEFAULT value"), `ack_driver` hilang, dan `actuator_logs` hilang. Ini sudah diuji di PostgreSQL lokal. |
| 5 | ESP versi 4 | |
| 6 | Aplikasi pindah ke `v_alerts`; `ACCEPT_V3=false`; buang `alert_type` | langkah terakhir; bila ada ESP yang belum diperbarui, ia berhenti menyimpan data |

Pemulihan bila gagal di langkah 4: bagian 4b satu transaksi sehingga tidak berubah sebagian; kembalikan `WRITE_STATUS_COLUMN=true`. (Pelajaran 3 Nov: bawaan semula `true` membuat Railway menolak semua bacaan setelah 4b karena variabel lupa diisi; bawaan sekarang `false`.) Bagian 4b yang sudah berhasil tidak bisa dibatalkan tanpa cadangan (D1 di [tugas-database-mvp.md](../tugas/tugas-database-mvp.md)).

## 8. Rencana uji

Uji memakai `node --test` dengan database tiruan seperti berkas uji yang ada.

| Berkas | Uji baru atau berubah |
|---|---|
| `security.test.js` | contoh r4 di bagian 2 lolos; mengubah `co_level` atau `co2_level` menolak; tingkat 3 ditolak; `status` dihitung dari tingkat; versi 3 tetap lolos dan dipetakan ke `co2_level`; `ACCEPT_V3=false` menolak versi 3; versi 2 ditolak |
| `sensor-handler.test.js` | baris bacaan memuat `co_level`, `co2_level`, `buzzer_state`, `event_id`; **peringatan disisipkan sebelum bacaan** (urutan panggilan); peringatan gagal berarti tidak ada ACK; `WRITE_STATUS_COLUMN=false` berarti `status` tidak ikut ditulis; ACK ke `/telemetry/ack` untuk versi 4 |
| `telemetry-state.test.js` | tingkat naik dari 1 ke 2 menaikkan `alert_type`; `device_state.status` dari tingkat tertinggi; tidak ada `ack_driver` atau `ack_at` di tulisan; peringatan lama tetap tidak dibuka ulang |
| `actuator-v3.test.js` | **dihapus** bersama `actuatorService.js` |
| uji kontrak | satu berkas yang menghitung contoh bagian 2 dan membandingkan dengan nilai di dokumen |
| uji ujung ke ujung | ESP asli: satu peringatan CO2 dan satu CO (bila memungkinkan, dengan perintah simulasi) muncul di `v_alerts` dengan gas dan tingkat yang benar; periksa `sensor_readings.event_id` terisi |

## 9. Keputusan (3 November 2026)

| Keputusan | Hasil |
|---|---|
| `created_at` peringatan | **jam worker** (tidak diisi, database memakai `now()`) |
| Bacaan versi 2 dan topik `aeros/data` | **dibuang** (ACK `dataack2` tetap) |
| Pesan versi 3 setelah ESP versi 4 terpasang | **ditolak** lewat `ACCEPT_V3=false`, di langkah terakhir |
| Pengerja worker | **pengguna** |

## 10. Rencana implementasi (setelah database selesai dirapikan)

### Prasyarat

| Hal | Bukti selesai |
|---|---|
| Salinan database sudah menjalankan 4a dan 4b, dan data uji dibersihkan | tugas D1 sampai D5 selesai (lihat [tugas-database-mvp.md](../tugas/tugas-database-mvp.md)) |
| Versi PostgreSQL di Supabase 15 atau lebih | D2 |
| `.env` worker menunjuk ke **salinan**, bukan database asli, selama uji | catatan di berkas lokal |

### Langkah kode (urut; tiap langkah diakhiri `npm test` hijau)

| # | Pekerjaan | Uji yang harus lulus |
|---|---|---|
| 1 | `securityService.js`: tingkat, `r4`, versi 2 dibuang, `ACCEPT_V3` | `security.test.js` (contoh r4 bagian 2, tingkat 3 ditolak, versi 2 ditolak) |
| 2 | `sensorDataHandler.js`: `pastikanPeringatan`, kolom baru, `WRITE_STATUS_COLUMN`, ACK `/telemetry/ack` | `sensor-handler.test.js` (urutan peringatan sebelum bacaan, tanpa ACK bila peringatan gagal) |
| 3 | `telemetryStateService.js`: `status` dari tingkat, naikkan `alert_type`, buang `ack_*` dan pembuatan peringatan | `telemetry-state.test.js` |
| 4 | `mqtt-worker.js`; hapus `actuatorService.js`, `realtimeAckService.js`, `actuator-v3.test.js` | `npm test` seluruhnya |
| 5 | `cek-database.js`, `test-publish.js`, salinan SQL ke `sql/` | `node cek-database.js` semua OK pada salinan |
| 6 | Uji kontrak r4 | string dan HMAC sama dengan contoh bagian 2 |
| 7 | Uji ujung ke ujung dengan ESP lama (v3) pada salinan | peringatan muncul di `v_alerts` |
| 8 | Rilis sesuai bagian 7 | langkah 1 sampai 6 di sana |

### Sketsa kode (gaya yang sama dengan kode yang ada)

`securityService.js`, di `verifyReading`:

```js
const LEVEL_NAMES = ['normal', 'waspada', 'bahaya'];

if (![3, 4].includes(p.version)) throw new Error('Versi atau identitas perangkat tidak valid');
if (p.version === 4) {
  for (const name of ['co_level', 'co2_level']) {
    if (!Number.isInteger(p[name]) || p[name] < 0 || p[name] > 2) throw new Error(`${name} tidak valid`);
  }
  p.status = LEVEL_NAMES[Math.max(p.co_level, p.co2_level)];   // status tidak dikirim; dihitung di sini
} else {
  if (process.env.ACCEPT_V3 === 'false') throw new Error('Versi 3 ditolak (ACCEPT_V3=false)');
  if (!LEVEL_NAMES.includes(p.status)) throw new Error('Status gas tidak valid');
  p.co_level = 0;                                 // versi 3 tidak membawa jenis gas: dianggap CO2
  p.co2_level = LEVEL_NAMES.indexOf(p.status);
}
// aturan keselarasan, jendela waktu, dan HMAC tetap, tetapi dijalankan sesudah blok ini
```

`sensorDataHandler.js`:

```js
async function pastikanPeringatan(p) {
  if (!p.event_id) return;
  const { error } = await supabase.from('alert_logs').insert({
    id: p.event_id, device_id: p.device_id, alert_type: p.status,   // created_at: bawaan database (jam worker)
  });
  if (!error) return;
  if (error.code !== '23505') throw new Error('INSERT alert_logs: ' + error.message);
  const found = await supabase.from('alert_logs').select('device_id').eq('id', p.event_id).maybeSingle();
  if (found.error || !found.data) throw new Error('Peringatan duplikat belum dapat dibuktikan');
  if (found.data.device_id !== p.device_id) throw new Error('event_id milik perangkat lain');
}

// di persistReading, tambahan pada row:
Object.assign(row, { co_level: p.co_level, co2_level: p.co2_level, buzzer_state: p.buzzer_state, event_id: p.event_id });
if ((process.env.WRITE_STATUS_COLUMN || '').trim().toLowerCase() === 'true') row.status = p.status;

// di handleSensorMessage:  assertActiveDevice -> pastikanPeringatan -> persistReading -> mirror -> ACK
```

`telemetryStateService.js`, menaikkan `alert_type`:

```js
if (p.event_id && p.status === 'bahaya') {
  await supabase.from('alert_logs').update({ alert_type: 'bahaya' })
    .eq('id', p.event_id).neq('alert_type', 'bahaya');
}
```

### Selesai bila

- `npm test` hijau dan tidak ada lagi acuan ke `actuator_logs`, `ack_driver`, `ack_at`, atau `acknowledged_at` di kode worker.
- Satu peringatan CO2 dari ESP asli muncul di `v_alerts` dengan tingkat dan gas yang benar, dan `sensor_readings.event_id` terisi pada bacaannya.
- Worker jalan di database sebelum dan sesudah SQL 4b dengan `WRITE_STATUS_COLUMN` yang sesuai.
