"""
Add a per-node notes column. Plain text, intended as an editor's review
log: "this paragraph needs rewriting", "wrong example here", etc.
The export endpoint pulls these together into a single AI-prompt-ready
markdown document.
"""
def apply(conn):
    with conn.cursor() as cur:
        cur.execute("""SELECT column_name FROM information_schema.columns
                       WHERE table_name = 'tree_nodes' AND column_name = 'notes'""")
        if cur.fetchone():
            return
        cur.execute("ALTER TABLE tree_nodes ADD COLUMN notes TEXT")
