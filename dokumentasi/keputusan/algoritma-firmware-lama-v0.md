# Algoritma Lama (Rencana Awal dan Alur Kode v0)

Disimpan **apa adanya** dari dokumen rencana desain 25 Oktober 2026 (bagian 3.4 dan 3.5), karena pseudocode ini sengaja tidak diubah selama firmware baru dirancang. Alur yang berlaku untuk firmware baru ada di [algoritma-firmware.md](algoritma-firmware.md). Kode v0: [src/main.cpp](../../src/main.cpp) (353 baris, 23 Oktober 2026).

## 3.4 Alur rencana (pseudocode)

```
SETIAP 1 DETIK:
  1. Baca CO2 dari MH-Z19C. Baca tegangan MiCS dari ADS1115.

  2. Cek data:
       CO2 gagal atau checksum salah       -> data CO2 tidak valid
       tegangan mentok atau tidak masuk akal -> data CO tidak valid
       nilai 410 atau 500 setelah sensor mulai ulang -> dianggap pemanasan, bukan "aman"

  3. Hitung:
       Rs dari tegangan -> filter SMA genap (4 sampai 6) -> rasio Rs/R0 -> ppm CO (estimasi)
       CO2 = angka dari sensor (tanpa filter tambahan)

  4. Kalau ada data tidak valid -> status GANGGUAN, jendela tidak digerakkan otomatis.
  5. Kalau masih masa pemanasan -> tidak ada alarm.

  6. ATURAN CO (prioritas tertinggi):
       kalau CO >= 35 selama 30 detik, atau CO >= batas bahaya, dan aturan CO belum aktif:
            aktifkan aturan CO: bunyi, buka jendela, mulai waktu uji arah
       kalau aturan CO aktif dan waktu uji selesai:
            kalau CO naik lagi melebihi kriteria -> sumber luar: tutup jendela, kunci (tidak menguji ulang)
            kalau CO turun                       -> sumber dalam: jendela tetap terbuka
       kalau aturan CO aktif dan CO < 30 selama 60 detik berturut-turut:
            matikan aturan CO, bunyi berhenti, jendela kembali tertutup
       selama aturan CO aktif: aturan CO2 DIABAIKAN

  7. ATURAN CO2 (hanya kalau aturan CO tidak aktif):
       CO2 >= 2500 selama 3 bacaan valid -> bunyi singkat satu kali + peringatan di aplikasi
       CO2 >= 4000 selama 3 bacaan valid -> bunyi + buka jendela (bukaan sesuai mobil)
       CO2 <  2400 selama 60 detik berturut-turut -> tutup jendela, hentikan bunyi

  8. Tampilkan di layar. Kirim data tiap 5 detik, atau segera saat status berubah. Catat log.

  9. Tombol "Saya Tahu" mematikan bunyi. Bunyi juga mati sendiri setelah 5 menit.
```

## 3.5 Alur kode yang berjalan sekarang (pseudocode)

Tanda ⚠ menandai bagian yang berbeda dari rencana. Kode: [src/main.cpp](../../src/main.cpp), 353 baris, versi 23 Oktober 2026.

```
SAAT DINYALAKAN:
  buka serial 115200, mulai sensor CO2 (UART 9600), nyalakan I2C, cek LCD
  cek ADS1115; kalau tidak ada: tampilkan error dan BERHENTI SELAMANYA
  ambil R0 dari memori (bawaan 1730 kOhm)
  ⚠ kalibrasi otomatis CO2 aktif (DISABLE_ABC = false)

SETIAP 1 DETIK:
  1. Cek perintah keyboard: 'r' = ukur R0 (120 detik di udara bersih), 'd' = R0 kembali ke bawaan
  2. Baca CO2 (9 byte, tunggu maksimal 0,5 detik, cek header dan checksum)
  3. Baca tegangan MiCS: rata-rata 16 pembacaan, atur gain otomatis (1.024 / 2.048 / 4.096 V)
        ⚠ saat saturasi data detik itu dibuang, tidak dibaca ulang
  4. Rs = RL x (VCC - V) / V  (RL = 9970, VCC = 4,64)
        ⚠ Rs dihaluskan EMA 0,2 (belum diputuskan)
        rasio = Rs / R0; ppm = (3,7 / rasio) ^ (1 / 0,856), dan 0 bila rasio >= 0,5
        ⚠ angka 3,7 dan 0,856 hasil membaca grafik datasheet
  5. Status CO: kalibrasi / pemanasan 300 detik / alarm
        alarm nyala: ppm >= 35 selama 10 detik berturut-turut
        alarm mati : ppm < 25 selama 30 detik berturut-turut
        ⚠ buzzer tetap bunyi selama 30 detik pemulihan walau ppm 0
  6. Status CO2: < 1000 BAIK, < 2000 SEDANG, < 5000 TINGGI, >= 5000 BAHAYA
        ⚠ tidak ada tingkat 2500 dan 4000, dan CO2 tidak membunyikan buzzer
        ⚠ pemanasan CO2 dihitung dari boot, tidak diulang kalau sensor mati
  7. Buzzer hanya untuk alarm CO. Tampilkan di LCD. Cetak satu baris CSV ke serial.
  8. Tunggu sampai genap 1 detik.
```

Bagian yang belum ada sama sekali di kode: aturan prioritas, uji arah, penggerak jendela, tingkat CO2 2500 dan 4000, mode simulasi, filter SMA 4, penanganan gangguan sensor, Wi-Fi dan MQTT.
