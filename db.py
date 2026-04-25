import sqlite3
import json
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "category.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# Columns added to tree_nodes after the initial schema. Kept as a list so init_db
# can apply each one idempotently via ALTER TABLE — safe to re-run and safe to
# deploy against an older DB that already has data.
SEO_COLUMNS = [
    ("name_lv",     "TEXT"),
    ("name_en",     "TEXT"),
    ("slug_lv",     "TEXT"),
    ("slug_en",     "TEXT"),
    ("seo_desc_lv", "TEXT"),
    ("seo_desc_en", "TEXT"),
]


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tree_nodes (
                code       TEXT PRIMARY KEY,
                label      TEXT NOT NULL,
                parent_code TEXT
            );

            CREATE TABLE IF NOT EXISTS supplier_categories (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier TEXT NOT NULL,
                category TEXT NOT NULL,
                UNIQUE(supplier, category)
            );

            -- Current mappings: one row per (supplier, category, tree_code) triple.
            -- Cleared and rebuilt on every save.
            CREATE TABLE IF NOT EXISTS mappings (
                supplier  TEXT NOT NULL,
                category  TEXT NOT NULL,
                tree_code TEXT NOT NULL,
                PRIMARY KEY (supplier, category, tree_code)
            );

            -- Tree editor state: confirmed nodes, deleted nodes, child order.
            CREATE TABLE IF NOT EXISTS tree_state (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_mappings_code ON mappings(tree_code);
            CREATE INDEX IF NOT EXISTS idx_sc_supplier ON supplier_categories(supplier);
        """)
        # Additive SEO migration
        existing = {r[1] for r in conn.execute("PRAGMA table_info(tree_nodes)").fetchall()}
        for col, typ in SEO_COLUMNS:
            if col not in existing:
                conn.execute(f"ALTER TABLE tree_nodes ADD COLUMN {col} {typ}")


# ---------- reads ----------

def load_tree_nodes():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT code, label, parent_code, name_lv, name_en, slug_lv, slug_en, "
            "seo_desc_lv, seo_desc_en FROM tree_nodes ORDER BY code"
        ).fetchall()
    return [dict(r) for r in rows]


def load_seo_map() -> dict:
    """Return {code: {name_lv, name_en, slug_lv, slug_en, seo_desc_lv, seo_desc_en}}.
    Entries with all SEO fields NULL are included with empty strings.
    """
    out = {}
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT code, name_lv, name_en, slug_lv, slug_en, seo_desc_lv, seo_desc_en "
            "FROM tree_nodes"
        ).fetchall()
    for r in rows:
        out[r["code"]] = {
            "name_lv":     r["name_lv"]     or "",
            "name_en":     r["name_en"]     or "",
            "slug_lv":     r["slug_lv"]     or "",
            "slug_en":     r["slug_en"]     or "",
            "seo_desc_lv": r["seo_desc_lv"] or "",
            "seo_desc_en": r["seo_desc_en"] or "",
        }
    return out


def save_seo(seo_edits: dict):
    """Apply {code: {field: value, ...}} edits to tree_nodes SEO columns.
    Only the fields present in each entry are updated; others are left as-is.
    """
    if not seo_edits:
        return
    allowed = {c for c, _ in SEO_COLUMNS}
    with get_conn() as conn:
        for code, fields in seo_edits.items():
            sets, vals = [], []
            for k, v in (fields or {}).items():
                if k in allowed:
                    sets.append(f"{k} = ?")
                    vals.append(v if v is not None else "")
            if not sets:
                continue
            vals.append(code)
            conn.execute(f"UPDATE tree_nodes SET {', '.join(sets)} WHERE code = ?", vals)


def load_supplier_categories():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT supplier, category FROM supplier_categories ORDER BY supplier, id"
        ).fetchall()
    return [dict(r) for r in rows]


def load_mappings():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT supplier, category, tree_code FROM mappings"
        ).fetchall()
    return [dict(r) for r in rows]


def load_state(key, default=None):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value FROM tree_state WHERE key = ?", (key,)
        ).fetchone()
    return json.loads(row["value"]) if row else default


# ---------- writes ----------

def save_mappings(supmap: dict):
    """Replace all mappings from a supmap dict: 'supplier||category' -> [code, ...]"""
    rows = []
    for key, codes in supmap.items():
        sep = key.index("||")
        supplier = key[:sep]
        category = key[sep + 2:]
        for code in codes:
            rows.append((supplier, category, code))
    with get_conn() as conn:
        conn.execute("DELETE FROM mappings")
        conn.executemany(
            "INSERT OR IGNORE INTO mappings(supplier, category, tree_code) VALUES (?,?,?)",
            rows,
        )


def update_node_labels(renames: dict):
    """Apply {code: new_label} renames to tree_nodes."""
    if not renames:
        return
    with get_conn() as conn:
        for code, label in renames.items():
            conn.execute("UPDATE tree_nodes SET label = ? WHERE code = ?", (label, code))


def sync_tree_nodes(nodes: list, deleted_codes: Optional[set] = None):
    """Sync tree structure: insert new, update existing, DROP any code not in the
    payload and not in `deleted_codes`. Drops handle slug renames — the old code
    disappears from tree_nodes so it never resurfaces on rebuild.

    `nodes` is a list of {code, label, parent_code} dicts (parent_code may be None).
    """
    if not nodes:
        return
    deleted_codes = deleted_codes or set()
    with get_conn() as conn:
        existing = {r["code"] for r in conn.execute("SELECT code FROM tree_nodes").fetchall()}
        live     = {n["code"] for n in nodes}
        to_insert = [
            (n["code"], n["label"], n.get("parent_code"))
            for n in nodes if n["code"] not in existing
        ]
        to_update = [
            (n["label"], n.get("parent_code"), n["code"])
            for n in nodes if n["code"] in existing
        ]
        # Zombies: in DB but not in current tree and not intentionally deleted.
        to_drop = [(c,) for c in existing - live - set(deleted_codes)]
        if to_insert:
            conn.executemany(
                "INSERT INTO tree_nodes(code, label, parent_code) VALUES (?,?,?)",
                to_insert,
            )
        if to_update:
            conn.executemany(
                "UPDATE tree_nodes SET label=?, parent_code=? WHERE code=?",
                to_update,
            )
        if to_drop:
            conn.executemany("DELETE FROM tree_nodes WHERE code=?", to_drop)


def save_state(key: str, value):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO tree_state(key, value) VALUES (?,?)",
            (key, json.dumps(value)),
        )


def build_supmap() -> dict:
    """Build 'supplier||category' -> [code, ...] from the mappings table."""
    supmap = {}
    with get_conn() as conn:
        for row in conn.execute(
            "SELECT supplier, category, tree_code FROM mappings ORDER BY supplier, category"
        ):
            key = row["supplier"] + "||" + row["category"]
            supmap.setdefault(key, []).append(row["tree_code"])
    return supmap


def build_tree_json(deleted_codes: set) -> dict:
    """Build nested tree dict from tree_nodes, respecting deleted codes and saved order."""
    nodes = load_tree_nodes()
    order = load_state("order", {})

    children = {}  # parent_code -> [code, ...]
    labels = {}    # code -> label
    for n in nodes:
        if n["code"] in deleted_codes:
            continue
        labels[n["code"]] = n["label"]
        parent = n["parent_code"]
        children.setdefault(parent, []).append(n["code"])

    def sort_key(code):
        lbl = labels.get(code, "").lower()
        is_other = code == "other" or code.endswith("/other") or lbl.startswith("other ")
        return (1 if is_other else 0, lbl)

    for parent, lst in children.items():
        key = "__root__" if parent is None else parent
        saved = order.get(key) or []
        if saved:
            pos = {c: i for i, c in enumerate(saved)}
            lst.sort(key=lambda c: (0, pos[c]) if c in pos else (1, *sort_key(c)))
        else:
            lst.sort(key=sort_key)

    def build(parent):
        return [
            {"code": c, "label": labels[c], "children": build(c)}
            for c in children.get(parent, [])
        ]

    return {"tree": build(None)}


def build_paths(deleted_codes: set) -> dict:
    """Build code -> full breadcrumb label for every non-deleted node."""
    nodes = load_tree_nodes()
    label_map = {n["code"]: n["label"] for n in nodes if n["code"] not in deleted_codes}
    parent_map = {n["code"]: n["parent_code"] for n in nodes if n["code"] not in deleted_codes}

    paths = {}
    for code in label_map:
        parts = []
        cur = code
        while cur:
            parts.append(label_map.get(cur, cur))
            cur = parent_map.get(cur)
        paths[code] = " > ".join(reversed(parts))
    return paths
