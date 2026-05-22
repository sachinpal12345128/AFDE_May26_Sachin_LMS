"""
Orchestrator — run the full Extract / Transform / Load pipeline.

Usage (from the project root):
    python -m etl.run_etl
or:
    python etl/run_etl.py

The script prints a summary table and exits with code 0 on success.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime

import pandas as pd

from . import extract, load, transform
from .config import REPORTS_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(name)s: %(message)s",
)
log = logging.getLogger("etl")


def main() -> int:
    log.info("=" * 70)
    log.info("Library Management System — Phase 2 ETL Pipeline")
    log.info("=" * 70)

    # ---------- EXTRACT ----------
    log.info("[1/3] Extract")
    raw = extract.extract_all()
    raw_counts = {k: len(v) for k, v in raw.items()}

    # ---------- TRANSFORM ----------
    log.info("[2/3] Transform")
    books = transform.clean_books(raw["books"])
    borrowers = transform.clean_borrowers(raw["borrowers"])
    transactions = transform.clean_transactions(raw["transactions"], books, borrowers)
    analytics = transform.build_analytics(books, borrowers, transactions)

    clean_counts = {
        "books": len(books),
        "borrowers": len(borrowers),
        "transactions": len(transactions),
    }

    # ---------- LOAD ----------
    log.info("[3/3] Load")
    load.load_operational(books, borrowers, transactions)
    load.load_analytics(analytics)
    run_id = load.log_run(raw_counts, clean_counts, notes="full pipeline run")

    # ---------- Persist CSV snapshots (handy for screenshots / debugging) ----------
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = REPORTS_DIR / stamp
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    books.to_csv(snapshot_dir / "books_clean.csv", index=False)
    borrowers.to_csv(snapshot_dir / "borrowers_clean.csv", index=False)
    transactions.to_csv(snapshot_dir / "transactions_clean.csv", index=False)
    for name, df in analytics.items():
        df.to_csv(snapshot_dir / f"analytics_{name}.csv", index=False)

    summary = {
        "run_id": run_id,
        "timestamp": stamp,
        "raw_counts": raw_counts,
        "clean_counts": clean_counts,
        "analytics_counts": {k: len(v) for k, v in analytics.items()},
        "snapshot_dir": str(snapshot_dir),
    }
    (snapshot_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    # ---------- Console summary ----------
    print()
    print("ETL run complete")
    print("-" * 70)
    print(f"{'Stage':22} {'Raw':>10} {'Cleaned':>10}")
    print("-" * 70)
    for key in ("books", "borrowers", "transactions"):
        print(f"{key:22} {raw_counts[key]:>10} {clean_counts[key]:>10}")
    print("-" * 70)
    print("Analytics tables built:")
    for k, v in analytics.items():
        print(f"  analytics_{k:22} rows = {len(v)}")
    print(f"\nSnapshot written to: {snapshot_dir}")
    print(f"ETL run id: {run_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
