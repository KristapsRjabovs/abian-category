"""
Seed bottom_seo (EN + LV) for three Computers & Servers subtrees:
notebook-accessories, desktops-workstations and point-of-sale-equipment.

Twelve nodes total (three intermediates plus nine leaves). Names, slugs,
meta descriptions and short descriptions are already curated on these
nodes from the live import; this migration only fills the long-form
bottom_seo HTML in both languages.

Idempotent per field: writes only when the existing value is empty, so a
re-run after manual UI edits is safe.
"""
import json
from pathlib import Path

DATA_FILE = Path(__file__).with_name("011_seed_cs_subtrees_bottom_seo.json")
FIELDS = ("bottom_seo_en", "bottom_seo_lv")


def apply(conn):
    data = json.loads(DATA_FILE.read_text())
    written = skipped_nonempty = skipped_missing = 0
    with conn.cursor() as cur:
        for code, fields in data.items():
            cur.execute(
                f"SELECT {', '.join(FIELDS)} FROM tree_nodes WHERE code = %s",
                (code,),
            )
            row = cur.fetchone()
            if not row:
                print(f"  no tree_node {code!r}, skipping")
                skipped_missing += 1
                continue
            existing = dict(zip(FIELDS, row))
            sets, vals = [], []
            for col in FIELDS:
                if (existing[col] or "").strip():
                    continue
                new_val = fields.get(col, "").strip()
                if not new_val:
                    continue
                sets.append(f"{col} = %s")
                vals.append(new_val)
            if not sets:
                skipped_nonempty += 1
                continue
            vals.append(code)
            cur.execute(
                f"UPDATE tree_nodes SET {', '.join(sets)} WHERE code = %s",
                vals,
            )
            written += 1
    print(f"  wrote {written} nodes, "
          f"skipped {skipped_nonempty} (already populated), "
          f"skipped {skipped_missing} (not in tree)")
