"""Tests for evidence pack generation."""
from app.evidence import build_evidence_pack, render_markdown
from app.ingest import ingest
from app.config import settings
from app.store import FindingsStore


def _store() -> FindingsStore:
    store = FindingsStore()
    store.replace_all(ingest(settings.sample_data_dir))
    return store


def test_evidence_pack_structure():
    pack = build_evidence_pack(_store(), generated_at="2026-06-14T00:00:00Z")
    assert pack["report"] == "CloudRiskIQ Control Evidence Pack"
    assert pack["generated_at"] == "2026-06-14T00:00:00Z"
    assert pack["summary"]["total_findings"] > 0
    assert len(pack["control_coverage"]) > 0
    # every finding record carries its controls
    assert all("controls" in r for r in pack["findings"])


def test_render_markdown_contains_tables():
    md = render_markdown(build_evidence_pack(_store()))
    assert "# CloudRiskIQ Control Evidence Pack" in md
    assert "## Control coverage" in md
    assert "| Framework | Control |" in md
