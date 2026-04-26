"""
Add the bottom-of-page SEO long-form text columns. Stored as HTML produced
by the WYSIWYG editor in the SEO panel. No length validation — long-form
copy is intentionally variable.
"""
def apply(conn):
    with conn.cursor() as cur:
        cur.execute("""SELECT column_name FROM information_schema.columns
                       WHERE table_name = 'tree_nodes'""")
        existing = {r[0] for r in cur.fetchall()}
        for col in ("bottom_seo_lv", "bottom_seo_en"):
            if col not in existing:
                cur.execute(f"ALTER TABLE tree_nodes ADD COLUMN {col} TEXT")
