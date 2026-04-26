"""
Add a covering index for the (supplier, category) lookup pattern. The save
flow and the supplier CSV exports both filter mappings on this pair; without
it Postgres falls back to a sequential scan once the table grows past a few
thousand rows.
"""
def apply(conn):
    with conn.cursor() as cur:
        cur.execute("""CREATE INDEX IF NOT EXISTS idx_mappings_supplier_category
                       ON mappings(supplier, category)""")
