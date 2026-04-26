"""
Build script — run by Netlify (and locally before netlify dev).
Generates:
  public/index.html               static tree editor with data embedded
  netlify/functions/_data.json    supplier categories + paths + SEO for serverless functions
"""
import csv
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import build_categories as bc

# state.json committed to the repo takes priority over output/tree_state.json
_state_file = Path(__file__).parent / "state.json"
if _state_file.exists():
    _s = json.loads(_state_file.read_text(encoding="utf-8"))
    bc.DELETED_CODES   = set(_s.get("deleted", []))
    bc.CONFIRMED_CODES = set(_s.get("confirmed", []))
    bc.ORDER           = dict(_s.get("order", {}))
    bc.OVERRIDES       = dict(_s.get("overrides", {}))
    # When state.json carries the full live tree (i.e. user has saved at least
    # once and committed the snapshot), bc.TREE should reflect ONLY those nodes.
    # Otherwise the legacy hardcoded tree from build_categories.py would leak
    # through with old codes and the build's baked paths/supmap would mix two
    # incompatible code schemes.
    _state_tree_nodes = _s.get("tree_nodes") or []
    if _state_tree_nodes:
        bc.TREE = {n["code"]: (n["label"], n.get("parent_code")) for n in _state_tree_nodes}
    # Live supmap (supplier||category -> [codes]) takes precedence if present.
    # build.py would otherwise rederive supmap from bc.MAPPING + bc.OVERRIDES,
    # which can't track per-supplier mappings. The live snapshot is authoritative.
    _state_supmap = _s.get("supmap") or {}

RAW_DIR  = Path(__file__).parent / "raw"
OUT_HTML = Path(__file__).parent / "public" / "index.html"
OUT_DATA = Path(__file__).parent / "netlify" / "functions" / "_data.json"
OUT_HTML.parent.mkdir(exist_ok=True)
OUT_DATA.parent.mkdir(parents=True, exist_ok=True)

# ---------- supplier categories (original order, deduplicated) ----------
sc_rows: list[dict] = []
seen: set = set()
for path in sorted(RAW_DIR.glob("*.csv")):
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            supplier = row["supplier_name"].strip()
            category = row["supplier_category"].strip()
            key = (supplier, category)
            if supplier and category and key not in seen:
                seen.add(key)
                sc_rows.append({"supplier": supplier, "category": category})

# ---------- initial SUPMAP from MAPPING (+ overrides from tree_state if present) ----------
deleted_set = set(bc.DELETED_CODES)

supmap = {}
for r in sc_rows:
    key = r["supplier"] + "||" + r["category"]
    if key in _state_supmap:
        # Authoritative live snapshot: trust it verbatim, only filter deleted nodes.
        norm = [c for c in _state_supmap[key] if c in bc.TREE and c not in deleted_set]
    else:
        codes = bc.MAPPING.get(r["category"], [])
        if r["category"] in bc.OVERRIDES:
            codes = bc.OVERRIDES[r["category"]]
        norm = []
        for code in codes:
            c = bc.normalise(code)
            if c in bc.TREE and c not in deleted_set and c not in norm:
                norm.append(c)
    supmap[key] = norm

# ---------- tree JSON (respects deleted + saved order) ----------
def build_tree_json() -> dict:
    children: dict = defaultdict(list)
    for code, (label, parent) in bc.TREE.items():
        if code not in deleted_set:
            children[parent].append(code)

    def sort_key(code):
        lbl = bc.TREE[code][0].lower()
        is_other = code == "other" or code.endswith("/other") or lbl.startswith("other ")
        return (1 if is_other else 0, lbl)

    for parent, lst in children.items():
        saved = bc.ORDER.get("__root__" if parent is None else parent) or []
        if saved:
            pos = {c: i for i, c in enumerate(saved)}
            lst.sort(key=lambda c: (0, pos[c]) if c in pos else (1, *sort_key(c)))
        else:
            lst.sort(key=sort_key)

    def build(parent):
        return [{"code": c, "label": bc.TREE[c][0], "children": build(c)}
                for c in children.get(parent, [])]
    return {"tree": build(None)}

