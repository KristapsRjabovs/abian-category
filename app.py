import csv
import io
import json
from flask import Flask, jsonify, render_template, request, Response

import db

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
    return dict(
        tree_json      = json.dumps(tree_json,  ensure_ascii=False),
        stats_json     = json.dumps(stats,      ensure_ascii=False),
        cov_json       = json.dumps(coverage,   ensure_ascii=False),
        sources_json   = json.dumps(sources,    ensure_ascii=False),
        supmap_json    = json.dumps(supmap,     ensure_ascii=False),
        paths_json     = json.dumps(paths,      ensure_ascii=False),
        confirmed_json = json.dumps(sorted(confirmed), ensure_ascii=False),
        deleted_json   = json.dumps(sorted(deleted),   ensure_ascii=False),
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
    return jsonify(dict(supmap=supmap, deleted=deleted, confirmed=confirmed, order=order, renames=renames))


@app.route("/api/save", methods=["POST"])
def api_save():
    payload   = request.get_json(force=True)
    supmap    = payload.get("supmap") or {}
    deleted   = payload.get("deleted") or []
    confirmed = payload.get("confirmed") or []
    order     = payload.get("order") or {}
    renames = payload.get("renames") or {}
    db.save_mappings(supmap)
    db.update_node_labels(renames)
    db.save_state("deleted",   sorted(set(deleted)))
    db.save_state("confirmed", sorted(set(confirmed)))
    db.save_state("order",     order)
    db.save_state("renames",   renames)
    return jsonify(ok=True, confirmed=len(confirmed), deleted=len(deleted))


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


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=5000)
