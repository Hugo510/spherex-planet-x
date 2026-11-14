"""Precómputo del showcase estático: apps/web/public/showcase/<id>/{index.json, visits/*.png, frames/*.png,
spectrum.json, lightcurve.json, known.json, diffs/*.json} para los 5 objetos de prueba y los campos extra.

Uso:
  python scripts/precompute.py                 # todos los campos
  python scripts/precompute.py wise0855 rdra   # solo algunos
  python scripts/precompute.py --list
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from app.adapters.frame_store import FrameStore  # noqa: E402
from app.domain.models import Target  # noqa: E402
from app.domain.targets import TARGETS  # noqa: E402
from app.usecases import known as known_uc  # noqa: E402
from app.usecases.build_visits import build_visits  # noqa: E402
from app.usecases.diff import diff_frames  # noqa: E402
from app.usecases.serialize import ATTRIBUTION, field_key, lightcurve_points, serialize_field, spectrum_points  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "apps" / "web" / "public" / "showcase"
ALL_DETS = (1, 2, 3, 4, 5, 6)

# Campos del showcase. `kind`: object | asteroid | deepfield | random. Textos es/en para la landing y el modo aula.
FIELDS: list[dict] = [
    {"id": "wise0855", "kind": "object", "target": TARGETS["wise0855"], "fov": 0.1, "max_per_visit": 8,
     "title": {"es": "WISE 0855−0714", "en": "WISE 0855−0714"},
     "blurb": {"es": "Enana marrón Y, el objeto más frío conocido fuera del Sistema Solar. Se mueve 8″/año (1.3 px/año) y solo brilla en D5–D6; en D1–D4 lo que ves es una estrella Gaia G = 16.3 a 7″ que no se mueve.",
               "en": "Y-type brown dwarf, the coldest known object outside the Solar System. It moves 8″/yr (1.3 px/yr) and shines only in D5–D6; in D1–D4 what you see is a Gaia G = 16.3 star 7″ away that does not move."},
     "default_det": 5},
    {"id": "epsindib", "kind": "object", "target": TARGETS["epsindib"], "fov": 0.1, "max_per_visit": 8,
     "title": {"es": "ε Indi Ba/Bb", "en": "ε Indi Ba/Bb"},
     "blurb": {"es": "Par de enanas T a 6.7′ de ε Indi A. No satura, se mueve 1 px/año y su «parpadeo» entre exposiciones es su propio espectro: 6 mJy en la banda de agua de 1.39 µm frente a 40 mJy en el pico H.",
               "en": "T-dwarf pair 6.7′ from ε Indi A. It does not saturate, moves 1 px/yr, and its ‘blinking’ between exposures is its own spectrum: 6 mJy in the 1.39 µm water band vs 40 mJy at the H-band peak."},
     "default_det": 2},
    {"id": "barnard", "kind": "object", "target": TARGETS["barnard"], "fov": 0.1, "max_per_visit": 6,
     "title": {"es": "Estrella de Barnard", "en": "Barnard's Star"},
     "blurb": {"es": "El mayor movimiento propio del cielo: 10.4″/año = 1.7 px/año. Satura el núcleo en D2 (OVERFLOW/BLOOM pintados en magenta); el anillo de la PSF se desplaza hacia el norte entre visitas.",
               "en": "The largest proper motion in the sky: 10.4″/yr = 1.7 px/yr. The core saturates in D2 (OVERFLOW/BLOOM painted magenta); the PSF ring shifts north between visits."},
     "default_det": 2},
    {"id": "rwaur", "kind": "object", "target": TARGETS["rwaur"], "fov": 0.1, "max_per_visit": 6,
     "title": {"es": "RW Aurigae", "en": "RW Aurigae"},
     "blurb": {"es": "T Tauri con eventos de oscurecimiento de 2–3 mag. El núcleo satura (1–4 px OVERFLOW): la fotometría de apertura no es fiable y el visor lo dice. Ejemplo de la Field Guide.",
               "en": "T Tauri star with 2–3 mag dimming events. The core saturates (1–4 px OVERFLOW): aperture photometry is unreliable and the viewer says so. Field Guide example."},
     "default_det": 2},
    {"id": "rdra", "kind": "object", "target": TARGETS["rdra"], "fov": 0.1, "max_per_visit": 3, "max_visits": 20,
     "title": {"es": "R Draconis", "en": "R Draconis"},
     "blurb": {"es": "Mira (P = 245.6 d) en el campo profundo del polo norte eclíptico: 61–67 visitas por detector. Satura por completo (núcleo NaN hasta r ≈ 10 px): no hay curva de luz honesta con este pipeline, y se muestra por qué.",
               "en": "Mira variable (P = 245.6 d) in the North Ecliptic Pole deep field: 61–67 visits per detector. Fully saturated (NaN core out to r ≈ 10 px): no honest light curve is possible with this pipeline, and the viewer shows why."},
     "default_det": 1},
    {"id": "nep-deep-1", "kind": "deepfield", "target": Target(270.0, 66.56, 2016.0, 0, 0, 0, "NEP deep field (center)"),
     "fov": 0.1, "max_per_visit": 3, "max_visits": 24, "releases": None,
     "title": {"es": "Campo profundo NEP (centro)", "en": "NEP deep field (center)"},
     "blurb": {"es": "Centro del campo profundo del polo norte eclíptico: ~5 000 exposiciones por detector en 17 meses. Aquí la línea de tiempo tiene decenas de visitas; se muestran 24 por detector.",
               "en": "Center of the North Ecliptic Pole deep field: ~5,000 exposures per detector in 17 months. Here the timeline has dozens of visits; 24 per detector are shown."},
     "default_det": 3},
    {"id": "nep-deep-2", "kind": "deepfield", "target": Target(268.8, 66.1, 2016.0, 0, 0, 0, "NEP deep field (offset)"),
     "fov": 0.1, "max_per_visit": 3, "max_visits": 24, "releases": None,
     "title": {"es": "Campo profundo NEP (borde)", "en": "NEP deep field (edge)"},
     "blurb": {"es": "A 0.7° del centro del campo profundo: la cadencia cae pero sigue siendo decenas de visitas. Útil para comparar el ruido del coadd con el centro.",
               "en": "0.7° from the deep-field center: cadence drops but is still dozens of visits. Useful to compare coadd noise with the center."},
     "default_det": 3},
    {"id": "random-1", "kind": "random", "target": Target(23.4617, 8.9021, 2016.0, 0, 0, 0, "random field"),
     "fov": 0.1, "max_per_visit": 6,
     "title": {"es": "Campo aleatorio", "en": "Random field"},
     "blurb": {"es": "Posición elegida al azar (semilla 2026) en el cielo del Wide Survey, cerca de la eclíptica: lo que ve cualquier usuario al escribir unas coordenadas.",
               "en": "Position drawn at random (seed 2026) in the Wide Survey sky near the ecliptic: what any user sees when typing coordinates."},
     "default_det": 3},
]


def asteroid_fields() -> list[dict]:
    p = ROOT / "scripts" / "asteroid_fields.json"
    if not p.exists():
        return []
    best: dict[str, dict] = {}
    for rec in json.loads(p.read_text()):  # por asteroide, el cruce con más exposiciones
        if rec["asteroid"] not in best or rec["n_exp"] > best[rec["asteroid"]]["n_exp"]:
            best[rec["asteroid"]] = rec
    out = []
    for rec in sorted(best.values(), key=lambda r: -r["n_exp"]):
        name = f"asteroid-{rec['asteroid']}"
        pmra, pmdec = asteroid_rate(rec["asteroid"], rec["mjd"])  # arcsec/año: el Target «persigue» al asteroide
        out.append({
            "id": name, "kind": "asteroid",
            "target": Target(rec["ra"], rec["dec"], rec["epoch"], pmra, pmdec, 0, f"({rec['asteroid']}) {rec['epoch']:.3f}"),
            "fov": 0.15, "max_per_visit": 12, "mjd_range": (rec["mjd"] - 0.5, rec["mjd"] + 1.5),
            "title": {"es": f"Asteroide ({rec['asteroid']})", "en": f"Asteroid ({rec['asteroid']})"},
            "blurb": {"es": f"Asteroide brillante (V ≈ {rec['vmag']:.1f}) observado por SPHEREx a {rec['elong']:.0f}° del Sol. Dentro de una visita se desplaza varios píxeles entre exposiciones: es lo único que «se mueve» a ojo en SPHEREx.",
                      "en": f"Bright asteroid (V ≈ {rec['vmag']:.1f}) observed by SPHEREx {rec['elong']:.0f}° from the Sun. Within a visit it moves several pixels between exposures: the only thing that visibly ‘moves’ in SPHEREx."},
            "default_det": 1, "asteroid": rec,
        })
    return out[:3]


def asteroid_rate(ast: str, mjd: float) -> tuple[float, float]:
    """Velocidad aparente geocéntrica (arcsec/año en RA·cos δ y Dec) de Horizons entre mjd y mjd + 1 h."""
    from math import cos, radians

    from app.adapters import cache, http

    pc = cache.path_for("horizons_rate", ast, f"{mjd:.3f}", ext=".json")
    if pc.exists():
        return tuple(json.loads(pc.read_text()))
    from astropy.time import Time

    t0, t1 = Time(mjd, format="mjd"), Time(mjd + 1 / 24, format="mjd")
    r = http.get("https://ssd.jpl.nasa.gov/api/horizons.api", params={
        "format": "text", "COMMAND": f"'{ast};'", "EPHEM_TYPE": "OBSERVER", "CENTER": "'500@399'",
        "START_TIME": f"'{t0.iso[:16]}'", "STOP_TIME": f"'{t1.iso[:16]}'", "STEP_SIZE": "'1h'", "QUANTITIES": "'1'",
        "CSV_FORMAT": "YES", "ANG_FORMAT": "DEG",
    })
    rows = [ln.split(",") for ln in r.text.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()]
    (ra0, de0), (ra1, de1) = (float(rows[0][3]), float(rows[0][4])), (float(rows[1][3]), float(rows[1][4]))
    dt_yr = (1 / 24) / 365.25
    pm = ((ra1 - ra0) * cos(radians(de0)) * 3600 / dt_yr, (de1 - de0) * 3600 / dt_yr)
    pc.write_text(json.dumps(pm))
    return pm


def canonical_diffs(data: dict, store: FrameStore, out_dir: Path) -> list[dict]:
    """Restas canónicas: visitas consecutivas del mismo detector y primera−última; y dentro de la primera visita del
    detector por defecto, exposiciones a Δ = 1, 4 y 12 canales (para mostrar los tres veredictos)."""
    (out_dir / "diffs").mkdir(exist_ok=True)
    diffs = []
    by_det: dict[int, list[dict]] = {}
    for v in data["visits"]:
        by_det.setdefault(v["detector"], []).append(v)
    for det, vs in by_det.items():
        pairs = [(vs[i], vs[i + 1]) for i in range(len(vs) - 1)][:6]
        if len(vs) > 2:
            pairs.append((vs[0], vs[-1]))
        for a, b in pairs:
            key = f"diff_{a['key']}_{b['key']}"
            d = diff_frames(store, a["key"], b["key"], key)
            if d:
                (out_dir / "diffs" / f"{key}.json").write_text(json.dumps(d))
                diffs.append({"a": a["id"], "b": b["id"], "detector": det, "verdict": d["verdict"]["verdict"], "json": f"diffs/{key}.json"})
        big = max(vs, key=lambda v: v["n_exp"])
        exps = sorted(big["exposures"], key=lambda e: e["lambda_um"] or 0)
        for step in (1, 4, 12):
            if len(exps) > step:
                a, b = exps[0], exps[step]
                key = f"diff_{a['key']}_{b['key']}"
                d = diff_frames(store, a["key"], b["key"], key)
                if d:
                    (out_dir / "diffs" / f"{key}.json").write_text(json.dumps(d))
                    diffs.append({"a": a["id"], "b": b["id"], "detector": det, "verdict": d["verdict"]["verdict"], "json": f"diffs/{key}.json"})
    return diffs


def build_field(spec: dict, *, skip_known: bool = False) -> dict:
    fid = spec["id"]
    out_dir = OUT / fid
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    t0 = time.time()
    tgt: Target = spec["target"]
    res = build_visits(tgt, size_deg=spec["fov"], detectors=ALL_DETS, releases=spec.get("releases"),
                       max_per_visit=spec.get("max_per_visit"), max_visits=spec.get("max_visits"),
                       mjd_range=spec.get("mjd_range"))
    fkey = field_key(tgt, spec["fov"], ALL_DETS, spec.get("releases"), spec.get("max_per_visit"))
    store = FrameStore(out_dir, f"/showcase/{fid}")
    data = serialize_field(res, store, fkey, mode="showcase", name=tgt.name)
    # las visitas van en visits/ (la escalera de λ en frames/): mover los PNG de las visitas
    (out_dir / "visits").mkdir(exist_ok=True)
    for v in data["visits"] + data.get("reference_frames", []):
        for k in ("png16", "mask_png"):
            src = out_dir / "frames" / Path(v[k]).name
            dst = out_dir / "visits" / src.name
            if src.exists():
                src.rename(dst)
            v[k] = f"/showcase/{fid}/visits/{src.name}"
        for ext in (".npy", ".sat.npy", ".json"):
            src = out_dir / "frames" / f"{v['key']}{ext}"
            if src.exists():
                src.rename(out_dir / "visits" / src.name)
    # diffs con los arrays aún en disco
    store_v = _TwoDirStore(out_dir, fid)
    diffs = canonical_diffs(data, store_v, out_dir)
    data["diffs"] = diffs
    data["showcase"] = {"id": fid, "kind": spec["kind"], "title": spec["title"], "blurb": spec["blurb"],
                        "default_det": spec.get("default_det", 1), "asteroid": spec.get("asteroid")}
    (out_dir / "index.json").write_text(json.dumps(data))
    (out_dir / "spectrum.json").write_text(json.dumps({"target": data["target"], "points": spectrum_points(data), "attribution": ATTRIBUTION}))
    (out_dir / "lightcurve.json").write_text(json.dumps({"target": data["target"], "detector": None, "points": lightcurve_points(data, None), "attribution": ATTRIBUTION}))
    if not skip_known and data["visits"]:
        last = max(data["visits"], key=lambda v: v["mjd_mean"])
        # vecinos de TODO el campo (radio = semidiagonal + 10″): el cliente filtra por distancia al clic sin llamar al API
        r_field = spec["fov"] * 3600 * 0.71 + 10
        known = known_uc.what_is_here(data["target"]["ra"], data["target"]["dec"], r_field, last["mjd_mean"])
        if spec["kind"] == "asteroid" and spec.get("asteroid"):
            known["asteroid_hint"] = spec["asteroid"]
        (out_dir / "known.json").write_text(json.dumps(known))
    for f in list(out_dir.rglob("*.npy")) + [p for p in out_dir.rglob("*.json") if p.parent.name in ("frames", "visits")]:
        f.unlink()
    size = sum(p.stat().st_size for p in out_dir.rglob("*") if p.is_file())
    summary = {"id": fid, "kind": spec["kind"], "title": spec["title"], "blurb": spec["blurb"], "default_det": spec.get("default_det", 1),
               "ra": data["target"]["ra"], "dec": data["target"]["dec"], "epoch": data["target"]["epoch"], "fov_deg": spec["fov"],
               "n_visits": len(data["visits"]), "n_exposures": data["n_exposures"], "detectors": data["detectors_available"],
               "releases": data["releases_present"], "failures": len(data["failures"]), "bytes": size, "seconds": round(time.time() - t0, 1),
               "thumbnail": _thumb(data, spec.get("default_det", 1)), "asteroid": spec.get("asteroid")}
    print(f"  {fid}: {summary['n_visits']} visitas, {summary['n_exposures']} exp, {size/1e6:.1f} MB, {summary['seconds']} s, fallos {summary['failures']}")
    return summary


class _TwoDirStore(FrameStore):
    """FrameStore que busca arrays en visits/ y frames/ y escribe diffs en diffs/."""

    def __init__(self, root: Path, fid: str):
        super().__init__(root, f"/showcase/{fid}")

    def get_array(self, key: str, sub: str = "frames"):
        for s in ("visits", "frames"):
            r = super().get_array(key, s)
            if r is not None:
                return r
        return None


def _thumb(data: dict, det: int) -> str | None:
    vs = [v for v in data["visits"] if v["detector"] == det] or data["visits"]
    if not vs:
        return None
    return max(vs, key=lambda v: v["n_exp"])["png16"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--skip-known", action="store_true")
    args = ap.parse_args()
    fields = FIELDS + asteroid_fields()
    if args.list:
        for f in fields:
            print(f["id"], f["kind"], f["target"])
        return 0
    if args.ids:
        fields = [f for f in fields if f["id"] in args.ids]
    OUT.mkdir(parents=True, exist_ok=True)
    idx_path = OUT / "index.json"
    index = json.loads(idx_path.read_text()) if idx_path.exists() else {"fields": []}
    existing = {f["id"]: f for f in index["fields"]}
    for spec in fields:
        try:
            existing[spec["id"]] = build_field(spec, skip_known=args.skip_known)
        except Exception as e:  # noqa: BLE001
            print(f"  {spec['id']}: FALLO {e}")
        order = [f["id"] for f in FIELDS + asteroid_fields()]
        index = {"generated_at": datetime.now(UTC).isoformat(timespec="seconds"), "attribution": ATTRIBUTION,
                 "fields": sorted(existing.values(), key=lambda f: order.index(f["id"]) if f["id"] in order else 99)}
        idx_path.write_text(json.dumps(index, indent=1))
    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"# showcase: {len(index['fields'])} campos, {total/1e6:.1f} MB en {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
