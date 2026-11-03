# Uji Rancangan Database (3NF)

Menguji [rancangan-database-mvp.md](../../../keputusan/rancangan-database-mvp.md) di PostgreSQL 17 **lokal sementara**, memakai data nyata `AEROS_01`. Tidak menyentuh Supabase.

| Berkas | Fungsi |
|---|---|
| `00-ekspor-data-nyata.js` | membaca data `AEROS_01` dari Supabase (hanya baca, kunci dari `worker/.env`) dan menulis `INSERT` ke berkas SQL |
| `01-skema-lama.sql` | perkiraan skema yang ada sekarang (disusun dari dokumen dan kolom yang terbaca, **bukan dump asli**) |
| `02-uji-perilaku.sql` | uji migrasi, batasan, kunci tamu, view, dan aturan hapus |
| `03-uji-ketergantungan-fungsional.py` | mencari ketergantungan fungsional antar kolom bukan-kunci pada data nyata (dari `\copy` ke CSV) |

Urutan: buat basis data kosong, jalankan `01`, muat data hasil `00`, jalankan SQL migrasi dari bagian 4 rancangan (diambil persis dari dokumen), lalu `02` dan `03`.
