from fastapi.testclient import TestClient

from app.main import app


def test_health():
    r = TestClient(app).get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["releases"]["qr3"] == "10.26131/IRSA662"
