"""
Seed the SQLite database from:
  - The TREE / MAPPING dicts defined in build_categories.py
  - The raw supplier CSV in raw/

Run once (or re-run with --reset to wipe and re-seed):
    python3 seed.py
    python3 seed.py --reset
"""

import csv
import sys
from pathlib import Path

# Import tree + mapping data from the existing script.
# build_categories.py executes module-level code that builds TREE and MAPPING,
# but stops before calling main() / serve() because those are guarded by if __name__=="__main__".
import build_categories as bc

from db import init_db, get_conn, DB_PATH

RAW_DIR = Path(__file__).parent / "raw"


def seed(reset: bool = False):
    if reset and DB_PATH.exists():
        DB_PATH.unlink()
        print("Wiped existing database.")

    init_db()

    with get_conn() as conn:
        existing = conn.execute("SELECT COUNT(*) FROM tree_nodes").fetchone()[0]

    if existing and not reset:
        print(f"DB already has {existing} tree nodes — skipping seed. Use --reset to re-seed.")
        return

    print("Seeding tree nodes …")
    tree_rows = [
        (code, label, parent)
        for code, (label, parent) in bc.TREE.items()
    ]
    with get_conn() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO tree_nodes(code, label, parent_code) VALUES (?,?,?)",
            tree_rows,
        )
    print(f"  Inserted {len(tree_rows)} tree nodes.")

    print("Seeding supplier categories …")
    raw_files = sorted(RAW_DIR.glob("*.csv"))
    if not raw_files:
        print(f"  WARNING: no CSV files found in {RAW_DIR}")
        return

    sc_rows: list[tuple[str, str]] = []
    for path in raw_files:
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                supplier = row["supplier_name"].strip()
                category = row["supplier_category"].strip()
                if supplier and category:
                    sc_rows.append((supplier, category))

    # Deduplicate while preserving order
    seen: set[tuple] = set()
    unique_sc: list[tuple[str, str]] = []
    for row in sc_rows:
        if row not in seen:
            seen.add(row)
            unique_sc.append(row)

    with get_conn() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO supplier_categories(supplier, category) VALUES (?,?)",
            unique_sc,
        )
    print(f"  Inserted {len(unique_sc)} supplier categories from {len(raw_files)} file(s).")

    print("Seeding initial mappings from MAPPING dict …")
    # OVERRIDES from tree_state.json (if it exists) take precedence over MAPPING defaults.
    mapping_rows: list[tuple[str, str, str]] = []
    for supplier, category in unique_sc:
        codes = bc.MAPPING.get(category, [])
        # Apply OVERRIDES from build_categories (populated from tree_state.json on import)
        if category in bc.OVERRIDES:
            codes = bc.OVERRIDES[category]
        for code in codes:
            # normalise through COLLAPSE table + validate against TREE
            c = bc.normalise(code)
            if c in bc.TREE:
                mapping_rows.append((supplier, category, c))

    # Deduplicate
    unique_mappings = list(set(mapping_rows))
    with get_conn() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO mappings(supplier, category, tree_code) VALUES (?,?,?)",
            unique_mappings,
        )
    print(f"  Inserted {len(unique_mappings)} mapping rows.")

    # Seed tree state from existing tree_state.json if present
    state_file = Path(__file__).parent / "output" / "tree_state.json"
    if state_file.exists():
        import json
        state = json.loads(state_file.read_text(encoding="utf-8"))
        with get_conn() as conn:
            for key in ("confirmed", "deleted", "order"):
                if key in state:
                    conn.execute(
                        "INSERT OR REPLACE INTO tree_state(key, value) VALUES (?,?)",
                        (key, json.dumps(state[key])),
                    )
        print(f"  Loaded tree state (confirmed/deleted/order) from tree_state.json.")

    print("Done.")


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
