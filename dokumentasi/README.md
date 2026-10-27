# Dokumentasi AEROS: mulai di sini

Kumpulan dokumen untuk prototipe pemantau CO dan CO2 di kabin mobil (firmware, rencana desain, bukti, dan uji). Dokumen dikelompokkan dalam tiga folder bernomor supaya mudah dicari.

## Konteks proyek
- **C-251** = dokumen rencana awal (14 Agustus 2026). **Tidak akan direvisi.**
- **C-501** = laporan implementasi dan hasil. **Tenggat setelah expo.** Dokumentasi di sini menjadi bahannya.
- Firmware lama (v0, 23 Okt 2026) disimpan di `../arsip-firmware/` sebagai pembanding sebelum firmware baru difinalkan.

## Baca dalam urutan ini

| # | Dokumen | Isi | Kapan dibuka |
|---|---|---|---|
| 1 | [1-utama/rencana-desain.md](1-utama/rencana-desain.md) | **Dokumen utama**: latar belakang, tinjauan, kebutuhan, implementasi | Pertama, untuk gambaran besar |
| 2 | [1-utama/pseudocode-baru.md](1-utama/pseudocode-baru.md) | Algoritma baru, pilihan filter, diagram alur, daftar bagian yang belum fix | Saat membahas atau menulis firmware |
| 3 | [1-utama/rancangan-data.md](1-utama/rancangan-data.md) | Data, pesan MQTT, tabel database, DFD (perkiraan) | Saat rapat dengan tim backend dan software |
| 4 | [1-utama/daftar-tugas.md](1-utama/daftar-tugas.md) | Daftar tugas, urutan pengerjaan, dan daftar asumsi | Setiap hari, untuk tahu "sekarang ngapain" |
| 5 | [1-utama/keputusan-terbuka.md](1-utama/keputusan-terbuka.md) | Semua yang belum diputuskan (UX, angka, hardware, data) dengan usulan | Sebelum pertemuan tim |

## Peta folder

| Folder | Isi |
|---|---|
| [1-utama/](1-utama/) | Empat dokumen di atas. **Ini sumber kebenaran.** Bila angka berbeda antar file, yang di sini yang benar |
| [2-lapangan/](2-lapangan/) | [skenario-uji-mobil.md](2-lapangan/skenario-uji-mobil.md) (rencana dan lembar catatan uji mobil) dan [agenda-pertemuan-tim.md](2-lapangan/agenda-pertemuan-tim.md) (daftar yang dibawa ke teman hardware, backend, dan software) |
| [3-bukti/](3-bukti/) | Catatan kerja rinci dan bukti: riwayat keputusan, hitungan, sumber. Dibuka hanya saat butuh alasan atau bukti |
| [analisis/](analisis/) | Skrip analisis data, data yang dianalisis, dan hasilnya |
| [diagram/](diagram/) | Diagram alur algoritma dan DFD (gambar PNG dan SVG, serta skrip pembuatnya) |
| [rencana-awal/](rencana-awal/) | PDF rencana awal tim (C-251) |
| [paper/](paper/) | Kosong. Untuk PDF jurnal bila perlu |
| `../logs/` | Rekaman data serial dari sensor (di luar folder dokumentasi) |

## Cari X di mana?

| Yang dicari | Buka |
|---|---|
| Alasan batas CO dan CO2 (NIOSH, OSHA, WHO, ASHRAE, UL 2034) | [3-bukti/desain-peringatan.md](3-bukti/desain-peringatan.md) bagian A2b dan B1, dan [3-bukti/daftar-pustaka.md](3-bukti/daftar-pustaka.md) |
| Pemilihan filter dan temuan noise | [3-bukti/filtering.md](3-bukti/filtering.md) dan [analisis/ringkasan-temuan-2026-10-25.md](analisis/ringkasan-temuan-2026-10-25.md) |
| Parameter di kode dan status buktinya | [3-bukti/validasi-parameter.md](3-bukti/validasi-parameter.md) |
| Batasan sistem dan kalimat contoh untuk penguji | [3-bukti/batasan-sistem.md](3-bukti/batasan-sistem.md) |
| Perbedaan rencana awal (C-251) dengan sekarang | [3-bukti/perbandingan-c251.md](3-bukti/perbandingan-c251.md) |
| Alasan laju kirim 5 detik dan retensi 7 hari | [3-bukti/desain-data-dfd.md](3-bukti/desain-data-dfd.md) |
| Daftar sumber format IEEE | [3-bukti/daftar-pustaka.md](3-bukti/daftar-pustaka.md) |
| Kurva CO dari datasheet MiCS-5524 | [3-bukti/kurva-co-mics5524.png](3-bukti/kurva-co-mics5524.png) |

## Gambar yang sering dicari

**DFD** (sensor ke MQTT ke database ke aplikasi):
- Level 0: [diagram/dfd-0-konteks.png](diagram/dfd-0-konteks.png)
- Level 1A (perangkat ESP32): [diagram/dfd-1a-perangkat.png](diagram/dfd-1a-perangkat.png)
- Level 1B (backend dan aplikasi): [diagram/dfd-1b-backend-aplikasi.png](diagram/dfd-1b-backend-aplikasi.png)

**Diagram alur algoritma:**
- [Alur utama](diagram/diagram-1-alur-utama.png), [aturan CO pemicu](diagram/diagram-2-aturan-co-pemicu.png), [aturan CO uji arah](diagram/diagram-3-aturan-co-uji-arah.png), [aturan CO2](diagram/diagram-4-aturan-co2.png)

Gambar juga tampil langsung di [pseudocode-baru.md](1-utama/pseudocode-baru.md) (diagram alur) dan [rancangan-data.md](1-utama/rancangan-data.md) (DFD) saat dibuka dengan pratinjau Markdown (Cmd+Shift+V).

## Aturan agar tetap rapi
1. Dokumen baru masuk ke salah satu folder bernomor dan dicatat di tabel README ini.
2. Angka final hanya ditulis di `1-utama/`. File di `3-bukti/` adalah riwayat dan bukti.
3. Bila `src/main.cpp` berubah, perbarui bagian "perbedaan kode dan rencana" di [rencana-desain.md](1-utama/rencana-desain.md).
4. Mengubah diagram berarti mengubah skrip di `diagram/` lalu menjalankannya lagi (`python3 buat_diagram.py` dan `python3 buat_dfd.py`).
