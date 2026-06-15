"""CloudRiskIQ FastAPI application entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8000
Then:
    curl http://localhost:8000/health           -> {"status": "ok", ...}
    curl http://localhost:8000/findings          -> prioritized findings
    curl http://localhost:8000/summary           -> dashboard rollups
    curl http://localhost:8000/controls          -> framework coverage
    curl http://localhost:8000/evidence          -> audit evidence pack

The findings store is hydrated from sample-data at startup, so the whole API is
usable offline with no cloud creds and no database.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import settings
from app.evidence import build_evidence_pack
from app.ingest import ingest
from app.models import (
    ControlCoverage,
    Finding,
    FindingList,
    Severity,
    Source,
    Status,
    Summary,
)
from app.store import store


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Load + score + control-map the sample findings into the in-memory store.
    store.replace_all(ingest(settings.sample_data_dir))
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="Aggregates and scores cloud + endpoint + source-control security findings, and maps them to NIST CSF / CIS / SOX-PCI-FISMA controls.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- system -------------------------------------------------------------

@app.get("/health", tags=["system"])
def health() -> dict:
    """Liveness probe. Intentionally has no external dependencies."""
    return {
        "status": "ok",
        "service": "cloudriskiq-api",
        "version": __version__,
        "environment": settings.environment,
    }


@app.get("/", tags=["system"])
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "findings_loaded": store.count(),
    }


# ---- findings -----------------------------------------------------------

@app.get("/findings", response_model=FindingList, tags=["findings"])
def list_findings(
    source: Optional[Source] = None,
    severity: Optional[Severity] = None,
    status: Optional[Status] = None,
    min_score: Optional[int] = Query(default=None, ge=0, le=100),
) -> FindingList:
    """List findings (highest risk first), with optional filters."""
    items = store.list(source=source, severity=severity, status=status, min_score=min_score)
    return FindingList(items=items, total=len(items))


@app.get("/findings/{finding_id}", response_model=Finding, tags=["findings"])
def get_finding(finding_id: str) -> Finding:
    finding = store.get(finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="finding not found")
    return finding


@app.patch("/findings/{finding_id}", response_model=Finding, tags=["findings"])
def update_finding_status(finding_id: str, status: Status) -> Finding:
    """Update a finding's status (acknowledge / resolve / suppress)."""
    finding = store.set_status(finding_id, status)
    if finding is None:
        raise HTTPException(status_code=404, detail="finding not found")
    return finding


# ---- rollups ------------------------------------------------------------

@app.get("/summary", response_model=Summary, tags=["dashboard"])
def summary() -> Summary:
    """Counts by source / severity / status / category for the dashboard."""
    return store.summary()


@app.get("/controls", response_model=ControlCoverage, tags=["compliance"])
def controls() -> ControlCoverage:
    """Control coverage: findings rolled up per NIST CSF / CIS / PCI / SOX / FISMA control."""
    return store.control_coverage()


@app.get("/evidence", tags=["compliance"])
def evidence() -> dict:
    """A structured control evidence pack for an audit binder."""
    return build_evidence_pack(store)


@app.post("/ingest", tags=["system"])
def reingest() -> dict:
    """Re-run ingestion from sample-data (re-reads files, re-scores, re-maps)."""
    store.replace_all(ingest(settings.sample_data_dir))
    return {"reingested": store.count()}
