# Firmware v3 dummy (ESP murni, data dummy)

Salinan firmware-v2 dengan **satu perbedaan**: sumber data. `src/sensorBridge.cpp` tidak membaca sensor, tetapi memainkan skenario dummy (CO2, CO, gabungan). Tanpa MH-Z19C, MiCS, ADS1115, LCD, buzzer, atau relay; tidak ada pin yang disentuh. Wi-Fi, MQTT, HMAC, dan pesan versi 4 memakai `main.cpp` yang sama.

- `main.cpp`: sama dengan firmware-v2 kecuali `DEVICE_ID = "AEROS_DUMMY_01"`.
- `sensorBridge.h`: sama.
- `sensorOriginal.inl`: tidak dipakai.
- Rencana, skenario, dan hasil yang diharapkan: [dokumentasi/tugas/rencana-simulator-integrasi.md](../dokumentasi/tugas/rencana-simulator-integrasi.md) bagian 6 dan 12.

## Pakai
1. `include/secrets.h` (tidak masuk git): Wi-Fi, HiveMQ pengguna ESP, `HMAC_SECRET` sama dengan worker.
2. `pio run -t upload`, lalu Serial Monitor 115200 dengan "New Line".
3. Tunggu `[BIRTH] ONLINE berhasil dikirim`. Data tidak disimpan saat MQTT putus.
4. Ketik satu karakter lalu Enter: `0` normal (40 detik), `1` CO2, `2` CO, `3` CO dan CO2 bersamaan, `4` CO2 dulu lalu CO, `a` semuanya berurutan (sekitar 34 menit), `s` berhenti sekarang, `h` bantuan.

Tiap skenario (1 sampai 4, sekitar 8,5 menit): normal naik bertahap ke bahaya selama **5 menit**, bahaya sekitar **3 menit** (jendela turun lalu terbuka), lalu turun dan jendela naik. **ESP tidak mengirim data sampai ada perintah, dan berhenti 10 detik setelah skenario selesai.** Detailnya di bagian 6 rencana.

Pesan berlabel `demo = true`: worker menolaknya kecuali `ALLOW_DEMO_READINGS=true`. `AEROS_DUMMY_01` harus terdaftar dan aktif di tabel `devices`.
