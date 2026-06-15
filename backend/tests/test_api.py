"""End-to-end API tests against the hydrated store (sample-data)."""
from fastapi.testclient import TestClient

from app.main import app


def test_findings_loaded_and_prioritized():
    with TestClient(app) as client:
        resp = client.get("/findings")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] > 0
        scores = [item["risk_score"] for item in body["items"]]
        assert scores == sorted(scores, reverse=True)  # highest risk first


def test_filter_by_source_and_min_score():
    with TestClient(app) as client:
        resp = client.get("/findings", params={"source": "aws", "min_score": 80})
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["source"] == "aws"
            assert item["risk_score"] >= 80


def test_get_single_finding_and_404():
    with TestClient(app) as client:
        listing = client.get("/findings").json()["items"]
        fid = listing[0]["id"]
        assert client.get(f"/findings/{fid}").status_code == 200
        assert client.get("/findings/does-not-exist").status_code == 404


def test_patch_status():
    with TestClient(app) as client:
        fid = client.get("/findings").json()["items"][0]["id"]
        resp = client.patch(f"/findings/{fid}", params={"status": "acknowledged"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "acknowledged"


def test_summary_and_controls_and_evidence():
    with TestClient(app) as client:
        summary = client.get("/summary").json()
        assert summary["total"] > 0
        assert "by_source" in summary

        controls = client.get("/controls").json()
        assert "PCI-DSS v4.0" in controls["frameworks"]
        assert len(controls["controls"]) > 0

        evidence = client.get("/evidence").json()
        assert evidence["report"] == "CloudRiskIQ Control Evidence Pack"
        assert len(evidence["findings"]) == summary["total"]
