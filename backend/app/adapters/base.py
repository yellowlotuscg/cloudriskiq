"""Adapter base class and shared normalization helpers."""
from __future__ import annotations

from typing import Dict, List

from app.models import Finding, Source


class Adapter:
    """Base adapter. Subclasses set `source` and implement `normalize`."""

    source: Source

    def normalize(self, payload: Dict) -> List[Finding]:  # pragma: no cover - interface
        raise NotImplementedError


def parse_compliance_scope(value) -> List[str]:
    """Accept "pci,sox" or ["pci","sox"] and return a clean lowercased list.

    Only the regimes the control mapper understands are kept.
    """
    known = {"pci", "sox", "fisma"}
    if not value:
        return []
    if isinstance(value, str):
        parts = [p.strip().lower() for p in value.split(",")]
    elif isinstance(value, (list, tuple)):
        parts = [str(p).strip().lower() for p in value]
    else:
        return []
    return [p for p in parts if p in known]


def derive_criticality(*, env: str = "", data_classification: str = "", public: bool = False) -> str:
    """Map context signals onto low | medium | high asset criticality.

    Production + sensitive data classification or public exposure pushes an asset
    to high; non-prod drops it to low. This mirrors how I'd triage in practice:
    a prod, cardholder-data system outranks a dev sandbox every time.
    """
    env = (env or "").lower()
    data_classification = (data_classification or "").lower()
    sensitive = data_classification in {"pii", "cardholder", "phi", "confidential", "secret"}
    if env in {"prod", "production"} and (sensitive or public):
        return "high"
    if env in {"prod", "production"}:
        return "medium" if not public else "high"
    if env in {"dev", "test", "sandbox", "staging"}:
        return "low"
    return "medium"
