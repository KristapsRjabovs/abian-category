"""
Seed SEO content for the Components subtree (37 categories: root + 36 descendants).

Fills meta_desc_en, slug_en, seo_desc_en and bottom_seo_en for every node under
'components'. Content is loaded from the sibling JSON file
009_seed_components_seo.json so the .py stays reviewable in git.

Idempotent: each field is only written when the existing value is empty, so
manual edits made through the UI after the migration runs are never overwritten
on re-run. Skips nodes that no longer exist in tree_nodes.
"""
import json
from pathlib import Path

DATA_FILE = Path(__file__).with_name("009_seed_components_seo.json")
FIELDS = ("meta_desc_en", "slug_en", "seo_desc_en", "bottom_seo_en")


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
