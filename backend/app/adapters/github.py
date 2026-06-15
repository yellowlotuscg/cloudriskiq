"""GitHub adapter: secret-scanning / Dependabot / code-scanning → normalized Finding."""
from __future__ import annotations

from typing import Dict, List

from app.adapters.base import Adapter, parse_compliance_scope
from app.models import Category, Finding, Severity, Source


def _classify(alert_type: str, title: str) -> Category:
    a = alert_type.lower()
    t = title.lower()
    if a == "secret_scanning" or "secret" in t or "access key" in t:
        return Category.secrets_exposure
    if a == "dependabot" or "dependency" in t or "vulnerable" in t:
        return Category.vulnerability_mgmt
    if "branch protection" in t or a == "config":
        return Category.change_management
    if a == "code_scanning":
        return Category.secrets_exposure if "secret" in t else Category.vulnerability_mgmt
    return Category.secure_config


class GitHubAdapter(Adapter):
    source = Source.github

    def normalize(self, payload: Dict) -> List[Finding]:
        out: List[Finding] = []
        for raw in payload.get("findings", []):
            alert_type = str(raw.get("type", ""))
            title = str(raw.get("title", ""))
            topics = [str(x).lower() for x in (raw.get("topics") or [])]
            public_repo = bool(raw.get("public_repo", False))
            category = _classify(alert_type, title)
            has_cve = bool(raw.get("cve"))
            is_secret = category == Category.secrets_exposure
            # A leaked secret in a public repo, or an exploitable CVE, is a live signal.
            exploit = (is_secret and public_repo) or has_cve
            criticality = "high" if "prod" in topics else "medium"
            out.append(
                Finding(
                    id=raw["id"],
                    source=self.source,
                    external_id=raw["id"],
                    title=title,
                    severity=Severity(raw.get("severity", "medium")),
                    category=category,
                    resource=str(raw.get("repo", "")) + (("/" + raw["path"]) if raw.get("path") else ""),
                    resource_type=alert_type or None,
                    location=raw.get("ecosystem"),
                    public_exposure=public_repo and is_secret,
                    asset_criticality=criticality,
                    exploit_signal=exploit,
                    compliance_scope=parse_compliance_scope([x for x in topics if x in {"pci", "sox", "fisma"}]),
                    first_seen=raw.get("first_seen", ""),
                    tags={"repo": str(raw.get("repo", ""))},
                    raw=raw,
                )
            )
        return out
