"""Ringkasan log firmware v1: sesi (tiap reset), nilai sensor, dan kejadian penting dalam tabel.
Jalankan: python3 -I analisis_v1.py ../../../logs/device-monitor-261028-182851.log
Format log: 'HH:MM:SS.mmm > baris' dengan baris data (CSV v1 atau tabel v1.1) dan baris kejadian ('# [detik s] TAG: isi')."""
import re, sys

def baca(path):
    sesi, cur = [], None
    for l in open(path, encoding='utf-8', errors='replace').read().replace('\x00', '').split('\n'):
        m = re.match(r'(\d\d:\d\d:\d\d)\.\d+ > (.*)$', l)
        if not m: continue
        jam, isi = m.groups()
        d = re.match(r'(\d+),([\d.]+),([\d.]+|n/a),([\d.]+|n/a),(\d+),(\d+|n/a),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),(\d),([\d.]+|n/a),', isi)
        if d:
            t = int(d.group(1))
            if cur is None or t < cur['t_akhir']:
                cur = dict(mulai=jam, data=[], ev=[], t_akhir=t); sesi.append(cur)
            cur['t_akhir'] = t
            cur['data'].append(dict(t=t, jam=jam, v=float(d.group(2)), rs=None if d.group(3) == 'n/a' else float(d.group(3)),
                                    rasio=None if d.group(4) == 'n/a' else float(d.group(4)), co=int(d.group(5)),
                                    co2=None if d.group(6) == 'n/a' else int(d.group(6)), stco=d.group(7), stco2=d.group(8),
                                    jendela=d.group(11), buzzer=d.group(12), rsh=None if d.group(14) == 'n/a' else float(d.group(14))))
        kf = isi.split(',')
        if not d and len(kf) == 10 and re.match(r'^\d+$', kf[0]):          # format ringkas (v1.3)
            t = int(kf[0])
            if cur is None or t < cur['t_akhir']:
                cur = dict(mulai=jam, data=[], ev=[], t_akhir=t); sesi.append(cur)
            cur['t_akhir'] = t
            try:
                num = lambda s: None if s in ('n/a', '') else float(s)
                cur['data'].append(dict(t=t, jam=jam, v=float(kf[1]), rs=num(kf[2]), rasio=num(kf[3]), co=int(kf[4]), co2=None if kf[5] == 'n/a' else int(kf[5]),
                                        stco=kf[6], stco2=kf[7], jendela=kf[8], buzzer=kf[9], rsh=num(kf[2])))
            except ValueError:
                pass
        tb = [x.strip() for x in isi.split('|')]
        if not d and len(tb) >= 11 and re.match(r'^\d+$', tb[0]):      # format tabel (v1.1)
            t = int(tb[0])
            if cur is None or t < cur['t_akhir']:
                cur = dict(mulai=jam, data=[], ev=[], t_akhir=t); sesi.append(cur)
            cur['t_akhir'] = t
            num = lambda s: None if s in ('n/a', '') else float(s)
            try:
                cur['data'].append(dict(t=t, jam=jam, v=0.0, rs=num(tb[3]), rasio=num(tb[4]), co=int(tb[1]), co2=None if tb[2] == 'n/a' else int(tb[2]),
                                        stco=tb[5], stco2=tb[6], jendela=tb[8], buzzer=tb[9], rsh=num(tb[3])))
            except ValueError:
                pass      # baris rusak (karakter serial tercampur): dilewati
        e = re.match(r'# \[(\d+)s\] (\S[^:]*): (.*)$', isi)
        if e and cur is not None:
            cur['ev'].append((jam, int(e.group(1)), e.group(2), e.group(3)))
    return sesi

def tabel(judul, kepala, baris):
    print('\n' + judul)
    lebar = [max(len(str(x)) for x in [k] + [b[i] for b in baris]) for i, k in enumerate(kepala)]
    print(' | '.join(k.ljust(lebar[i]) for i, k in enumerate(kepala)))
    print('-+-'.join('-' * w for w in lebar))
    for b in baris:
        print(' | '.join(str(x).ljust(lebar[i]) for i, x in enumerate(b)))

sesi = baca(sys.argv[1])
rows = []
for i, s in enumerate(sesi, 1):
    d = s['data']; sah = [x for x in d if x['t'] >= 181]
    co2 = [x['co2'] for x in d if x['co2'] is not None]
    rsh = [x['rsh'] for x in d if x['rsh'] is not None]
    rasio = [x['rasio'] for x in d if x['rasio'] is not None]
    vv = [x['v'] for x in d]
    rows.append((i, d[0]['jam'], d[-1]['jam'], f"{d[-1]['t']} dtk", f"{min(vv):.1f}-{max(vv):.1f}", f"{min(co2)}-{max(co2)}",
                 f"{min(rsh):.0f}-{max(rsh):.0f}" if rsh else '-', f"{min(rasio):.2f}-{max(rasio):.2f}" if rasio else '-',
                 max(x['co'] for x in d), 'ya' if d[-1]['t'] >= 181 else 'tidak'))
tabel('1. Sesi (tiap reset ESP32 memulai sesi baru)', ['Sesi', 'Mulai', 'Berakhir', 'Lama', 'V MiCS (mV)', 'CO2 (ppm)', 'Rs halus (kOhm)', 'Rs/R0', 'CO maks (ppm)', 'Lewat pemanasan'], rows)

for i, s in enumerate(sesi, 1):
    kej = [e for e in s['ev'] if e[2] in ('CO2', 'CO', 'JENDELA', 'PEMANASAN', 'UJI ARAH', 'STATUS CO')]
    baris = []
    for jam, t, tag, isi in kej:
        isi = isi.split(' | ')[0]
        baris.append((jam, t, tag, isi[:95]))
    tabel(f'2.{i} Kejadian penting sesi {i}', ['Jam', 'Detik sesi', 'Jenis', 'Isi'], baris)

# pasangan buka-tutup jendela
baris = []
for i, s in enumerate(sesi, 1):
    buka = None
    for jam, t, tag, isi in s['ev']:
        if tag == 'JENDELA' and isi.startswith('BUKA'): buka = (jam, t, isi)
        elif tag == 'JENDELA' and isi.startswith('TUTUP') and buka:
            m = re.search(r'terbuka (\d+) detik', isi)
            baris.append((i, buka[0], jam, f'{m.group(1)} detik' if m else '-', buka[2].split('alasan: ')[1].split(' |')[0], isi.split('alasan: ')[1].split(' |')[0])); buka = None
    if buka: baris.append((i, buka[0], '(tidak tercatat)', '-', buka[2].split('alasan: ')[1].split(' |')[0], 'log berakhir atau ESP reset saat jendela masih terbuka'))
tabel('3. Siklus jendela (buka lalu tutup)', ['Sesi', 'Buka', 'Tutup', 'Lama terbuka', 'Alasan buka', 'Alasan tutup'], baris)
