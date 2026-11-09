#!/usr/bin/env python3
"""PoC 1 — ¿Qué exposiciones de SPHEREx contienen una posición?

Consulta el servicio TAP de IRSA (tablas spherex.artifact + spherex.plane),
imprime las exposiciones agrupadas por detector y guarda un CSV.

Uso:
  python 01_find_epochs.py wise0855
  python 01_find_epochs.py --ra 133.795 --dec -7.245
  python 01_find_epochs.py barnard --release qr3

Qué queremos confirmar con esto:
  1. Que las tablas/columnas del tutorial de IRSA siguen vigentes con QR3.
  2. La unidad de time_bounds_lower (¿MJD?).
  3. Cuántas épocas/visitas hay por detector para cada objeto de prueba.
"""
import argparse
import csv
import re
import sys
from collections import defaultdict

import pyvo
from astropy.time import Time

from targets import TARGETS

# Windows: la consola cp1252 no puede imprimir "µ" ni "≈"; degradar en vez de tronar.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

TAP_URL = "https://irsa.ipac.caltech.edu/TAP"
VERSION_RE = re.compile(r"l2b(?:_retry)?-v\d+-\d+-\d+")
RELEASE_RE = re.compile(r"spherex/(qr\d+)/")

QUERY = """
SELECT a.uri, a.planeid, p.time_bounds_lower, p.time_bounds_upper,
       p.energy_bandpassname, p.energy_bounds_lower, p.energy_bounds_upper
FROM spherex.artifact a
JOIN spherex.plane p ON a.planeid = p.planeid
WHERE 1 = CONTAINS(POINT('ICRS', {ra}, {dec}), p.poly)
ORDER BY p.time_bounds_lower
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", choices=sorted(TARGETS), help="objeto de prueba")
    ap.add_argument("--ra", type=float)
    ap.add_argument("--dec", type=float)
    ap.add_argument("--release", default=None, help="filtrar uri por release, p. ej. qr3 o qr2")
    ap.add_argument("--out", default=None, help="CSV de salida")
    args = ap.parse_args()

    if args.target:
        tgt = TARGETS[args.target]
        # posición propagada a 2026.0 (mitad del rango QR2/QR3); el footprint es de 3.5°, así que
        # 4' de pm no cambian la lista, pero así el CSV lleva la posición que usará el cutout.
        ra, dec = tgt.at(2026.0)
        print(f"# {args.target}: {tgt.note}")
    elif args.ra is not None and args.dec is not None:
        ra, dec = args.ra, args.dec
    else:
        ap.error("indica un target o --ra/--dec")

    print(f"# TAP {TAP_URL}  pos=({ra:.5f}, {dec:.5f})")
    svc = pyvo.dal.TAPService(TAP_URL)
    q = QUERY.format(ra=ra, dec=dec)
    res = svc.search(q)  # consulta síncrona; basta para una posición
    tab = res.to_table()
    print(f"# {len(tab)} exposiciones en total")
    if len(tab) == 0:
        return 0

    print("# columnas:", ", ".join(tab.colnames))
    for col in ("time_bounds_lower", "energy_bounds_lower", "energy_bounds_upper"):
        if col in tab.colnames:
            print(f"#   {col}: unit={tab[col].unit!s}  dtype={tab[col].dtype}  ejemplo={tab[col][0]}")

    rows = []
    by_det = defaultdict(list)
    for r in tab:
        uri = str(r["uri"])
        if args.release and f"/{args.release}/" not in uri and not uri.startswith(f"{args.release}/"):
            continue
        t = float(r["time_bounds_lower"])
        # Suposición a verificar: time_bounds_lower en MJD (estándar CAOM). Si el ISO sale absurdo, no es MJD.
        iso = Time(t, format="mjd").iso if 50000 < t < 70000 else "?"
        band = str(r["energy_bandpassname"])
        det = band.replace("SPHEREx-D", "")
        m_rel, m_ver = RELEASE_RE.search(uri), VERSION_RE.search(uri)
        row = dict(uri=uri, planeid=str(r["planeid"]), mjd=t, iso=iso, band=band, det=det,
                   lam_lo=r["energy_bounds_lower"], lam_hi=r["energy_bounds_upper"],
                   release=m_rel.group(1) if m_rel else "?", l2b_version=m_ver.group(0) if m_ver else "?")
        rows.append(row)
        by_det[det].append(row)

    print(f"# {len(rows)} tras filtro release={args.release}")
    rel_count = defaultdict(int)
    for r in rows:
        rel_count[r["release"]] += 1
    print("# por release:", dict(rel_count), "| versiones l2b distintas:", len({r["l2b_version"] for r in rows}))
    for det in sorted(by_det):
        lst = by_det[det]
        # agrupar en "visitas": gaps > 1 día
        visits, cur, last = [], [], None
        for r in lst:
            if last is not None and r["mjd"] - last > 1.0:
                visits.append(cur); cur = []
            cur.append(r); last = r["mjd"]
        if cur:
            visits.append(cur)
        print(f"\n== Detector {det}: {len(lst)} exposiciones en {len(visits)} visita(s)")
        for i, v in enumerate(visits, 1):
            print(f"   visita {i}: {v[0]['iso'][:10]} .. {v[-1]['iso'][:10]}  ({len(v)} exp)")
        print(f"   primera uri: {lst[0]['uri']}")

    out = args.out or f"epochs_{args.target or 'pos'}.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\n# guardado {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