# ---------- breadcrumb paths ----------
def build_paths() -> dict:
    paths = {}
    for code in bc.TREE:
        if code in deleted_set:
            continue
        parts, cur = [], code
        while cur and cur in bc.TREE:
            parts.append(bc.TREE[cur][0])
            cur = bc.TREE[cur][1]
        paths[code] = " > ".join(reversed(parts))
    return paths

tree_json   = build_tree_json()
paths       = build_paths()
stats       = {"categories": len([c for c in bc.TREE if c not in deleted_set])}
sources     = {}
for r in sc_rows:
    sources.setdefault(r["supplier"], []).append([r["supplier"], r["category"]])

coverage: dict = {}
for key, codes in supmap.items():
    sup = key[:key.index("||")]
    for code in codes:
        coverage.setdefault(code, []).append(sup)

confirmed         = sorted(bc.CONFIRMED_CODES)
content_confirmed = sorted(set(_s.get("content_confirmed", []))) if _state_file.exists() else []
deleted           = sorted(deleted_set)

# ---------- SEO content from XML (hand-authored, version-controlled) ----------
SEO_DIR = Path(__file__).parent / "seo_content"
# name_en intentionally NOT baked from XML — it is derived from each node's
# tree label at read time (see _data.json patch below) so the tree label and
# the SEO English name remain a single source of truth.
SEO_FIELDS = ("name_lv", "slug_en", "slug_lv",
              "seo_desc_en", "seo_desc_lv", "meta_desc_en", "meta_desc_lv")
seo_data: dict = {}
if SEO_DIR.is_dir():
    for xml_path in sorted(SEO_DIR.glob("*.xml")):
        try:
            root = ET.parse(xml_path).getroot()
        except ET.ParseError:
            continue
        for cat in root.findall("category"):
            code = cat.get("code")
            if not code or code in deleted_set:
                continue
            entry = {}
            for f in SEO_FIELDS:
                el = cat.find(f)
                if el is not None and (el.text or "").strip():
                    entry[f] = el.text.strip()
            if entry:
                seo_data[code] = entry

# Mirror tree labels into SEO entries as name_en so the live tree label
# always wins over anything XML or Blobs might say. One name per language.
for _code, (_label, _parent) in bc.TREE.items():
    if _code in deleted_set:
        continue
    seo_data.setdefault(_code, {})
    seo_data[_code]["name_en"] = _label

# ---------- write _data.json for serverless functions ----------
OUT_DATA.write_text(json.dumps({
    "sources": sources, "paths": paths, "supmap": supmap, "seo": seo_data
}, ensure_ascii=False), encoding="utf-8")
print(f"  → netlify/functions/_data.json  ({len(seo_data)} SEO entries)")

# ---------- stamp data into HTML template ----------
tpl = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")

replacements = {
    "{{ tree_json | safe }}":      json.dumps(tree_json,  ensure_ascii=False),
    "{{ stats_json | safe }}":     json.dumps(stats,      ensure_ascii=False),
    "{{ cov_json | safe }}":       json.dumps(coverage,   ensure_ascii=False),
    "{{ sources_json | safe }}":   json.dumps(sources,    ensure_ascii=False),
    "{{ supmap_json | safe }}":    json.dumps(supmap,     ensure_ascii=False),
    "{{ paths_json | safe }}":     json.dumps(paths,      ensure_ascii=False),
    "{{ confirmed_json | safe }}":         json.dumps(confirmed,         ensure_ascii=False),
    "{{ content_confirmed_json | safe }}": json.dumps(content_confirmed, ensure_ascii=False),
    "{{ deleted_json | safe }}":           json.dumps(deleted,           ensure_ascii=False),
    "{{ seo_json | safe }}":       json.dumps(seo_data,   ensure_ascii=False),
}
for placeholder, value in replacements.items():
    tpl = tpl.replace(placeholder, value)

OUT_HTML.write_text(tpl, encoding="utf-8")
print(f"  → public/index.html  ({len(sc_rows)} categories, {len(supmap)} mapping keys)")
