"""Endpoint adapter: EDR / device-posture agent output → normalized Finding."""
from __future__ import annotations

from typing import Dict, List

from app.adapters.base import Adapter
from app.models import Category, Finding, Severity, Source


def _classify(title: str) -> Category:
    t = title.lower()
    if "encryption" in t or "filevault" in t or "bitlocker" in t:
        return Category.encryption
    if "cve" in t or "outdated" in t or "patch" in t:
        return Category.vulnerability_mgmt
    if "edr" in t or "endpoint protection" in t or "antivirus" in t or "malware" in t:
        return Category.endpoint_protection
    if "administrator" in t or "admin account" in t:
        return Category.identity_access
    return Category.secure_config


class EndpointAdapter(Adapter):
    source = Source.endpoint

    def normalize(self, payload: Dict) -> List[Finding]:
        out: List[Finding] = []
        for raw in payload.get("findings", []):
            title = str(raw.get("title", ""))
            category = _classify(title)
            internet_facing = bool(raw.get("internet_facing", False))
            has_cve = bool(raw.get("cve"))
            owner = str(raw.get("owner_group", "")).lower()
            # Finance/platform-owned hosts treated as higher criticality.
            criticality = "high" if owner in {"finance", "platform"} else "medium"
            out.append(
                Finding(
                    id=raw["id"],
                    source=self.source,
                    external_id=raw["id"],
                    title=title,
                    severity=Severity(raw.get("severity", "medium")),
                    category=category,
                    resource=str(raw.get("hostname", "")),
                    resource_type="host",
                    location=raw.get("os"),
                    public_exposure=internet_facing,
                    asset_criticality=criticality,
                    exploit_signal=has_cve or (internet_facing and category == Category.vulnerability_mgmt),
                    compliance_scope=[],
                    first_seen=raw.get("first_seen", ""),
                    tags={"owner_group": owner} if owner else {},
                    raw=raw,
                )
            )
        return out
