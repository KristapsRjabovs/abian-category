import csv
import io
import json
from flask import Flask, jsonify, render_template, request, Response

import db

app = Flask(__name__)


def _build_page_data():
    """Assemble all data the template needs."""
    deleted = set(db.load_state("deleted", []))
    confirmed = db.load_state("confirmed", [])

    tree_json = db.build_tree_json(deleted)
    paths = db.build_paths(deleted)
    supmap = db.build_supmap()

    # SOURCES: supplier -> [[supplier, category], ...]  (preserves original order)
    sc_rows = db.load_supplier_categories()
    sources: dict[str, list] = {}
    for row in sc_rows:
        sources.setdefault(row["supplier"], []).append([row["supplier"], row["category"]])

    # Bootstrap supmap with empty entries for unmapped categories
    for row in sc_rows:
        key = row["supplier"] + "||" + row["category"]
        supmap.setdefault(key, [])

    stats = {
        "categories": sum(1 for n in db.load_tree_nodes() if n["code"] not in deleted),
    }

    # Coverage stats
    coverage: dict[str, list] = {}
    for row in db.load_mappings():
        coverage.setdefault(row["tree_code"], []).append(row["supplier"])

    return {
        "tree_json": json.dumps(tree_json, ensure_ascii=False),
        "stats_json": json.dumps(stats, ensure_ascii=False),
        "cov_json": json.dumps(coverage, ensure_ascii=False),
        "sources_json": json.dumps(sources, ensure_ascii=False),
        "supmap_json": json.dumps(supmap, ensure_ascii=False),
        "paths_json": json.dumps(paths, ensure_ascii=False),
        "confirmed_json": json.dumps(sorted(confirmed), ensure_ascii=False),
        "deleted_json": json.dumps(sorted(deleted), ensure_ascii=False),
    }


@app.route("/")
def index():
    data = _build_page_data()
    return render_template("index.html", **data)


@app.route("/save", methods=["POST"])
def save():
    payload = request.get_json(force=True)
    supmap = payload.get("supmap") or {}
    deleted = payload.get("deleted") or []
    confirmed = payload.get("confirmed") or []
    order = payload.get("order") or {}

    db.save_mappings(supmap)
    db.save_state("deleted", sorted(set(deleted)))
    db.save_state("confirmed", sorted(set(confirmed)))
    db.save_state("order", order)

    return jsonify({
        "ok": True,
        "mappings": sum(len(v) for v in supmap.values()),
        "deleted": len(deleted),
        "confirmed": len(confirmed),
    })


def _build_csv(supplier: str) -> str:
    sc_rows = [r for r in db.load_supplier_categories() if r["supplier"] == supplier]
    deleted = set(db.load_state("deleted", []))
    paths = db.build_paths(deleted)

    # Build mapping lookup
    mapping: dict[str, list] = {}
    for row in db.load_mappings():
        if row["supplier"] == supplier:
            mapping.setdefault(row["category"], []).append(row["tree_code"])

    buf = io.StringIO()
    w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    w.writerow(["supplier_name", "supplier_category", "client_category_code", "client_category_label"])
    for row in sc_rows:
        cat = row["category"]
        codes = mapping.get(cat, [])
        if not codes:
            w.writerow([supplier, cat, "", ""])
        else:
            for code in codes:
                w.writerow([supplier, cat, code, paths.get(code, "")])
    return buf.getvalue()


@app.route("/download/also")
def download_also():
    content = _build_csv("also_data")
    return Response(
        content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=also_mapping.csv"},
    )


@app.route("/download/elko")
def download_elko():
    content = _build_csv("elko")
    return Response(
        content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=elko_mapping.csv"},
    )


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=5000)
