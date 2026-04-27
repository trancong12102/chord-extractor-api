from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_extract_rejects_invalid_url() -> None:
    client = TestClient(app)
    resp = client.post("/extract", json={"url": "not-a-url"})
    assert resp.status_code == 422
