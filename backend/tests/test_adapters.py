"""Tests for the source adapters' normalization."""
from app.adapters import AwsAdapter, AzureAdapter, EndpointAdapter, GitHubAdapter
from app.adapters.base import derive_criticality, parse_compliance_scope
from app.models import Category, Severity, Source


def test_parse_compliance_scope_handles_string_and_list():
    assert parse_compliance_scope("pci,sox") == ["pci", "sox"]
    assert parse_compliance_scope(["PCI", "fisma", "unknown"]) == ["pci", "fisma"]
    assert parse_compliance_scope(None) == []


def test_derive_criticality():
    assert derive_criticality(env="prod", data_classification="cardholder") == "high"
    assert derive_criticality(env="dev") == "low"
    assert derive_criticality(env="prod", public=True) == "high"


def test_aws_adapter_normalizes_and_classifies():
    payload = {
        "findings": [
            {
                "id": "aws-x",
                "service": "s3",
                "resource": "arn:aws:s3:::b",
                "title": "S3 bucket allows public read",
                "severity": "high",
                "region": "us-east-1",
                "public": True,
                "first_seen": "2026-06-01T00:00:00Z",
                "tags": {"env": "prod", "compliance": "pci,sox"},
            }
        ]
    }
    findings = AwsAdapter().normalize(payload)
    assert len(findings) == 1
    f = findings[0]
    assert f.source == Source.aws
    assert f.category == Category.public_exposure
    assert f.public_exposure is True
    assert f.compliance_scope == ["pci", "sox"]
    assert f.severity == Severity.high


def test_azure_adapter_classifies_encryption():
    payload = {
        "findings": [
            {
                "id": "az-x",
                "resource_type": "Microsoft.Sql/servers/databases",
                "resource": "/db",
                "title": "SQL database Transparent Data Encryption (TDE) is disabled",
                "severity": "high",
                "location": "eastus",
                "labels": {"env": "prod", "compliance": "pci"},
            }
        ]
    }
    f = AzureAdapter().normalize(payload)[0]
    assert f.category == Category.encryption
    assert f.compliance_scope == ["pci"]


def test_github_adapter_flags_leaked_secret_as_exploit():
    payload = {
        "findings": [
            {
                "id": "gh-x",
                "repo": "o/r",
                "type": "secret_scanning",
                "title": "Committed AWS access key detected",
                "severity": "critical",
                "path": "x.env",
                "public_repo": True,
                "first_seen": "2026-06-01T00:00:00Z",
            }
        ]
    }
    f = GitHubAdapter().normalize(payload)[0]
    assert f.category == Category.secrets_exposure
    assert f.exploit_signal is True


def test_endpoint_adapter_classifies_encryption_and_vuln():
    payload = {
        "findings": [
            {"id": "ep-1", "hostname": "h", "title": "Disk encryption (FileVault) disabled", "severity": "high", "first_seen": "2026-06-01T00:00:00Z"},
            {"id": "ep-2", "hostname": "h2", "title": "Outdated OpenSSL with known CVE", "severity": "medium", "cve": "CVE-1", "first_seen": "2026-06-01T00:00:00Z"},
        ]
    }
    findings = {f.id: f for f in EndpointAdapter().normalize(payload)}
    assert findings["ep-1"].category == Category.encryption
    assert findings["ep-2"].category == Category.vulnerability_mgmt
    assert findings["ep-2"].exploit_signal is True
