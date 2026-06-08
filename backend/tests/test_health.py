"""Tests for the /health endpoint."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "cloudriskiq-api"
    assert "version" in body


def test_root_returns_metadata():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "version" in resp.json()
