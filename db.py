import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "category.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


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


# ---------- reads ----------

def load_tree_nodes():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT code, label, parent_code FROM tree_nodes ORDER BY code"
        ).fetchall()
    return [dict(r) for r in rows]


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

    children: dict[str | None, list] = {}
    labels: dict[str, str] = {}
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
