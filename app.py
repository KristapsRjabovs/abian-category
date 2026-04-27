import csv
import io
import json
import re
from flask import Flask, jsonify, render_template, request, Response

import db


# ── SEO validation rules (single source of truth) ─────────────────────────────
SEO_DESC_WORDS  = (50, 70)
META_DESC_CHARS = (120, 160)
CANNIBAL_HARD   = 0.75


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def validate_description(text: str):
    n = _word_count(text)
    lo, hi = SEO_DESC_WORDS
    if n < lo: return False, f"too short ({n} words, min {lo})"
    if n > hi: return False, f"too long ({n} words, max {hi})"
    return True, None


def validate_meta_description(text: str):
    n = len((text or "").strip())
    lo, hi = META_DESC_CHARS
    if n < lo: return False, f"too short ({n} chars, min {lo})"
    if n > hi: return False, f"too long ({n} chars, max {hi})"
    return True, None


def _trigrams(text: str) -> set:
    t = re.sub(r"\s+", " ", (text or "").lower().strip())
    return {t[i:i+3] for i in range(len(t) - 2)} if len(t) >= 3 else {t}


def find_cannibalization(seo_map: dict, lang: str = "en", threshold: float = CANNIBAL_HARD):
    field = "seo_desc_" + lang
    items = [(c, (v.get(field) or "")) for c, v in seo_map.items() if v.get(field)]
    out = []
    for i, (ca, da) in enumerate(items):
        ga = _trigrams(da)
        for cb, db_ in items[i + 1:]:
            gb = _trigrams(db_)
            inter = len(ga & gb); union = len(ga | gb)
            sc = inter / union if union else 0.0
            if sc >= threshold:
                out.append((ca, cb, round(sc, 3)))
    out.sort(key=lambda x: -x[2])
    return out

app = Flask(__name__)


def _page_data():
    deleted           = set(db.load_state("deleted", []))
    confirmed         = db.load_state("confirmed", [])
    content_confirmed = db.load_state("content_confirmed", [])
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
        confirmed_json         = json.dumps(sorted(confirmed),         ensure_ascii=False),
        content_confirmed_json = json.dumps(sorted(content_confirmed), ensure_ascii=False),
        deleted_json           = json.dumps(sorted(deleted),           ensure_ascii=False),
        seo_json               = json.dumps(seo_map,                   ensure_ascii=False),
    )


@app.route("/")
def index():
    return render_template("index.html", **_page_data())


@app.route("/api/state")
def api_state():
    deleted           = db.load_state("deleted", [])
    confirmed         = db.load_state("confirmed", [])
    content_confirmed = db.load_state("content_confirmed", [])
    order             = db.load_state("order", {})
    supmap            = db.build_supmap()
    seo_map           = db.load_seo_map()
    return jsonify(dict(supmap=supmap, deleted=deleted, confirmed=confirmed,
                        content_confirmed=content_confirmed,
                        order=order, renames={}, seo=seo_map))


@app.route("/api/save", methods=["POST"])
def api_save():
    payload    = request.get_json(force=True)
    force      = bool(payload.get("force"))
    supmap     = payload.get("supmap") or {}
    deleted    = payload.get("deleted") or []
    confirmed  = payload.get("confirmed") or []
    order      = payload.get("order") or {}
    renames    = payload.get("renames") or {}
    tree_nodes = payload.get("tree_nodes") or []
    seo_edits  = payload.get("seo_edits") or {}

    # Safety net: refuse to wipe a populated database with an empty payload
    # (the classic "user clicked Save before /api/state finished loading" bug).
    # Caller must pass force=true to override.
    if not force:
        existing = db.load_mappings()
        existing_nodes = db.load_tree_nodes()
        if not tree_nodes and existing_nodes:
            return jsonify(ok=False, error="empty tree_nodes would wipe DB",
                           hint="set force=true to override"), 409
        # supmap is supplier||cat -> [code]; sum the entries to catch zeroing
        incoming_pairs = sum(len(v or []) for v in supmap.values())
        if existing and incoming_pairs == 0:
            return jsonify(ok=False, error="empty supmap would wipe mappings",
                           hint="set force=true to override"), 409

    db.sync_tree_nodes(tree_nodes, set(deleted))
    orphans_dropped = db.save_mappings(supmap)
    db.update_node_labels(renames)
    db.save_seo(seo_edits)
    content_confirmed = payload.get("content_confirmed") or []
    # `renames` is applied via update_node_labels above; no need to persist
    # the diff in tree_state — update_node_labels mutates tree_nodes.label
    # directly and that becomes the new baseline for next load.
    db.save_state("deleted",           sorted(set(deleted)))
    db.save_state("confirmed",         sorted(set(confirmed)))
    db.save_state("content_confirmed", sorted(set(content_confirmed)))
    db.save_state("order",             order)
    return jsonify(ok=True, confirmed=len(confirmed), deleted=len(deleted),
                   content_confirmed=len(content_confirmed),
                   seo_updated=len(seo_edits),
                   orphans_dropped=orphans_dropped)


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
            ok, why = validate_description(s.get(f"seo_desc_{lang}") or "")
            if not ok:
                problems.append({"code": code, "field": f"seo_desc_{lang}", "reason": why})
            ok, why = validate_meta_description(s.get(f"meta_desc_{lang}") or "")
            if not ok:
                problems.append({"code": code, "field": f"meta_desc_{lang}", "reason": why})

    for lang in ("en", "lv"):
        for a, b, sc in find_cannibalization(seo_map, lang=lang, threshold=CANNIBAL_HARD):
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
                "meta_description_lv", "meta_description_en",
                "bottom_seo_lv", "bottom_seo_en"])

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
            s.get("bottom_seo_lv", ""),
            s.get("bottom_seo_en", ""),
        ])

    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=magento_categories.csv"})


