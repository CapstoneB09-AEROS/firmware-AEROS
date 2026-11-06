# Firmware v3.1 (sensor CO MQ-7)

Salinan firmware-v2 terbaru dengan **sumber sensor diganti**: MQ-7 (modul 4 pin, AO lewat pembagi 10k/20k ke GPIO34) menggantikan MiCS + ADS1115, dan CO2 dinonaktifkan (tanpa MH-Z19C). Logika, ambang, jendela, Wi-Fi portal, MQTT, dan HMAC **sama dengan v2**:

- `sensorBridge.h`: identik dengan firmware-v2. `main.cpp`: identik kecuali dua baris: jeda pencarian Wi-Fi ulang 5 menit (`WIFI_RETRY_PAUSE_MS` 300000, v2: 30000) dan satu baris log yang menyebut jeda itu.
- `sensorBridge.cpp`: sama, ditambah satu aturan: tanpa CO2, data TIDAK dikirim selama CO WARMUP, KALIBRASI, ERR, atau GANGGUAN (nol tidak boleh terbaca "udara aman").
- `sensorOriginal.inl`: aturan CO (waspada 35 ppm selama 30 detik, bahaya 87 ppm, uji arah 30 detik, selesai di bawah 30 ppm selama 60 detik), siklus jendela (GPIO26 turun, GPIO18 naik), pola bunyi, dan LCD tidak diubah. Yang berubah: pembacaan AO MQ-7 (`bacaMics`), rumus ppm (bentuk sama dengan MiCS: `Rs/R0 = A x ppm^-BETA`, A = 0,751, BETA = 0,659, diturunkan dari kurva datasheet `ppm = 99,042 x (Rs/R0ds)^-1,518` dengan R0ds = Rs udara bersih / 27,5), **R0 = Rs udara bersih** seperti MiCS (bawaan 220 kOhm, estimasi; ukur ulang dengan perintah `r`), R0 disimpan di NVS namespace `mq7` (terpisah dari R0 MiCS), CO2 mati (status OFF, nilai 0).

Pin: AO GPIO34, buzzer GPIO27, relay turun GPIO26, relay naik GPIO18, LCD I2C GPIO21/22, tombol Wi-Fi GPIO32. Perangkat: `AEROS_01` (data asli, `demo = false`).

Setelah menyala: pemanasan 180 detik (tanpa kalibrasi otomatis, sama seperti rencana MiCS). Ukur R0 di papan akhir dengan `r` (120 detik di udara bersih); `d` kembali ke R0 bawaan. Selama pemanasan dan kalibrasi tidak ada telemetri.

Ganti Wi-Fi: tahan GPIO32 ke GND 5 detik (portal `AEROS-Setup`, 192.168.4.1).
