import csv
import io
import json
from flask import Flask, jsonify, render_template, request, Response

import db
import seo

app = Flask(__name__)


def _page_data():
    deleted   = set(db.load_state("deleted", []))
    confirmed = db.load_state("confirmed", [])
    tree_json = db.build_tree_json(deleted)
    paths     = db.build_paths(deleted)
    supmap    = db.build_supmap()
    sc_rows   = db.load_supplier_categories()
    sources: dict = {}
    for row in sc_rows:
        sources.setdefault(row["supplier"], []).append([row["supplier"], row["category"]])
        supmap.setdefault(row["supplier"] + "||" + row["category"], [])
    stats    = {"categories": sum(1 for n in db.load_tree_nodes() if n["code"] not in deleted)}
    coverage: dict = {}
    for row in db.load_mappings():
        coverage.setdefault(row["tree_code"], []).append(row["supplier"])
    seo_map = db.load_seo_map()
    return dict(
        tree_json      = json.dumps(tree_json,  ensure_ascii=False),
        stats_json     = json.dumps(stats,      ensure_ascii=False),
        cov_json       = json.dumps(coverage,   ensure_ascii=False),
        sources_json   = json.dumps(sources,    ensure_ascii=False),
        supmap_json    = json.dumps(supmap,     ensure_ascii=False),
        paths_json     = json.dumps(paths,      ensure_ascii=False),
        confirmed_json = json.dumps(sorted(confirmed), ensure_ascii=False),
        deleted_json   = json.dumps(sorted(deleted),   ensure_ascii=False),
        seo_json       = json.dumps(seo_map,    ensure_ascii=False),
    )


@app.route("/")
def index():
    return render_template("index.html", **_page_data())


@app.route("/api/state")
def api_state():
    deleted   = db.load_state("deleted", [])
    confirmed = db.load_state("confirmed", [])
    order     = db.load_state("order", {})
    renames   = db.load_state("renames", {})
    supmap    = db.build_supmap()
    seo_map   = db.load_seo_map()
    return jsonify(dict(supmap=supmap, deleted=deleted, confirmed=confirmed,
                        order=order, renames=renames, seo=seo_map))


@app.route("/api/save", methods=["POST"])
def api_save():
    payload   = request.get_json(force=True)
    supmap    = payload.get("supmap") or {}
    deleted   = payload.get("deleted") or []
    confirmed = payload.get("confirmed") or []
    order     = payload.get("order") or {}
    renames = payload.get("renames") or {}
    tree_nodes = payload.get("tree_nodes") or []
    seo_edits  = payload.get("seo_edits") or {}
    db.sync_tree_nodes(tree_nodes, set(deleted))
    db.save_mappings(supmap)
    db.update_node_labels(renames)
    db.save_seo(seo_edits)
    db.save_state("deleted",   sorted(set(deleted)))
    db.save_state("confirmed", sorted(set(confirmed)))
    db.save_state("order",     order)
    db.save_state("renames",   renames)
    return jsonify(ok=True, confirmed=len(confirmed), deleted=len(deleted),
                   seo_updated=len(seo_edits))


@app.route("/api/download")
def api_download():
    supplier = request.args.get("supplier", "also_data")
    sc_rows  = [r for r in db.load_supplier_categories() if r["supplier"] == supplier]
    deleted  = set(db.load_state("deleted", []))
    paths    = db.build_paths(deleted)
    mapping: dict = {}
    for row in db.load_mappings():
        if row["supplier"] == supplier:
            mapping.setdefault(row["category"], []).append(row["tree_code"])
    buf = io.StringIO()
    w   = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    w.writerow(["supplier_name", "supplier_category", "client_category_code", "client_category_label"])
    for row in sc_rows:
        codes = mapping.get(row["category"], [])
        if not codes:
            w.writerow([supplier, row["category"], "", ""])
        else:
            for code in codes:
                w.writerow([supplier, row["category"], code, paths.get(code, "")])
    filename = "also_mapping.csv" if supplier == "also_data" else "elko_mapping.csv"
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