@app.route("/api/save-notes", methods=["POST"])
def api_save_notes():
    """Standalone notes save. Updates a single node's notes column without
    going through the heavy save guard, so editors can quickly save a
    review note without touching mappings, tree_nodes, etc."""
    payload = request.get_json(force=True)
    code  = (payload.get("code")  or "").strip()
    notes = payload.get("notes")
    if not code:
        return jsonify(ok=False, error="code is required"), 400
    db.save_seo({code: {"notes": notes if notes is not None else ""}})
    return jsonify(ok=True)


@app.route("/api/notes-export")
def api_notes_export():
    """Plain-text markdown listing every page with editor notes, in a format
    that pastes cleanly into an AI prompt for content revisions."""
    nodes = db.load_tree_nodes()
    deleted = set(db.load_state("deleted", []))
    paths   = db.build_paths(deleted)
    confirmed         = set(db.load_state("confirmed", []))
    content_confirmed = set(db.load_state("content_confirmed", []))

    entries = []
    for n in nodes:
        if n["code"] in deleted:
            continue
        notes = (n.get("notes") or "").strip()
        if not notes:
            continue
        entries.append({
            "code":  n["code"],
            "label": n["label"],
            "path":  paths.get(n["code"], n["code"]),
            "notes": notes,
            "mappings_confirmed": n["code"] in confirmed,
            "content_confirmed":  n["code"] in content_confirmed,
        })

    if not entries:
        body = ("# Category content review notes\n\n"
                "_No editor notes recorded. Add notes from the SEO panel "
                "on any tree node to surface them here._\n")
    else:
        lines = ["# Category content review notes",
                 "",
                 f"You are reviewing SEO content on {len(entries)} category page(s).",
                 "Each block below contains the page identifier, the current "
                 "approval status, and the editor's notes. Update the SEO "
                 "description, meta description and bottom SEO text on each "
                 "page to address every point in the notes. Keep all existing "
                 "constraints (50-70 word seo_desc, 120-160 char meta_desc, "
                 "no brand names, no em-dashes, abbreviations expanded on "
                 "first use, language-mixed where appropriate).",
                 ""]
        for e in entries:
            lines.append(f"## {e['label']}")
            lines.append(f"- **Path:** {e['path']}")
            lines.append(f"- **Code:** `{e['code']}`")
            lines.append(f"- **Mappings confirmed:** {'yes' if e['mappings_confirmed'] else 'no'}")
            lines.append(f"- **Content confirmed:** {'yes' if e['content_confirmed'] else 'no'}")
            lines.append("")
            lines.append("**Notes:**")
            for raw_line in e["notes"].splitlines():
                stripped = raw_line.strip()
                if stripped:
                    lines.append(f"> {stripped}")
                else:
                    lines.append(">")
            lines.append("")
            lines.append("---")
            lines.append("")
        body = "\n".join(lines).rstrip() + "\n"

    return Response(body, mimetype="text/markdown; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=category-notes.md"})


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=5000)
