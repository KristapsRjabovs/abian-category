"""
Initial Postgres schema. Idempotent — safe to run against an empty
database or one that already has these tables/columns.
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
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tree_nodes (
                code        TEXT PRIMARY KEY,
                label       TEXT NOT NULL,
                parent_code TEXT
            );
            CREATE TABLE IF NOT EXISTS supplier_categories (
                id       SERIAL PRIMARY KEY,
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
        # Additive SEO columns
        cur.execute("""SELECT column_name FROM information_schema.columns
                       WHERE table_name = 'tree_nodes'""")
        existing = {r[0] for r in cur.fetchall()}
        for col, typ in SEO_COLUMNS:
            if col not in existing:
                cur.execute(f"ALTER TABLE tree_nodes ADD COLUMN {col} {typ}")
