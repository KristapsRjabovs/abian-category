"""
Fix typo in tree_nodes label: 'Phones & Tabels' → 'Phones & Tablets'.
The node code (phones-tabels) is unchanged as it is the primary key.
"""


def apply(conn):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE tree_nodes SET label = %s WHERE code = %s AND label = %s",
            ("Phones & Tablets", "phones-tabels", "Phones & Tabels"),
        )
        print(f"  updated {cur.rowcount} row(s)")
