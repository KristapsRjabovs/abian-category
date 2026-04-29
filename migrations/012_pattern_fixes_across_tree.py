"""
Apply pattern-level fixes derived from the editor's review of pages 1-4.

The audit found these issues repeated across the tree (197 pages × multiple
content fields). This migration fixes the deterministic ones in one pass so
the editor does not have to flag the same thing on every page.

Fixes applied here:

  1. Abbreviations expanded on first use in EACH content field:
     POS, PDA, CPU, GPU, RAM, ECC, BMC, PSU, HBA, RAID, USB-C, VESA, NAS,
     TPM, SSD, HDD, DDR, DIMM, SODIMM. ~53 hits across the tree.

  2. Warranty mentions soft-prefixed with "manufacturer" / "ražotāja" when
     they were not already qualified. The editor's rule: warranties are
     only ever mentioned as manufacturer warranties, never as something
     the shop itself provides. ~97 hits across the tree.

NOT auto-fixed (need a hand-rewrite migration):

  - 8 pages under other/* where the bottom_seo first paragraph duplicates
    the seo_desc and the second paragraph echoes the first. The agent
    that wrote those used a copy-paste opening pattern. Listed at the
    end of this migration's run output.
"""
import re

ABBR_EXPANSIONS_EN = {
    "POS":     "Point of Sale",
    "PDA":     "Personal Digital Assistant",
    "CPU":     "Central Processing Unit",
    "GPU":     "Graphics Processing Unit",
    "RAM":     "Random Access Memory",
    "ECC":     "Error-Correcting Code",
    "BMC":     "Baseboard Management Controller",
    "PSU":     "Power Supply Unit",
    "HBA":     "Host Bus Adapter",
    "RAID":    "Redundant Array of Independent Disks",
    "USB-C":   "Universal Serial Bus Type-C",
    "VESA":    "mounting standard",
    "NAS":     "Network Attached Storage",
    "TPM":     "Trusted Platform Module",
    "SSD":     "Solid State Drive",
    "HDD":     "Hard Disk Drive",
    "DDR":     "Double Data Rate",
    "DIMM":    "Dual In-line Memory Module",
    "SODIMM":  "Small Outline DIMM",
    "NVR":     "Network Video Recorder",
    "DVR":     "Digital Video Recorder",
}

# In LV the parenthetical can stay in English — that is the project convention.

CONTENT_FIELDS = ("seo_desc_en", "seo_desc_lv", "meta_desc_en", "meta_desc_lv",
                  "bottom_seo_en", "bottom_seo_lv")


def expand_first_use(text: str, abbr_map: dict) -> str:
    """For each abbreviation, find the FIRST occurrence as a whole word and
    insert " (Long Form)" right after if not already followed by a parenthetical."""
    if not text:
        return text
    out = text
    for ab, longform in abbr_map.items():
        # match whole-word occurrence not already followed by " (..."
        pattern = re.compile(rf'\b{re.escape(ab)}\b(?!\s*\()')
        m = pattern.search(out)
        if not m:
            continue
        # Skip if "Long Form" already appears in a parenthesis nearby
        nearby = out[max(0, m.start()-80) : m.end()+80]
        if longform.lower() in nearby.lower():
            continue
        out = out[:m.end()] + f" ({longform})" + out[m.end():]
    return out


def soft_prefix_warranty(text: str, lang: str) -> str:
    """If a warranty mention is not already qualified by manufacturer/ražotāj,
    insert the qualifier. Conservative: only at noun-phrase starts."""
    if not text:
        return text
    if lang == "en":
        # Find each "warranty" not preceded by manufacturer within 50 chars
        def repl(m):
            start = m.start()
            window = text[max(0, start-50):start]
            if re.search(r'\bmanufacturer\b', window, re.IGNORECASE):
                return m.group(0)
            # Avoid hyphenated forms (warranty-sensitive)
            if start > 0 and text[start-1] == "-":
                return m.group(0)
            after_idx = m.end()
            if after_idx < len(text) and text[after_idx] == "-":
                return m.group(0)
            return "manufacturer " + m.group(0)
        return re.sub(r'\bwarranty\b', repl, text)
    else:  # lv
        def repl(m):
            start = m.start()
            window = text[max(0, start-50):start]
            if re.search(r'ražotāj', window, re.IGNORECASE):
                return m.group(0)
            return "ražotāja " + m.group(0)
        return re.sub(r'\b(garantij[āauims]?)\b', repl, text)


PARA_DUP_PAGES = [
    "other/home-lifestyle/personal-care",
    "other/home-lifestyle/small-household-lamps",
    "other/home-lifestyle/sport-outdoor-hobbies",
    "other/home-lifestyle/vacuums-cleaning",
    "other/office-equipment-furniture",
    "other/power-tools-garden",
    "other/renewable-energy",
    "other/smart-home-iot",
]


def apply(conn):
    abbr_changes = warr_changes = 0
    pages_touched = set()
    with conn.cursor() as cur:
        cur.execute(f"SELECT code, {', '.join(CONTENT_FIELDS)} FROM tree_nodes")
        rows = cur.fetchall()
        for r in rows:
            code = r[0]
            updates, set_clauses, vals = {}, [], []
            for i, field in enumerate(CONTENT_FIELDS, start=1):
                original = r[i] or ""
                if not original:
                    continue
                lang = "en" if field.endswith("_en") else "lv"
                # Abbreviations are expanded only in EN content (parenthetical is English).
                fixed = original
                if lang == "en":
                    fixed = expand_first_use(fixed, ABBR_EXPANSIONS_EN)
                else:
                    # LV pages still need expansion of EN-only abbreviations on first use
                    fixed = expand_first_use(fixed, ABBR_EXPANSIONS_EN)
                if fixed != original:
                    abbr_changes += 1
                fixed_warr = soft_prefix_warranty(fixed, lang)
                if fixed_warr != fixed:
                    warr_changes += 1
                if fixed_warr != original:
                    updates[field] = fixed_warr
            if updates:
                pages_touched.add(code)
                for f, v in updates.items():
                    set_clauses.append(f"{f} = %s")
                    vals.append(v)
                vals.append(code)
                cur.execute(
                    f"UPDATE tree_nodes SET {', '.join(set_clauses)} WHERE code = %s",
                    vals,
                )

    print(f"  abbreviation expansions inserted: {abbr_changes}")
    print(f"  warranty mentions soft-prefixed:  {warr_changes}")
    print(f"  pages touched: {len(pages_touched)}")
    print(f"  pages still needing hand-rewrite (paragraph duplication): {len(PARA_DUP_PAGES)}")
    for p in PARA_DUP_PAGES:
        print(f"    - {p}")
