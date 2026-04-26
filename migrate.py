"""
Tiny migrations runner.

A migration is a Python file in migrations/ named NNN_short_name.py that
exposes an `apply(conn)` function. Files are applied in numeric order; each
applied filename is recorded in the _migrations table so it never re-runs.

Run any time after pulling new code:
    python3 migrate.py

Status only:
    python3 migrate.py --status
"""
import argparse
import importlib.util
import sys
from pathlib import Path

import db


MIG_DIR = Path(__file__).parent / "migrations"


def _list_migrations():
    return sorted(p for p in MIG_DIR.glob("[0-9][0-9][0-9]_*.py"))


def _ensure_table(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS _migrations (
        name      TEXT PRIMARY KEY,
        applied_at TEXT NOT NULL DEFAULT (datetime('now'))
    )""")


def _applied(conn) -> set:
    return {r[0] for r in conn.execute("SELECT name FROM _migrations").fetchall()}


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def status() -> int:
    with db.get_conn() as conn:
        _ensure_table(conn)
        done = _applied(conn)
    files = _list_migrations()
    if not files:
        print("No migrations on disk.")
        return 0
    for p in files:
        mark = "[x]" if p.name in done else "[ ]"
        print(f"  {mark} {p.name}")
    pending = [p for p in files if p.name not in done]
    print(f"\n{len(pending)} pending of {len(files)} total.")
    return 0


def apply_pending() -> int:
    with db.get_conn() as conn:
        _ensure_table(conn)
        done = _applied(conn)
    pending = [p for p in _list_migrations() if p.name not in done]
    if not pending:
        print("Nothing to migrate.")
        return 0
    for path in pending:
        print(f"applying {path.name} ...")
        mod = _load(path)
        with db.get_conn() as conn:
            mod.apply(conn)
            conn.execute("INSERT INTO _migrations(name) VALUES (?)", (path.name,))
        print(f"  ok")
    print(f"\nApplied {len(pending)} migration(s).")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    if args.status:
        return status()
    return apply_pending()


if __name__ == "__main__":
    sys.exit(main())
