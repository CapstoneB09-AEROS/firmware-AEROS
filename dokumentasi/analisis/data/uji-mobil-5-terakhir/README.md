# Log 5 uji mobil terakhir (4 penumpang)

Salinan apa adanya dari `../../../../logs/` (rekaman serial `pio device monitor`). Dianalisis di [../../perbandingan-mobil-2026-11-04.md](../../perbandingan-mobil-2026-11-04.md) dengan [../../skrip/bandingkan_mobil.py](../../skrip/bandingkan_mobil.py).

| Folder | Mobil | Tanggal | Firmware | Berkas |
|---|---|---|---|---|
| `1-avanza-2026-10-26/` | Toyota Avanza | 26 Okt 2026 | v0 | `device-monitor-261026-193817.log` (19:38–20:26) |
| `2-civic-2026-10-30/` | Honda Civic EG6 1994 | 30 Okt 2026 | v2.0 | `device-monitor-261030-183128.log` (18:31–19:10) |
| `3-ayla-2026-11-04/` | Daihatsu Ayla 2023 | 4 Nov 2026 sore | v2.4 + casing 3D | `device-monitor-261104-145200.log` (14:52–16:07) |
| `4-avanza-2026-11-04/` | Toyota Avanza | 4 Nov 2026 malam | v2.4 + casing 3D | `...183919`, `...190712`, `...193811` (18:39–19:42, satu proses alat) |
| `5-civic-2026-11-04/` | Honda Civic EG6 1994 | 4 Nov 2026 malam | v2.4 + casing 3D | `...200829`, `...202311`, `...205203` (20:08–20:53, **alat mulai ulang 20:23 dan 20:52**) |

Kolom data: `t_s, V_mV, Rs_kOhm, Rs/R0, CO_ppm_estimasi, CO2_ppm, status_CO, status_CO2, ...`. CO2 = 500 adalah nilai pengisi saat pemanasan. Jam buka dan tutup jendela (manual) tidak ada di log.
