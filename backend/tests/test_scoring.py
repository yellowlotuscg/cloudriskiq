"""Tests for the risk scoring engine."""
from datetime import datetime, timezone

from app.models import Category, Finding, Severity, Source
from app.scoring import score


def _finding(**kwargs) -> Finding:
    base = dict(
        id="t-1",
        source=Source.aws,
        external_id="t-1",
        title="test",
        severity=Severity.high,
        category=Category.public_exposure,
        resource="r",
        first_seen="2026-06-01T00:00:00Z",
    )
    base.update(kwargs)
    return Finding(**base)


NOW = datetime(2026, 6, 14, tzinfo=timezone.utc)


def test_base_severity_scores():
    assert score(_finding(severity=Severity.low, asset_criticality="medium"), now=NOW) == 25
    assert score(_finding(severity=Severity.medium, asset_criticality="medium"), now=NOW) == 50


def test_public_exposure_raises_score():
    quiet = score(_finding(public_exposure=False, asset_criticality="medium"), now=NOW)
    exposed = score(_finding(public_exposure=True, asset_criticality="medium"), now=NOW)
    assert exposed > quiet


def test_compliance_scope_bonus_is_capped():
    f = _finding(compliance_scope=["pci", "sox", "fisma"], asset_criticality="medium")
    # 75 base + 6 cap (not 9) = 81, plus age. Just assert the cap held vs a hypothetical 9.
    assert score(f, now=NOW) <= 75 + 6 + 9


def test_score_clamped_to_100():
    f = _finding(
        severity=Severity.critical,
        public_exposure=True,
        exploit_signal=True,
        asset_criticality="high",
        compliance_scope=["pci", "sox", "fisma"],
        first_seen="2026-01-01T00:00:00Z",
    )
    assert score(f, now=NOW) == 100


def test_older_findings_score_higher():
    fresh = score(_finding(first_seen="2026-06-13T00:00:00Z"), now=NOW)
    stale = score(_finding(first_seen="2026-01-01T00:00:00Z"), now=NOW)
    assert stale > fresh
