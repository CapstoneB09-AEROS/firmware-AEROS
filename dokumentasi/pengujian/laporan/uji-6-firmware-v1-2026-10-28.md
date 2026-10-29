# Laporan Uji 6: Firmware v1 di Meja, 28 Oktober 2026 sore

Firmware v1 (mode pengembangan) di board CP2102 (`/dev/cu.usbserial-0001`), ruang terbuka, napas ke sensor untuk menaikkan CO2. Log: `logs/device-monitor-261028-182851.log`. Skrip: [analisis_v1.py](../../analisis/skrip/analisis_v1.py), hasil mentah: [hasil-uji-v1-2026-10-28.txt](../../analisis/hasil/hasil-uji-v1-2026-10-28.txt).

## 1. Sesi
| Sesi | Mulai | Berakhir | Lama | V MiCS (mV) | CO2 (ppm) | Rs halus (kOhm) | Rs/R0 | CO maks |
|---|---|---|---|---|---|---|---|---|
| 1 | 18:28:52 | 18:32:24 (ESP reset) | 371 detik | 8,0-11,7 | 609-1297 | 4148-5503 | 2,40-3,18 | 0 ppm |
| 2 | 18:32:30 | 18:36:43 (log berhenti) | 254 detik | 7,6-12,0 | 688-2913 | 3976-5430 | 2,30-3,14 | 0 ppm |

## 2. Hasil per fungsi
| Fungsi | Hasil |
|---|---|
| Pemanasan 180 detik | aturan CO dan CO2 aktif pada detik ke-181 di kedua sesi |
| CO2 peringatan (>= 700, 3 bacaan) | berbunyi 3 bip pendek, selesai dalam sekitar 2 detik |
| CO2 tindakan (>= 800, 3 bacaan) | 1 bip panjang 3 detik, pulsa buka 2000 ms di GPIO26 |
| CO2 selesai (< 700 selama 10 detik) | jendela ditutup 92 detik setelah dibuka, pulsa tutup 1000 ms |
| Jeda minimum 30 detik | buka kedua 51 detik setelah tutup, tidak ditunda |
| Peringatan tanpa buka (sesi 2, detik 183-196) | kembali NORMAL tanpa menggerakkan jendela |
| Aturan CO | tidak teruji: ppm CO selalu 0 (lihat temuan 1) |

## 3. Temuan
1. **Rs sekitar 4000-5500 kOhm (rasio 2,3-3,2 terhadap R0 1730 kOhm), V MiCS hanya 8-12 mV.** Di uji lama V sekitar 25-30 mV dan Rs sekitar 1500-2000 kOhm. Dengan R0 1730, ppm CO selalu 0 dan alarm CO tidak mungkin berbunyi. Sensor di board ini perlu R0 sendiri (`r` di udara bersih).
2. **ESP mati dan menyala tiga kali** pada 18:32:25-28 (`POWERON_RESET`, `flash read err`, lalu `RTCWDT_RTC_RESET`), 4 detik setelah pulsa buka kedua. Gejala catu tidak stabil atau kontak longgar.
3. **Keadaan jendela hilang saat reset**: firmware menyala dengan status TERTUTUP walau jendela fisik mungkin sedang terbuka. Belum ditangani (usulan: tutup saat boot, atau simpan keadaan).

## 4. Yang belum diuji
Aturan CO (uji arah dan simulasi `p<ppm>`), perintah `o` dan `c`, penutupan karena lama buka maksimum, "Saya Tahu", dan sinyal TBout dengan LED atau multimeter.

## 5. Penelusuran lanjutan (28-29 Okt malam)
Log tambahan: `logs/device-monitor-261028-185946.log`, `-205315`, `-205435` (format tabel v1.1 dan v1.2; sebagian besar baris berupa deretan nol dari gangguan serial, data sebenarnya hanya 82-368 baris tiap file), `-210219` dan `-223629` (v1.3), serta [alat-uji/uji-gpio26/logs/](../../../alat-uji/uji-gpio26/logs/).

| Temuan | Bukti | Status |
|---|---|---|
| Rs selalu mulai rendah setelah menyala lalu naik sampai sekitar menit ke-5, jadi pemanasan 180 detik hanyalah timer, bukan tanda stabil | sesi 12:41, 16:01, 21:02: Rs awal 300-1900 kΩ, sekitar 4200-4800 kΩ di detik 180, puncak 5700-6200 kΩ di detik 300, lalu turun pelan | `r` hanya boleh dijalankan setelah Rs mendatar (usulan: firmware menolak bila Rs masih berubah) |
| Rs dasar papan CP2102 sekitar 2,5-3 kali uji lama (rasio 2,9 terhadap R0 1730 kΩ); format v0 pun sama | V 8-12 mV (median 9-11,5 mV) pada 28 Okt, 20-43 mV pada 25-26 Okt | tidak berasal dari firmware v1.x |
| Multimeter di A0 membaca 30 mV (catatan pengguna), sedangkan firmware melaporkan sekitar 10 mV | 30 mV setara Rs sekitar 1530 kΩ, normal | dugaan: selisih ground atau catu lemah; belum diukur di GND ADS dan GND MiCS |
| Sensor merespons gas | 21:04:55: V naik ke 1687 mV, Rs turun ke 856 kΩ (rasio 0,495) saat parfum | deteksi berfungsi; ppm baru bermakna setelah R0 benar |
| ESP boot berulang | log 223629 diawali teks sampah; log uji-gpio26 berisi 6393 dan 6582 baris `entry 0x4008059c` sebelum jalan normal; alasan reset `WDT` | penyebab belum diketahui; sejalan dengan dugaan catu |
| LCD menampilkan karakter acak saat pemanasan (dicatu adaptor DC, tanpa log) | foto pengguna | dugaan LCD kehilangan sinkron 4-bit; `lcd.init()` hanya dipanggil sekali (usulan: init ulang berkala) |
| Pulsa jendela | `o` menaikkan GPIO26 selama 2000 ms; waktu turun fisik belum diukur | uji relay di [rencana-uji.md](../rencana-uji.md) bagian 2.1 |
