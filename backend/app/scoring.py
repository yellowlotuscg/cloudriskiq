"""Risk scoring engine.

A raw severity label ("high") isn't a priority on its own. A "high" on a public,
production, cardholder-data resource that's been open for two months is not the
same as a "high" on an internal dev box from yesterday. This engine starts from
the severity base score and adjusts it by the context the adapters captured, so
the dashboard can answer the only question that matters at standup: *what do I
fix first?*

Output is clamped to 0-100. The weighting is deliberately simple and explainable.
I'd rather defend a transparent model to an auditor than ship a black box.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.models import Finding, Severity

# Base score per severity (matches docs/data-model.md).
_BASE = {
    Severity.low: 25,
    Severity.medium: 50,
    Severity.high: 75,
    Severity.critical: 90,
}

# Additive context modifiers.
_PUBLIC_EXPOSURE_BONUS = 10
_EXPLOIT_SIGNAL_BONUS = 8
_CRITICALITY_BONUS = {"low": -5, "medium": 0, "high": 8}
_COMPLIANCE_BONUS_PER_SCOPE = 3  # pci/sox/fisma in scope => regulatory pressure
_COMPLIANCE_BONUS_CAP = 6

# Age: an open finding that lingers is a worse risk than a fresh one.
_AGE_BONUS_30D = 3
_AGE_BONUS_60D = 6
_AGE_BONUS_90D = 9


def _parse_ts(ts: str) -> datetime:
    # Tolerate trailing "Z".
    cleaned = ts.replace("Z", "+00:00")
    dt = datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _age_bonus(first_seen: str, now: datetime) -> int:
    try:
        age_days = (now - _parse_ts(first_seen)).days
    except (ValueError, TypeError):
        return 0
    if age_days >= 90:
        return _AGE_BONUS_90D
    if age_days >= 60:
        return _AGE_BONUS_60D
    if age_days >= 30:
        return _AGE_BONUS_30D
    return 0


def score(finding: Finding, now: datetime = None) -> int:
    """Compute the 0-100 risk score for a finding."""
    if now is None:
        now = datetime.now(timezone.utc)

    value = _BASE[finding.severity]

    if finding.public_exposure:
        value += _PUBLIC_EXPOSURE_BONUS
    if finding.exploit_signal:
        value += _EXPLOIT_SIGNAL_BONUS

    value += _CRITICALITY_BONUS.get(finding.asset_criticality, 0)

    if finding.compliance_scope:
        value += min(
            len(finding.compliance_scope) * _COMPLIANCE_BONUS_PER_SCOPE,
            _COMPLIANCE_BONUS_CAP,
        )

    value += _age_bonus(finding.first_seen, now)

    return max(0, min(100, value))
