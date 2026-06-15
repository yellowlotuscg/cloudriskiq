"""Source ingestion adapters.

Each adapter takes one source's raw payload and returns normalized `Finding`s.
The rest of the system never sees source-specific shapes — that's the contract.
"""
from __future__ import annotations

from typing import Dict, Type

from app.adapters.aws import AwsAdapter
from app.adapters.azure import AzureAdapter
from app.adapters.base import Adapter
from app.adapters.endpoint import EndpointAdapter
from app.adapters.github import GitHubAdapter
from app.models import Source

REGISTRY: Dict[Source, Type[Adapter]] = {
    Source.aws: AwsAdapter,
    Source.azure: AzureAdapter,
    Source.endpoint: EndpointAdapter,
    Source.github: GitHubAdapter,
}

__all__ = ["Adapter", "REGISTRY", "AwsAdapter", "AzureAdapter", "EndpointAdapter", "GitHubAdapter"]
