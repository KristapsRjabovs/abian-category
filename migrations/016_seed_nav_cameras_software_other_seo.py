"""
Seed full SEO content (EN + LV, all five fields) for the Navigation & Radios,
Cameras, Software Applications, and Other subtrees.

Sixty-five nodes total:
- navigation-radios (1)
- cameras subtree (4)
- software-applications subtree (6)
- other subtree (54): root, chargers/warranties/medical leaves,
  office-equipment-furniture (4), power-tools-garden (3),
  home-lifestyle subtree (32), renewable-energy (7), smart-home-iot (4)

The first H2 in every bottom_seo here is a long descriptive title that
includes the category name (matching the convention from migration 012).

Idempotent per field: only writes columns that are currently empty, so
existing curated values survive a re-run.
"""
import json
from pathlib import Path

DATA_FILE = Path(__file__).with_name("016_seed_nav_cameras_software_other_seo.json")
FIELDS = (
    "slug_en", "meta_desc_en", "seo_desc_en", "bottom_seo_en",
    "name_lv", "slug_lv", "meta_desc_lv", "seo_desc_lv", "bottom_seo_lv",
)


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
