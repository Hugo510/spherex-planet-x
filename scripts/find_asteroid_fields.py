"""Busca asteroides brillantes dentro de exposiciones SPHEREx (DR1/QR3) para el showcase.

SPHEREx apunta a ~90° del Sol (nunca a la oposición), así que se buscan los cruces de cada asteroide por elongación
solar ≈ 90° y se consulta el TAP de IRSA en la posición del asteroide (Horizons, observador 500@399) día a día.
Salida: scripts/asteroid_fields.json con los campos encontrados (ra, dec, mjd, exposiciones, detectores).
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from app.adapters import http, irsa_tap  # noqa: E402
from app.domain.models import mjd_to_year  # noqa: E402

CANDIDATES = ["4", "1", "2", "7", "6", "3", "15", "8", "29", "9", "16", "20", "532", "10", "11", "18", "19", "21", "22", "44"]
MJD0, MJD1 = 60800.0, 61310.0  # 2025-05-05 .. 2026-09-27 (rango de DR1+QR3 visto en TAP)
ADQL = """
SELECT a.uri, p.obs_publisher_did, p.time_bounds_lower, p.time_bounds_upper,
       p.energy_bandpassname, p.energy_bounds_lower, p.energy_bounds_upper
FROM spherex.artifact a JOIN spherex.plane p ON a.planeid = p.planeid
WHERE 1 = CONTAINS(POINT('ICRS', {ra:.5f}, {dec:.5f}), p.poly)
  AND p.time_bounds_lower BETWEEN {t0:.3f} AND {t1:.3f}
"""


def ephemeris(ast: str) -> list[dict]:
    r = http.get("https://ssd.jpl.nasa.gov/api/horizons.api", params={
        "format": "text", "COMMAND": f"'{ast};'", "EPHEM_TYPE": "OBSERVER", "CENTER": "'500@399'",
        "START_TIME": "'2025-05-05'", "STOP_TIME": "'2026-09-27'", "STEP_SIZE": "'1d'", "QUANTITIES": "'1,9,23'",
        "CSV_FORMAT": "YES", "ANG_FORMAT": "DEG", "CAL_FORMAT": "JD",
    })
    txt = r.text
    body = txt.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
    out = []
    for line in body:
        f = [x.strip() for x in line.split(",")]
        try:
            jd, ra, dec, mag, elong = float(f[0]), float(f[3]), float(f[4]), float(f[5]), float(f[7])
        except (ValueError, IndexError):
            continue
        out.append({"mjd": jd - 2400000.5, "ra": ra, "dec": dec, "mag": mag, "elong": elong})
    return out


def main():
    found = []
    out = Path(__file__).with_name("data") / "asteroid_fields.json"
    for ast in CANDIDATES:
        try:
            eph = ephemeris(ast)
        except Exception as e:  # noqa: BLE001
            print(ast, "horizons fallo", e)
            continue
        cand = [e for e in eph if 82 <= e["elong"] <= 98 and MJD0 <= e["mjd"] <= MJD1]
        print(f"# asteroide {ast}: {len(eph)} días, {len(cand)} con elongación 82–98°, V {min(e['mag'] for e in eph):.1f}–{max(e['mag'] for e in eph):.1f}")
        hits = 0
        for e in cand:
            t0 = time.time()
            try:
                rows = irsa_tap.query_csv(ADQL.format(ra=e["ra"], dec=e["dec"], t0=e["mjd"] - 0.5, t1=e["mjd"] + 1.5))
            except Exception as ex:  # noqa: BLE001
                print("  tap fallo", ex)
                time.sleep(5)
                continue
            if rows:
                refs = [irsa_tap.parse_exposure(r) for r in rows]
                dets = sorted({r.detector for r in refs})
                rec = {"asteroid": ast, "ra": e["ra"], "dec": e["dec"], "mjd": e["mjd"], "epoch": round(mjd_to_year(e["mjd"]), 4),
                       "vmag": e["mag"], "elong": e["elong"], "n_exp": len(refs), "detectors": dets,
                       "mjd_min": min(r.mjd for r in refs), "mjd_max": max(r.mjd for r in refs)}
                print("  HIT", rec, f"({time.time()-t0:.0f} s)")
                found.append(rec)
                hits += 1
                out.write_text(json.dumps(found, indent=1))
                if hits >= 2:
                    break
        if len({f["asteroid"] for f in found}) >= 4:
            break
    out.write_text(json.dumps(found, indent=1))
    print("# listo:", len(found), "campos")


if __name__ == "__main__":
    main()