# ── Magento category export ───────────────────────────────────────────────────
# Stable category IDs come from a depth-first pre-order traversal of the live
# tree (deleted nodes excluded). Same input -> same numeric IDs every export.
def _build_category_ids(deleted: set):
    nodes = db.load_tree_nodes()
    by_parent: dict = {}
    for n in nodes:
        if n["code"] in deleted:
            continue
        by_parent.setdefault(n["parent_code"], []).append(n)
    order = db.load_state("order", {})

    def sort_children(parent_code):
        lst = by_parent.get(parent_code, [])
        key = "__root__" if parent_code is None else parent_code
        saved = order.get(key) or []
        if saved:
            pos = {c: i for i, c in enumerate(saved)}
            lst.sort(key=lambda n: (0, pos[n["code"]]) if n["code"] in pos else (1, n["label"].lower()))
        else:
            lst.sort(key=lambda n: (1 if n["code"].endswith("/other") or n["label"].lower().startswith("other") else 0,
                                    n["label"].lower()))
        return lst

    ids: dict = {}
    counter = [1]  # category_id 1+ ; parent of root = 0

    def walk(parent_code):
        for n in sort_children(parent_code):
            ids[n["code"]] = counter[0]
            counter[0] += 1
            walk(n["code"])

    walk(None)
    return ids


@app.route("/api/category-export")
def api_category_export():
    deleted  = set(db.load_state("deleted", []))
    nodes    = db.load_tree_nodes()
    paths    = db.build_paths(deleted)
    seo_map  = db.load_seo_map()
    by_code  = {n["code"]: n for n in nodes if n["code"] not in deleted}
    cat_ids  = _build_category_ids(deleted)

    # Validation: descriptions 50-70 words, meta descriptions 120-160 chars,
    # all required fields present, no cross-category duplication. Block export
    # if any rule fails.
    problems: list = []
    for code, n in by_code.items():
        s = seo_map.get(code) or {}
        for f in ("name_lv", "name_en", "slug_lv", "slug_en",
                  "seo_desc_lv", "seo_desc_en", "meta_desc_lv", "meta_desc_en"):
            if not (s.get(f) or "").strip():
                problems.append({"code": code, "field": f, "reason": "missing"})
        for lang in ("en", "lv"):
            ok, why = seo.validate_description(s.get(f"seo_desc_{lang}") or "")
            if not ok:
                problems.append({"code": code, "field": f"seo_desc_{lang}", "reason": why})
            ok, why = seo.validate_meta_description(s.get(f"meta_desc_{lang}") or "")
            if not ok:
                problems.append({"code": code, "field": f"meta_desc_{lang}", "reason": why})

    for lang in ("en", "lv"):
        for a, b, sc in seo.find_cannibalization(seo_map, lang=lang, threshold=seo.CANNIBAL_HARD):
            problems.append({"code": a, "field": f"seo_desc_{lang}",
                             "reason": f"cannibalization with {b} (similarity {sc})"})

    if problems and not request.args.get("force"):
        return jsonify(ok=False, problems=problems[:200], total=len(problems)), 422

    buf = io.StringIO()
    w   = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    w.writerow(["category_id", "parent_category_id", "category_path",
                "category_name_lv", "category_name_en",
                "url_slug_lv", "url_slug_en",
                "seo_description_lv", "seo_description_en",
                "meta_description_lv", "meta_description_en"])

    for n in sorted(by_code.values(), key=lambda x: cat_ids[x["code"]]):
        code = n["code"]
        s = seo_map.get(code) or {}
        parent_id = cat_ids.get(n["parent_code"], 0) if n.get("parent_code") else 0
        w.writerow([
            cat_ids[code],
            parent_id,
            paths.get(code, ""),
            s.get("name_lv", ""),
            s.get("name_en", ""),
            s.get("slug_lv", ""),
            s.get("slug_en", ""),
            s.get("seo_desc_lv", ""),
            s.get("seo_desc_en", ""),
            s.get("meta_desc_lv", ""),
            s.get("meta_desc_en", ""),
        ])

    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=magento_categories.csv"})


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=5000)
