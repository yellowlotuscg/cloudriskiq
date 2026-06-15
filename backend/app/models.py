"""Normalized data model for CloudRiskIQ.

Everything the rest of the app touches is a normalized `Finding`. Source-specific
shapes (AWS Security Hub, Defender for Cloud, EDR agents, GitHub alerts) get
converted into this one model at ingest time by the adapters in `app.adapters`.

I keep the model dependency-light (pydantic only) so the API, scoring engine,
control mapper, and evidence exporter all agree on one contract.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Source(str, Enum):
    aws = "aws"
    azure = "azure"
    endpoint = "endpoint"
    github = "github"


class Status(str, Enum):
    open = "open"
    acknowledged = "acknowledged"
    resolved = "resolved"
    suppressed = "suppressed"


class Category(str, Enum):
    """The control-relevant bucket a finding falls into.

    Adapters classify each raw finding into one of these. The control mapper
    (`app.controls`) then translates the category into NIST CSF / CIS / SOX-PCI-
    FISMA control references. This indirection means a new source only has to
    pick a category, not re-map every framework.
    """

    public_exposure = "public_exposure"
    identity_access = "identity_access"
    vulnerability_mgmt = "vulnerability_mgmt"
    secrets_exposure = "secrets_exposure"
    encryption = "encryption"
    secure_config = "secure_config"
    logging_monitoring = "logging_monitoring"
    change_management = "change_management"
    endpoint_protection = "endpoint_protection"


class ControlRef(BaseModel):
    """A single control reference in one framework."""

    framework: str  # e.g. "NIST CSF 2.0", "CIS v8", "PCI-DSS v4.0"
    control_id: str  # e.g. "PR.DS-01", "3.11", "3.4.1"
    title: str


class Finding(BaseModel):
    """One normalized security finding."""

    id: str
    source: Source
    external_id: str
    title: str
    severity: Severity
    category: Category
    resource: str
    resource_type: Optional[str] = None
    location: Optional[str] = None
    status: Status = Status.open

    # Context the scoring engine uses (set by adapters from source fields/tags).
    public_exposure: bool = False
    asset_criticality: str = "medium"  # low | medium | high
    exploit_signal: bool = False  # known CVE, leaked secret, open admin port, etc.
    compliance_scope: List[str] = Field(default_factory=list)  # pci | sox | fisma

    first_seen: str  # ISO-8601 UTC
    last_seen: Optional[str] = None

    # Filled by the pipeline (scoring + control mapping), not by adapters.
    risk_score: int = 0
    controls: List[ControlRef] = Field(default_factory=list)

    tags: Dict[str, str] = Field(default_factory=dict)
    raw: Dict = Field(default_factory=dict)


# ---- API response shapes -------------------------------------------------

class FindingList(BaseModel):
    items: List[Finding]
    total: int


class SeverityCount(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class Summary(BaseModel):
    total: int
    by_source: Dict[str, int]
    by_severity: SeverityCount
    by_status: Dict[str, int]
    by_category: Dict[str, int]
    open_critical_high: int
    average_risk_score: float
    top_findings: List[Finding]


class FrameworkCoverage(BaseModel):
    framework: str
    control_id: str
    title: str
    finding_count: int
    max_risk_score: int
    finding_ids: List[str]


class ControlCoverage(BaseModel):
    frameworks: List[str]
    controls: List[FrameworkCoverage]
