"""
Build script — run by Netlify (and locally before netlify dev).
Generates:
  public/index.html               static tree editor with data embedded
  netlify/functions/_data.json    supplier categories + paths for download function
"""
import csv
import json
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
    # Merge user-created / renamed nodes into bc.TREE. state.json is authoritative:
    # labels + parent relationships here override the hardcoded tree.
    for _n in _s.get("tree_nodes", []):
        bc.TREE[_n["code"]] = (_n["label"], _n.get("parent_code"))

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

supmap: dict[str, list] = {}
for r in sc_rows:
    key = r["supplier"] + "||" + r["category"]
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

confirmed = sorted(bc.CONFIRMED_CODES)
deleted   = sorted(deleted_set)

# ---------- write _data.json for download function ----------
OUT_DATA.write_text(json.dumps({"sources": sources, "paths": paths, "supmap": supmap}, ensure_ascii=False), encoding="utf-8")
print(f"  → netlify/functions/_data.json")

# ---------- stamp data into HTML template ----------
tpl = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")

replacements = {
    "{{ tree_json | safe }}":      json.dumps(tree_json,  ensure_ascii=False),
    "{{ stats_json | safe }}":     json.dumps(stats,      ensure_ascii=False),
    "{{ cov_json | safe }}":       json.dumps(coverage,   ensure_ascii=False),
    "{{ sources_json | safe }}":   json.dumps(sources,    ensure_ascii=False),
    "{{ supmap_json | safe }}":    json.dumps(supmap,     ensure_ascii=False),
    "{{ paths_json | safe }}":     json.dumps(paths,      ensure_ascii=False),
    "{{ confirmed_json | safe }}": json.dumps(confirmed,  ensure_ascii=False),
    "{{ deleted_json | safe }}":   json.dumps(deleted,    ensure_ascii=False),
}
for placeholder, value in replacements.items():
    tpl = tpl.replace(placeholder, value)

OUT_HTML.write_text(tpl, encoding="utf-8")
print(f"  → public/index.html  ({len(sc_rows)} categories, {len(supmap)} mapping keys)")
