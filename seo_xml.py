"""
Load hand-authored SEO content from XML file(s) into the tree_nodes table.

The XML file is the source of truth for initial SEO content — it is version-
controlled, human-editable, and the CI/migration pipeline uses it to seed any
database missing SEO fields. After deployment, ongoing edits happen through
the UI (which writes directly to the DB), so this script is idempotent and
non-destructive by default: it only fills fields that are currently empty.

XML format:
    <categories>
      <category code="components/storage/ram/desktop">
        <name_en>Desktop Memory (DIMM)</name_en>
        <name_lv>Datora atmiņa (DIMM)</name_lv>
        <slug_en>desktop-memory-dimm</slug_en>
        <slug_lv>datora-atmina-dimm</slug_lv>
        <seo_desc_en>...50-70 words of English copy...</seo_desc_en>
        <seo_desc_lv>...50-70 words of Latvian copy...</seo_desc_lv>
      </category>
      ...
    </categories>

Usage:
    python3 seo_xml.py --load              # fill empty fields from seo_content.xml
    python3 seo_xml.py --load --force      # overwrite all fields (destructive)
    python3 seo_xml.py --validate          # check length + cannibalization only
    python3 seo_xml.py --dump              # export current DB state to XML
"""
import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import db
import seo


XML_PATH = Path(__file__).parent / "seo_content"   # directory of *.xml files
FIELDS   = ("name_en", "name_lv", "slug_en", "slug_lv",
            "seo_desc_en", "seo_desc_lv", "meta_desc_en", "meta_desc_lv")


def _parse_one(path: Path) -> dict:
    root = ET.parse(path).getroot()
    out = {}
    for cat in root.findall("category"):
        code = cat.get("code")
        if not code:
            continue
        entry = {}
        for f in FIELDS:
            el = cat.find(f)
            if el is not None and (el.text or "").strip():
                entry[f] = el.text.strip()
        out[code] = entry
    return out


def load_xml(path: Path) -> dict:
    """Parse SEO content. `path` can be a single XML file OR a directory — in
    the directory case all *.xml files are merged (later files override earlier
    ones on code collisions, sorted by filename)."""
    if path.is_dir():
        merged = {}
        for f in sorted(path.glob("*.xml")):
            merged.update(_parse_one(f))
        return merged
    if path.exists() and path.is_file():
        return _parse_one(path)
    # Backward-compat: accept path with .xml if the directory form doesn't exist
    alt = path.with_suffix(".xml") if not path.suffix else path
    if alt.exists():
        return _parse_one(alt)
    raise FileNotFoundError(f"SEO content not found at {path}")


def dump_xml(path: Path) -> int:
    """Serialize current DB SEO fields into an XML file (pretty-printed)."""
    seo_map = db.load_seo_map()
    root = ET.Element("categories")
    for code in sorted(seo_map.keys()):
        entry = seo_map[code]
        el = ET.SubElement(root, "category", attrib={"code": code})
        for f in FIELDS:
            child = ET.SubElement(el, f)
            child.text = entry.get(f) or ""
    ET.indent(root, space="  ")
    path.write_text(ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n")
    return len(seo_map)


def apply_load(xml_entries: dict, force: bool = False) -> int:
    """Write XML entries to DB. Without --force, only fields currently empty
    in the DB are touched, so UI edits made after initial load survive."""
    current  = db.load_seo_map()
    patch    = {}
    for code, entry in xml_entries.items():
        fields = {}
        for f, val in entry.items():
            if not force and (current.get(code, {}).get(f) or "").strip():
                continue
            fields[f] = val
        if fields:
            patch[code] = fields
    if patch:
        db.save_seo(patch)
    return len(patch)


def validate(strict: bool = False) -> int:
    """Return non-zero exit code if SEO content is invalid."""
    seo_map = db.load_seo_map()
    problems = []
    for code, entry in seo_map.items():
        for lang in ("en", "lv"):
            desc = entry.get(f"seo_desc_{lang}") or ""
            if not desc:
                problems.append((code, lang, "missing description"))
                continue
            ok, why = seo.validate_description(desc)
            if not ok:
                problems.append((code, lang, why))
        for f in ("name_en", "name_lv", "slug_en", "slug_lv"):
            if not (entry.get(f) or "").strip():
                problems.append((code, f, "empty"))

    print(f"[length + presence]: {len(problems)} issue(s)")
    for code, f, why in problems[:30]:
        print(f"  {code} [{f}]: {why}")
    if len(problems) > 30:
        print(f"  … and {len(problems) - 30} more")

    for lang in ("en", "lv"):
        hard = seo.find_cannibalization(seo_map, lang=lang, threshold=seo.CANNIBAL_HARD)
        soft = seo.find_cannibalization(seo_map, lang=lang, threshold=seo.CANNIBAL_SOFT)
        print(f"[cannibalization {lang}]: {len(hard)} hard (>=0.75) · {len(soft)} soft (>=0.55)")
        for a, b, s in hard[:10]:
            print(f"  HARD  {s:.2f}  {a}  <>  {b}")

    hard_total = sum(
        len(seo.find_cannibalization(seo_map, lang=lang, threshold=seo.CANNIBAL_HARD))
        for lang in ("en", "lv")
    )
    return 0 if not problems and (hard_total == 0 or not strict) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--load",     action="store_true")
    ap.add_argument("--force",    action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--strict",   action="store_true",
                    help="Exit non-zero if any hard cannibalization remains")
    ap.add_argument("--dump",     action="store_true")
    ap.add_argument("--path",     type=Path, default=XML_PATH)
    args = ap.parse_args()

    db.init_db()

    if args.dump:
        n = dump_xml(args.path)
        print(f"Wrote {n} categories to {args.path}")

    if args.load:
        entries = load_xml(args.path)
        written = apply_load(entries, force=args.force)
        print(f"Loaded {len(entries)} categories from {args.path}; wrote {written} field-sets.")
        missing = [n["code"] for n in db.load_tree_nodes() if n["code"] not in entries]
        if missing:
            print(f"  {len(missing)} live categories have no XML entry (will fall back to template if migrate_seo.py runs)")
            for c in missing[:10]:
                print(f"    - {c}")

    if args.validate:
        return validate(strict=args.strict)

    return 0


if __name__ == "__main__":
    sys.exit(main())
