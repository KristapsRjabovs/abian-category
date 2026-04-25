"""
SEO metadata generator for the category tree.

Produces deterministic, template-driven category names, URL slugs and
50-70 word SEO descriptions in English and Latvian. Designed to seed sensible
defaults — human editors refine via the UI.

Public API
    slugify_en(text)            -> str           # ASCII, lowercase, hyphenated
    slugify_lv(text)            -> str           # transliterates LV diacritics
    translate_to_lv(label)      -> str           # dictionary lookup, fallback = label
    generate(node, context)     -> dict          # full SEO dict for one node
    similarity(a, b)            -> float         # trigram Jaccard
    find_cannibalization(seo_map, lang, t)       # [(code_a, code_b, score), ...]
    validate_description(text)  -> (ok, reason)  # 50-70 word check

Generator output is stable: same inputs -> same outputs (hash-based variant pick).
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


# ───────────────────────────────────────── slugify ───────────────────────────

_LV_TRANSLIT = str.maketrans({
    "ā": "a", "č": "c", "ē": "e", "ģ": "g", "ī": "i",
    "ķ": "k", "ļ": "l", "ņ": "n", "š": "s", "ū": "u", "ž": "z",
    "Ā": "a", "Č": "c", "Ē": "e", "Ģ": "g", "Ī": "i",
    "Ķ": "k", "Ļ": "l", "Ņ": "n", "Š": "s", "Ū": "u", "Ž": "z",
})


def _slug(text: str) -> str:
    text = (text or "").strip().lower()
    # strip any residual combining marks (e.g. accidental NFD input)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def slugify_en(text: str) -> str:
    return _slug(text)


def slugify_lv(text: str) -> str:
    # Apply LV diacritic → ASCII mapping first, then the standard slug pipeline
    return _slug((text or "").translate(_LV_TRANSLIT))


# ───────────────────────────────── LV translation dictionary ─────────────────
# Covers common IT-retail category terms. Unknown tokens fall through to the
# original English word (transliteration via slugify handles the URL side).
# Keys are lowercase. For phrases, the whole phrase is checked first, then
# individual words.

_LV_PHRASES = {
    # Top-level
    "components & accessories":          "Komponentes un piederumi",
    "components and accessories":        "Komponentes un piederumi",
    "computers, servers & tablets":      "Datori, serveri un planšetes",
    "networking":                        "Tīkla iekārtas",
    "displays & projectors":             "Monitori un projektori",
    "phones & devices":                  "Telefoni un ierīces",
    "printers & scanners":               "Printeri un skeneri",
    "audio & video & tv":                "Audio, video un TV",
    "cameras":                           "Fotokameras",
    "software applications":             "Programmatūra",
    "navigation & radios":               "Navigācija un radio",

    # Storage family
    "storage & memory":                  "Atmiņa un datu nesēji",
    "memory (ram)":                      "Operatīvā atmiņa (RAM)",
    "desktop memory (dimm)":             "Datora atmiņa (DIMM)",
    "notebook memory (sodimm)":          "Portatīvā datora atmiņa (SODIMM)",
    "hard drives (hdd)":                 "Cietie diski (HDD)",
    "internal hdds":                     "Iekšējie cietie diski",
    "external hdds":                     "Ārējie cietie diski",
    "solid state drives (ssd)":          "SSD diski",
    "internal ssds":                     "Iekšējie SSD diski",
    "external ssds":                     "Ārējie SSD diski",
    "enterprise ssds":                   "Uzņēmumu klases SSD",
    "flash memory (usb, sd, cf)":        "Flash atmiņa (USB, SD, CF)",
    "storage media (cd, dvd, blu-ray)":  "Datu nesēji (CD, DVD, Blu-ray)",
    "nas & disk arrays":                 "NAS un diska masīvi",
    "optical drives":                    "Optiskie diskdziņi",
    "tape backup":                       "Lenšu rezerves kopijas",

    # Peripherals
    "keyboards & mice":                  "Tastatūras un peles",
    "keyboards":                         "Tastatūras",
    "mice":                              "Peles",
    "mouse":                             "Peles",
    "numeric keypads":                   "Cipartaustiņu bloki",
    "mousepads, desk pads & wrist rests":"Peles paliktņi un plaukstu balsti",
    "digitizers & stylus pens":          "Grafikas planšetes un stili",
    "presenters & remotes":              "Prezentāciju pultis",

    # Cables & power
    "cables":                            "Kabeļi",
    "data cables & adapters":            "Datu kabeļi un adapteri",
    "power cables":                      "Barošanas kabeļi",
    "usb & interface hubs":              "USB un interfeisa habi",
    "card readers":                      "Karšu lasītāji",
    "power supplies (psu)":              "Barošanas bloki (PSU)",
    "power protection devices":          "Barošanas aizsardzība",
    "ups systems (ups)":                 "UPS sistēmas",
    "power distribution units (pdu)":    "PDU sadales bloki",
    "power accessories":                 "Barošanas piederumi",
    "batteries & chargers":              "Baterijas un lādētāji",
    "chargers & powerbanks":             "Lādētāji un powerbanks",

    # Components
    "processors (cpu)":                  "Procesori (CPU)",
    "desktop cpus":                      "Datoru procesori",
    "motherboards":                      "Mātesplates",
    "video cards (gpu)":                 "Videokartes",
    "fans & cooling systems":            "Ventilatori un dzesēšanas sistēmas",
    "cases":                             "Korpusi",
    "pc add-ons & accessories":          "Datoru papildinājumi un piederumi",
    "internal pc cables":                "Iekšējie datora kabeļi",
    "tpm modules":                       "TPM moduļi",
    "other pc accessories":              "Citi datora piederumi",
    "controller cards (raid/hba)":       "Kontroliera kartes (RAID/HBA)",
    "sound cards":                       "Skaņas kartes",
    "web cameras":                       "Web kameras",
    "kvm":                               "KVM pārslēdzēji",

    # Displays
    "monitors":                          "Monitori",
    "projectors":                        "Projektori",
    "large format displays & video walls":"Liela formāta displeji un video sienas",
    "video walls":                       "Video sienas",
    "signage displays":                  "Informatīvie displeji",
    "monitor accessories":               "Monitoru piederumi",

    # AV
    "tvs":                               "Televizori",
    "led & smart tvs":                   "LED un Smart TV",
    "speakers":                          "Skaļruņi",
    "portable speakers":                 "Pārnēsājamie skaļruņi",
    "soundbars":                         "Soundbar skaļruņi",
    "headphones":                        "Austiņas",
    "car audio & video":                 "Auto audio un video",
    "radios":                            "Radio",
    "media players":                     "Multimediju atskaņotāji",
    "game consoles":                     "Spēļu konsoles",
    "surveillance":                      "Videonovērošana",
    "access readers":                    "Piekļuves kontroles lasītāji",
    "nvr, dvr & accessories":            "NVR, DVR un piederumi",
    "cctv cameras":                      "Novērošanas kameras",

    # Phones
    "mobile phones":                     "Mobilie telefoni",
    "smartphones":                       "Viedtālruņi",
    "wearables":                         "Valkājamās ierīces",
    "smartwatches":                      "Viedpulksteņi",
    "tablets":                           "Planšetes",
    "notebook accessories":              "Portatīvo datoru piederumi",
    "tablet accessories":                "Planšetdatoru piederumi",

    # Networking
    "routers":                           "Maršrutētāji",
    "switches":                          "Komutatori",
    "network cards & adapters":          "Tīkla kartes un adapteri",
    "wireless":                          "Bezvadu iekārtas",
    "access points":                     "Piekļuves punkti",
    "transceivers":                      "Raiduztvērēji (SFP)",

    # Print
    "printers":                          "Printeri",
    "scanners":                          "Skeneri",
    "consumables":                       "Izejmateriāli",
    "toner":                             "Toneris",
    "ink":                               "Tinte",

    # Generic nouns (word-level fallback)
    "accessories":                       "piederumi",
    "other":                             "Cits",
    "drones":                            "Droni",
    "servers":                           "Serveri",
    "desktop":                           "Dators",
    "notebook":                          "Klēpjdators",
    "laptops":                           "Klēpjdatori",
    "tools":                             "Rīki",
    "software":                          "Programmatūra",
}


def translate_to_lv(label: str) -> str:
    """Translate a category label to Latvian using the phrase dictionary.
    Falls back to the original label if no match (editor can refine manually)."""
    if not label:
        return ""
    key = label.strip().lower()
    if key in _LV_PHRASES:
        return _LV_PHRASES[key]
    # Try stripping trailing " (X)" parentheticals and retrying
    stripped = re.sub(r"\s*\([^)]*\)\s*$", "", key).strip()
    if stripped and stripped in _LV_PHRASES:
        # preserve the parenthetical in the returned LV name
        tail = label[len(label) - (len(label) - len(stripped)):].strip()
        if tail.startswith("("):
            return f"{_LV_PHRASES[stripped]} {tail}"
        return _LV_PHRASES[stripped]
    return label


# ─────────────────────────── description generator ──────────────────────────

# Use-case hints keyed by the root (top-level) segment of the code path.
_EN_USECASE = {
    "components":         "PC builds, upgrades, and repairs",
    "computers":          "home, office, and workstation use",
    "networking":         "home, office, and enterprise networks",
    "displays":           "office, gaming, and creative work",
    "phones-radios":      "everyday mobile use and communication",
    "print-scan":         "document workflows in home and office",
    "av":                 "home entertainment and professional AV",
    "cameras":            "photography, vlogging, and content creation",
    "software-apps":      "business productivity and system management",
    "other":              "daily office and specialty needs",
}

_LV_USECASE = {
    "components":         "datoru komplektēšanai, uzlabojumiem un remontam",
    "computers":          "mājām, birojam un darbstacijām",
    "networking":         "mājas, biroja un uzņēmuma tīkliem",
    "displays":           "birojam, spēlēm un radošam darbam",
    "phones-radios":      "ikdienas mobilai lietošanai un saziņai",
    "print-scan":         "dokumentu apstrādei mājās un birojā",
    "av":                 "mājas izklaidei un profesionālām AV sistēmām",
    "cameras":            "fotogrāfijai, vlogošanai un satura veidošanai",
    "software-apps":      "biznesa produktivitātei un sistēmu pārvaldībai",
    "other":              "ikdienas biroja un speciāliem risinājumiem",
}


# Openers are picked deterministically by hash; each template has its own tone
_EN_OPENERS = [
    "Browse our selection of {label} suited to {uc}.",
    "Shop {label} built for {uc}.",
    "Discover {label} from trusted manufacturers covering {uc}.",
    "Find the right {label} for {uc}.",
    "Explore our {label} range assembled for {uc}.",
    "Our {label} line-up is curated for {uc}.",
]

_EN_CHILD_MENTION = [
    "The category covers {children}.",
    "Options include {children}.",
    "Choose between {children}.",
    "Our range spans {children}.",
]

_EN_PRODUCT_MENTION = [
    "Typical items here include {samples}.",
    "Popular picks include {samples}.",
    "You will find {samples} within this section.",
]

_EN_CONTEXT = [
    "Sitting inside {parent}, this section focuses on {label_short} without overlapping neighbouring groups.",
    "Grouped under {parent}, it isolates {label_short} so buyers can compare like-for-like models.",
    "We separate {label_short} from the wider {parent} group to keep search and filtering focused.",
    "Kept distinct from the rest of {parent}, this node covers only {label_short}.",
]

_EN_LEAF_HINT = [
    "Expect specs sheets, compatibility notes, and price tiers you can filter by brand or form factor.",
    "Listings carry manufacturer part numbers, stock status, and warranty terms so procurement stays straightforward.",
    "Each entry shows the current distributor price, availability window, and the closest alternatives if stock runs low.",
    "Datasheets, EAN codes, and warranty information sit on every product page to speed up B2B decisions.",
]

_EN_TRUST = [
    "Stock is verified across authorized distributors, so specifications and compatibility stay accurate.",
    "Every listing is cross-checked with our distributors to keep availability and pricing reliable.",
    "We source from official channels, giving you warranty-backed products and honest stock signals.",
    "Each product is matched to distributor data so you can order with confidence in compatibility.",
    "Items are kept in sync with distributor catalogs for up-to-date specs and stock status.",
]

_EN_CTA = [
    "Compare specifications, pick what fits your setup, and order with same-day dispatch on in-stock items.",
    "Use the filters to narrow by brand or specification and place an order at wholesale-friendly pricing.",
    "Review details, add to cart, and receive fast delivery across Latvia and the Baltics.",
    "Check detailed specs, pick the best match, and benefit from transparent B2B pricing.",
]

_LV_OPENERS = [
    "Pārlūkojiet {label}, kas piemērotas {uc}.",
    "Iegādājieties {label}, kas veidotas {uc}.",
    "Izvēlieties {label} no uzticamiem ražotājiem — {uc}.",
    "Atrodiet piemērotas {label}, lai apmierinātu {uc}.",
    "Aplūkojiet {label} klāstu, kas sagatavots {uc}.",
    "Mūsu {label} izlase ir atlasīta {uc}.",
]

_LV_CHILD_MENTION = [
    "Kategorijā ietilpst {children}.",
    "Pieejami varianti: {children}.",
    "Izvēle starp {children}.",
    "Klāsts ietver {children}.",
]

_LV_PRODUCT_MENTION = [
    "Šeit atradīsiet {samples}.",
    "Populārākie piedāvājumi ir {samples}.",
    "Sadaļā ietilpst {samples}.",
]

_LV_CONTEXT = [
    "Šī sadaļa atrodas {parent} grupā un koncentrējas tikai uz {label_short}, nedublējot blakus sadaļas.",
    "Sagrupēta {parent} ietvaros, tā nošķir {label_short}, lai pircēji var salīdzināt līdzīgus modeļus.",
    "{label_short} ir atdalīta no pārējā {parent} klāsta, lai meklēšana un filtri paliktu precīzi.",
    "Atsevišķa no pārējā {parent} klāsta — šī sadaļa aptver tikai {label_short}.",
]

_LV_LEAF_HINT = [
    "Sagaidiet tehniskās specifikācijas, saderības piezīmes un cenu kategorijas, ko var filtrēt pēc zīmola vai formāta.",
    "Katrai pozīcijai norādīti ražotāja artikula numuri, krājumu statuss un garantijas nosacījumi — iepirkums kļūst vienkāršāks.",
    "Katrā ierakstā parādīta pašreizējā izplatītāja cena, pieejamības laiks un tuvākās alternatīvas, ja krājumi ir maz.",
    "Datu lapas, EAN kodi un garantijas informācija pieejami katrā preces lapā, lai paātrinātu B2B lēmumus.",
]

_LV_TRUST = [
    "Krājumi tiek pārbaudīti pie oficiāliem izplatītājiem, tāpēc specifikācijas un saderība ir precīzas.",
    "Katra pozīcija ir salāgota ar izplatītāju datiem, lai pieejamība un cena būtu uzticama.",
    "Mēs iegādājamies tikai oficiālos kanālos, tāpēc saņemat preces ar garantiju un skaidriem krājuma datiem.",
    "Preces tiek sinhronizētas ar izplatītāju katalogiem — aktuālas specifikācijas un krājuma statuss.",
]

_LV_CTA = [
    "Salīdziniet specifikācijas, izvēlieties piemērotāko un izmantojiet ātru piegādi Baltijā.",
    "Izmantojiet filtrus, atlasiet pēc zīmola un pasūtiet par izdevīgām B2B cenām.",
    "Apskatiet detalizētas specifikācijas, pievienojiet grozam un saņemiet ātri.",
    "Iepazīstieties ar specifikācijām un izvēlieties risinājumu ar caurskatāmu B2B cenošanu.",
]


def _hash_pick(seed: str, bucket: List[str], salt: str = "", offset: int = 0) -> str:
    """Deterministic choice from a list based on a string seed.
    `offset` lets callers request the Nth alternate variant when the default
    collides with a sibling description (used by the cannibalization retry pass).
    """
    h = hashlib.md5((seed + "|" + salt).encode("utf-8")).digest()
    return bucket[(h[0] + offset) % len(bucket)]


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def _endswith_sentence(text: str) -> bool:
    return bool(text) and text.rstrip()[-1:] in ".!?"


def _ensure_sentence(text: str) -> str:
    t = text.rstrip(" ,;:")
    return t if _endswith_sentence(t) else t + "."


def _fit_word_range(text: str, lo: int = 50, hi: int = 70, filler_en: bool = True) -> str:
    """Trim or pad a description to fit [lo, hi] words without breaking sentences."""
    # Squash double terminal punctuation like ".." that accidentally occurs when a
    # template already ends with "." and gets wrapped again.
    text = re.sub(r"([.!?])\s*\1+", r"\1", text)
    words = re.findall(r"\S+", text)
    if len(words) > hi:
        # Trim to hi words, then cut back to the last sentence-ending punctuation
        clipped = " ".join(words[:hi])
        m = re.search(r"^(.*[.!?])[^.!?]*$", clipped)
        text = _ensure_sentence(m.group(1) if m else clipped)
        words = re.findall(r"\S+", text)
    if len(words) < lo:
        # Pad with an honest extra clause rather than repeating phrases
        fillers_en = [
            "Get in touch for bulk orders or custom configurations.",
            "Technical questions are answered same day by our product team.",
            "Volume pricing is available on request for qualified resellers.",
        ]
        fillers_lv = [
            "Sazinieties par apjoma pasūtījumiem vai individuālām konfigurācijām.",
            "Tehniskos jautājumus mūsu komanda atbild tajā pašā dienā.",
            "Apjoma cenas pieejamas pēc pieprasījuma kvalificētiem tālākpārdevējiem.",
        ]
        pool = fillers_en if filler_en else fillers_lv
        i = 0
        while _word_count(text) < lo and i < len(pool):
            text = (text.rstrip() + " " + pool[i]).strip()
            i += 1
        # Last resort: gentle repeat
        while _word_count(text) < lo:
            text = text + " " + pool[0]
    return text


def _children_phrase(children_labels: List[str], lang: str) -> str:
    names = [c for c in children_labels if c]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        joiner = " and " if lang == "en" else " un "
        return joiner.join(names)
    joiner = ", ".join(names[:-1])
    tail = names[-1]
    last_joiner = ", and " if lang == "en" else " un "
    return f"{joiner}{last_joiner}{tail}"


def generate(node: Dict[str, Any], context: Dict[str, Any],
             variant_offset: int = 0) -> Dict[str, str]:
    """Generate SEO fields for one node.

    node:    {code, label, parent_code, ...}
    context: {
        "children_labels":   [str, ...],      # immediate children's labels
        "supplier_samples":  [str, ...],      # a few mapped supplier categories
        "breadcrumb":        "Root > Parent > Label",
        "parent_label_en":   str,
        "parent_label_lv":   str,
    }
    variant_offset: 0 = default template pick. Callers that detect cannibalization
                    can retry with 1, 2, ... to get structurally different output.

    Returns all six SEO fields. Caller decides whether to commit.
    """
    vo = variant_offset
    code  = node.get("code")  or ""
    label = node.get("label") or code.split("/")[-1].replace("-", " ").title()
    root  = code.split("/", 1)[0] if code else "other"

    # Names
    name_en = label
    name_lv = translate_to_lv(label)
    # Slugs
    slug_en = slugify_en(name_en)
    slug_lv = slugify_lv(name_lv)

    # Build descriptions
    children = context.get("children_labels") or []
    samples  = context.get("supplier_samples") or []

    uc_en = _EN_USECASE.get(root, _EN_USECASE["other"])
    uc_lv = _LV_USECASE.get(root, _LV_USECASE["other"])

    # Lowercase only if the label is regular words — keep acronyms / mixed-case intact.
    def _for_prose(s: str) -> str:
        if not s:
            return s
        # Preserve if it has any uppercase letter after the first character (acronyms, "LED", "TV's")
        return s if any(c.isupper() for c in s[1:]) else s.lower()
    opener_en = _hash_pick(code, _EN_OPENERS, "open", vo).format(label=_for_prose(name_en), uc=uc_en)
    opener_lv = _hash_pick(code, _LV_OPENERS, "open", vo).format(label=_for_prose(name_lv), uc=uc_lv)

    mid_en, mid_lv = "", ""
    if children:
        shown = children[:4]
        mid_en = _hash_pick(code, _EN_CHILD_MENTION, "mid", vo).format(children=_children_phrase(shown, "en"))
        mid_lv = _hash_pick(code, _LV_CHILD_MENTION, "mid", vo).format(children=_children_phrase(shown, "lv"))
    elif samples:
        shown = samples[:3]
        joined_en = _children_phrase(shown, "en")
        joined_lv = _children_phrase(shown, "lv")
        mid_en = _hash_pick(code, _EN_PRODUCT_MENTION, "mid", vo).format(samples=joined_en)
        mid_lv = _hash_pick(code, _LV_PRODUCT_MENTION, "mid", vo).format(samples=joined_lv)

    # Context sentence grounds each description in its parent-segment + label
    parent_en = context.get("parent_label_en") or "the catalog"
    parent_lv = context.get("parent_label_lv") or "katalogs"
    label_short_en = _for_prose(name_en)
    label_short_lv = _for_prose(name_lv)
    ctx_en = _hash_pick(code, _EN_CONTEXT, "ctx", vo).format(parent=parent_en, label_short=label_short_en)
    ctx_lv = _hash_pick(code, _LV_CONTEXT, "ctx", vo).format(parent=parent_lv, label_short=label_short_lv)

    # Leaf-only hint adds more unique surface area for nodes without children/samples
    leaf_en = leaf_lv = ""
    if not children and not samples:
        leaf_en = _hash_pick(code, _EN_LEAF_HINT, "leaf", vo)
        leaf_lv = _hash_pick(code, _LV_LEAF_HINT, "leaf", vo)

    trust_en = _hash_pick(code, _EN_TRUST, "trust", vo)
    trust_lv = _hash_pick(code, _LV_TRUST, "trust", vo)
    cta_en   = _hash_pick(code, _EN_CTA, "cta", vo)
    cta_lv   = _hash_pick(code, _LV_CTA, "cta", vo)

    desc_en = " ".join(p for p in [opener_en, ctx_en, mid_en, leaf_en, trust_en, cta_en] if p)
    desc_lv = " ".join(p for p in [opener_lv, ctx_lv, mid_lv, leaf_lv, trust_lv, cta_lv] if p)

    desc_en = _fit_word_range(desc_en, 50, 70, filler_en=True)
    desc_lv = _fit_word_range(desc_lv, 50, 70, filler_en=False)

    return {
        "name_lv":     name_lv,
        "name_en":     name_en,
        "slug_lv":     slug_lv,
        "slug_en":     slug_en,
        "seo_desc_lv": desc_lv,
        "seo_desc_en": desc_en,
    }


# ─────────────────────────── similarity / validation ─────────────────────────


def _trigrams(text: str) -> set:
    t = re.sub(r"\s+", " ", (text or "").lower().strip())
    return {t[i:i + 3] for i in range(len(t) - 2)} if len(t) >= 3 else {t}


def similarity(a: str, b: str) -> float:
    """Trigram Jaccard similarity in [0, 1]. 0.0 means disjoint."""
    ga, gb = _trigrams(a), _trigrams(b)
    if not ga or not gb:
        return 0.0
    inter = len(ga & gb)
    union = len(ga | gb)
    return inter / union if union else 0.0


# Trigram-Jaccard thresholds tuned for this template set:
#   >= 0.75  treat as blocking for export (real cannibalization)
#   >= 0.55  soft warning for manual review, non-blocking
CANNIBAL_HARD = 0.75
CANNIBAL_SOFT = 0.55


def find_cannibalization(seo_map: Dict[str, Dict[str, str]],
                         lang: str = "en",
                         threshold: float = CANNIBAL_HARD) -> List[Tuple[str, str, float]]:
    """Return [(code_a, code_b, score)] for description pairs above threshold
    in the given language. Used by migration + pre-export validation.

    Defaults to the hard threshold (0.75). Pass 0.55 to surface softer warnings.
    """
    field = "seo_desc_" + lang
    items = [(c, (v.get(field) or "")) for c, v in seo_map.items() if v.get(field)]
    out = []
    for i, (ca, da) in enumerate(items):
        for cb, db in items[i + 1:]:
            s = similarity(da, db)
            if s >= threshold:
                out.append((ca, cb, round(s, 3)))
    out.sort(key=lambda x: -x[2])
    return out


def validate_description(text: str, lo: int = 50, hi: int = 70) -> Tuple[bool, Optional[str]]:
    n = _word_count(text)
    if n < lo:
        return False, f"too short ({n} words, min {lo})"
    if n > hi:
        return False, f"too long ({n} words, max {hi})"
    return True, None


# ───────────────────────────────── helpers ───────────────────────────────────


def build_context_from_tree(node: Dict[str, Any],
                            all_nodes: List[Dict[str, Any]],
                            mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Helper: assemble generator context from raw DB rows."""
    by_code  = {n["code"]: n for n in all_nodes}
    children = [n["label"] for n in all_nodes if n.get("parent_code") == node["code"]]
    # Keep only the last segment of supplier category names so prose stays readable
    def _tail(cat: str) -> str:
        for sep in (" > ", " - "):
            if sep in cat:
                return cat.rsplit(sep, 1)[-1].strip()
        return cat.strip()
    seen, samples = set(), []
    for m in mappings:
        if m["tree_code"] != node["code"]:
            continue
        t = _tail(m["category"])
        if t and t.lower() not in seen:
            seen.add(t.lower())
            samples.append(t)
        if len(samples) == 3:
            break
    parts = []
    cur = node["code"]
    while cur:
        p = by_code.get(cur)
        if not p:
            break
        parts.append(p["label"])
        cur = p.get("parent_code")
    parent_node = by_code.get(node.get("parent_code")) if node.get("parent_code") else None
    parent_en = parent_node["label"] if parent_node else ""
    parent_lv = translate_to_lv(parent_en) if parent_en else ""
    return {
        "children_labels":  children,
        "supplier_samples": samples,
        "breadcrumb":       " > ".join(reversed(parts)),
        "parent_label_en":  parent_en,
        "parent_label_lv":  parent_lv,
    }
