"""
Single SQLite-style API on top of Neon Postgres.

Connection comes from $DATABASE_URL or $NETLIFY_DATABASE_URL (the latter is
auto-injected by the Netlify Neon extension). For local dev, drop the URL
into a .env file or `export` it in your shell — see .env.example.
"""
import json
import os
import re
import threading
from contextlib import contextmanager
from typing import Optional

import psycopg2
import psycopg2.extras
import psycopg2.pool

# Auto-load .env so local Flask/migrate runs work without manual `export`s.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _dsn(prefer_unpooled: bool = False) -> str:
    """Pick a Postgres DSN from env. Pass prefer_unpooled=True for migrations
    or anything that runs DDL — Neon's pooled endpoint drops sessions per
    statement which can confuse multi-statement DDL."""
    if prefer_unpooled:
        url = (os.environ.get("NETLIFY_DATABASE_URL_UNPOOLED")
               or os.environ.get("DATABASE_URL")
               or os.environ.get("NETLIFY_DATABASE_URL"))
    else:
        url = (os.environ.get("DATABASE_URL")
               or os.environ.get("NETLIFY_DATABASE_URL")
               or os.environ.get("NETLIFY_DATABASE_URL_UNPOOLED"))
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Add it to your environment or .env "
            "(see .env.example). On Netlify the Neon extension sets "
            "NETLIFY_DATABASE_URL automatically.")
    return url


# Lazy-initialized thread-safe connection pool. Cold-start cost paid once per
# process; subsequent get_conn() calls reuse a warm connection.
_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
_pool_lock = threading.Lock()


def _get_pool() -> psycopg2.pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=1, maxconn=10, dsn=_dsn())
    return _pool


@contextmanager
def get_conn(prefer_unpooled: bool = False):
    if prefer_unpooled:
        # DDL path — bypass the pool, open a fresh single-purpose connection
        # against the unpooled endpoint and close it when done.
        conn = psycopg2.connect(_dsn(prefer_unpooled=True))
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def _cursor(conn):
    """Dict-row cursor so callers can use row['code'] instead of row[0]."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


# Writable SEO columns. name_en is intentionally absent: it is mirrored from
# tree_nodes.label at read time so there is one source of truth per language.
SEO_COLUMNS = [
    ("name_lv",       "TEXT"),
    ("slug_lv",       "TEXT"),
    ("slug_en",       "TEXT"),
    ("seo_desc_lv",   "TEXT"),
    ("seo_desc_en",   "TEXT"),
    ("meta_desc_lv",  "TEXT"),
    ("meta_desc_en",  "TEXT"),
    ("bottom_seo_lv", "TEXT"),  # long-form HTML produced by WYSIWYG editor
    ("bottom_seo_en", "TEXT"),
]


def init_db():
    """Apply any pending migrations. Safe to call repeatedly."""
    import migrate
    migrate.apply_pending()


# ─── reads ─────────────────────────────────────────────────────────────────

def load_tree_nodes():
    cols = "code, label, parent_code, " + ", ".join(c for c, _ in SEO_COLUMNS)
    with get_conn() as conn, _cursor(conn) as cur:
        cur.execute(f"SELECT {cols} FROM tree_nodes ORDER BY code")
        return [dict(r) for r in cur.fetchall()]


def load_seo_map() -> dict:
    out = {}
    cols = "code, label, " + ", ".join(c for c, _ in SEO_COLUMNS)
    with get_conn() as conn, _cursor(conn) as cur:
        cur.execute(f"SELECT {cols} FROM tree_nodes")
        for r in cur.fetchall():
            out[r["code"]] = {
                "name_en":       r["label"]          or "",
                "name_lv":       r["name_lv"]        or "",
                "slug_lv":       r["slug_lv"]        or "",
                "slug_en":       r["slug_en"]        or "",
                "seo_desc_lv":   r["seo_desc_lv"]    or "",
                "seo_desc_en":   r["seo_desc_en"]    or "",
                "meta_desc_lv":  r["meta_desc_lv"]   or "",
                "meta_desc_en":  r["meta_desc_en"]   or "",
                "bottom_seo_lv": r["bottom_seo_lv"]  or "",
                "bottom_seo_en": r["bottom_seo_en"]  or "",
            }
    return out


def load_supplier_categories():
    with get_conn() as conn, _cursor(conn) as cur:
        cur.execute("SELECT supplier, category FROM supplier_categories ORDER BY supplier, id")
        return [dict(r) for r in cur.fetchall()]


def load_mappings():
    with get_conn() as conn, _cursor(conn) as cur:
        cur.execute("SELECT supplier, category, tree_code FROM mappings")
        return [dict(r) for r in cur.fetchall()]


def load_state(key, default=None):
    with get_conn() as conn, _cursor(conn) as cur:
        cur.execute("SELECT value FROM tree_state WHERE key = %s", (key,))
        r = cur.fetchone()
    return json.loads(r["value"]) if r else default


# ─── writes ────────────────────────────────────────────────────────────────

_WRITABLE_SEO = {c for c, _ in SEO_COLUMNS}


def save_seo(seo_edits: dict):
    if not seo_edits:
        return
    with get_conn() as conn, conn.cursor() as cur:
        for code, fields in seo_edits.items():
            sets, vals = [], []
            for k, v in (fields or {}).items():
                if k in _WRITABLE_SEO:
                    sets.append(f"{k} = %s")
                    vals.append(v if v is not None else "")
            if not sets:
                continue
            vals.append(code)
            cur.execute(f"UPDATE tree_nodes SET {', '.join(sets)} WHERE code = %s", vals)


def save_mappings(supmap: dict) -> int:
    """Replace all mappings; drop tree_codes not in tree_nodes (orphans).
    Returns the count of dropped rows."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT code FROM tree_nodes")
        live = {r[0] for r in cur.fetchall()}
        rows, dropped = [], 0
        for key, codes in supmap.items():
            sep = key.index("||")
            supplier, category = key[:sep], key[sep + 2:]
            for code in codes:
                if code in live:
                    rows.append((supplier, category, code))
                else:
                    dropped += 1
        cur.execute("DELETE FROM mappings")
        if rows:
            psycopg2.extras.execute_values(
                cur,
                "INSERT INTO mappings(supplier, category, tree_code) VALUES %s "
                "ON CONFLICT (supplier, category, tree_code) DO NOTHING",
                rows,
            )
    return dropped


