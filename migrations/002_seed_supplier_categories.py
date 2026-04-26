"""
Seed supplier_categories from the raw/ CSV files (the original source data
provided by suppliers). Idempotent on (supplier, category) unique constraint.
"""
import csv
from pathlib import Path

import psycopg2.extras


RAW_DIR = Path(__file__).resolve().parent.parent / "raw"


def apply(conn):
    rows = []
    seen = set()
    for path in sorted(RAW_DIR.glob("*.csv")):
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                sup = (row.get("supplier_name") or "").strip()
                cat = (row.get("supplier_category") or "").strip()
                if not (sup and cat):
                    continue
                key = (sup, cat)
                if key in seen:
                    continue
                seen.add(key)
                rows.append((sup, cat))

    if not rows:
        print("  no supplier rows found in raw/")
        return

    with conn.cursor() as cur:
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO supplier_categories(supplier, category) VALUES %s "
            "ON CONFLICT (supplier, category) DO NOTHING",
            rows)
    print(f"  seeded {len(rows)} supplier_categories from raw/")
