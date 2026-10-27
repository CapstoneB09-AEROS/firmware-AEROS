# Laporan Uji 3: Ruang Pertemuan 13 Orang, 26 Oktober 2026 sore (ESP baru)

ESP baru (CH9102), firmware lama (v0). Hasil mentah: [hasil-uji-ruang-2026-10-26.txt](../../analisis/hasil/hasil-uji-ruang-2026-10-26.txt).

## Kondisi ruangan (dari catatan)

| Hal | Isi |
|---|---|
| Ukuran | 4,6 m × 6,7 m, tinggi paling 2,5 m |
| Volume | sekitar **77 m³** (4,6 × 6,7 × 2,5 = 77,05 m³) |
| Penghuni | **13 orang** (sekitar 5,9 m³ per orang) |
| AC | 2 unit |
| Pintu | Semua tertutup |
| Perangkat | ESP baru (CH9102), firmware lama (v0, EMA 0,2), kode terunggah 26 Okt 17:08 |

Dari log: mulai **17:15:16**, berkas `device-monitor-261026-171515.log`, direkam sampai sekitar 18:01. Hasil (analisis/ringkasan-temuan.md bagian 7): siklus Rs yang di ESP lama 7,0 menit menjadi sekitar 11,9 menit di ESP baru, dengan amplitudo sama; CO2 hanya 1116–1549 ppm. Di mobil, ESP baru memberi 7,6 menit (uji 4), jadi periode tidak hanya ditentukan ESP.

Belum diisi (lengkapi dari ingatan): Wi-Fi mati atau menyala ____, posisi alat dan jaraknya dari AC dan orang ____, setelan AC (suhu, arah angin) ____, nama berkas log ____, apakah ada pintu yang dibuka di tengah acara dan jamnya ____.

## Catatan membaca hasilnya
- **Ini bukan kamar udara bersih.** 13 orang menambah CO2, uap air, dan bau napas, jadi Rs dan siklus 7 menit **tidak boleh dibandingkan langsung** dengan log kamar kemarin. Yang dibandingkan hanya noise dan perilaku ESP baru.
- **CO2 bisa naik cepat.** Perkiraan kasar (bukan pengukuran): satu orang duduk menghasilkan sekitar 0,005 L CO2 per detik, jadi 13 orang di 77 m³ tanpa pertukaran udara menaikkan CO2 sekitar 50 ppm per menit. Pertukaran udara sebenarnya (AC, celah pintu) tidak diketahui. Angka sebenarnya diambil dari log.
- **Batas aman:** bila CO2 mendekati 4000, buka pintu. Ruangan penuh orang, bukan ruang uji.
- **Data yang berguna:** laju naik CO2 untuk 13 orang di ruang tertutup (satu kondisi lagi untuk model well-mixed), dan kemampuan sensor membaca CO2 tinggi di ruang nyata.
