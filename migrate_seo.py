"""
Backfill SEO metadata for every category that is missing any of:
  name_lv, name_en, slug_lv, slug_en, seo_desc_lv, seo_desc_en

Idempotent — running twice does nothing on the second pass.
After backfill, runs a cannibalization check against the full set and prints
any description pairs with trigram Jaccard >= 0.55 for manual review.

Usage:
    python3 migrate_seo.py            # apply
    python3 migrate_seo.py --dry-run  # preview counts only
"""
import argparse
import sys

import db
import seo


REQUIRED = ("name_lv", "name_en", "slug_lv", "slug_en", "seo_desc_lv", "seo_desc_en")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="Regenerate every node (overwrites existing SEO fields)")
    args = ap.parse_args()

    db.init_db()
    nodes    = db.load_tree_nodes()
    mappings = db.load_mappings()

    to_write = {}
    skipped_complete = 0
    for node in nodes:
        missing = [f for f in REQUIRED if not (node.get(f) or "").strip()]
        if not args.force and not missing:
            skipped_complete += 1
            continue
        ctx = seo.build_context_from_tree(node, nodes, mappings)
        generated = seo.generate(node, ctx)
        # Only fill fields currently empty (unless --force), so human edits survive
        patch = {}
        for field in REQUIRED:
            if args.force or not (node.get(field) or "").strip():
                patch[field] = generated[field]
        if patch:
            to_write[node["code"]] = patch

    print(f"Scanned {len(nodes)} nodes")
    print(f"  already complete: {skipped_complete}")
    print(f"  will generate:    {len(to_write)}")

    if args.dry_run:
        print("(dry run — no changes written)")
        return 0

    if to_write:
        db.save_seo(to_write)
        print(f"Wrote SEO fields for {len(to_write)} nodes.")

    # ── Cannibalization retry pass ────────────────────────────────────────────
    # Any pair >= HARD threshold gets one side regenerated with variant_offset=1
    # (and up to 3 more offsets) until they drop below threshold.
    by_code = {n["code"]: n for n in nodes}
    for lang in ("en", "lv"):
        field = "seo_desc_" + lang
        for attempt in range(4):
            seo_map = db.load_seo_map()
            dupes = seo.find_cannibalization(seo_map, lang=lang, threshold=seo.CANNIBAL_HARD)
            if not dupes:
                break
            # Regenerate the SECOND code in each offending pair so the list shrinks
            # deterministically; avoid double-regenerating the same code in one pass.
            regen_patch, regen_seen = {}, set()
            for _, code_b, _ in dupes:
                if code_b in regen_seen:
                    continue
                regen_seen.add(code_b)
                n = by_code.get(code_b)
                if not n:
                    continue
                ctx = seo.build_context_from_tree(n, nodes, mappings)
                fresh = seo.generate(n, ctx, variant_offset=attempt + 1)
                regen_patch[code_b] = {field: fresh[field]}
            if regen_patch:
                db.save_seo(regen_patch)
                print(f"  retry pass {attempt + 1} [{lang}]: regenerated {len(regen_patch)} description(s)")
            else:
                break

    # Final report
    seo_map = db.load_seo_map()
    for lang in ("en", "lv"):
        hard = seo.find_cannibalization(seo_map, lang=lang, threshold=seo.CANNIBAL_HARD)
        soft = seo.find_cannibalization(seo_map, lang=lang, threshold=seo.CANNIBAL_SOFT)
        print(f"\n[cannibalization {lang}]: {len(hard)} hard (>=0.75) · {len(soft)} soft (>=0.55)")
        for a, b, s in hard[:10]:
            print(f"  HARD  {s:.2f}  {a}  <>  {b}")
        for a, b, s in [p for p in soft if p not in hard][:5]:
            print(f"  soft  {s:.2f}  {a}  <>  {b}")

    # Length validation
    bad = []
    for code, fields in seo_map.items():
        for lang in ("en", "lv"):
            ok, why = seo.validate_description(fields.get(f"seo_desc_{lang}") or "")
            if not ok:
                bad.append((code, lang, why))
    print(f"\n[length validation]: {len(bad)} description(s) outside 50-70 words")
    for code, lang, why in bad[:20]:
        print(f"  {code} [{lang}]: {why}")
    if len(bad) > 20:
        print(f"  … and {len(bad) - 20} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
