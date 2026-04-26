"""
Mass-generate SEO category content via Anthropic's Message Batches API.

Submit one batch covering many categories at once, poll for status, then write
the parsed results back into tree_nodes. Each request is one category; the
custom_id is the category code so results are matched safely on return.

Subcommands:
    submit  --prompt FILE [--root CODE] [--codes a,b,c] [--language en|lv]
            [--only-empty] [--limit N] [--model M] [--max-tokens N] [--dry-run]
    status  BATCH_ID
    fetch   BATCH_ID [--write]      (default is dry-run; --write commits to DB)

Requires ANTHROPIC_API_KEY (read by the anthropic SDK) and DATABASE_URL (read
by db.py). Manifests are persisted to .batches/<batch_id>.json so fetch knows
which language fields the batch was targeting.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import time
from pathlib import Path

import db


BATCHES_DIR = Path(".batches")
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 8000

# Map of generic key -> column suffix used by save_seo. The submit command
# materializes this against the chosen language ("_en" / "_lv") before saving
# the manifest, so fetch knows exactly which columns to update.
GENERIC_FIELD_KEYS = ("meta_desc", "slug", "seo_desc", "bottom_seo")


# ─── tree helpers ──────────────────────────────────────────────────────────

def _build_tree_index():
    """Return (nodes_by_code, children_of, path_labels) for fast lookups."""
    nodes = db.load_tree_nodes()
    by_code = {n["code"]: n for n in nodes}
    children_of: dict[str | None, list[str]] = {}
    for n in nodes:
        children_of.setdefault(n.get("parent_code"), []).append(n["code"])
    path_labels: dict[str, list[str]] = {}
    for code in by_code:
        parts, cur = [], code
        while cur:
            parts.append(by_code[cur]["label"])
            cur = by_code[cur].get("parent_code")
        path_labels[code] = list(reversed(parts))
    return by_code, children_of, path_labels


def _descendants_inclusive(root: str, children_of) -> list[str]:
    out, stack = [], [root]
    while stack:
        c = stack.pop()
        out.append(c)
        stack.extend(sorted(children_of.get(c, [])))
    return out


def _category_kind(code: str, by_code, children_of) -> str:
    parent = by_code[code].get("parent_code")
    has_kids = bool(children_of.get(code))
    if parent is None:
        return "root category"
    if not has_kids:
        return "leaf category"
    return "intermediate category"


# ─── prompt + data block ───────────────────────────────────────────────────

def _render_data_block(code: str, language: str, by_code, children_of,
                       path_labels, seo_map) -> str:
    """Build the structured 'Category data' block that becomes the user
    message. Mirrors the fields the prompt asks for."""
    node = by_code[code]
    seo = seo_map.get(code, {})
    name = node["label"] if language == "en" else (seo.get("name_lv") or node["label"])
    path = " > ".join(path_labels[code])
    parent_code = node.get("parent_code")
    parent_label = by_code[parent_code]["label"] if parent_code else None
    child_codes = sorted(children_of.get(code, []))
    child_labels = [by_code[c]["label"] for c in child_codes]
    kind = _category_kind(code, by_code, children_of)

    lang_label = "English" if language == "en" else "Latvian"
    lines = [
        f"Language: {lang_label}",
        f"Category name: {name}",
        f"Category code: {code}",
        f"Category path: {path}",
        f"Category type: {kind}",
    ]
    if parent_label:
        lines.append(f"Parent category: {parent_label}")
    if child_labels:
        lines.append("Child categories: " + ", ".join(child_labels))
    else:
        lines.append("Child categories: (none, this is a leaf)")

    # Existing values, only when populated, so the model can keep tone aligned
    # with anything already curated.
    suffix = "_" + language
    existing = []
    for key, label in (("slug" + suffix, "Existing URL slug"),
                       ("meta_desc" + suffix, "Existing meta description"),
                       ("seo_desc" + suffix, "Existing short description")):
        v = (seo.get(key) or "").strip()
        if v:
            existing.append(f"{label}: {v}")
    if existing:
        lines.append("")
        lines.extend(existing)

    return "\n".join(lines)


def _build_request(code: str, system_prompt: str, data_block: str,
                   model: str, max_tokens: int) -> dict:
    return {
        "custom_id": code,
        "params": {
            "model": model,
            "max_tokens": max_tokens,
            "system": [{
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }],
            "messages": [{
                "role": "user",
                "content": (
                    "Now generate the category content based on this data:\n\n"
                    "Category data:\n" + data_block
                ),
            }],
        },
    }


# ─── response parser ───────────────────────────────────────────────────────

# Anchored at start-of-line section headers from the prompt's Output format.
_SECTION_RE = re.compile(
    r"^(Meta Title|Meta Description|URL Slug|Short Description|Long Description|FAQ)\s*:\s*$",
    re.MULTILINE,
)


def parse_response(text: str) -> dict:
    """Split a model response into the five named sections. Missing sections
    come back as empty strings so the caller can detect partial output."""
    matches = list(_SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for i, m in enumerate(matches):
        key = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[key] = text[start:end].strip()
    return {
        "meta_title": sections.get("Meta Title", ""),
        "meta_desc": sections.get("Meta Description", ""),
        "slug": sections.get("URL Slug", ""),
        "seo_desc": sections.get("Short Description", ""),
        "long_desc": sections.get("Long Description", ""),
        "faq": sections.get("FAQ", ""),
    }


def assemble_bottom_seo(long_desc: str, faq: str) -> str:
    """Join the long-description HTML with the FAQ HTML under a single
    <h2> heading, matching the on-site bottom_seo layout."""
    parts = [long_desc.strip()]
    if faq.strip():
        parts.append("<h2>Frequently asked questions</h2>")
        parts.append(faq.strip())
    return "\n\n".join(p for p in parts if p)


# ─── manifest ──────────────────────────────────────────────────────────────

def _manifest_path(batch_id: str) -> Path:
    return BATCHES_DIR / f"{batch_id}.json"


def _write_manifest(manifest: dict) -> Path:
    BATCHES_DIR.mkdir(exist_ok=True)
    p = _manifest_path(manifest["batch_id"])
    p.write_text(json.dumps(manifest, indent=2))
    return p


def _read_manifest(batch_id: str) -> dict:
    p = _manifest_path(batch_id)
    if not p.exists():
        sys.exit(f"No manifest at {p}. Was this batch submitted from this checkout?")
    return json.loads(p.read_text())


# ─── subcommands ───────────────────────────────────────────────────────────

def cmd_submit(args):
    if not args.root and not args.codes:
        sys.exit("Specify --root CODE or --codes a,b,c.")

    system_prompt = Path(args.prompt).read_text()
    by_code, children_of, path_labels = _build_tree_index()

    if args.root:
        if args.root not in by_code:
            sys.exit(f"Unknown root code: {args.root}")
        codes = _descendants_inclusive(args.root, children_of)
    else:
        codes = [c.strip() for c in args.codes.split(",") if c.strip()]
        unknown = [c for c in codes if c not in by_code]
        if unknown:
            sys.exit(f"Unknown codes: {', '.join(unknown)}")

    seo_map = db.load_seo_map()
    suffix = "_" + args.language
    target_cols = {k: k + suffix for k in GENERIC_FIELD_KEYS}

    if args.only_empty:
        codes = [c for c in codes
                 if not all((seo_map.get(c, {}).get(col) or "").strip()
                            for col in target_cols.values())]

    if args.limit:
        codes = codes[: args.limit]

    if not codes:
        sys.exit("No categories to submit (filters left an empty set).")

    requests = [
        _build_request(
            c,
            system_prompt,
            _render_data_block(c, args.language, by_code, children_of,
                               path_labels, seo_map),
            args.model,
            args.max_tokens,
        )
        for c in codes
    ]

    print(f"Prepared {len(requests)} requests for language={args.language} "
          f"model={args.model}.")
    print("First request preview:")
    first = requests[0]
    print(f"  custom_id: {first['custom_id']}")
    print(f"  user message:\n    " +
          first["params"]["messages"][0]["content"].replace("\n", "\n    "))

    if args.dry_run:
        print("\n--dry-run set; not submitting.")
        return

    import anthropic
    client = anthropic.Anthropic()
    batch = client.messages.batches.create(requests=requests)
    print(f"\nSubmitted batch {batch.id}")

    manifest = {
        "batch_id": batch.id,
        "submitted_at": _dt.datetime.utcnow().isoformat() + "Z",
        "language": args.language,
        "model": args.model,
        "max_tokens": args.max_tokens,
        "prompt_file": str(Path(args.prompt).resolve()),
        "codes": codes,
        "field_map": target_cols,
    }
    p = _write_manifest(manifest)
    print(f"Manifest saved: {p}")
    print(f"Check status:  python batch_generate.py status {batch.id}")
    print(f"Fetch results: python batch_generate.py fetch  {batch.id}")


def cmd_status(args):
    import anthropic
    client = anthropic.Anthropic()
    batch = client.messages.batches.retrieve(args.batch_id)
    rc = batch.request_counts
    print(f"batch_id:           {batch.id}")
    print(f"processing_status:  {batch.processing_status}")
    print(f"created_at:         {batch.created_at}")
    print(f"ended_at:           {getattr(batch, 'ended_at', None)}")
    print(f"counts:             processing={rc.processing} succeeded={rc.succeeded} "
          f"errored={rc.errored} canceled={rc.canceled} expired={rc.expired}")


def cmd_fetch(args):
    manifest = _read_manifest(args.batch_id)
    field_map = manifest["field_map"]

    import anthropic
    client = anthropic.Anthropic()
    batch = client.messages.batches.retrieve(args.batch_id)
    if batch.processing_status != "ended":
        sys.exit(f"Batch not finished; processing_status={batch.processing_status}")

    seo_edits: dict[str, dict] = {}
    failures: list[tuple[str, str]] = []

    for result in client.messages.batches.results(args.batch_id):
        code = result.custom_id
        rtype = result.result.type
        if rtype != "succeeded":
            failures.append((code, rtype))
            continue
        text = result.result.message.content[0].text
        parsed = parse_response(text)
        bottom = assemble_bottom_seo(parsed["long_desc"], parsed["faq"])
        edits = {
            field_map["meta_desc"]:   parsed["meta_desc"],
            field_map["slug"]:        parsed["slug"],
            field_map["seo_desc"]:    parsed["seo_desc"],
            field_map["bottom_seo"]:  bottom,
        }
        # Drop empty fields so we never blank a column on partial parses.
        edits = {k: v for k, v in edits.items() if v.strip()}
        if edits:
            seo_edits[code] = edits

    print(f"Parsed {len(seo_edits)} successful results; {len(failures)} failures.")
    for code, kind in failures:
        print(f"  FAILED  {code}  ({kind})")

    if not seo_edits:
        return

    if not args.write:
        sample = next(iter(seo_edits.items()))
        code, edits = sample
        print(f"\n--write not set; nothing committed. Sample for {code}:")
        for col, val in edits.items():
            preview = val.replace("\n", " ")[:160]
            print(f"  {col}: {preview}{'…' if len(val) > 160 else ''}")
        print(f"\nRe-run with --write to commit {len(seo_edits)} categories to the DB.")
        return

    db.save_seo(seo_edits)
    print(f"Wrote {len(seo_edits)} categories to tree_nodes.")


# ─── argparse ──────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("submit", help="Build and submit a batch.")
    s.add_argument("--prompt", required=True, help="Path to prompt file (system prompt).")
    s.add_argument("--root", help="Category code: include this code and all descendants.")
    s.add_argument("--codes", help="Comma-separated explicit category codes.")
    s.add_argument("--language", choices=("en", "lv"), default="en")
    s.add_argument("--only-empty", action="store_true",
                   help="Skip categories where all four target fields are already filled.")
    s.add_argument("--limit", type=int, help="Cap the number of requests (testing).")
    s.add_argument("--model", default=DEFAULT_MODEL)
    s.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    s.add_argument("--dry-run", action="store_true",
                   help="Build requests and preview, but do not submit.")
    s.set_defaults(func=cmd_submit)

    s = sub.add_parser("status", help="Print processing counts for a batch.")
    s.add_argument("batch_id")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("fetch", help="Download results and (with --write) save to DB.")
    s.add_argument("batch_id")
    s.add_argument("--write", action="store_true",
                   help="Commit parsed content to the DB. Default is dry-run.")
    s.set_defaults(func=cmd_fetch)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
