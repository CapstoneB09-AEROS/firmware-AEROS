"""Digitalisasi kurva CO MiCS-5524 dari gambar datasheet (piksel -> angka), lalu bandingkan dengan rumus di kode.
Jalankan: python3 -I digitasi_kurva_co.py   (butuh pillow dan numpy)
Sumbu dikalibrasi dari garis grid utama gambar (dideteksi otomatis). Keluaran: teks + hasil/kurva-co-overlay.png
"""
from PIL import Image, ImageDraw
import numpy as np, itertools, os
here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, '..', 'data', 'kurva-co-mics5524.png')
img = Image.open(src).convert('RGB'); im = np.array(img.convert('L')).astype(float)
A_KODE, BETA_KODE = 3.7, 0.856

cols = [x for x in range(60, 780) if (im[40:335, x] < 110).mean() > 0.8]   # 0.1,1,10,...,10000 ppm
rows = [y for y in range(20, 345) if (im[y, 90:750] < 110).mean() > 0.8]   # Rs/R0 = 1.00 dan 0.01
x1, x1000, y1, y001 = cols[1], cols[4], rows[0], rows[1]
dx = (x1000 - x1) / 3.0; dy = (y001 - y1) / 2.0
X = lambda p, s=0: 10 ** ((p - x1 + s) / dx)
Y = lambda p, s=0: 10 ** (-(p - y1 + s) / dy)
print(f'Sumbu: 1 ppm di x={x1}, 1000 ppm di x={x1000}; Rs/R0=1 di y={y1}, 0.01 di y={y001}')

pts = []
for x in range(x1 + 5, x1000 - 2):                     # garis tebal CO: piksel sangat gelap dekat diagonal
    yc = 75 + (x - x1) * (y001 - 75) / (x1000 - x1)
    ys = np.arange(int(yc - 10), int(yc + 11)); m = im[ys, x] < 70
    if m.sum() >= 2: pts.append((x, ys[m].mean()))
pts = np.array(pts)
lx = np.log10(X(pts[:, 0])); ly = np.log10(Y(pts[:, 1]))
b, a = np.polyfit(lx, ly, 1); res = ly - (a + b * lx)
print(f'Titik kurva dipakai: {len(pts)}')
print(f'Hasil ukur piksel : A = {10**a:.3f}, BETA = {-b:.3f}  (simpangan baku residu {res.std():.4f} dekade, maks {abs(res).max():.4f})')
print(f'Nilai di kode     : A = {A_KODE}, BETA = {BETA_KODE}')
fits = []
for s in (-1.5, 0, 1.5):                                # kalibrasi sumbu Y bisa meleset +-1.5 piksel
    l2 = np.log10(Y(pts[:, 1], s)); b2, a2 = np.polyfit(lx, l2, 1); fits.append((10**a2, -b2))
print(f'Ketidakpastian sumbu (+-1.5 piksel): A {min(f[0] for f in fits):.2f}-{max(f[0] for f in fits):.2f}, BETA {min(f[1] for f in fits):.3f}-{max(f[1] for f in fits):.3f}')
print('\nppm  | Rs/R0 hasil ukur | Rs/R0 rumus kode | selisih Rs/R0 | ppm yg dibaca kode dari Rs/R0 hasil ukur')
for p in (1, 2, 5, 10, 20, 35, 60, 87, 100, 300, 1000):
    r_fit = 10 ** (a + b * np.log10(p)); r_kode = A_KODE / p ** BETA_KODE
    ppm_kode = (A_KODE / r_fit) ** (1 / BETA_KODE)
    print(f'{p:4d} | {r_fit:.4f}           | {r_kode:.4f}           | {100*(r_kode/r_fit-1):+5.1f}%        | {ppm_kode:7.1f}')
print(f'\nFaktor sensitivitas (Rs udara / Rs pada 60 ppm) menurut kurva: {1/(10**(a+b*np.log10(60))):.1f} (rentang datasheet S60: 1.2-50)')

ov = img.copy(); d = ImageDraw.Draw(ov)
prev = None
for p in np.logspace(0, 3, 120):                        # garis merah = rumus kode
    px = x1 + dx * np.log10(p); py = y1 + dy * -np.log10(A_KODE / p ** BETA_KODE)
    if prev: d.line([prev, (px, py)], fill=(255, 0, 0), width=1)
    prev = (px, py)
ov.save(os.path.join(here, '..', 'hasil', 'kurva-co-overlay.png'))
