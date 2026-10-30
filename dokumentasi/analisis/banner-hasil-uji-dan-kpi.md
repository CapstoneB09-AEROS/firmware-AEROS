# Hasil Uji Lapangan dan Evaluasi KPI (isi x-banner)

Versi 30 Oktober 2026. Ringkasan untuk x-banner. Sumber: [uji 4 Avanza](../pengujian/laporan/uji-4-mobil-avanza-2026-10-26.md) dan [uji 7 Civic](../pengujian/laporan/uji-7-mobil-civic-firmware-v2-2026-10-30.md).

## Uji lapangan: Avanza vs Civic (4 penumpang, jendela tertutup)

| | Avanza (26 Okt) | Civic (30 Okt) |
|---|---|---|
| Sistem | firmware lama, tanpa cloud, jendela dibuka manual | **firmware v2.1, ujung ke ujung sampai database**, jendela dibuka manual |
| Laju naik CO2 | 207–218 ppm/menit | 213–268 ppm/menit |
| Puncak CO2 | 4453 ppm | 4025 ppm |
| Dari 2500 ke 4000 ppm | sekitar 7 menit | sekitar 15 menit |
| Turun setelah jendela dibuka | 4437 → 2384 dalam sekitar 95 detik | 4025 → 2210 dalam 75 detik |
| Alarm | tidak ada | waspada 3 kali, bahaya 1 kali |

Kesimpulan: kabin tertutup dengan 4 orang melewati 2500 ppm dalam beberapa menit di kedua mobil. Laju naiknya hampir sama, sekitar 210–270 ppm/menit. Membuka jendela menurunkan CO2 lebih dari 1500 ppm dalam kurang dari 2 menit.

## Skema sistem

```
MH-Z19C → ESP32 → buzzer · LCD · sinyal jendela (GPIO26)
            │ Wi-Fi
            ▼
   HiveMQ Cloud → worker → Supabase → aplikasi

Aman (< 2500)  →  WASPADA (≥ 2500): 3 bip pendek
               →  BAHAYA (≥ 4000): bip panjang + jendela turun 1,5 detik
               →  kembali aman (< 2500 selama 10 detik): jendela naik 5 detik
```

## Hasil terhadap KPI

| KPI | Target | Hasil | Status |
|---|---|---|---|
| Deteksi CO2 > 2500 | 5 uji | 3 dari 3 lewat 2500 terdeteksi (satu sesi mobil) | Terpenuhi, tetapi baru 3 dari 5 uji |
| Waktu respons buzzer | ≤ 5 detik | berbunyi ≤ 2 detik setelah bacaan pertama melewati ambang | Terpenuhi |
| Waktu respons aktuator | ≤ 10 detik | sinyal jendela 1,3 detik setelah bacaan pertama ≥ 4000 | Terpenuhi (sinyal; gerak fisik belum diukur) |
| Buka panel | hanya saat ambang terlewati | 1 dari 1 saat bahaya; 0 gerakan salah di 3 kali waspada | Terpenuhi |
| Tutup panel | stabil aman ≥ 60 detik | tutup 75 detik setelah bahaya; CO2 bertahan < 2400 sekitar 5 menit | Terpenuhi |
| Data tampil di aplikasi | ≤ 20 detik | sampai database 2,6–4,6 detik; peringatan tercatat 5,9–6,9 detik | Sisi ESP sampai database terpenuhi; tampil di ponsel belum diukur |
| Deteksi CO > 35 ppm | 4 dari 5 uji | CO tidak dipakai di MVP | Tidak masuk MVP |

Catatan: jendela dibuka manual di kedua mobil, jadi gerak fisik jendela otomatis belum terbukti. Anggaran tidak dibahas.
