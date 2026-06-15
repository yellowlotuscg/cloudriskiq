"""Control mapping: findings → frameworks.

This is the piece that turns a pile of technical findings into something I can
put in front of an auditor. Every finding is classified into a `Category` by its
adapter; here I map each category to the controls it touches across:

  * **NIST CSF 2.0** and **CIS Controls v8**, applied to everything, since they're
    the hardening baseline I work from regardless of regime.
  * **PCI-DSS v4.0**, **SOX ITGC**, and **FISMA / NIST SP 800-53 Rev 5**, applied
    only when the finding is tagged in that compliance scope, so a PCI control
    doesn't show up against a box that never touches cardholder data.

The mapping is intentionally a readable lookup table, not magic. When I sat as the
primary contact for SOX/PCI/FISMA audits, the questions were always "which control
does this map to, and show me the evidence", so that traceability is the whole
point of this module.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from app.models import Category, ControlRef, Finding

# Baseline frameworks applied to every finding, keyed by category.
# Each entry: (framework, control_id, title)
_BASELINE: Dict[Category, List[Tuple[str, str, str]]] = {
    Category.public_exposure: [
        ("NIST CSF 2.0", "PR.IR-01", "Networks and environments are protected from unauthorized access"),
        ("CIS v8", "12.3", "Securely manage network infrastructure"),
    ],
    Category.identity_access: [
        ("NIST CSF 2.0", "PR.AA-01", "Identities and credentials are managed"),
        ("CIS v8", "5.3", "Disable dormant accounts"),
        ("CIS v8", "6.5", "Require MFA for administrative access"),
    ],
    Category.vulnerability_mgmt: [
        ("NIST CSF 2.0", "ID.RA-01", "Vulnerabilities in assets are identified and recorded"),
        ("CIS v8", "7.4", "Perform automated application patch management"),
    ],
    Category.secrets_exposure: [
        ("NIST CSF 2.0", "PR.AA-02", "Identities are proofed and bound to credentials"),
        ("CIS v8", "16.4", "Establish and manage an inventory of secrets"),
    ],
    Category.encryption: [
        ("NIST CSF 2.0", "PR.DS-01", "The confidentiality of data-at-rest is protected"),
        ("CIS v8", "3.11", "Encrypt sensitive data at rest"),
    ],
    Category.secure_config: [
        ("NIST CSF 2.0", "PR.PS-01", "Configuration management practices are established"),
        ("CIS v8", "4.1", "Establish and maintain a secure configuration process"),
    ],
    Category.logging_monitoring: [
        ("NIST CSF 2.0", "DE.CM-01", "Networks and services are monitored to find adverse events"),
        ("CIS v8", "8.2", "Collect audit logs"),
    ],
    Category.change_management: [
        ("NIST CSF 2.0", "PR.PS-01", "Configuration management practices are established"),
        ("CIS v8", "16.1", "Establish and maintain a secure development process"),
    ],
    Category.endpoint_protection: [
        ("NIST CSF 2.0", "PR.PS-05", "Installation and execution of unauthorized software is prevented"),
        ("CIS v8", "10.1", "Deploy and maintain anti-malware software"),
    ],
}

# Regulatory frameworks applied only when the regime is in the finding's
# compliance_scope. Keyed by (regime, category).
_COMPLIANCE: Dict[Tuple[str, Category], List[Tuple[str, str, str]]] = {
    # ---- PCI-DSS v4.0 ----
    ("pci", Category.public_exposure): [("PCI-DSS v4.0", "1.3", "Restrict inbound/outbound traffic to the CDE")],
    ("pci", Category.identity_access): [("PCI-DSS v4.0", "8.3", "Strong authentication for users and administrators")],
    ("pci", Category.encryption): [("PCI-DSS v4.0", "3.5", "Protect stored account data (render PAN unreadable)")],
    ("pci", Category.vulnerability_mgmt): [("PCI-DSS v4.0", "6.3", "Identify and address security vulnerabilities")],
    ("pci", Category.secrets_exposure): [("PCI-DSS v4.0", "8.6", "Manage application/system accounts and credentials")],
    ("pci", Category.secure_config): [("PCI-DSS v4.0", "2.2", "Configure system components securely")],
    ("pci", Category.logging_monitoring): [("PCI-DSS v4.0", "10.2", "Implement audit logs to reconstruct events")],
    ("pci", Category.endpoint_protection): [("PCI-DSS v4.0", "5.2", "Deploy and maintain anti-malware solutions")],
    ("pci", Category.change_management): [("PCI-DSS v4.0", "6.5", "Manage changes to system components")],
    # ---- SOX ITGC ----
    ("sox", Category.identity_access): [("SOX ITGC", "AC", "Access to Programs and Data: logical access controls")],
    ("sox", Category.change_management): [("SOX ITGC", "CM", "Change Management: authorized, tested changes")],
    ("sox", Category.logging_monitoring): [("SOX ITGC", "CO", "Computer Operations: monitoring and logging")],
    ("sox", Category.secure_config): [("SOX ITGC", "AC", "Access to Programs and Data: secure configuration")],
    ("sox", Category.encryption): [("SOX ITGC", "AC", "Access to Programs and Data: data protection")],
    ("sox", Category.secrets_exposure): [("SOX ITGC", "AC", "Access to Programs and Data: credential protection")],
    ("sox", Category.public_exposure): [("SOX ITGC", "AC", "Access to Programs and Data: network exposure")],
    ("sox", Category.vulnerability_mgmt): [("SOX ITGC", "CO", "Computer Operations: patch and vulnerability mgmt")],
    # ---- FISMA / NIST SP 800-53 Rev 5 ----
    ("fisma", Category.public_exposure): [("NIST 800-53 Rev5", "SC-7", "Boundary Protection")],
    ("fisma", Category.identity_access): [("NIST 800-53 Rev5", "AC-2", "Account Management"), ("NIST 800-53 Rev5", "IA-2", "Identification and Authentication")],
    ("fisma", Category.encryption): [("NIST 800-53 Rev5", "SC-28", "Protection of Information at Rest")],
    ("fisma", Category.vulnerability_mgmt): [("NIST 800-53 Rev5", "RA-5", "Vulnerability Monitoring and Scanning"), ("NIST 800-53 Rev5", "SI-2", "Flaw Remediation")],
    ("fisma", Category.secrets_exposure): [("NIST 800-53 Rev5", "IA-5", "Authenticator Management")],
    ("fisma", Category.secure_config): [("NIST 800-53 Rev5", "CM-6", "Configuration Settings")],
    ("fisma", Category.logging_monitoring): [("NIST 800-53 Rev5", "AU-6", "Audit Record Review, Analysis, and Reporting")],
    ("fisma", Category.change_management): [("NIST 800-53 Rev5", "CM-3", "Configuration Change Control")],
    ("fisma", Category.endpoint_protection): [("NIST 800-53 Rev5", "SI-3", "Malicious Code Protection")],
}


def map_controls(finding: Finding) -> List[ControlRef]:
    """Return all control references a finding maps to (baseline + in-scope regimes)."""
    refs: List[ControlRef] = []
    for fw, cid, title in _BASELINE.get(finding.category, []):
        refs.append(ControlRef(framework=fw, control_id=cid, title=title))
    for regime in finding.compliance_scope:
        for fw, cid, title in _COMPLIANCE.get((regime, finding.category), []):
            refs.append(ControlRef(framework=fw, control_id=cid, title=title))
    return refs


def frameworks_in_use() -> List[str]:
    """All frameworks this catalog can emit, for the coverage report header."""
    names = set()
    for entries in _BASELINE.values():
        for fw, _, _ in entries:
            names.add(fw)
    for entries in _COMPLIANCE.values():
        for fw, _, _ in entries:
            names.add(fw)
    return sorted(names)
