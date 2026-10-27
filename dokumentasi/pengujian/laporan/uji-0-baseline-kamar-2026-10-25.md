# Laporan Uji 0: Baseline Kamar, 25 Oktober 2026

Tujuan: melihat seberapa stabil Rs MiCS dan berapa R0 di udara kamar (menjawab A4, A5, dan D7 di [parameter-dan-sumber.md](../../keputusan/parameter-dan-sumber.md)). Hasil analisis noise dan filter: [analisis/ringkasan-temuan.md](../../analisis/ringkasan-temuan.md) dan [analisis/filter.md](../../analisis/filter.md). Hasil singkat: baseline **tidak stabil** (Rs turun lebih dari 50% dalam sekitar 4 jam), jadi R0 tidak ditetapkan dari data ini; sekitar 95% goyangan Rs berupa pola bergantian 0,5 Hz.

## Temuan dari log serial awal (`.vscode/readme.md`)
Dicatat untuk dibuktikan ulang dengan data baru.
- Tegangan MiCS mencapai 3681 mV saat gas kuat (t=369), melewati sekitar 3,6 V, batas input ADS1115 bila diberi daya 3,3 V.
- `ADC_SATURASI` sesaat di t=367, 368, 377, 384, 386 akibat penggantian gain otomatis.
- Alarm menyala di t=395 dan mati di t=431; selama 30 detik terakhir buzzer tetap bunyi walau ppm sudah 0.
- Sensor CO2 sempat `n/a` di t=115 lalu kembali 410 dan 500 (kemungkinan mulai ulang).
- Rs naik dari 512 kOhm sampai 2296 kOhm dalam sekitar 8 menit (belum stabil).
- Tegangan MiCS bergoyang bolak-balik tiap detik (72 dan 59 mV) pada awal log.
- Ada beberapa detik data hilang dan baris teks terpotong di t sekitar 268-274 dan 366-387.

## Catatan percobaan baseline (udara kamar)

Untuk menjawab A4, A5, D7 (percobaan E1 dan E2).

| Catatan | Isi |
|---|---|
| Tanggal | 25 Oktober 2026 |
| Penanda waktu | Pada `t_s = 3700` jam di komputer menunjukkan sekitar 11:00 WIB (pembacaan dari pengguna) |
| Perkiraan waktu nyala (`t_s = 0`) | sekitar 09:58 WIB (11:00 dikurangi 3700 detik) |
| Kecocokan | Log serial awal (`.vscode/readme.md`) berakhir di `t_s = 517`, sekitar 10:07 WIB, sama dengan waktu terakhir file itu disimpan |
| Lokasi | Kamar, diasumsikan udara bersih (belum dibuktikan dengan alat ukur) |
| Suhu dan kelembapan | Tidak diukur. Diputuskan tidak dikompensasi karena keterbatasan waktu dan pengetahuan. Ini keterbatasan. |
| Kriteria "stabil" | (isi sebelum menganalisis, misalnya perubahan Rs < 2% per jam) |
| Catatan kejadian (parfum, pintu/jendela, orang di kamar, dll.) | (isi sambil jalan) |

Peringatan: `t_s` kembali ke 0 setiap ESP32 mulai ulang (dicabut, ditekan EN, atau port serial dibuka). Catat jam setiap kali itu terjadi.

## Kondisi ruangan, run kedua (mulai dingin, log ke file)

Dicatat oleh pengguna sebelum mencolok sensor, 25 Oktober 2026 (jam mulai: isi saat dicolok).

