"""CloudRiskIQ command-line tool.

Same engine as the API, driven from a terminal. Handy for CI, for piping into a
ticketing workflow, or for generating an evidence pack on a schedule without
standing up the web app.

    python -m app.cli ingest                 # load + score, print a summary
    python -m app.cli report                 # print the prioritized findings table
    python -m app.cli evidence --out ./out    # write JSON + Markdown evidence pack
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from app.config import settings
from app.evidence import build_evidence_pack, render_markdown
from app.ingest import ingest
from app.store import FindingsStore


def _hydrate() -> FindingsStore:
    store = FindingsStore()
    store.replace_all(ingest(settings.sample_data_dir))
    return store


def _cmd_ingest(_args) -> int:
    store = _hydrate()
    s = store.summary()
    print(f"Ingested {s.total} findings from {settings.sample_data_dir}")
    print(
        f"  critical {s.by_severity.critical} · high {s.by_severity.high} · "
        f"medium {s.by_severity.medium} · low {s.by_severity.low}"
    )
    print(f"  open critical/high: {s.open_critical_high}")
    print(f"  average risk score: {s.average_risk_score}")
    return 0


def _cmd_report(_args) -> int:
    store = _hydrate()
    print(f"{'RISK':>4}  {'SEV':<8} {'SOURCE':<8} TITLE")
    print("-" * 72)
    for f in store.list():
        print(f"{f.risk_score:>4}  {f.severity.value:<8} {f.source.value:<8} {f.title}")
    return 0


def _cmd_evidence(args) -> int:
    store = _hydrate()
    pack = build_evidence_pack(store)
    os.makedirs(args.out, exist_ok=True)
    json_path = os.path.join(args.out, "evidence-pack.json")
    md_path = os.path.join(args.out, "evidence-pack.md")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(pack))
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="cloudriskiq", description="CloudRiskIQ CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ingest", help="Load + score sample findings and print a summary")
    sub.add_parser("report", help="Print the prioritized findings table")
    ev = sub.add_parser("evidence", help="Write a control evidence pack (JSON + Markdown)")
    ev.add_argument("--out", default="./evidence-out", help="Output directory")

    args = parser.parse_args(argv)
    if args.command == "ingest":
        return _cmd_ingest(args)
    if args.command == "report":
        return _cmd_report(args)
    if args.command == "evidence":
        return _cmd_evidence(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
