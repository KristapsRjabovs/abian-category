"""
Round-trip integration test for the save/load pipeline.

Catches the class of regressions we keep shipping: SEO content disappearing,
empty strings overwriting baked content, name_en drifting from tree label,
and orphan mapping codes sneaking through.

Usage:
    python3 test_roundtrip.py
"""
import json
import sqlite3
import sys

import app
import db


def assert_eq(actual, expected, label):
    if actual != expected:
        print(f"  FAIL {label}: expected {expected!r}, got {actual!r}")
        return 1
    print(f"  ok   {label}")
    return 0


def snapshot_state(client):
    return json.loads(client.get("/api/state").data)


def main() -> int:
    client = app.app.test_client()
    fails = 0

    # Snapshot current state so we can restore it at the end
    before = snapshot_state(client)
    # Tree nodes come from the DB directly; /api/state doesn't ship them on Flask
    tree_rows = db.load_tree_nodes()
    full_nodes_rows = [{"code": n["code"], "label": n["label"], "parent_code": n["parent_code"]}
                       for n in tree_rows]

    # ─── Test 1: name_en mirrors tree label ─────────────────────────────────
    seo = before.get("seo", {})
    nodes = {n["code"]: n["label"] for n in tree_rows}
    drifted = [c for c, e in seo.items()
               if (e.get("name_en") or "") and c in nodes
               and e["name_en"] != nodes[c]]
    fails += assert_eq(len(drifted), 0, "name_en matches tree label for every node")

    # ─── Test 2: save+load round-trip preserves SEO edits ───────────────────
    test_code = next(iter(nodes.keys()))
    test_lv   = "TEST-ROUNDTRIP-" + test_code
    # Preserve full parent_code map so sync_tree_nodes doesn't flatten the tree
    full_nodes = full_nodes_rows
    payload = {
        # send the existing supmap so the empty-payload safety guard doesn't
        # 409 us — we're testing SEO + tree, not wiping mappings
        "supmap":     before.get("supmap", {}),
        "deleted":    before.get("deleted", []),
        "confirmed":  before.get("confirmed", []),
        "content_confirmed": before.get("content_confirmed", []),
        "order":      before.get("order", {}),
        "renames":    before.get("renames", {}),
        "tree_nodes": full_nodes,
        "seo_edits":  {test_code: {"name_lv": test_lv}},
    }
    r = client.post("/api/save", json=payload)
    fails += assert_eq(r.status_code, 200, "save returns 200")
    after = snapshot_state(client)
    fails += assert_eq(after["seo"][test_code]["name_lv"], test_lv,
                       "seo_edits round-trips through save+load")
    # name_en still equals tree label after save (the bug we just shipped a fix for)
    fails += assert_eq(after["seo"][test_code]["name_en"], nodes[test_code],
                       "name_en still equals tree label after save")

    # ─── Test 3: empty SEO fields don't shadow the live value ───────────────
    payload["seo_edits"] = {test_code: {"name_lv": ""}}
    client.post("/api/save", json=payload)
    after2 = snapshot_state(client)
    # An empty edit should clear the field, not crash. Either "" or unset is acceptable.
    got = (after2["seo"][test_code].get("name_lv") or "")
    fails += assert_eq(got, "", "empty seo_edit clears the field")

    # ─── Test 4: orphan mapping codes are dropped ───────────────────────────
    payload["supmap"]    = {"test_supplier||test_cat": ["NONEXISTENT_CODE_XYZ"]}
    payload["seo_edits"] = {}
    r = client.post("/api/save", json=payload)
    body = json.loads(r.data)
    fails += assert_eq(body.get("orphans_dropped"), 1, "orphan mapping was dropped")
    after3 = snapshot_state(client)
    fails += assert_eq(after3["supmap"].get("test_supplier||test_cat"), None,
                       "orphan mapping not in returned state")

    # ─── Restore original state ─────────────────────────────────────────────
    client.post("/api/save", json={
        "supmap":     before.get("supmap", {}),
        "deleted":    before.get("deleted", []),
        "confirmed":  before.get("confirmed", []),
        "content_confirmed": before.get("content_confirmed", []),
        "order":      before.get("order", {}),
        "renames":    before.get("renames", {}),
        "tree_nodes": full_nodes,
        "seo_edits":  {test_code: {"name_lv": (before["seo"].get(test_code, {}).get("name_lv") or "")}},
    })

    print()
    if fails:
        print(f"FAILED ({fails} assertion(s))")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
