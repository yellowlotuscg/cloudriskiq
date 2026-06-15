"""Azure adapter: Defender for Cloud-style assessments → normalized Finding."""
from __future__ import annotations

from typing import Dict, List

from app.adapters.base import Adapter, derive_criticality, parse_compliance_scope
from app.models import Category, Finding, Severity, Source


def _classify(resource_type: str, title: str) -> Category:
    rt = resource_type.lower()
    t = title.lower()
    if "public" in t or "0.0.0.0/0" in t or "internet" in t:
        return Category.public_exposure
    if "encryption" in t or "tde" in t:
        return Category.encryption
    if "logging" in t or "diagnostic" in t or "log" in t:
        return Category.logging_monitoring
    if "keyvault" in rt or "soft-delete" in t or "purge" in t:
        return Category.secure_config
    if "networksecuritygroups" in rt:
        return Category.public_exposure
    return Category.secure_config


class AzureAdapter(Adapter):
    source = Source.azure

    def normalize(self, payload: Dict) -> List[Finding]:
        out: List[Finding] = []
        for raw in payload.get("findings", []):
            resource_type = str(raw.get("resource_type", ""))
            title = str(raw.get("title", ""))
            labels = {str(k): str(v) for k, v in (raw.get("labels") or {}).items()}
            exposed = bool(raw.get("exposed_to_internet", False))
            category = _classify(resource_type, title)
            criticality = derive_criticality(
                env=labels.get("env", ""),
                data_classification=labels.get("data_classification", ""),
                public=exposed,
            )
            out.append(
                Finding(
                    id=raw["id"],
                    source=self.source,
                    external_id=raw["id"],
                    title=title,
                    severity=Severity(raw.get("severity", "medium")),
                    category=category,
                    resource=str(raw.get("resource", "")),
                    resource_type=resource_type or None,
                    location=raw.get("location"),
                    public_exposure=exposed,
                    asset_criticality=criticality,
                    exploit_signal=exposed and category == Category.public_exposure,
                    compliance_scope=parse_compliance_scope(labels.get("compliance")),
                    first_seen=raw.get("first_seen", ""),
                    tags=labels,
                    raw=raw,
                )
            )
        return out