def update_node_labels(renames: dict):
    if not renames:
        return
    with get_conn() as conn, conn.cursor() as cur:
        for code, label in renames.items():
            cur.execute("UPDATE tree_nodes SET label = %s WHERE code = %s", (label, code))


def sync_tree_nodes(nodes: list, deleted_codes: Optional[set] = None):
    """Sync tree structure: insert new, update existing, drop zombies."""
    if not nodes:
        return
    deleted_codes = deleted_codes or set()
    live = {n["code"] for n in nodes}
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT code FROM tree_nodes")
        existing = {r[0] for r in cur.fetchall()}
        to_insert = [(n["code"], n["label"], n.get("parent_code"))
                     for n in nodes if n["code"] not in existing]
        to_update = [(n["label"], n.get("parent_code"), n["code"])
                     for n in nodes if n["code"] in existing]
        to_drop = [(c,) for c in existing - live - set(deleted_codes)]
        if to_insert:
            cur.executemany(
                "INSERT INTO tree_nodes(code, label, parent_code) VALUES (%s,%s,%s)",
                to_insert)
        if to_update:
            cur.executemany(
                "UPDATE tree_nodes SET label=%s, parent_code=%s WHERE code=%s",
                to_update)
        if to_drop:
            cur.executemany("DELETE FROM tree_nodes WHERE code=%s", to_drop)


def save_state(key: str, value):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tree_state(key, value) VALUES (%s, %s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            (key, json.dumps(value)))


# ─── derived views (used by the editor) ────────────────────────────────────

def build_supmap() -> dict:
    supmap = {}
    with get_conn() as conn, _cursor(conn) as cur:
        cur.execute("SELECT supplier, category, tree_code FROM mappings "
                    "ORDER BY supplier, category")
        for row in cur.fetchall():
            key = row["supplier"] + "||" + row["category"]
            supmap.setdefault(key, []).append(row["tree_code"])
    return supmap


def build_tree_json(deleted_codes: set) -> dict:
    nodes = load_tree_nodes()
    order = load_state("order", {})
    children = {}
    labels = {}
    for n in nodes:
        if n["code"] in deleted_codes:
            continue
        labels[n["code"]] = n["label"]
        children.setdefault(n["parent_code"], []).append(n["code"])

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
        return [{"code": c, "label": labels[c], "children": build(c)}
                for c in children.get(parent, [])]
    return {"tree": build(None)}


def build_paths(deleted_codes: set) -> dict:
    nodes = load_tree_nodes()
    label_map = {n["code"]: n["label"] for n in nodes if n["code"] not in deleted_codes}
    parent_map = {n["code"]: n["parent_code"] for n in nodes if n["code"] not in deleted_codes}
    paths = {}
    for code in label_map:
        parts, cur = [], code
        while cur:
            parts.append(label_map.get(cur, cur))
            cur = parent_map.get(cur)
        paths[code] = " > ".join(reversed(parts))
    return paths
