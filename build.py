"""
Build script. Reads category.db and emits two static artifacts consumed by
Netlify:
    public/index.html              the editor with all data baked in
    netlify/functions/_data.json   tree, paths, supmap, SEO for serverless functions

The database is the only source of truth. There is no state.json, no XML
files, no hardcoded category tree. Run `python3 migrate.py` first to apply
any pending schema migrations, then `python3 build.py`.
"""
import json
from collections import defaultdict
from pathlib import Path

import db


OUT_HTML = Path(__file__).parent / "public" / "index.html"
OUT_DATA = Path(__file__).parent / "netlify" / "functions" / "_data.json"
OUT_HTML.parent.mkdir(exist_ok=True)
OUT_DATA.parent.mkdir(parents=True, exist_ok=True)


def _load_state():
    db.init_db()  # apply pending migrations if any
    nodes    = db.load_tree_nodes()
    sc_rows  = db.load_supplier_categories()
    mappings = db.load_mappings()
    seo_map  = db.load_seo_map()
    deleted           = set(db.load_state("deleted",   []))
    confirmed         = sorted(set(db.load_state("confirmed", [])))
    content_confirmed = sorted(set(db.load_state("content_confirmed", [])))
    order             = db.load_state("order", {})
    return dict(nodes=nodes, sc_rows=sc_rows, mappings=mappings, seo_map=seo_map,
                deleted=deleted, confirmed=confirmed,
                content_confirmed=content_confirmed, order=order)


def _build_tree_json(nodes, deleted, order):
    children = defaultdict(list)
    for n in nodes:
        if n["code"] in deleted:
            continue
        children[n["parent_code"]].append(n["code"])

    label = {n["code"]: n["label"] for n in nodes if n["code"] not in deleted}

    def sort_key(code):
        lbl = label.get(code, "").lower()
        is_other = code == "other" or code.endswith("/other") or lbl.startswith("other ")
        return (1 if is_other else 0, lbl)

    for parent_code, lst in children.items():
        key = "__root__" if parent_code is None else parent_code
        saved = order.get(key) or []
        if saved:
            pos = {c: i for i, c in enumerate(saved)}
            lst.sort(key=lambda c: (0, pos[c]) if c in pos else (1, *sort_key(c)))
        else:
            lst.sort(key=sort_key)

    def build(parent_code):
        return [{"code": c, "label": label[c], "children": build(c)}
                for c in children.get(parent_code, [])]

    return {"tree": build(None)}


def _build_paths(nodes, deleted):
    label = {n["code"]: n["label"] for n in nodes if n["code"] not in deleted}
    parent = {n["code"]: n["parent_code"] for n in nodes if n["code"] not in deleted}
    paths = {}
    for code in label:
        parts, cur = [], code
        while cur and cur in label:
            parts.append(label[cur])
            cur = parent.get(cur)
        paths[code] = " > ".join(reversed(parts))
    return paths


def _build_supmap(sc_rows, mappings, deleted, live_codes):
    """{supplier||category: [codes]}, including empty lists for unmapped categories."""
    by_cat = defaultdict(list)
    for m in mappings:
        if m["tree_code"] in live_codes and m["tree_code"] not in deleted:
            by_cat[(m["supplier"], m["category"])].append(m["tree_code"])
    supmap = {}
    for r in sc_rows:
        key = r["supplier"] + "||" + r["category"]
        supmap[key] = list(by_cat.get((r["supplier"], r["category"]), []))
    return supmap


def main():
    s = _load_state()
    live_codes = {n["code"] for n in s["nodes"] if n["code"] not in s["deleted"]}

    tree_json = _build_tree_json(s["nodes"], s["deleted"], s["order"])
    paths     = _build_paths(s["nodes"], s["deleted"])
    supmap    = _build_supmap(s["sc_rows"], s["mappings"], s["deleted"], live_codes)
    sources   = defaultdict(list)
    for r in s["sc_rows"]:
        sources[r["supplier"]].append([r["supplier"], r["category"]])
    coverage = defaultdict(list)
    for key, codes in supmap.items():
        sup = key.split("||", 1)[0]
        for c in codes:
            coverage[c].append(sup)
    stats = {"categories": len(live_codes)}

    # SEO map: keep only live nodes, force name_en from tree label.
    by_label = {n["code"]: n["label"] for n in s["nodes"]}
    seo_data = {}
    for code in live_codes:
        entry = {k: v for k, v in (s["seo_map"].get(code) or {}).items() if v}
        entry["name_en"] = by_label.get(code, code)
        seo_data[code] = entry

    OUT_DATA.write_text(json.dumps({
        "sources": dict(sources), "paths": paths, "supmap": supmap, "seo": seo_data
    }, ensure_ascii=False), encoding="utf-8")
    print(f"  -> netlify/functions/_data.json  ({len(seo_data)} SEO entries)")

    tpl = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")
    replacements = {
        "{{ tree_json | safe }}":              json.dumps(tree_json,                   ensure_ascii=False),
        "{{ stats_json | safe }}":             json.dumps(stats,                       ensure_ascii=False),
        "{{ cov_json | safe }}":               json.dumps(dict(coverage),              ensure_ascii=False),
        "{{ sources_json | safe }}":           json.dumps(dict(sources),               ensure_ascii=False),
        "{{ supmap_json | safe }}":            json.dumps(supmap,                      ensure_ascii=False),
        "{{ paths_json | safe }}":             json.dumps(paths,                       ensure_ascii=False),
        "{{ confirmed_json | safe }}":         json.dumps(s["confirmed"],              ensure_ascii=False),
        "{{ content_confirmed_json | safe }}": json.dumps(s["content_confirmed"],      ensure_ascii=False),
        "{{ deleted_json | safe }}":           json.dumps(sorted(s["deleted"]),        ensure_ascii=False),
        "{{ seo_json | safe }}":               json.dumps(seo_data,                    ensure_ascii=False),
    }
    for placeholder, value in replacements.items():
        tpl = tpl.replace(placeholder, value)
    OUT_HTML.write_text(tpl, encoding="utf-8")
    print(f"  -> public/index.html  ({len(s['sc_rows'])} supplier categories, {len(supmap)} mapping keys)")


if __name__ == "__main__":
    main()
