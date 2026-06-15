"""Ingestion pipeline: sample-data → normalized, scored, control-mapped findings.

This is the offline path: read each source's `findings.sample.json`, run it
through its adapter, score it, and attach control references. No cloud creds, no
database required — which keeps the whole thing demoable on a laptop and testable
in CI. Swapping the file reads for live API calls later doesn't change anything
downstream of the adapter.
"""
from __future__ import annotations

import json
import os
from typing import List, Optional

from app.adapters import REGISTRY
from app.controls import map_controls
from app.models import Finding, Source
from app.scoring import score


def _load_source_file(sample_dir: str, source: Source) -> Optional[dict]:
    path = os.path.join(sample_dir, source.value, "findings.sample.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def enrich(finding: Finding) -> Finding:
    """Score the finding and attach control references (idempotent)."""
    finding.risk_score = score(finding)
    finding.controls = map_controls(finding)
    if not finding.last_seen:
        finding.last_seen = finding.first_seen
    return finding


def ingest(sample_dir: str) -> List[Finding]:
    """Load and enrich findings from every source that has sample data."""
    findings: List[Finding] = []
    for source, adapter_cls in REGISTRY.items():
        payload = _load_source_file(sample_dir, source)
        if not payload:
            continue
        adapter = adapter_cls()
        for finding in adapter.normalize(payload):
            findings.append(enrich(finding))
    # Highest risk first — that's the order I want to fix things in.
    findings.sort(key=lambda f: f.risk_score, reverse=True)
    return findings
