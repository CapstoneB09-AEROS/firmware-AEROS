# Langkah Integrasi Firmware v2.0 (Komunikasi sampai Database)

Versi 29 Oktober 2026. Proyek ada di [firmware-v2/](../../firmware-v2/): kode komunikasi teman (Wi-Fi, MQTT TLS, antrean offline, tanda tangan HMAC) digabung dengan inti firmware v1.8 (CO2, buzzer, relay jendela turun dan naik). Skema MVP: [mvp-co2.md](../keputusan/mvp-co2.md). Firmware v1.8 di `src/main.cpp` tetap utuh sebagai cadangan.

## Sudah dikerjakan (asisten)
| Hal | Hasil |
|---|---|
| Inti v1.8 menjadi `sensorOriginal.inl` v2.0, dibungkus namespace (tidak bentrok `lcd` dan `prefs`) | terkompilasi, flash 44% dari 3 MB |
| Pembaca CSV tim disesuaikan ke format baru (10 kolom); buzzer GPIO27; `huge_app.csv` | data lolos sampai antrean (`[QUEUE] Simpan`) |
| Inti dimulai **lebih dulu**; konfigurasi atau flash gagal tidak lagi menghentikan alarm | uji: tanpa rahasia, alarm CO2 dan `event_id` tetap jalan |
| **Antrean offline dimatikan** (keputusan 29 Okt): data hanya dikirim saat MQTT tersambung; penyangga kecil di RAM (4 data terbaru, dibuang bila tanpa ACK lebih dari 30 detik) | kirim dan ACK berpasangan tiap 5 detik, ACK sekitar 0,7 detik |
| Data simulasi (`q<ppm>`) diberi `demo = true` | agar tidak tercampur data nyata |
| `window_status`: 0 (atas), 50 (bawah, estimasi), null (bergerak) | perlu disetujui teman software |
| `root_ca.h` berisi ISRG Root X1 | CA publik, bukan rahasia |

## Pemetaan env: apa masuk ke mana
| Nilai di env | Dipakai oleh | Ditaruh di |
|---|---|---|
| Host HiveMQ, username, password MQTT | ESP **dan** worker | ESP: `firmware-v2/include/secrets.h`; worker: `.env` |
| `HMAC_SECRET` | ESP **dan** worker (harus sama) | keduanya |
| Port HiveMQ | ESP tetap 8883 di kode | pastikan sama dengan 8883 |
| File CA | ESP butuh **isinya** (teks sertifikat), bukan alamat file | sudah ada di `root_ca.h` |
| `SUPABASE_URL`, service role atau secret key | **hanya worker** | `.env` worker. **Jangan** di ESP, aplikasi, git, atau chat |
| Kunci publik (anon) Supabase | aplikasi Flutter | milik teman software |
| `MAX_OFFLINE_AGE_DAYS`, `MAX_FUTURE_SKEW_SECONDS`, `LIVE_STALENESS_SECONDS`, `COMMAND_RETRY_MS`, `POLL_INTERVAL_MS` | **hanya worker** | `.env` worker; kamu tidak perlu mengubahnya |

Catatan: di baris terakhir yang kamu tempel ada `POLL_INTERVAL_MS=5000huh`. Hapus tulisan `huh` kalau itu ikut tersalin ke `.env`.

## Langkah untuk kamu
1. **Tanya teman backend** (tiga hal):
   - `device_id` yang dipakai ESP adalah `AEROS_01`. Apakah sudah ada dan aktif di tabel `devices`?
   - Apakah worker sedang berjalan, dan dengan `HMAC_SECRET` yang sama?
   - Apakah kolom `co_peak_ppm`, `co2_peak_ppm`, `co_peak_second`, `co2_peak_second` sudah ada di `sensor_readings`?
2. **Isi `firmware-v2/include/secrets.h`** (file lokal, diabaikan git):
```cpp
#pragma once
static const char *MQTT_HOST = "xxxx.s1.eu.hivemq.cloud";  // hostname saja, tanpa mqtts:// dan tanpa :8883
static const char *MQTT_USERNAME = "...";
static const char *MQTT_PASSWORD = "...";
static const char *HMAC_SECRET = "...";           // sama dengan worker, minimal 32 karakter
static const char *CONFIG_AP_PASSWORD = "...";    // 8-63 karakter, karanganmu sendiri (portal Wi-Fi)
static const char *WIFI_SSID = "...";             // hotspot 2,4 GHz
static const char *WIFI_PASSWORD = "...";
```
3. **Cek CA**: jalankan `openssl s_client -connect HOST:8883 -showcerts </dev/null | grep -E " s:| i:"` (ganti HOST). Kalau rantai berakhir di `ISRG Root X1`, `root_ca.h` sudah benar. Kalau tidak, kabari.
4. **Siapkan hotspot ponsel**: pita 2,4 GHz, WPA2, nama tanpa karakter khusus. Ponsel yang sama jangan dipakai sebagai hotspot dan memberi daya ESP.
5. **Unggah dan rekam** (hentikan monitor dulu dengan Ctrl+C):
```bash
cd /Users/maritzavania/Downloads/aeros-sensor/firmware-v2
~/.platformio/penv/bin/pio run -t upload --upload-port /dev/cu.usbserial-5CD20006351
cd ..
~/.platformio/penv/bin/pio device monitor -p /dev/cu.usbserial-5CD20006351 -b 115200 -f time -f log2file -f send_on_enter --echo
```
   Yang harus terlihat berurutan: `[WiFi] CONNECTED`, `[NTP]` selesai, MQTT tersambung (`[BIRTH] ONLINE ...`), lalu `[QUEUE]` dan data terkirim dengan ACK.
6. **Cek database**: di Supabase (editor SQL atau tabel) cari baris terbaru di `sensor_readings` dengan `device_id = 'AEROS_01'`.
7. **Uji alarm sampai database**: napas ke sensor sampai ≥ 800 ppm. Harus muncul baris di `alert_logs` dan `device_state`, relay turun 1,5 detik, lalu naik 5 detik setelah CO2 aman.
8. **Aplikasi**: teman software mengecek data tampil dan tombol "Saya Tahu".

## Bila gagal
| Gejala | Kemungkinan |
|---|---|
| `[CONFIG] Lengkapi secrets.h/root_ca.h` | ada nilai kosong atau `HMAC_SECRET` kurang dari 32 karakter |
| Wi-Fi gagal berulang | hotspot bukan 2,4 GHz, atau kata sandi salah (portal terbuka otomatis) |
| MQTT `state=-2` | host salah atau rantai TLS tidak cocok dengan `root_ca.h` |
| MQTT `state=4` atau `5` | username atau password MQTT salah |
| Pesan terkirim tapi tidak masuk database | `HMAC_SECRET` beda dengan worker, atau `device_id` belum terdaftar |
| ESP reset saat Wi-Fi menyala | catu kurang (Wi-Fi menarik arus lonjakan); pakai USB yang kuat |
