"""AWS adapter: Security Hub / Config-style findings → normalized Finding."""
from __future__ import annotations

from typing import Dict, List

from app.adapters.base import Adapter, derive_criticality, parse_compliance_scope
from app.models import Category, Finding, Severity, Source


def _classify(service: str, title: str) -> Category:
    s = service.lower()
    t = title.lower()
    if "public" in t or "0.0.0.0/0" in t or "publicly" in t:
        return Category.public_exposure
    if s == "iam" or "mfa" in t or "access key" in t or "root account" in t:
        return Category.identity_access
    if "encrypt" in t:
        return Category.encryption
    if s == "cloudtrail" or "logging" in t or "log" in t:
        return Category.logging_monitoring
    if s == "ec2" and ("port" in t or "security group" in t):
        return Category.public_exposure
    return Category.secure_config


class AwsAdapter(Adapter):
    source = Source.aws

    def normalize(self, payload: Dict) -> List[Finding]:
        out: List[Finding] = []
        for raw in payload.get("findings", []):
            service = str(raw.get("service", ""))
            title = str(raw.get("title", ""))
            tags = {str(k): str(v) for k, v in (raw.get("tags") or {}).items()}
            public = bool(raw.get("public", False))
            category = _classify(service, title)
            criticality = derive_criticality(
                env=tags.get("env", ""),
                data_classification=tags.get("data_classification", ""),
                public=public,
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
                    resource_type=service or None,
                    location=raw.get("region"),
                    public_exposure=public,
                    asset_criticality=criticality,
                    exploit_signal=public and category == Category.public_exposure,
                    compliance_scope=parse_compliance_scope(tags.get("compliance")),
                    first_seen=raw.get("first_seen", ""),
                    tags=tags,
                    raw=raw,
                )
            )
        return out
