# Desain Data: Laju Sampling, Pengiriman, dan Retensi (untuk DFD)

> **Catatan 25 Okt malam:** skema tabel yang dipakai (skema tim backend beserta penyesuaian yang diusulkan) ada di [rancangan-data.md](../1-utama/rancangan-data.md) bagian 4. Nama tiga tabel di bawah ini adalah rancangan awal saya. Bagian yang masih berlaku dari dokumen ini: alasan laju kirim 5 detik dan retensi 7 hari.

Status: **usulan, belum disetujui tim**. Angka ukuran data adalah perkiraan dengan asumsi yang tertulis. Terkait: [desain-peringatan.md](desain-peringatan.md).

## 1. Dua hal yang perlu dipisahkan

| Hal | Pertanyaannya | Usulan |
|---|---|---|
| Laju **keputusan** di ESP32 | Seberapa sering sensor dibaca dan logika alarm dievaluasi | Tetap sekitar 1 detik (sekarang). Cukup cepat menangkap lonjakan terpendek yang relevan (C-251 menyebut lonjakan CO 10 detik) |
| Laju **pengiriman dan penyimpanan** ke MQTT dan database | Seberapa sering data dikirim dan disimpan | Setiap 5 detik, ditambah pesan langsung saat status berubah |

C-251 menulis siklus 5 detik untuk keduanya. Dengan pemisahan ini keputusan tidak harus menunggu 5 detik.

## 2. Mengapa tidak menyimpan tiap detik

Perkiraan, dengan asumsi satu baris sekitar 150 byte di database dan sekitar 200 byte per pesan di jaringan (termasuk tambahan protokol). Nilai itu belum diukur.

| Laju | Baris per hari | Baris per 7 hari | Perkiraan ukuran 7 hari | Perkiraan data jaringan per hari |
|---|---|---|---|---|
| Tiap 1 detik | 86.400 | 604.800 | sekitar 91 MB | sekitar 17 MB |
| Tiap 5 detik | 17.280 | 120.960 | sekitar 18 MB | sekitar 3,5 MB |
| Rata-rata 1 menit | 1.440 | 10.080 | sekitar 1,5 MB | sekitar 0,3 MB |

Catatan:
- Rancangan C-251 memakai hotspot ponsel pengguna untuk internet, jadi data jaringan juga menyangkut kuota pengguna.
- Batas ukuran database pada paket gratis Supabase perlu dicek di halaman paketnya (belum diverifikasi).
- Laju 1 detik tidak bermasalah secara teknis untuk ESP32, tetapi boros untuk riwayat yang hanya ditampilkan sebagai grafik.

## 3. Jangan mengambil satu sampel tiap 5 detik

Analisis kita menunjukkan Rs MiCS bergoyang bolak-balik tiap detik (periode sekitar 2 detik). Mengambil **satu** sampel tiap 5 detik bisa menghasilkan pola lambat palsu (aliasing). Yang benar: **rata-ratakan sampel 1 detik di dalam setiap interval 5 detik**, lalu kirim rata-rata itu. Untuk grafik riwayat itu cukup. Untuk keputusan alarm tetap dipakai filter dari analisis di [filtering.md](filtering.md).

Kirim juga **nilai maksimum** (atau minimum untuk Rs) di setiap interval agar lonjakan pendek tidak hilang dari riwayat.

## 4. Retensi 7 hari: apakah dihapus?

Pilihan:

| Pilihan | Isi | Kelebihan | Kekurangan |
|---|---|---|---|
| A. Hapus semua data lebih dari 7 hari | Satu tabel, ada tugas terjadwal penghapus | Paling sederhana, ukuran tetap | Riwayat lebih dari 7 hari hilang |
| B. Data 5 detik disimpan 7 hari, lalu diringkas jadi rata-rata (dan maksimum) 1 menit untuk disimpan lebih lama | Dua tabel | Tren jangka panjang tetap ada, ukuran kecil | Sedikit lebih rumit |
| C. Simpan semua | Satu tabel, tanpa penghapusan | Paling mudah | Ukuran terus bertambah dan bisa melewati batas paket |

Usulan: **B ringan**. Pembacaan 5 detik disimpan 7 hari. Catatan peringatan (`alert_logs`) dan catatan aktuator (`actuator_logs`) disimpan lama karena jumlahnya sedikit dan itu bukti paling penting. Ringkasan 1 menit disimpan sesuai kebutuhan laporan. Untuk capstone, pilihan A saja juga wajar, asalkan **dinyatakan** dan data pengujian untuk laporan **disimpan terpisah** sebagai berkas (CSV) di komputer, jangan hanya di database.

## 5. Dampak ke DFD

Tambahkan atau ubah:
- **Proses di ESP32: "Agregasi 5 detik dan deteksi kejadian"** (rata-rata dan maksimum per interval, serta pesan langsung saat status berubah) sebelum proses pengiriman MQTT.
- **Penyimpanan D1 `sensor_readings`** diberi keterangan retensi (7 hari).
- **Proses terjadwal "Hapus atau ringkas data lama"** yang berjalan pada D1.
- **Penyimpanan D2 `alert_logs`** dan **D3 `actuator_logs`** tanpa penghapusan (atau penghapusan sangat panjang).
- Penyimpanan data uji (CSV lokal) di luar jalur sistem, untuk bukti laporan.

## 6. Yang harus diputuskan tim

1. Pilihan retensi (A, B, atau C).
2. Apakah riwayat lebih dari 7 hari memang dibutuhkan pengguna (kebutuhan aplikasi, bukan teknis).
3. Format pesan MQTT (field tetap) agar tim software dan tim firmware bisa jalan paralel.