| Item | Kondisi |
|---|---|
| Sensor sebelumnya | Dicabut sekitar 20 menit supaya dingin |
| Kipas | Menyala, dengan pewangi ruangan (aroma dahlia) terpasang. **Potensi gangguan**: pewangi melepas senyawa yang bisa ikut terbaca MiCS (sensor bereaksi ke banyak gas, bukan hanya CO) |
| Orang | Pengguna sendirian di kamar |
| Jendela dan pintu | Jendela tertutup, pintu kamar terbuka (tersambung ke ruang tengah) |
| Posisi sensor | Di atas meja, di sebelah siku pengguna saat mengetik. Dekat tubuh dan napas pengguna, sehingga CO2 bisa naik |
| Catatan | Run ini tidak bisa dianggap "udara bersih murni" bila pewangi dan kipas tetap menyala. Bandingkan dengan run tanpa pewangi bila ada waktu |
| Jam sensor dicolok (`t_s = 0`) | sekitar 11:39:53 WIB (dihitung dari `t_s = 20` pada 11:40:13) |
| File log | `logs/device-monitor-261025-114013.log`, tiap baris diawali jam. Rekaman mulai di `t_s = 20`, jadi 20 detik pertama tidak terekam |
| Gangguan 1 | 11:53:17 WIB: log sistem macOS mencatat perangkat USB CP2102 terlepas (`Removed`) lalu tersambung lagi 11:53:18. ESP32 mulai ulang (`t_s` kembali ke 0). File log baru: `device-monitor-261025-115319.log`. Run pertama berakhir di `t_s = 803` |
| Gangguan 2 | 11:53:34 WIB: terulang. Terlepas 11:53:34, tersambung 11:53:35. File log baru: `device-monitor-261025-115335.log`. Pengguna tidak menyentuh perangkat |
| Dugaan penyebab | Sambungan USB atau catu daya terputus sesaat (kabel/konektor, breadboard, atau tegangan turun). Belum terbukti. Perlu dicek oleh rekan hardware |
| Dampak | Warm-up MiCS dan MH-Z19C mulai dari awal setiap kejadian. Data sebelum dan sesudah gangguan berada di file berbeda dan tidak boleh disambung sebagai satu run |
| Koreksi kondisi | Pewangi dahlia **dicopot sebelum rekaman dimulai** (keterangan pengguna, 25 Okt 2026). Status kipas belum dicatat |
| Kehadiran pengguna | Tidak di kamar sekitar 12:46–13:00. Di kamar lagi sejak sekitar 13:36. Pada rentang itu CO2 terendah 924 ppm (12:52) dan tertinggi 1116 ppm (13:40) |
| Pengamatan Rs (14:02) | Rs rata-rata turun dari sekitar 2040 kΩ ke sekitar 1460–1540 kΩ dalam sekitar 2 jam. Lereng 60 menit terakhir sekitar −29% per jam dan 30 menit terakhir sekitar −17% per jam, jauh dari kriteria stabil (di bawah 2% per jam). Penurunan tajam sekitar 13:16–13:36 (1792 ke 1491 kΩ) **belum dapat dijelaskan**: pengguna menyatakan tidak ada perubahan di kamar. Pewangi sudah disingkirkan, jadi penyebab yang tersisa adalah suhu atau kelembapan kamar, drift sensor, atau sebab lain. Tidak ada sensor suhu dan kelembapan untuk memisahkannya |
| Akhir rekaman | Dihentikan sekitar 16:05 WIB karena baterai laptop 9%. Sesi `115335`: `t_s` 3 sampai 15071 (sekitar 4 jam 11 menit), 15.064 baris, tanpa mulai ulang, lima celah masing-masing sekitar 1 detik |
| Pengamatan Rs sampai akhir | Rs rata-rata per 15 menit: sekitar 2045 kΩ (11:53), 1508 (13:53), 1466 (14:53), 1332 (15:08), 1111 (15:23), 1014 (15:38), 907 (15:53). Pada 16:04 Rs 832 kΩ, rasio 0,48, ppm CO estimasi 11 ("OK", bukan "OK(<10ppm)"). Penurunan **mempercepat sejak sekitar 15:00** (lereng 60 menit terakhir sekitar −50% per jam). Tidak ada baseline stabil. Penyebab **belum diketahui**: gas pereduksi di kamar (VOC, alkohol, dan lain-lain), suhu atau kelembapan, atau drift. Data ini **tidak boleh dipakai untuk menetapkan R0** |
| Kegiatan pengguna (keterangan 16:07) | Pengguna mandi tanpa pewangi tambahan dan keluar kamar. CO2 di bawah 800 ppm dari 15:18:52 sampai 15:48:25 (minimum 766 ppm), cocok dengan pengguna tidak di kamar. Pada rentang itu Rs turun paling cepat (rata-rata 10 menit: 1395 kΩ pada 15:05, 1244, 1070, 1075, 963, lalu 918 kΩ pada 15:55 setelah pengguna kembali) |
| Tafsir (hipotesis, belum terbukti) | Penurunan Rs terjadi saat **tidak ada orang di kamar**, jadi bukan akibat kehadiran atau pewangi pengguna. Kandidat: kelembapan (uap mandi masuk ke kamar), suhu, atau drift. Tanpa sensor suhu dan kelembapan tidak bisa dibuktikan. Temuan yang aman dituliskan: pada kamar tanpa gas yang diketahui, Rs bergeser lebih dari 50% (sekitar 2045 ke sekitar 900–1000 kΩ) dalam sekitar 4 jam, sehingga **R0 tidak konstan** dan kalibrasi R0 harus diulang pada kondisi yang dicatat |
