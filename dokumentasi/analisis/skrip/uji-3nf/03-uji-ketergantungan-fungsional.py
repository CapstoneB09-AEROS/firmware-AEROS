import csv, itertools, sys
rows = list(csv.DictReader(open(sys.argv[1])))
attrs = ['co_ppm','co2_ppm','co_level','co2_level','window_status','co_peak_ppm','co2_peak_ppm']
keys = [['id'], ['device_id','measured_at']]
def uniq(cols): return len({tuple(r[c] for c in cols) for r in rows}) == len(rows)
print("baris:", len(rows))
for k in keys: print("kunci kandidat", k, "unik:", uniq(k))
# FD X->Y: grup X dengan >1 nilai Y = pelanggar
def cek(X, Y):
    g = {}
    for r in rows: g.setdefault(tuple(r[c] for c in X), set()).add(r[Y])
    support = sum(1 for k,v in g.items() if sum(1 for r in rows if tuple(r[c] for c in X)==k) >= 2) if len(rows)<0 else None
    cnt = {}
    for r in rows:
        k = tuple(r[c] for c in X); cnt[k] = cnt.get(k,0)+1
    multi = [k for k,c in cnt.items() if c >= 2]
    viol = [k for k in multi if len(g[k]) > 1]
    return len(g), len(multi), len(viol)
const = [a for a in attrs if len({r[a] for r in rows}) == 1]
print("atribut konstan (bukan bukti apa pun):", const)
print()
print("%-30s -> %-14s %8s %10s %10s  %s" % ("penentu X","Y","grup","grup>=2","pelanggar","FD berlaku?"))
for Y in attrs:
    if Y in const: continue
    cands = [[a] for a in attrs if a != Y] + [list(c) for c in itertools.combinations([a for a in attrs if a != Y], 2)]
    for X in cands:
        if any(a in const for a in X): continue
        n, m, v = cek(X, Y)
        if v == 0 and m >= 20:   # FD tampak berlaku DAN ada cukup bukti (>=20 grup dengan >=2 baris)
            print("%-30s -> %-14s %8d %10d %10d  berlaku (data)" % (",".join(X), Y, n, m, v))
print()
print("Uji penentu yang dicurigai (semantik):")
for X,Y in [(['co2_ppm'],'co2_level'),(['co_ppm'],'co_level'),(['co2_ppm','co_ppm'],'co2_level'),(['co2_level'],'co2_ppm'),(['co2_ppm'],'window_status'),(['co2_level'],'window_status')]:
    if Y in const or any(a in const for a in X):
        print("  %s -> %s : dilewati (atribut konstan di data ini)" % (",".join(X), Y)); continue
    n,m,v = cek(X,Y); print("  %-22s -> %-14s grup=%d grup>=2=%d pelanggar=%d  %s" % (",".join(X),Y,n,m,v,"FD TIDAK berlaku" if v else "tampak berlaku"))
