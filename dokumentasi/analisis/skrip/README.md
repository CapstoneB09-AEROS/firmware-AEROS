# Skrip Analisis

Semua skrip hanya memakai Python 3 (dan `pillow`, `numpy` untuk `digitasi_kurva_co.py`). Jalankan dari folder ini. Log mentah ada di `../../../logs/`.

| Skrip | Fungsi | Contoh perintah | Hasil |
|---|---|---|---|
| `skrip/filter_compare.py` | membandingkan filter (SMA, EMA, median): noise, respons 90%, lonjakan yang lolos | `python3 filter_compare.py ../data/data-baseline-t3314-4313.csv 1000` | [../hasil/hasil-filter-2026-10-25.txt](../hasil/hasil-filter-2026-10-25.txt), [hasil-filter-3jam](../hasil/hasil-filter-3jam-2026-10-25.txt) |
| `noise_profile.py` | profil noise rekaman panjang (komponen bergantian 0,5 Hz, periode sumber) | `python3 noise_profile.py ../../../logs/device-monitor-261025-115335.log 300` | [../hasil/hasil-noise-2026-10-25.txt](../hasil/hasil-noise-2026-10-25.txt) |
| `analisis_mobil.py` | noise, filter, ppm, Rs per menit, siklus lambat di mobil | `python3 analisis_mobil.py ../../../logs/device-monitor-261025-214144.log 120` | [../hasil/hasil-uji-mobil-2026-10-25.txt](../hasil/hasil-uji-mobil-2026-10-25.txt), [2026-10-26](../hasil/hasil-uji-mobil-2026-10-26.txt) |
| `analisis_fase.py` | analisis per fase (kipas, AC, pintu): noise, siklus 7 menit, periode seluruh log | `python3 analisis_fase.py ../../../logs/device-monitor-261026-090343.log ...` | [../hasil/hasil-uji-kamar-pagi-2026-10-26.txt](../hasil/hasil-uji-kamar-pagi-2026-10-26.txt), [ruang rapat](../hasil/hasil-uji-ruang-2026-10-26.txt) |
| `analisis_parfum.py` | lonjakan Rs, estimasi ppm, lama di atas ambang, pemulihan, respons aturan baru | `python3 -I analisis_parfum.py ../../../logs/device-monitor-261027-140826.log` | [../hasil/hasil-uji-parfum-2026-10-27.txt](../hasil/hasil-uji-parfum-2026-10-27.txt) |
| `digitasi_kurva_co.py` | membaca kurva CO datasheet dari gambar (piksel menjadi angka) dan membandingkan dengan rumus di kode | `python3 -I digitasi_kurva_co.py` | [../hasil/hasil-digitasi-kurva-co-2026-10-27.txt](../hasil/hasil-digitasi-kurva-co-2026-10-27.txt), [../hasil/kurva-co-overlay.png](../hasil/kurva-co-overlay.png) |

Ringkasan temuan: [../ringkasan-temuan.md](../ringkasan-temuan.md).
