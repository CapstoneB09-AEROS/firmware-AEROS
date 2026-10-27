# Dokumentasi AEROS

Prototipe pemantau CO dan CO2 di kabin mobil (ESP32, MiCS-5524 lewat ADS1115, MH-Z19C, LCD, buzzer, jendela). Folder ini hanya berisi: **keputusan** (yang sudah dan belum), **pengujian**, **analisis** (hasil dan skripnya), dan **tugas per subsistem**.

## Konteks
- **C-251** = rencana awal tim (14 Agustus 2026). **Tidak direvisi.**
- **C-501** = laporan hasil. **Tenggat setelah expo.** Dokumentasi ini menjadi bahannya.
- Expo **30 Oktober 2026**; firmware dibekukan **29 Oktober siang**.
- Firmware lama (v0, 23 Okt 2026) tetap di `../src/main.cpp`, cadangannya di `../arsip-firmware/`. Firmware baru ditulis di cabang `firmware-baru`.
- Rekaman serial ada di `../logs/`. Salinan kode tim (komunikasi) di `../kode-tim/` (tidak masuk git).

## Peta folder
| Folder | Isi | Mulai dari |
|---|---|---|
| [keputusan/](keputusan/) | Semua keputusan dan alasannya, termasuk yang **belum** diputuskan | [keputusan.md](keputusan/keputusan.md), lalu [belum-diputuskan.md](keputusan/belum-diputuskan.md) |
| [pengujian/](pengujian/) | Rencana uji, lembar catatan, dan laporan tiap uji | [rencana-uji.md](pengujian/rencana-uji.md) |
| [analisis/](analisis/) | Hasil analisis data, skrip, dan data yang dianalisis | [ringkasan-temuan.md](analisis/ringkasan-temuan.md) |
| [tugas/](tugas/) | Tugas dan parkir per subsistem (firmware, hardware, komunikasi, aplikasi, pengujian, laporan) | [tugas-per-subsistem.md](tugas/tugas-per-subsistem.md) |
| [referensi/](referensi/) | Daftar pustaka dan PDF rencana awal | [daftar-pustaka.md](referensi/daftar-pustaka.md) |

## Isi folder keputusan
| Berkas | Isi |
|---|---|
| [keputusan.md](keputusan/keputusan.md) | Semua yang sudah ditetapkan: aturan alarm, pengolahan sinyal, status dan bunyi, data, kebutuhan (FR dan NFR) |
| [belum-diputuskan.md](keputusan/belum-diputuskan.md) | Semua yang masih terbuka, dengan usulan, dan asumsi yang belum terbukti |
| [algoritma-firmware.md](keputusan/algoritma-firmware.md) | Pseudocode firmware baru dan diagram alur |
| [algoritma-firmware-lama-v0.md](keputusan/algoritma-firmware-lama-v0.md) | Pseudocode lama dan alur kode v0 (disimpan apa adanya) |
| [komunikasi.md](keputusan/komunikasi.md) | Kontrak pesan v3, rancangan jaringan ESP32, worker, diagram alur data dan perintah |
| [data-dan-database.md](keputusan/data-dan-database.md) | Tabel database, retensi, DFD |
| [peringatan-dan-ambang.md](keputusan/peringatan-dan-ambang.md) | Dasar angka CO dan CO2 dan prinsip waktu tunggu |
| [parameter-dan-sumber.md](keputusan/parameter-dan-sumber.md) | Tiap parameter firmware, sumbernya, dan statusnya |
| [batasan-sistem.md](keputusan/batasan-sistem.md) | Batasan sensor dan kalimat aman untuk penguji |
| [diagram/](keputusan/diagram/) | Gambar diagram (PNG dan SVG) dan skrip pembuatnya |

## Aturan agar tetap rapi
1. Dokumen baru masuk ke salah satu dari lima folder di atas. Jangan membuat folder baru tanpa alasan.
2. Angka final hanya ditulis di `keputusan/keputusan.md` dan `keputusan/algoritma-firmware.md`. Berkas lain menunjuk ke sana.
3. Satu fakta, satu tempat: hasil per uji hanya di `pengujian/laporan/`, kesimpulan lintas uji hanya di `analisis/ringkasan-temuan.md`.
4. Butir yang diputuskan dipindah dari `belum-diputuskan.md` ke `keputusan.md`.
5. Mengubah diagram berarti mengubah skripnya di `keputusan/diagram/` lalu menjalankannya lagi.
