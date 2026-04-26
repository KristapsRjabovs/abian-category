"""
Smoke test against a deployed Netlify environment.

Hits the read endpoints and asserts shapes match what the editor expects.
Does NOT mutate state. Pass the base URL via env or arg:

    NETLIFY_URL=https://your-site.netlify.app python3 test_netlify_live.py
    python3 test_netlify_live.py https://your-site.netlify.app

Run after each deploy to confirm the JS functions still talk to Postgres.
"""
import json
import os
import sys
from urllib.request import Request, urlopen


def get(url: str) -> tuple:
    req = Request(url, headers={"User-Agent": "abian-smoke-test"})
    with urlopen(req, timeout=15) as r:
        return r.status, r.read()


def main(base: str) -> int:
    base = base.rstrip("/")
    fails = 0

    # /api/state
    status, body = get(base + "/api/state")
    if status != 200:
        print(f"  FAIL /api/state HTTP {status}"); return 1
    s = json.loads(body)
    for key in ("seo", "supmap", "tree_nodes", "deleted", "confirmed",
                "content_confirmed", "order"):
        if key not in s:
            print(f"  FAIL /api/state missing key {key!r}"); fails += 1
    if not s.get("tree_nodes"):
        print(f"  FAIL /api/state.tree_nodes is empty"); fails += 1
    else:
        print(f"  ok   /api/state ({len(s['tree_nodes'])} nodes, "
              f"{len(s['supmap'])} supmap keys, {len(s['seo'])} SEO entries)")
    nodes = s.get("tree_nodes") or []
    name_drift = sum(1 for n in nodes
                     if (s["seo"].get(n["code"], {}).get("name_en") or "") != n["label"])
    if name_drift:
        print(f"  FAIL {name_drift} nodes have name_en != tree label"); fails += 1
    else:
        print(f"  ok   name_en mirrors tree label for every node")

    # /api/download (CSV)
    for sup in ("also_data", "elko"):
        status, body = get(base + "/api/download?supplier=" + sup)
        rows = body.decode().count("\n")
        if status != 200 or rows < 2:
            print(f"  FAIL /api/download?supplier={sup} HTTP {status}, {rows} rows")
            fails += 1
        else:
            print(f"  ok   /api/download?supplier={sup} ({rows} rows)")

    # /api/category-export — without ?force, may return 422 if SEO incomplete
    status, body = get(base + "/api/category-export?force=true")
    rows = body.decode().count("\n")
    if status != 200 or rows < 2:
        print(f"  FAIL /api/category-export?force=true HTTP {status}"); fails += 1
    else:
        first = body.decode().splitlines()[0]
        expected = "category_id"
        if expected not in first:
            print(f"  FAIL /api/category-export header missing {expected!r}"); fails += 1
        else:
            print(f"  ok   /api/category-export ({rows} rows)")

    print()
    if fails:
        print(f"FAILED ({fails} assertion(s))"); return 1
    print("PASS"); return 0


if __name__ == "__main__":
    base = os.environ.get("NETLIFY_URL")
    if not base and len(sys.argv) > 1:
        base = sys.argv[1]
    if not base:
        print("usage: NETLIFY_URL=https://your-site.netlify.app python3 test_netlify_live.py")
        sys.exit(2)
    sys.exit(main(base))
