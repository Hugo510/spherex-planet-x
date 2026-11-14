from fastapi import APIRouter

router = APIRouter()

RELEASES = {"qr2": "10.26131/IRSA652", "qr3": "10.26131/IRSA662"}


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "releases": RELEASES, "pixscale_arcsec": 6.15}
