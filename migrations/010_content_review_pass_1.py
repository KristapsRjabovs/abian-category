"""
Editorial review pass 1: applies AI-reviewed content rewrites for the
displays-projectors and printers-scanners branches (18 pages total).

The rewrites came from sub-agents working through every page in those
branches against a 12-rule editorial brief: no brand names, no em-dashes,
no warranty claims, abbreviations expanded on first use per content
field, Latvian primary nouns, long-format unique H2s on bottom_seo,
no IA-explanation sections, no first-paragraph duplication with
seo_desc, etc.

Subsequent passes (011, 012, ...) will cover the remaining branches:
audio-video-tv, components, computers-servers, networking, phones-tabels.

Each agent output is a JSON file at migrations/_agent_outputs/ with
shape:

    [
      {"code": "...", "fields": {"bottom_seo_en": "...", ...}},
      ...
    ]

Apply is a per-field UPDATE. Field whitelist below. Each field write is
parameterised so HTML content is safe.
"""
import json
from pathlib import Path


WRITABLE = {
    "name_lv", "slug_lv", "slug_en",
    "seo_desc_en", "seo_desc_lv",
    "meta_desc_en", "meta_desc_lv",
    "bottom_seo_en", "bottom_seo_lv",
    "notes",
}

OUTPUTS_DIR = Path(__file__).resolve().parent / "_agent_outputs"
SOURCES = [
    "agent_output_displays-projectors.json",
    "agent_output_printers-scanners.json",
]


def apply(conn):
    total_pages = 0
    total_fields = 0
    for fname in SOURCES:
        path = OUTPUTS_DIR / fname
        if not path.exists():
            print(f"  skipping missing {fname}")
            continue
        entries = json.loads(path.read_text(encoding="utf-8"))
        with conn.cursor() as cur:
            for entry in entries:
                code   = entry.get("code")
                fields = entry.get("fields") or {}
                if not code or not fields:
                    continue
                # Build SET clause from whitelisted fields only
                sets, vals = [], []
                for k, v in fields.items():
                    if k in WRITABLE:
                        sets.append(f"{k} = %s")
                        vals.append(v)
                if not sets:
                    continue
                vals.append(code)
                cur.execute(
                    f"UPDATE tree_nodes SET {', '.join(sets)} WHERE code = %s",
                    vals,
                )
                total_pages += 1
                total_fields += len(sets)
        print(f"  applied {len(entries)} pages from {fname}")
    print(f"  total: {total_pages} page updates, {total_fields} field writes")
