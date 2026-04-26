"""
Initial schema baseline.

This migration is idempotent and reflects the current shape of the database
captured by db.init_db. It exists as a marker so future schema changes can
be added as 002_*.py, 003_*.py etc. without question about where the baseline
came from.
"""
SEO_COLUMNS = [
    ("name_lv",      "TEXT"),
    ("slug_lv",      "TEXT"),
    ("slug_en",      "TEXT"),
    ("seo_desc_lv",  "TEXT"),
    ("seo_desc_en",  "TEXT"),
    ("meta_desc_lv", "TEXT"),
    ("meta_desc_en", "TEXT"),
]


def apply(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tree_nodes (
            code        TEXT PRIMARY KEY,
            label       TEXT NOT NULL,
            parent_code TEXT
        );
        CREATE TABLE IF NOT EXISTS supplier_categories (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier TEXT NOT NULL,
            category TEXT NOT NULL,
            UNIQUE(supplier, category)
        );
        CREATE TABLE IF NOT EXISTS mappings (
            supplier  TEXT NOT NULL,
            category  TEXT NOT NULL,
            tree_code TEXT NOT NULL,
            PRIMARY KEY (supplier, category, tree_code)
        );
        CREATE TABLE IF NOT EXISTS tree_state (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_mappings_code ON mappings(tree_code);
        CREATE INDEX IF NOT EXISTS idx_sc_supplier ON supplier_categories(supplier);
    """)
    existing = {r[1] for r in conn.execute("PRAGMA table_info(tree_nodes)").fetchall()}
    for col, typ in SEO_COLUMNS:
        if col not in existing:
            conn.execute(f"ALTER TABLE tree_nodes ADD COLUMN {col} {typ}")
    # name_en column was previously stored separately; now mirrored from
    # tree_nodes.label at read time. Drop it if it lingers.
    if "name_en" in existing:
        # SQLite < 3.35 lacks DROP COLUMN. Just leave it; load_seo_map ignores it.
        pass
