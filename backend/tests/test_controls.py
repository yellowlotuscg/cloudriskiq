"""Tests for control mapping."""
from app.controls import map_controls
from app.models import Category, Finding, Severity, Source


def _finding(category, scope) -> Finding:
    return Finding(
        id="c-1",
        source=Source.aws,
        external_id="c-1",
        title="t",
        severity=Severity.high,
        category=category,
        resource="r",
        compliance_scope=scope,
        first_seen="2026-06-01T00:00:00Z",
    )


def test_baseline_controls_always_present():
    refs = map_controls(_finding(Category.encryption, []))
    frameworks = {r.framework for r in refs}
    assert "NIST CSF 2.0" in frameworks
    assert "CIS v8" in frameworks


def test_pci_only_added_when_in_scope():
    without = map_controls(_finding(Category.encryption, []))
    with_pci = map_controls(_finding(Category.encryption, ["pci"]))
    assert not any(r.framework == "PCI-DSS v4.0" for r in without)
    assert any(r.framework == "PCI-DSS v4.0" for r in with_pci)


def test_fisma_identity_access_maps_to_ac_and_ia():
    refs = map_controls(_finding(Category.identity_access, ["fisma"]))
    ids = {(r.framework, r.control_id) for r in refs}
    assert ("NIST 800-53 Rev5", "AC-2") in ids
    assert ("NIST 800-53 Rev5", "IA-2") in ids


def test_sox_change_management_maps_to_cm():
    refs = map_controls(_finding(Category.change_management, ["sox"]))
    assert any(r.framework == "SOX ITGC" and r.control_id == "CM" for r in refs)
