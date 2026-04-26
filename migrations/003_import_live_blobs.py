"""
One-shot import of the final Netlify Blobs snapshot into Postgres.

Imports tree_nodes, supmap (mappings), tree_state (deleted, confirmed,
content_confirmed, order, renames) and any per-field SEO that lived in
Blobs and isn't already in tree_nodes.

After this migration runs successfully on each environment, the
_live_snapshot.json file can be deleted; the data lives in Postgres.

Idempotent: skips silently if mappings already has rows.
"""
import json
from pathlib import Path

import psycopg2.extras


SNAPSHOT = Path(__file__).resolve().parent / "_live_snapshot.json"


def apply(conn):
    if not SNAPSHOT.exists():
        print("  no _live_snapshot.json on disk, skipping")
        return

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM mappings")
        if cur.fetchone()[0] > 0:
            print("  mappings already populated, skipping live import")
            return

    state = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    # ── tree_nodes ───────────────────────────────────────────────────────
    nodes = state.get("tree_nodes") or []
    rows = [(n["code"], n["label"], n.get("parent_code")) for n in nodes]
    with conn.cursor() as cur:
        if rows:
            psycopg2.extras.execute_values(
                cur,
                "INSERT INTO tree_nodes(code, label, parent_code) VALUES %s "
                "ON CONFLICT (code) DO UPDATE SET label = EXCLUDED.label, "
                "parent_code = EXCLUDED.parent_code",
                rows)
    print(f"  upserted {len(rows)} tree_nodes")

    # ── per-field SEO from Blobs (only non-empty fields) ────────────────
    seo = state.get("seo") or {}
    seo_field_cols = ("name_lv", "slug_lv", "slug_en",
                      "seo_desc_lv", "seo_desc_en", "meta_desc_lv", "meta_desc_en")
    written = 0
    with conn.cursor() as cur:
        for code, fields in seo.items():
            sets, vals = [], []
            for k in seo_field_cols:
                v = (fields or {}).get(k)
                if isinstance(v, str) and v.strip():
                    sets.append(f"{k} = %s")
                    vals.append(v)
            if not sets:
                continue
            vals.append(code)
            cur.execute(f"UPDATE tree_nodes SET {', '.join(sets)} WHERE code = %s", vals)
            written += 1
    print(f"  updated SEO fields on {written} nodes")

    # ── mappings ─────────────────────────────────────────────────────────
    live_codes = {n["code"] for n in nodes}
    map_rows, dropped = [], 0
    for key, codes in (state.get("supmap") or {}).items():
        if "||" not in key: continue
        sup, cat = key.split("||", 1)
        for code in codes or []:
            if code in live_codes:
                map_rows.append((sup, cat, code))
            else:
                dropped += 1
    with conn.cursor() as cur:
        if map_rows:
            psycopg2.extras.execute_values(
                cur,
                "INSERT INTO mappings(supplier, category, tree_code) VALUES %s "
                "ON CONFLICT DO NOTHING",
                map_rows)
    print(f"  imported {len(map_rows)} mappings, dropped {dropped} orphans")

    # ── tree_state (lists / dicts) ───────────────────────────────────────
    upserts = {
        "deleted":           sorted(set(state.get("deleted") or [])),
        "confirmed":         sorted(set(state.get("confirmed") or [])),
        "content_confirmed": sorted(set(state.get("content_confirmed") or [])),
        "order":             state.get("order")   or {},
        "renames":           state.get("renames") or {},
    }
    with conn.cursor() as cur:
        for key, value in upserts.items():
            cur.execute(
                "INSERT INTO tree_state(key, value) VALUES (%s, %s) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                (key, json.dumps(value)))
    print(f"  upserted {len(upserts)} tree_state entries")
