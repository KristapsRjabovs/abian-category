"""
Unified B2B category tree v2.

Rules:
- Max 13 top-level categories (#13 = "Other" catch-all for niche verticals).
- No attribute splits (wired/wireless/ergonomic/color/mono) unless BOTH suppliers
  already categorise that way. Those become product-listing filters, not tree nodes.
- Splits reflect genuine product types both suppliers carry (or at least won't leave
  a client leaf with zero products from one side).
- Dual-placement preserved: a PC accessory lives under Computers > Accessories AND
  Peripherals > Accessories. Webcam lives under Peripherals AND Cameras. Etc.
- Outputs two CSVs matching the input format, plus a clickable HTML tree.
- Diagnostics: per-leaf supplier coverage printed so single-supplier leaves are
  visible for review.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

TREE: dict[str, tuple[str, str | None]] = {}

def add(code: str, label: str):
    parent = code.rsplit("/", 1)[0] if "/" in code else None
    TREE[code] = (label, parent)

# =============================================================================
# 16 TOP-LEVEL CATEGORIES (Markit-based)
# =============================================================================
ROOTS = [
    ("computers",      "Computers, Servers & Tablets"),
    ("displays",       "Displays & Projectors"),
    ("print-scan",     "Printers & Scanners"),
    ("networking",     "Networking"),
    ("components",     "Components & Accessories"),
    ("software-apps",  "Software Applications"),
    ("subscriptions",  "Software Subscriptions"),
    ("phones-radios",  "Phones & Devices"),
    ("navigation",     "Navigation & Radios"),
    ("av",             "Audio & Video & TV"),
    ("cameras",        "Cameras & Camcorders"),
    ("photo",          "Photo Equipment"),
    ("other",          "Other"),
]
for c, l in ROOTS: add(c, l)

# ---------------------------------------------------------------------------
# 11. Computers, Servers & Tablets  (Markit 11)
# ---------------------------------------------------------------------------
add("computers/desktops",                    "Desktops & Workstations")
# /gaming (single-provider attribute variant) folds into /standard.
add("computers/desktops/standard",           "Desktops")
add("computers/desktops/aio",                "All-in-One PCs")
add("computers/desktops/mini",               "Mini PCs & NUC")

add("computers/notebooks",                        "Notebooks")
# Notebooks is a product-bearing leaf — it cannot also have children.
# Accessories live as their own sibling branch below.

add("computers/notebook-accessories",             "Notebook Accessories")
add("computers/notebook-accessories/bags",        "Bags, Sleeves & Backpacks")
add("computers/notebook-accessories/batteries",   "Batteries")
add("computers/notebook-accessories/chargers",    "Chargers & Power Adapters")
add("computers/notebook-accessories/docks",       "Docking Stations")
add("computers/notebook-accessories/other",       "Other Accessories")

add("computers/tablets",                     "Tablets")
# Tablets is a product-bearing leaf — E-Readers and Tablet Accessories live
# as their own sibling branches (same rule as Notebooks).

add("computers/ereaders",                    "E-Readers")

add("computers/tablet-accessories",          "Tablet Accessories")

add("computers/servers",                     "Servers")
add("computers/servers/rack-tower",          "Rack & Tower Servers")
add("computers/servers/components",          "Server Components")
add("computers/servers/components/cpu",      "Server CPUs")
add("computers/servers/components/memory",   "Server Memory")
add("computers/servers/components/motherboards","Server Motherboards")
add("computers/servers/components/psu",      "Server PSUs")
add("computers/servers/components/controllers","Server Storage Controllers")
# /cooling, /cases, /cables, /gpu are all single-provider — folded into /other
# (Other Server Parts) so single-provider items don't stand alone.
add("computers/servers/components/other",    "Other Server Parts")
add("computers/servers/racks",               "Racks, Cabinets & Mounting")
add("computers/servers/racks/standard",      "Rack Cabinets & Enclosures")
add("computers/servers/racks/accessories",   "Rack Accessories")
# Server & Storage Accessories (single-provider) folds into components/other
# so it isn't a stranded leaf at the servers level.

add("computers/pos",                         "Point Of Sale Equipment")
add("computers/pos/terminals",               "POS Terminals & PDAs")
add("computers/pos/kiosks",                  "Kiosks & Self-Checkout")
add("computers/pos/printers",                "POS Printers")
add("computers/pos/accessories",             "POS Accessories")
add("computers/pos/other",                   "Other POS Products")

# ---------------------------------------------------------------------------
# 12. Displays & Projectors  (Markit 12)
# ---------------------------------------------------------------------------
add("displays/monitors",                         "Monitors")
# /standard (same-name) and /gaming (attribute variant) fold into parent.
add("displays/monitors/accessories",             "Monitor Accessories")
add("displays/monitors/accessories/mounts",      "Monitor Mounts, Stands & Arms")
add("displays/monitors/accessories/privacy",     "Privacy Filters")
add("displays/monitors/accessories/usb-adapters","USB Graphics Adapters")
add("displays/monitors/accessories/other",       "Other Monitor Accessories")

add("displays/large-format",                     "Large Format Displays & Video Walls")
# /standard and /video-wall fold into parent — supplier merges them anyway
# and /video-wall is single-provider.

add("displays/projectors",                       "Projectors")
# Merged leaf: elko ships "Projectors & Screens" as one category, so splitting
# projectors vs screens would cross-contaminate both leaves. also_data's four
# screen sub-types (Electric/Manual/Options/Portable) land here too.
add("displays/projectors/standard",              "Projectors & Screens")
add("displays/projectors/lamps",                 "Projector Lamps & Lenses")
add("displays/projectors/mounting",              "Projector Mounts")
add("displays/projectors/other",                 "Other Projector Accessories")

# ---------------------------------------------------------------------------
# 13. Printers & Scanners  (Markit 13)
# ---------------------------------------------------------------------------
add("print-scan/printers",                   "Printers")
# /standard (same-name) folds into parent.
add("print-scan/printers/mfp",               "Multifunction Printers (MFP)")
add("print-scan/printers/lfp",               "Large Format Printers & Plotters")
add("print-scan/printers/lfp/accessories",   "Large Format Accessories")
add("print-scan/printers/3d",                "3D Printers & Supplies")

add("print-scan/scanners",                   "Scanners")
add("print-scan/scanners/standard",          "Document & Photo Scanners")
add("print-scan/scanners/barcode",           "Barcode Scanners")

add("print-scan/office-products",            "Office Products")
add("print-scan/office-products/shredders",  "Shredders")
add("print-scan/office-products/binding",    "Binding Machines")

add("print-scan/consumables",                "Printer Consumables")
add("print-scan/consumables/ink",            "Ink Cartridges & Printheads")
add("print-scan/consumables/toner",          "Toners")
add("print-scan/consumables/drums",          "Drums & Imaging Units")
add("print-scan/consumables/paper",          "Paper & Media")
add("print-scan/consumables/other",          "Other Consumables")

add("print-scan/print-servers",              "Print Servers")
add("print-scan/trays",                      "Printer Trays & Accessories")

# ---------------------------------------------------------------------------
# Storage & Memory  (nested under Components & Accessories)
# ---------------------------------------------------------------------------
add("components/storage",                            "Storage & Memory")
add("components/storage/hdd",                        "Hard Drives (HDD)")
add("components/storage/hdd/internal",               "Internal HDDs")
add("components/storage/hdd/external",               "External HDDs")
add("components/storage/hdd/enterprise",             "Enterprise HDDs")

add("components/storage/ram",                        "Memory (RAM)")
add("components/storage/ram/desktop",                "Desktop Memory (DIMM)")
add("components/storage/ram/notebook",               "Notebook Memory (SODIMM)")

add("components/storage/ssd",                        "Solid State Drives (SSD)")
add("components/storage/ssd/internal",               "Internal SSDs")
add("components/storage/ssd/enterprise",             "Enterprise SSDs")

add("components/storage/enclosures",                 "External Storage Enclosures")
add("components/storage/flash",                      "Flash Memory (USB, SD, CF)")
add("components/storage/optical",                    "Optical Drives")
add("components/storage/tape",                       "Tape Backup")
add("components/storage/duplicators",                "Disc Duplicators")
# /nas folded in: elko's "Storage Systems > Storage" dual-maps NAS and
# SAN/JBOD, so the two leaves are kept as one bucket.
add("components/storage/arrays",                     "NAS & Disk Arrays")
add("components/storage/legacy",                     "Legacy Drives")
add("components/storage/media",                      "Storage Media (CD, DVD, Blu-ray)")
add("components/storage/cables",                     "Storage Cables")

# ---------------------------------------------------------------------------
# 15. Networking  (Markit 15)
# ---------------------------------------------------------------------------
add("networking/routers",                    "Bridges & Routers")
# /standard and /bridges fold into the parent: its label covers both, and
# also_data's generic "Routers" category ships a mix of both items.
add("networking/routers/cellular",           "3G/4G/5G Routers")

add("networking/switches",                   "Hubs & Switches")
# /standard and /modules fold into the parent: also_data's "Switch - Chassis"
# dual-maps to both, and several SKUs don't distinguish the split.
add("networking/switches/poe",               "PoE Switches & PoE Devices")

add("networking/adapters",                   "Network Adapters (NIC)")
add("networking/modems",                     "Modems")
# /standard (same-name) folds into parent.
add("networking/modems/powerline",           "Powerline Adapters")

add("networking/transceivers",               "Transceivers & Multiplexers")
add("networking/transceivers/standard",      "Transceiver Modules")
add("networking/transceivers/media-converters","Media Converters")

add("networking/voip",                       "VoIP")

add("networking/wireless",                   "Wireless")
add("networking/wireless/standard",          "Access Points & Controllers")
add("networking/wireless/mesh",              "Mesh Wi-Fi")
add("networking/wireless/extenders",         "Range Extenders")
add("networking/wireless/outdoor",           "Outdoor Wireless")
add("networking/wireless/antennas",          "Antennas & Accessories")

add("networking/security",                   "Network Security")
add("networking/security/firewalls",         "Firewalls")

add("networking/cabling",                    "Network Cabling")

# ---------------------------------------------------------------------------
# 16. Components & Accessories  (Markit 16)
# ---------------------------------------------------------------------------
add("components/keyboards-mice",             "Keyboards & Mice")
# /keyboards and /mice fold into the parent: its label already covers both,
# and also_data dual-mapped generic "Keyboards & Mouse" to both leaves.
add("components/keyboards-mice/numeric",     "Numeric Keypads")
add("components/keyboards-mice/mousepads",   "Mousepads, Desk Pads & Wrist Rests")
add("components/keyboards-mice/presenters",  "Presenters & Remotes")
add("components/keyboards-mice/digitizers",  "Digitizers & Stylus Pens")

add("components/kvm",                        "KVM")

add("components/cables",                     "Cables")
add("components/cables/av",                  "AV Cables & Adapters")
add("components/cables/data",                "Data Cables & Adapters")
add("components/cables/hubs",                "USB & Interface Hubs")
add("components/cables/card-readers",        "Card Readers")
add("components/cables/power",               "Power Cables")
add("components/cables/io-cards",            "I/O Cards & Adapters")

add("components/cpu",                        "Processors (CPU)")
add("components/cpu/desktop",                "Desktop CPUs")

add("components/motherboards",               "Motherboards")

add("components/cases",                      "System Cases")
add("components/controllers",                "Controller Cards (RAID/HBA)")
add("components/sound-cards",                "Sound Cards")
add("components/gpu",                        "Video Cards (GPU)")
add("components/psu",                        "Power Supplies (PSU)")
add("components/cooling",                    "Fans & Cooling Systems")
add("components/game-controllers",           "Game Controllers")
add("components/webcams",                    "Web & Network Cameras")

add("components/power-protection",           "Power Protection Devices")
add("components/power-protection/ups",         "UPS Systems (UPS)")
add("components/power-protection/pdu",        "Power Distribution Units (PDU)")
add("components/power-protection/accessories","Power Accessories")

add("components/batteries",                  "Batteries & Chargers")
add("components/batteries/chargers",         "Chargers & Powerbanks")

add("components/cases-accessories",          "PC Add-ons & Accessories")
add("components/cases-accessories/tpm",      "TPM Modules")
add("components/cases-accessories/internal-cables","Internal PC Cables")
add("components/cases-accessories/mounts",   "Mounts & Brackets")
add("components/cases-accessories/other",    "Other PC Accessories")

add("components/books",                      "Books & Manuals")

# ---------------------------------------------------------------------------
# Service & Support — nested under Other
# ---------------------------------------------------------------------------
add("other/service-support",                 "Service & Support")
add("other/service-support/hardware",        "Hardware Warranties & Support")
add("other/service-support/training",        "Training Courses")

# ---------------------------------------------------------------------------
# 21. Software Applications  (Markit 21)
# ---------------------------------------------------------------------------
add("software-apps/antivirus",               "Antivirus & Security Software")

add("software-apps/office",                  "Office Software")

add("software-apps/business",                "Business & Productivity Software")
add("software-apps/business/server",         "Server Software & CALs")
add("software-apps/business/cloud",          "Cloud Software & Services")
add("software-apps/business/backup",         "Backup & Storage Software")
add("software-apps/business/virtualization", "Virtualization Software")

add("software-apps/network",                 "Network Software")
add("software-apps/network/management",      "Network & Enterprise Management")
add("software-apps/network/webconf",         "Web Conferencing Software")

add("software-apps/development",             "Development Tools")
add("software-apps/graphics",                "Graphics & Publishing Software")
add("software-apps/audio-video",             "Audio & Video Software")
add("software-apps/education",               "Education & Reference")
add("software-apps/home",                    "Home & Hobbies")
add("software-apps/suites",                  "Software Suites")
add("software-apps/mac",                     "Mac Software")
add("software-apps/unix-linux",              "Unix / Linux Software")

# ---------------------------------------------------------------------------
# Operating Systems  (nested under Software Applications)
# ---------------------------------------------------------------------------
add("software-apps/os",                      "Operating Systems")
add("software-apps/os/windows",              "Microsoft Windows")
add("software-apps/os/linux",                "Linux / Unix")

# ---------------------------------------------------------------------------
# 24. Software Subscriptions  (Markit 24)
# ---------------------------------------------------------------------------
add("subscriptions/all",                     "Software Subscriptions & Support")

# ---------------------------------------------------------------------------
# 31. Phones & Devices  (Markit 31)
# ---------------------------------------------------------------------------
add("phones-radios/mobile",                  "Mobile Phones")
# /smartphones and /feature fold into the parent: its label already covers both,
# and some suppliers list a single mobile-phones category without that split.
add("phones-radios/mobile/accessories",      "Smartphone Accessories")
add("phones-radios/mobile/accessories/cases",     "Cases & Covers")
add("phones-radios/mobile/accessories/chargers",  "Chargers & Powerbanks")
add("phones-radios/mobile/accessories/cables",    "Cables & Adapters")
add("phones-radios/mobile/accessories/holders",   "Holders & Car Mounts")
add("phones-radios/mobile/accessories/protectors","Screen Protectors")
add("phones-radios/mobile/accessories/headsets",  "Phone Headsets")
add("phones-radios/mobile/accessories/other",     "Other Phone Accessories")

add("phones-radios/telephones",              "Telephones")
add("phones-radios/telephones/standard",     "Desk Phones")
add("phones-radios/telephones/accessories",  "Landline Accessories")
add("phones-radios/telephones/conferencing", "Audio & Video Conferencing")

# Wearables — under Phones & Devices (closer fit than Navigation)
add("phones-radios/wearables",               "Wearable Electronics")
add("phones-radios/wearables/smartwatches",  "Smartwatches")
add("phones-radios/wearables/fitness",       "Fitness Bands")
add("phones-radios/wearables/accessories",   "Wearable Accessories")

# ---------------------------------------------------------------------------
# 32. Navigation & Radios  (Markit 32)
# ---------------------------------------------------------------------------
add("navigation/gps",                        "GPS & Navigation Systems")
add("navigation/marine",                     "Marine Electronics")
add("navigation/accessories",                "Navigation Accessories")
add("navigation/two-way",                    "Two-Way Radios")
add("navigation/two-way/portable",           "Portable Radios")
add("navigation/two-way/accessories",        "Radio Accessories & Repeaters")
add("navigation/radios",                     "Consumer Radios")

# ---------------------------------------------------------------------------
# 33. Audio & Video & TV  (Markit 33)
# ---------------------------------------------------------------------------
add("av/home",                               "Home Audio & Video")
add("av/home/audio",                         "Home & Network Audio")

add("av/tvs",                                "Televisions")
# /standard (same-name) folds into parent.
add("av/tvs/specialty",                      "Hospitality & Portable TVs")
add("av/tvs/mounts",                         "TV Mounts & Stands")
add("av/tvs/media-players",                  "Media Players & Smart TV Boxes")
add("av/tvs/accessories",                    "TV Cables & Other Accessories")

add("av/satellite",                          "Satellite & Cable TV")

add("av/portable",                           "Portable Audio & Video")
add("av/portable/mp3",                       "MP3 & Portable Media Players")
add("av/portable/speakers",                  "Portable & Wireless Speakers")

add("av/car",                                "Car Audio & Video")
add("av/car/audio",                          "Car Audio Systems")
add("av/car/dashcams",                       "Car Video Recorders (Dashcams)")

add("av/speakers",                           "Speakers")
# /loudspeakers, /pc, /soundbars fold into the parent: also_data's
# "PC Speakers & Sound Bars" dual-maps across pc+soundbars and /loudspeakers
# is single-provider. Parent label "Speakers" covers all three.

add("av/games",                              "Video Games & Gadgets")
add("av/games/consoles",                     "Consoles & VR")
add("av/games/games",                        "Games & Software")
add("av/games/peripherals",                  "Gaming Peripherals")
add("av/games/furniture",                    "Gaming Chairs & Tables")

add("av/surveillance",                       "Video Surveillance")
add("av/surveillance/cameras",               "Security Cameras")
add("av/surveillance/nvr-dvr",               "NVR, DVR & Decoders")
add("av/surveillance/accessories",           "CCTV Accessories & Lenses")
add("av/surveillance/access-control",        "Access Control")
add("av/surveillance/door-entry",            "Door Entry & Intercoms")
add("av/surveillance/alarms",                "Intruder & Fire Alarms")
add("av/surveillance/software",              "Surveillance Software")

add("av/accessories",                        "AV Accessories")
add("av/accessories/cables",                 "AV Cables & Adapters")
add("av/accessories/microphones",            "Microphones & Stands")

# Headsets & Headphones — their own branch (not an "accessory").
add("av/headsets",                           "Headsets & Headphones")
# /standard (same-name) folds into parent.
add("av/headsets/accessories",               "Headset Accessories")

# ---------------------------------------------------------------------------
# 34. Cameras & Camcorders  (Markit 34)
# ---------------------------------------------------------------------------
add("cameras/film",                          "Film Cameras")

add("cameras/digital",                       "Digital Cameras")
# /standard (same-name) folds into parent.
add("cameras/digital/instant",               "Instant Cameras")
add("cameras/digital/action",                "Action Cameras")

add("cameras/lenses",                        "Camera Lenses")
add("cameras/camcorders",                    "Camcorders")

add("cameras/camera-accessories",            "Camera Accessories")
add("cameras/camera-accessories/memory",     "Memory Cards & Readers")
add("cameras/camera-accessories/drones",     "Drones & Accessories")
add("cameras/camera-accessories/gimbals",    "Gimbals & Accessories")
add("cameras/camera-accessories/optical",    "Binoculars, Microscopes & Telescopes")
add("cameras/camera-accessories/other",      "Other Camera Accessories")

add("cameras/camcorder-accessories",         "Camcorder Accessories")

# ---------------------------------------------------------------------------
# 35. Photo Equipment  (Markit 35)
# ---------------------------------------------------------------------------
add("photo/darkroom",                        "Darkroom")
add("photo/lighting",                        "Lighting & Studio")
add("photo/albums",                          "Albums, Frames & Presentation")

# ---------------------------------------------------------------------------
# 99. Other  (Markit 99) — niche verticals that don't fit Markit's mainline
# ---------------------------------------------------------------------------
# Smart Home & IoT
add("other/smart-home",                      "Smart Home & IoT")
add("other/smart-home/lighting",             "Smart Lighting & Bulbs")
add("other/smart-home/energy",               "Smart Energy & Plugs")
add("other/smart-home/security",             "Smart Security & Assisted Living")
add("other/smart-home/accessories",          "Smart Home Accessories")
add("other/smart-home/iot",                  "IoT Devices, Sensors & Services")
add("other/smart-home/robots",               "Service Robots")

# Renewable Energy
add("other/energy",                          "Renewable Energy")
add("other/energy/panels",                   "Solar Panels")
add("other/energy/inverters",                "Solar Inverters & Optimizers")
add("other/energy/batteries",                "Battery Storage")
add("other/energy/stations",                 "Power Stations")
add("other/energy/ev",                       "EV Charging")
add("other/energy/accessories",              "Solar Accessories & Tools")

# Office Equipment & Furniture
add("other/office",                          "Office Equipment & Furniture")
add("other/office/furniture",                "Desks, Trolleys & Chairs")
add("other/office/standing-desks",           "Standing Desks")
add("other/office/charging-carts",           "Charging Stations & Carts")
add("other/office/ergonomics",               "Workspace Ergonomics")
add("other/office/air-quality",              "Humidifiers & Dehumidifiers")
add("other/office/stationery",               "Office Stationery")
add("other/office/sneeze-guards",            "Sneeze Guards")
add("other/office/other",                    "Other Office Products")

# Medical
add("other/medical",                         "Medical Equipment")
add("other/medical/it",                      "Medical IT Accessories")
add("other/medical/mounting",                "Medical Display Mounts")
add("other/medical/workstations",            "Medical Workstations & Trolleys")

# Education
add("other/education",                       "Education")
add("other/education/accessories",           "EDU Computer Accessories & Trolleys")
add("other/education/presentation",          "Presentation EDU")

# Home & Lifestyle (kitchen, personal care, etc.)
add("other/home",                            "Home & Lifestyle")
add("other/home/kitchen",                    "Kitchen Appliances")
add("other/home/kitchen/coffee",             "Coffee Makers & Accessories")
add("other/home/kitchen/kettles",            "Kettles & Teapots")
add("other/home/kitchen/blenders",           "Blenders, Mixers & Food Processors")
add("other/home/kitchen/fryers",             "Air Fryers & Accessories")
add("other/home/kitchen/grills",             "Electric Grills & Sandwich Makers")
add("other/home/kitchen/microwaves",         "Microwaves & Multicookers")
add("other/home/kitchen/toasters",           "Toasters & Waffle Irons")
add("other/home/kitchen/refrigerators",      "Refrigerators")
add("other/home/kitchen/cookware",           "Cookware & Kitchenware")

add("other/home/cleaning",                   "Vacuums & Cleaning")
add("other/home/cleaning/robots",            "Robot Vacuums & Accessories")
add("other/home/cleaning/accessories",       "Vacuum Accessories")
add("other/home/cleaning/floor-care",        "Mops, Carpet & Patio Cleaners")

add("other/home/garment",                    "Garment Care (Irons & Steamers)")
add("other/home/climate",                    "Air Conditioners")

add("other/home/personal-care",              "Personal Care")
add("other/home/personal-care/shavers",      "Shavers & Trimmers")
add("other/home/personal-care/hair",         "Hair Care")
add("other/home/personal-care/dental",       "Dental Care")
add("other/home/personal-care/other",        "Other Beauty Appliances")

add("other/home/pet-care",                   "Pet Care")

add("other/home/household",                  "Small Household & Lamps")
add("other/home/household/clocks",           "Clocks & Alarm Clocks")
add("other/home/household/lamps",            "Light Bulbs, Lamps & Fixtures")
add("other/home/household/other",            "Other Small Appliances")

add("other/home/sports",                     "Sport, Outdoor & Hobbies")
add("other/home/sports/illumination",        "Lanterns & Illumination")
add("other/home/sports/pool",                "Swimming Pool Accessories")
add("other/home/sports/e-mobility",          "E-Scooters & Mobility")
add("other/home/sports/other",               "Other Sport & Hobby Accessories")

# Power Tools & Garden
add("other/tools",                           "Power Tools & Garden")
add("other/tools/power-tools",               "Power Tools & Workwear")
add("other/tools/compressors",               "Car Air Compressors")
add("other/tools/cordless-batteries",        "Cordless Tool Batteries")
add("other/tools/generators",                "Generators")
add("other/tools/garden",                    "Garden Equipment")
add("other/tools/garden/mowers",             "Lawn Mowers & Accessories")
add("other/tools/garden/trimmers",           "Grass Trimmers & Leaf Blowers")
add("other/tools/garden/washers",            "Pressure Washers & Sweepers")
add("other/tools/garden/pumps",              "Water Pumps")
# /workwear folded into /power-tools: elko's "Tools & Workwear > Tools"
# dual-maps across both.

# Car accessories (non-audio/video)

# =============================================================================
# MAPPING: supplier_category -> list of client codes (dual/multi-placement)
# =============================================================================
MAPPING: dict[str, list[str]] = {
    # =========================================================================
    # also_data
    # =========================================================================

    # AV
    "Audio, Video, Display & TV - Audio & Video Systems - Digital AV Systems": ["av/av-systems"],
    "Audio, Video, Display & TV - Cameras & Optical Systems - Binocular, Microscope & Telescope": ["cameras/optical"],
    "Audio, Video, Display & TV - Cameras & Optical Systems - Camcorders": ["cameras/camcorders"],
    "Audio, Video, Display & TV - Cameras & Optical Systems - Digital Cameras": ["cameras/digital/standard"],
    "Audio, Video, Display & TV - Cameras & Optical Systems - Network Cameras": ["cameras/surveillance"],
    "Audio, Video, Display & TV - Cameras & Optical Systems - Webcams": ["peripherals/webcams"],

    "Audio, Video, Display & TV - Displays - Business Monitors": ["peripherals/monitors"],
    "Audio, Video, Display & TV - Displays - Consumer & Gaming Monitors": ["peripherals/monitors", "other/gaming/monitors"],
    "Audio, Video, Display & TV - Displays - Portable Monitors": ["peripherals/monitors/portable", "peripherals/monitors"],

    "Audio, Video, Display & TV - Headsets & Microphones - Business Headsets": ["peripherals/headsets"],
    "Audio, Video, Display & TV - Headsets & Microphones - Consumer & Gaming Headsets": ["peripherals/headsets"],
    "Audio, Video, Display & TV - Headsets & Microphones - Microphones & Dictaphones": ["peripherals/microphones", "av/audio/microphones"],

    "Audio, Video, Display & TV - Options & Accessories - Audio & Video Accessories": ["av/audio/cables"],
    "Audio, Video, Display & TV - Options & Accessories - Audio, Video Adapters & Cables": ["av/av-cables/adapters", "av/av-cables", "av/audio/cables"],
    "Audio, Video, Display & TV - Options & Accessories - Camera, Drone, Webcam - Accessories": ["cameras/accessories/other"],
    "Audio, Video, Display & TV - Options & Accessories - Floor Stands & Trolleys": ["peripherals/monitors/accessories/mounts", "av/tvs/mounts"],
    "Audio, Video, Display & TV - Options & Accessories - Headset & Microphone Accessories": ["peripherals/headsets/accessories"],
    "Audio, Video, Display & TV - Options & Accessories - Mounts - Ceiling": ["peripherals/monitors/accessories/mounts", "av/tvs/mounts"],
    "Audio, Video, Display & TV - Options & Accessories - Mounts - Desk Stand": ["peripherals/monitors/accessories/mounts"],
    "Audio, Video, Display & TV - Options & Accessories - Mounts - Other": ["peripherals/monitors/accessories/mounts", "av/tvs/mounts"],
    "Audio, Video, Display & TV - Options & Accessories - Mounts - Video Wall": ["peripherals/signage/video-wall", "peripherals/monitors/accessories/mounts"],
    "Audio, Video, Display & TV - Options & Accessories - Mounts - Wall": ["peripherals/monitors/accessories/mounts", "av/tvs/mounts"],
    "Audio, Video, Display & TV - Options & Accessories - Privacy Filters": ["peripherals/monitors/accessories/privacy"],

    "Audio, Video, Display & TV - Projector Accessories - Lamps": ["av/projectors/lamps"],
    "Audio, Video, Display & TV - Projector Accessories - Lens": ["av/projectors/lamps"],
    "Audio, Video, Display & TV - Projector Accessories - Projector Accessories - Other": ["av/projectors/other"],
    "Audio, Video, Display & TV - Projector Accessories - Projector Mounting": ["av/projectors/mounting"],
    "Audio, Video, Display & TV - Projector Accessories - Projector Screens - Electric": ["av/projectors"],
    "Audio, Video, Display & TV - Projector Accessories - Projector Screens - Manual": ["av/projectors"],
    "Audio, Video, Display & TV - Projector Accessories - Projector Screens - Options": ["av/projectors"],
    "Audio, Video, Display & TV - Projector Accessories - Projector Screens - Portable": ["av/projectors"],

    "Audio, Video, Display & TV - Projectors - Business Projectors": ["av/projectors"],
    "Audio, Video, Display & TV - Projectors - Consumer Projectors": ["av/projectors"],
    "Audio, Video, Display & TV - Projectors - Installation Projectors": ["av/projectors"],

    "Audio, Video, Display & TV - Public Display & Signage - Digital Signage Displays": ["peripherals/signage"],
    "Audio, Video, Display & TV - Public Display & Signage - Digital Signage Displays - Outdoors": ["peripherals/signage/outdoor", "peripherals/signage"],
    "Audio, Video, Display & TV - Public Display & Signage - Digital Signage Displays - TouchScreen": ["peripherals/signage/touch", "peripherals/signage"],
    "Audio, Video, Display & TV - Public Display & Signage - Hotel TVs": ["av/tvs/hotel"],
    "Audio, Video, Display & TV - Public Display & Signage - LED Wall Systems": ["peripherals/signage/video-wall", "peripherals/signage"],
    "Audio, Video, Display & TV - Public Display & Signage - Signage software": ["software/utilities/cloud"],

    "Audio, Video, Display & TV - Radios - Car & Consumer Radios": ["av/radios", "av/audio/car"],
    "Audio, Video, Display & TV - Speakers - PC Speakers & Sound Bars": ["av/speakers"],
    "Audio, Video, Display & TV - Speakers - Portable & Wireless Speakers": ["av/audio/portable-speakers"],
    "Audio, Video, Display & TV - Televisions - TVs": ["av/tvs/standard"],
    "Audio, Video, Display & TV - Televisions - TVs Accessories": ["av/tvs/other"],

    # Components
    "Components - Chassis & System Cases - PC Chassis & System Cases": ["components/cases"],
    "Components - Chassis & System Cases - Server System Cases": ["servers/components/cases", "servers/components"],
    "Components - Components Accessories - Components Accessories - Other": ["components/accessories/other"],
    "Components - Components Accessories - Graphic Card Accessories": ["components/accessories/other"],
    "Components - Components Accessories - Storage Drive Accessories": ["components/storage/accessories"],
    "Components - Controllers - Host Bus Adapters (HBA)": ["servers/components/controllers"],
    "Components - Controllers - Raid Controllers": ["components/controllers", "servers/components/controllers"],
    "Components - Fans & Cooling Systems - Computer Coolers": ["components/cooling"],
    "Components - Fans & Cooling Systems - Computer Fans": ["components/cooling"],
    "Components - Fans & Cooling Systems - Fans & Cooling Systems": ["components/cooling"],
    "Components - Graphic Cards (GPU) - Graphic Cards - Consumer & Gaming": ["components/gpu"],
    "Components - Graphic Cards (GPU) - Graphic Cards - Server": ["components/gpu/server", "components/gpu", "servers/components/gpu"],
    "Components - Graphic Cards (GPU) - Graphic Cards - Workstation": ["components/gpu/workstation", "components/gpu"],
    "Components - Memory": ["components/storage/ram/desktop"],
    "Components - Memory - Desktop Memory": ["components/memory/desktop"],
    "Components - Memory - Flash Memory": ["components/memory/flash"],
    "Components - Memory - Notebook Memory": ["components/memory/notebook"],
    "Components - Memory - Server Memory": ["servers/components/memory"],
    "Components - Memory - USB Flash Drives": ["components/memory/usb"],
    "Components - Motherboards": ["components/motherboards"],
    "Components - Motherboards - Motherboards - AMD": ["components/motherboards"],
    "Components - Motherboards - Motherboards - INTEL": ["components/motherboards"],
    "Components - Motherboards - Motherboards - Servers": ["servers/components/motherboards", "components/motherboards"],
    "Components - Optical Drives - Blu-Ray, CD/DVD & Floppy Drives": ["components/storage/optical"],
    "Components - Power Supplies (PSU) - Power Supply - PC": ["components/psu"],
    "Components - Power Supplies (PSU) - Power Supply - Server": ["servers/components/psu", "servers/components"],
    "Components - Processors (CPU) - Desktop Processors": ["components/cpu/desktop"],
    "Components - Processors (CPU) - Server & Workstation Processors": ["servers/components/cpu"],
    "Components - Sound Cards - Sound Cards": ["components/sound-cards"],
    "Components - Storage Drives - External HDDs": ["servers/external"],
    "Components - Storage Drives - External SSDs": ["servers/external"],
    "Components - Storage Drives - Internal HDDs": ["components/storage/hdd/internal"],
    "Components - Storage Drives - Internal SSDs": ["components/storage/ssd/internal"],

    # Conferencing
    "Conferencing Systems - Audio Conferencing - Audio Conferencing": ["communication/conferencing/audio-video"],
    "Conferencing Systems - Audio Conferencing - IP Phones": ["communication/desk-phones"],
    "Conferencing Systems - Conferencing PC - Conferencing PCs": ["communication/conferencing/pc"],
    "Conferencing Systems - Conferencing Systems Accessories - Conferencing Systems Accessories": ["communication/conferencing/accessories"],
    "Conferencing Systems - Video Conferencing - Video Conferencing": ["communication/conferencing/audio-video"],

    # Education
    "Education - Computer Accessory EDU - Input Pen EDU": ["other/education/accessories", "peripherals/digitizers"],
    "Education - Computer Accessory EDU - Notebook & Tablet Trolley EDU": ["other/education/accessories", "other/office/charging-carts"],
    "Education - Presentation EDU - Presentation Accessory EDU": ["other/education/presentation", "peripherals/presenters"],

    # Electrical Energy
    "Electrical Energy Products - Battery Storage - Battery Storage": ["power/renewable/battery", "power/renewable"],
    "Electrical Energy Products - Battery Storage - Battery Storage Accessories": ["power/renewable/accessories"],
    "Electrical Energy Products - Chargers - Chargers": ["power/chargers/batteries", "power/chargers"],
    "Electrical Energy Products - Panels - Panels": ["power/renewable/panels", "power/renewable"],
    "Electrical Energy Products - Solar Energy Components - Inverters": ["power/renewable/inverters", "power/renewable"],
    "Electrical Energy Products - Solar Energy Components - Optimizers": ["power/renewable/inverters", "power/renewable"],
    "Electrical Energy Products - Solar Energy Components - Solar Energy Components Accessories": ["power/renewable/accessories"],
    "Electrical Energy Products - Solar Energy Components - Tools": ["power/renewable/accessories", "other/tools/power-tools"],

    # Gaming
    "Gaming - Gaming Accessories - Gamepads & Joysticks": ["other/gaming/peripherals/controllers"],
    "Gaming - Gaming Accessories - Gaming Chairs & Tables": ["other/gaming/furniture", "other/office/furniture"],
    "Gaming - Gaming Accessories - Gaming Headsets & Speakers": ["peripherals/headsets"],
    "Gaming - Gaming Accessories - Gaming Mouse & Keyboards": ["peripherals/keyboards", "peripherals/mice"],
    "Gaming - Gaming Accessories - Gaming Mousepads": ["peripherals/mousepads"],
    "Gaming - Gaming Components - Gaming Cases & Chassis": ["components/cases"],
    "Gaming - Gaming Components - Gaming CPU Coolers & Fans": ["components/cooling"],
    "Gaming - Gaming Components - Gaming Graphics cards": ["components/gpu"],
    "Gaming - Gaming Components - Gaming Motherboards": ["components/motherboards"],
    "Gaming - Gaming Components - Gaming Power Supply Unit (PSU)": ["components/psu"],
    "Gaming - Gaming Components - Gaming Storage & Memory": ["components/storage/ram/desktop", "components/storage/ssd/internal"],
    "Gaming - Gaming Computers - Gaming Notebooks": ["computers/notebooks/gaming"],
    "Gaming - Gaming Computers - Gaming PCs": ["computers/desktops/gaming"],
    "Gaming - Gaming Displays - Gaming Monitors": ["displays/monitors/gaming"],
    "Gaming - Video Games - Console Games": ["av/games/games"],

    # Household
    "Household Products - Ironing & Cleaning - Cleaning - Chemical Products": ["other/home/cleaning/chemical"],
    "Household Products - Ironing & Cleaning - Vacuum Cleaners & Accessories": ["other/home/cleaning/accessories"],
    "Household Products - Kitchen Appliances - Blenders & Slicing Machines": ["other/home/kitchen/blenders"],
    "Household Products - Kitchen Appliances - Other Kitchen Appliances": ["other/home/kitchen/other"],
    "Household Products - Small Household Products - Clocks": ["other/home/household/clocks"],
    "Household Products - Small Household Products - Home Tools & Accessories": ["other/home/household/other", "other/tools/power-tools"],
    "Household Products - Small Household Products - Light Bulbs & Lamps": ["other/home/household/lamps"],
    "Household Products - Sport & Hobbies - Sport & Hobbies Product Accessories": ["other/home/sports/other"],

    # IoT
    "Internet of Things (IoT) - IoT Applications & Services - IoT Services": ["smart-home/iot-services"],
    "Internet of Things (IoT) - IoT Connectivity Services - IoT Connectivity Services": ["smart-home/iot-services"],
    "Internet of Things (IoT) - IoT Devices - IoT Accessories": ["smart-home/iot-accessories"],
    "Internet of Things (IoT) - IoT Devices - IoT Devices (Sensors & Actuators)": ["smart-home/iot-devices"],
    "Internet of Things (IoT) - IoT Devices - IoT Gateways": ["smart-home/iot-devices"],
    "Internet of Things (IoT) - IoT Devices - IoT Switches": ["smart-home/iot-devices"],
    "Internet of Things (IoT) - IoT Devices - IoT Wearables": ["smart-home/iot-wearables", "communication/wearables"],

    # Medical
    "Medical Equipment - Medical IT Accessories - Medical IT Accessories": ["other/medical/it"],
    "Medical Equipment - Medical Mounting Systems - Medical Display Mounts": ["other/medical/mounting"],
    "Medical Equipment - Medical Workstation & Trolleys - Medical Trolleys": ["other/medical/workstations"],
    "Medical Equipment - Medical Workstation & Trolleys - Medical Workstations": ["other/medical/workstations"],

    # Network & Smart Home
    "Network & Smart Home - Network - Accesspoints & Controllers": ["networking/wireless/standard"],
    "Network & Smart Home - Network - Firewalls": ["networking/firewalls"],
    "Network & Smart Home - Network - Modems": ["networking/modems/standard", "networking/routers/cellular"],
    "Network & Smart Home - Network - Network Antennas": ["networking/wireless/antennas"],
    "Network & Smart Home - Network - Powerline Adapters": ["networking/powerline"],
    "Network & Smart Home - Network - Routers": ["networking/routers"],
    "Network & Smart Home - Network - Switch - Cabled": ["networking/switches"],
    "Network & Smart Home - Network - Switch - Chassis": ["networking/switches"],
    "Network & Smart Home - Network - Switch - CLI Managed": ["networking/switches"],
    "Network & Smart Home - Network - Switch - PoE": ["networking/switches/poe"],
    "Network & Smart Home - Network - Switch - Unmanaged": ["networking/switches"],
    "Network & Smart Home - Network - Switch - Webmanaged": ["networking/switches"],
    "Network & Smart Home - Network Accessories - Network & DAC Cables": ["networking/cables"],
    "Network & Smart Home - Network Accessories - Network Cards & Adapters": ["networking/cards", "networking/switches/media-converters"],
    "Network & Smart Home - Network Accessories - Network Other Accessories": ["networking/accessories", "networking/switches/transceivers"],
    "Network & Smart Home - Network Accessories - Network Power Supply": ["networking/accessories"],
    "Network & Smart Home - Smart Home - Smart Energy Products": ["smart-home/energy"],
    "Network & Smart Home - Smart Home - Smart Home Devices Accessories & Parts": ["smart-home/accessories"],
    "Network & Smart Home - Smart Home - Smart Lighting & Electrical Products": ["smart-home/lighting", "other/home/household/lamps"],
    "Network & Smart Home - Smart Home - Smart Security & Assisted Living": ["smart-home/security-living"],

    # Notebook, PC & Tablet
    "Notebook, PC & Tablet - Notebooks - Business Notebooks": ["computers/notebooks/standard"],
    "Notebook, PC & Tablet - Notebooks - Consumer & Gaming Notebooks": ["computers/notebooks/standard", "computers/notebooks/gaming"],
    "Notebook, PC & Tablet - Notebooks - Refurbished Notebooks": ["computers/notebooks/standard"],
    "Notebook, PC & Tablet - Notebooks - Workstation Notebooks": ["computers/notebooks/standard"],
    "Notebook, PC & Tablet - Options & Accessories - Docking - Notebooks & Tablets": ["computers/accessories/docks", "peripherals/docks"],
    "Notebook, PC & Tablet - Options & Accessories - Notebook Batteries": ["computers/accessories/batteries"],
    "Notebook, PC & Tablet - Options & Accessories - Notebook Power Adapters": ["computers/accessories/chargers", "power/chargers/notebook"],
    "Notebook, PC & Tablet - Options & Accessories - PC Accessories": ["computers/accessories/pc", "peripherals/accessories"],
    "Notebook, PC & Tablet - Options & Accessories - Point Of Sale (POS) Accessories": ["other/pos/accessories"],
    "Notebook, PC & Tablet - Options & Accessories - Tablet Accessories": ["computers/accessories/tablet", "peripherals/bags/tablet"],
    "Notebook, PC & Tablet - Personal Computers (PC) - All In One Desktops": ["computers/desktops/aio"],
    "Notebook, PC & Tablet - Personal Computers (PC) - Barebones": ["computers/desktops/standard"],
    "Notebook, PC & Tablet - Personal Computers (PC) - Business Desktops": ["computers/desktops/standard"],
    "Notebook, PC & Tablet - Personal Computers (PC) - Consumer & Gaming Desktops": ["computers/desktops/standard", "computers/desktops/gaming"],
    "Notebook, PC & Tablet - Personal Computers (PC) - Refurbished PCs": ["computers/desktops/standard"],
    "Notebook, PC & Tablet - Personal Computers (PC) - Terminal & Thin Client PC": ["computers/desktops/standard"],
    "Notebook, PC & Tablet - Personal Computers (PC) - Workstation Desktops": ["computers/desktops/standard"],
    "Notebook, PC & Tablet - Tablets - Tablets - Android": ["computers/tablets/standard"],
    "Notebook, PC & Tablet - Tablets - Tablets - Windows": ["computers/tablets/standard"],

    # Office Equipment
    "Office Equipment - Furniture - Charging Stations & Carts": ["other/office/charging-carts"],
    "Office Equipment - Furniture - Trolleys, Desks & Chairs": ["other/office/furniture"],
    "Office Equipment - Office Supplies - Batteries & Chargers": ["power/chargers/batteries"],
    "Office Equipment - Office Supplies - Small Office Stationery": ["other/office/stationery"],
    "Office Equipment - Office Supplies - Storage Media, CD, DVD, Bluray, Floppy": ["other/office/media"],
    "Office Equipment - Office Supplies - Work Ergonomic Products": ["other/office/ergonomics", "peripherals/mousepads"],

    # Peripherals & Accessories
    "Peripherals & Accessories - Bag & Cases - Backpacks": ["peripherals/bags", "computers/accessories/bags"],
    "Peripherals & Accessories - Bag & Cases - Notebook Bags & Cases": ["peripherals/bags", "computers/accessories/bags"],
    "Peripherals & Accessories - Bag & Cases - Notebook Sleeves": ["peripherals/bags", "computers/accessories/bags"],
    "Peripherals & Accessories - Bag & Cases - Tablet Cases & Sleeves": ["peripherals/bags/tablet", "computers/accessories/tablet"],
    "Peripherals & Accessories - Cable & Adapters - Adapters": ["peripherals/cables-adapters"],
    "Peripherals & Accessories - Cable & Adapters - Cable - Locks": ["peripherals/cables-adapters"],
    "Peripherals & Accessories - Cable & Adapters - Cable - Others": ["peripherals/cables-adapters"],
    "Peripherals & Accessories - Cable & Adapters - Cable - Power": ["power/cables"],
    "Peripherals & Accessories - Cable & Adapters - Cable - USB & Thunderbolt": ["peripherals/cables-adapters"],
    "Peripherals & Accessories - Cable & Adapters - USB Hub": ["peripherals/hubs"],
    "Peripherals & Accessories - Desktop & Combos - Mouse & Keyboard - Wired": ["peripherals/combos"],
    "Peripherals & Accessories - Desktop & Combos - Mouse & Keyboard - Wireless": ["peripherals/combos"],
    "Peripherals & Accessories - Digitizers - Digitizer Pens & Stylus": ["peripherals/digitizers"],
    "Peripherals & Accessories - Keyboards - Keyboards - Ergonomic": ["peripherals/keyboards"],
    "Peripherals & Accessories - Keyboards - Keyboards - Wired": ["peripherals/keyboards"],
    "Peripherals & Accessories - Keyboards - Keyboards - Wireless": ["peripherals/keyboards"],
    "Peripherals & Accessories - Keyboards - Numeric Keypads": ["peripherals/keyboards/numeric"],
    "Peripherals & Accessories - KVM - KVM Accessories": ["peripherals/kvm"],
    "Peripherals & Accessories - KVM - KVM Switches": ["peripherals/kvm"],
    "Peripherals & Accessories - Mouse, Trackballs & Presenters - Mouse - Ergonomic": ["peripherals/mice"],
    "Peripherals & Accessories - Mouse, Trackballs & Presenters - Mouse - Wired": ["peripherals/mice"],
    "Peripherals & Accessories - Mouse, Trackballs & Presenters - Mouse - Wireless": ["peripherals/mice"],
    "Peripherals & Accessories - Mouse, Trackballs & Presenters - Mousepads": ["peripherals/mousepads"],
    "Peripherals & Accessories - Mouse, Trackballs & Presenters - Multimedia Controllers": ["peripherals/digitizers"],
    "Peripherals & Accessories - Mouse, Trackballs & Presenters - Presenters": ["peripherals/presenters"],
    "Peripherals & Accessories - Power Protection - Power Protection & Surge Outlets": ["power/surge"],
    "Peripherals & Accessories - USB & Card Readers - Flash Card Readers": ["peripherals/card-readers", "cameras/accessories/memory"],
    "Peripherals & Accessories - USB & Card Readers - USB Card Readers": ["peripherals/card-readers"],

    # Print, Scan & Supplies
    "Print, Scan & Supplies - 3D Printer & Scanner Accessories - 3D Supplies & Filaments": ["print-scan/3d"],
    "Print, Scan & Supplies - 3D Printers & Scanners - 3D Printers": ["print-scan/3d"],
    "Print, Scan & Supplies - Copier & Telefax - Copier & Telefax Accessories": ["print-scan/accessories"],
    "Print, Scan & Supplies - Large Format Printer (LFP) - Large Format Accessories": ["print-scan/lfp/accessories"],
    "Print, Scan & Supplies - Large Format Printer (LFP) - Plotter & Scanners": ["print-scan/lfp"],
    "Print, Scan & Supplies - Printers & Multifunction (MFP) - Multifunction Printers - Ink": ["print-scan/mfp/inkjet", "print-scan/mfp"],
    "Print, Scan & Supplies - Printers & Multifunction (MFP) - Multifunction Printers - Laser Color": ["print-scan/mfp/laser", "print-scan/mfp"],
    "Print, Scan & Supplies - Printers & Multifunction (MFP) - Multifunction Printers - Laser Mono": ["print-scan/mfp/laser", "print-scan/mfp"],
    "Print, Scan & Supplies - Printers & Multifunction (MFP) - Printers - Ink": ["print-scan/printers/standard"],
    "Print, Scan & Supplies - Printers & Multifunction (MFP) - Printers - Ink Photo": ["print-scan/printers/standard"],
    "Print, Scan & Supplies - Printers & Multifunction (MFP) - Printers - Label": ["print-scan/printers/standard"],
    "Print, Scan & Supplies - Printers & Multifunction (MFP) - Printers - Laser Color": ["print-scan/printers/standard"],
    "Print, Scan & Supplies - Printers & Multifunction (MFP) - Printers - Laser Mono": ["print-scan/printers/standard"],
    "Print, Scan & Supplies - Printers & Multifunction (MFP) - Printers - Matrix": ["print-scan/printers/standard"],
    "Print, Scan & Supplies - Printers, Scanner, Copier Accessories - Matrix Printer Accessories": ["print-scan/accessories"],
    "Print, Scan & Supplies - Printers, Scanner, Copier Accessories - Print Server Adaptors": ["print-scan/accessories"],
    "Print, Scan & Supplies - Printers, Scanner, Copier Accessories - Printer Accessories - Other": ["print-scan/accessories"],
    "Print, Scan & Supplies - Printers, Scanner, Copier Accessories - Scanner Accessories - Other": ["print-scan/accessories"],
    "Print, Scan & Supplies - Printers, Scanner, Copier Accessories - Stackers & Staplers": ["print-scan/accessories"],
    "Print, Scan & Supplies - Printers, Scanner, Copier Accessories - Stands": ["print-scan/accessories"],
    "Print, Scan & Supplies - Printers, Scanner, Copier Accessories - Trays": ["print-scan/accessories"],
    "Print, Scan & Supplies - Scanners - Barcode Scanners": ["print-scan/scanners/barcode", "other/pos/terminals"],
    "Print, Scan & Supplies - Scanners - Document Scanners": ["print-scan/scanners/standard"],
    "Print, Scan & Supplies - Scanners - Photo Scanners": ["print-scan/scanners/standard"],
    "Print, Scan & Supplies - Supplies - Ink - Inks & Ink Printheads": ["print-scan/supplies/ink", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Ink - Other Inkjet Accessories": ["print-scan/supplies/other", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Label Printer - Tapes & Labels": ["print-scan/supplies/ribbons", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Large Format Printer (LFP) - LFP Inks & LFP Printheads": ["print-scan/supplies/ink", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Large Format Printer (LFP) - LFP Maintenance & Cleaning Kits": ["print-scan/supplies/fuser", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Laser - Laser Drums": ["print-scan/supplies/drums", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Laser - Laser Maintenance Kit": ["print-scan/supplies/fuser", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Laser - Laser Photoconductors": ["print-scan/supplies/drums", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Laser - Printer Fuser Kits": ["print-scan/supplies/fuser", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Laser - Staples": ["print-scan/supplies/other"],
    "Print, Scan & Supplies - Supplies - Laser - Toners": ["print-scan/supplies/toner", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Laser - Transfer Belt Units & Kits": ["print-scan/supplies/fuser", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Laser - Waste Toner Boxes": ["print-scan/supplies/other", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Matrix Printer - Ribbons": ["print-scan/supplies/ribbons", "print-scan/supplies"],
    "Print, Scan & Supplies - Supplies - Paper - Labels, Receipts & Matrix": ["print-scan/paper"],
    "Print, Scan & Supplies - Supplies - Paper - Large Format Papers": ["print-scan/paper"],
    "Print, Scan & Supplies - Supplies - Paper - Office & Photo Papers": ["print-scan/paper"],

    # Professional Radios
    "Professional Radios & Repeaters - Portable Radios - License-free Radios": ["communication/pro-radio/portable"],
    "Professional Radios & Repeaters - Professional Radios - Accessories - Chargers and accessories": ["communication/pro-radio/accessories"],
    "Professional Radios & Repeaters - Repeaters - accessories - Other accessories": ["communication/pro-radio/accessories"],

    # Server, Storage & UPS
    "Server, Storage & UPS - Power Distribution Units (PDU) - PDU Basic": ["power/pdu/standard"],
    "Server, Storage & UPS - Power Distribution Units (PDU) - PDU Managed": ["power/pdu/managed"],
    "Server, Storage & UPS - Power Distribution Units (PDU) - PDU Metered": ["power/pdu/standard"],
    "Server, Storage & UPS - Power Distribution Units (PDU) - PDU Monitored": ["power/pdu/managed"],
    "Server, Storage & UPS - Power Distribution Units (PDU) - PDU Switched": ["power/pdu/managed"],
    "Server, Storage & UPS - Rack Enclosures - Rack Cabinets": ["servers/racks/standard"],
    "Server, Storage & UPS - Server, Storage & UPS Accessories - PDU Options": ["power/pdu/accessories"],
    "Server, Storage & UPS - Server, Storage & UPS Accessories - Rack Cabinet Accessories": ["servers/racks/accessories", "servers/racks"],
    "Server, Storage & UPS - Server, Storage & UPS Accessories - Server, Storage - Other Accessories": ["servers/accessories"],
    "Server, Storage & UPS - Server, Storage & UPS Accessories - UPS Accessories & Battery Packs": ["power/ups/accessories"],
    "Server, Storage & UPS - Servers - Rack Servers": ["servers/rack-tower"],
    "Server, Storage & UPS - Servers - Tower Servers": ["servers/rack-tower"],
    "Server, Storage & UPS - Storage - Disk Shelves": ["servers/san-jbod"],
    "Server, Storage & UPS - Storage - Infrastructure Storage": ["servers/san-jbod"],
    "Server, Storage & UPS - Storage - JBOD & SANs": ["servers/san-jbod"],
    "Server, Storage & UPS - Storage - NAS": ["components/storage/arrays"],
    "Server, Storage & UPS - Storage - Server HDD": ["servers/enterprise-hdd"],
    "Server, Storage & UPS - Storage - Server SSD": ["servers/enterprise-ssd"],
    "Server, Storage & UPS - Storage - Tape Storage": ["servers/tape"],
    "Server, Storage & UPS - Uninterruptible Power Supply (UPS) - Line Interactive Rack Mounts": ["power/ups/rack"],
    "Server, Storage & UPS - Uninterruptible Power Supply (UPS) - Line Interactive Towers": ["power/ups/tower"],
    "Server, Storage & UPS - Uninterruptible Power Supply (UPS) - Off Line UPS": ["power/ups/tower"],
    "Server, Storage & UPS - Uninterruptible Power Supply (UPS) - Online Rack Mounts": ["power/ups/rack"],
    "Server, Storage & UPS - Uninterruptible Power Supply (UPS) - Online Towers": ["power/ups/tower"],

    # Software
    "Software & Cloud - Antivirus & Security Software - Authentication Software": ["software/security/auth", "software/security"],
    "Software & Cloud - Antivirus & Security Software - Firewall Software": ["software/security/firewall", "software/security"],
    "Software & Cloud - Antivirus & Security Software - Security Suites Software": ["software/security/antivirus", "software/security"],
    "Software & Cloud - Antivirus & Security Software - VPN Software": ["software/security/vpn", "software/security"],
    "Software & Cloud - Network Software - Network & Enterprise Management Software": ["software/network/management"],
    "Software & Cloud - Network Software - Network Appliance Software": ["software/network/management"],
    "Software & Cloud - Network Software - Web Conferencing Software": ["software/network/webconf"],
    "Software & Cloud - Office Software - Office Application Suites": ["software/office"],
    "Software & Cloud - Operating Systems - Linux & Unix Software": ["software/os/linux"],
    "Software & Cloud - Operating Systems - Microsoft Windows Software": ["software/os/windows"],
    "Software & Cloud - Server Software & Licences - Server CAL": ["software/server/cal"],
    "Software & Cloud - Server Software & Licences - Server Software": ["software/server/standard"],
    "Software & Cloud - Utilities Software - Cloud Software & Services": ["software/utilities/cloud"],
    "Software & Cloud - Utilities Software - Recovery, Backup & Storage Software": ["software/utilities/backup"],
    "Software & Cloud - Utilities Software - Virtualization Software": ["software/utilities/virtualization"],

    # Telecom & Wearables
    "Telecom & Wearables - Landline Telephones - Desk Phone analog & SIP": ["communication/desk-phones"],
    "Telecom & Wearables - Landline Telephones - Landline Telephone Accessories": ["communication/desk-phones/accessories"],
    "Telecom & Wearables - Mobile Phones - Classic Mobile Phones": ["communication/smartphones/feature", "communication/smartphones"],
    "Telecom & Wearables - Smartphone Accessories - Smartphone - Cables & Adapters": ["communication/smartphones/accessories/cables"],
    "Telecom & Wearables - Smartphone Accessories - Smartphone - Case & Bags": ["communication/smartphones/accessories/cases"],
    "Telecom & Wearables - Smartphone Accessories - Smartphone - Chargers & Powerbank": ["communication/smartphones/accessories/chargers"],
    "Telecom & Wearables - Smartphone Accessories - Smartphone - Headsets": ["communication/smartphones/accessories/headsets"],
    "Telecom & Wearables - Smartphone Accessories - Smartphone - Holders": ["communication/smartphones/accessories/holders"],
    "Telecom & Wearables - Smartphone Accessories - Smartphone - Screen Filter & Protectors": ["communication/smartphones/accessories/protectors"],
    "Telecom & Wearables - Smartphones - Android Smartphones": ["communication/smartphones"],
    "Telecom & Wearables - Smartphones - iPhone": ["communication/smartphones"],
    "Telecom & Wearables - Wearable Accessories - Wearable Accessories": ["communication/wearables/accessories", "communication/wearables"],
    "Telecom & Wearables - Wearables - Smartwatches": ["communication/wearables/smartwatches"],

    # Video Surveillance
    "Video Surveillance - Access Control - Access Control - Controllers": ["cameras/access-control"],
    "Video Surveillance - Access Control - Access Control - Others": ["cameras/access-control"],
    "Video Surveillance - Access Control - Access Control - Readers": ["cameras/access-control"],
    "Video Surveillance - Security Cameras - IP Bullet Security Cameras": ["cameras/surveillance"],
    "Video Surveillance - Security Cameras - IP Cube Security Cameras": ["cameras/surveillance"],
    "Video Surveillance - Security Cameras - IP Outdoor Security Cameras": ["cameras/surveillance"],
    "Video Surveillance - Security Cameras - IP Wireless Security Cameras": ["cameras/surveillance"],
    "Video Surveillance - Security Cameras - Security Camera Accessories": ["cameras/surveillance/accessories"],
    "Video Surveillance - Security Cameras - Security Cameras": ["cameras/surveillance"],

    # Warranty
    "Warranty & Services - Warranty & Support - Conferencing System Warranty  & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Digital Signage Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Display Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Large Format Printer Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Network Product Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Notebook Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - PC Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Printer & MFP Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Projector Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Scanner Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Server Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Storage Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - Tablet Warranty & Licences": ["software/warranty"],
    "Warranty & Services - Warranty & Support - UPS Warranty & Licences": ["software/warranty"],

    # =========================================================================
    # elko
    # =========================================================================

    # Gadgets & Mobility
    "Gadgets & Mobility > E-mobility > Scooters": ["other/gadgets/e-mobility"],
    "Gadgets & Mobility > Navigation & Car Electronics > Car Accessories": ["other/gadgets/navigation"],
    "Gadgets & Mobility > Navigation & Car Electronics > Navigation Accessories": ["other/gadgets/navigation"],
    "Gadgets & Mobility > Navigation & Car Electronics > Navigation Systems": ["other/gadgets/navigation"],
    "Gadgets & Mobility > Smart Home > Light Fixtures & Bulbs": ["smart-home/lighting", "other/home/household/lamps"],
    "Gadgets & Mobility > Sports & Wearables > Camping Lanterns": ["other/home/sports/illumination"],
    "Gadgets & Mobility > Sports & Wearables > Fitness Bands": ["communication/wearables/fitness"],
    "Gadgets & Mobility > Sports & Wearables > Illumination": ["other/home/sports/illumination"],
    "Gadgets & Mobility > Sports & Wearables > Illumination Accessories": ["other/home/sports/illumination"],
    "Gadgets & Mobility > Sports & Wearables > Robots": ["other/smart-home/robots"],
    "Gadgets & Mobility > Sports & Wearables > Smartwatches": ["communication/wearables/smartwatches"],
    "Gadgets & Mobility > Sports & Wearables > Sports and Watches Accessories": ["phones-radios/wearables/accessories"],
    "Gadgets & Mobility > Sports & Wearables > Swimming Pool Accessories": ["other/home/sports/pool"],
    "Gadgets & Mobility > Tools & Workwear > Tools": ["other/tools/power-tools"],

    # Gardening & Power Tools
    "Gardening & Power Tools > Garden Products > Grass Trimmers": ["other/tools/garden/trimmers"],
    "Gardening & Power Tools > Garden Products > High Pressure Washers": ["other/tools/garden/washers"],
    "Gardening & Power Tools > Garden Products > Lawn Mower Accessories": ["other/tools/garden/mowers"],
    "Gardening & Power Tools > Garden Products > Lawn Mowers": ["other/tools/garden/mowers"],
    "Gardening & Power Tools > Garden Products > Leaf Blowers": ["other/tools/garden/trimmers"],
    "Gardening & Power Tools > Garden Products > Sweepers": ["other/tools/garden/washers"],
    "Gardening & Power Tools > Garden Products > Water Pumps": ["other/tools/garden/pumps"],
    "Gardening & Power Tools > Power Products > Generators": ["other/tools/power-tools"],
    "Gardening & Power Tools > Power Tools > Car Air Compressors": ["other/tools/power-tools"],
    "Gardening & Power Tools > Power Tools > Cordless Tool Batteries": ["other/tools/power-tools"],
    "Gardening & Power Tools > Power Tools > Screwdrivers": ["other/tools/power-tools"],

    # Home Appliances (elko) — mapped flat without unnecessary subcategories
    "Home Appliances > Kitchen Appliances > Air Fryer Accessories": ["other/home/kitchen/fryers"],
    "Home Appliances > Kitchen Appliances > Air Fryers": ["other/home/kitchen/fryers"],
    "Home Appliances > Kitchen Appliances > Bakeware": ["other/home/kitchen/cookware"],
    "Home Appliances > Kitchen Appliances > Blenders": ["other/home/kitchen/blenders"],
    "Home Appliances > Kitchen Appliances > Casseroles": ["other/home/kitchen/cookware"],
    "Home Appliances > Kitchen Appliances > Coffee Maker Accessories": ["other/home/kitchen/coffee"],
    "Home Appliances > Kitchen Appliances > Coffee Makers": ["other/home/kitchen/coffee"],
    "Home Appliances > Kitchen Appliances > Electric Grills": ["other/home/kitchen/grills"],
    "Home Appliances > Kitchen Appliances > Electric Kettles": ["other/home/kitchen/kettles"],
    "Home Appliances > Kitchen Appliances > Food Processors": ["other/home/kitchen/blenders"],
    "Home Appliances > Kitchen Appliances > French Presses": ["other/home/kitchen/coffee"],
    "Home Appliances > Kitchen Appliances > Frying Pans": ["other/home/kitchen/cookware"],
    "Home Appliances > Kitchen Appliances > Juice Extractors": ["other/home/kitchen/blenders"],
    "Home Appliances > Kitchen Appliances > Kettles": ["other/home/kitchen/kettles"],
    "Home Appliances > Kitchen Appliances > Kitchenware": ["other/home/kitchen/cookware"],
    "Home Appliances > Kitchen Appliances > Microwaves": ["other/home/kitchen/microwaves"],
    "Home Appliances > Kitchen Appliances > Milk Frothers & Warmers": ["other/home/kitchen/coffee"],
    "Home Appliances > Kitchen Appliances > Mixers": ["other/home/kitchen/blenders"],
    "Home Appliances > Kitchen Appliances > Multicookers": ["other/home/kitchen/microwaves"],
    "Home Appliances > Kitchen Appliances > Refrigerators": ["other/home/kitchen/refrigerators"],
    "Home Appliances > Kitchen Appliances > Sandwich Makers": ["other/home/kitchen/grills"],
    "Home Appliances > Kitchen Appliances > Teapots": ["other/home/kitchen/kettles"],
    "Home Appliances > Kitchen Appliances > Toasters": ["other/home/kitchen/toasters"],
    "Home Appliances > Kitchen Appliances > Waffle Irons": ["other/home/kitchen/toasters"],
    "Home Appliances > Personal Care > Beard Trimmers": ["other/home/personal-care/shavers"],
    "Home Appliances > Personal Care > Body Groomers / Shavers": ["other/home/personal-care/shavers"],
    "Home Appliances > Personal Care > Electric Toothbrushes": ["other/home/personal-care/dental"],
    "Home Appliances > Personal Care > Epilators": ["other/home/personal-care/other"],
    "Home Appliances > Personal Care > Hair Clippers": ["other/home/personal-care/hair"],
    "Home Appliances > Personal Care > Hair Dryers": ["other/home/personal-care/hair"],
    "Home Appliances > Personal Care > Hair Straighteners": ["other/home/personal-care/hair"],
    "Home Appliances > Personal Care > Hair Stylers": ["other/home/personal-care/hair"],
    "Home Appliances > Personal Care > Oral Irrigators": ["other/home/personal-care/dental"],
    "Home Appliances > Personal Care > Other Beauty Appliances": ["other/home/personal-care/other"],
    "Home Appliances > Personal Care > Precision Trimmers": ["other/home/personal-care/shavers"],
    "Home Appliances > Personal Care > Shavers": ["other/home/personal-care/shavers"],
    "Home Appliances > Personal Care > Toothbrush Heads": ["other/home/personal-care/dental"],
    "Home Appliances > Pet Care > Pet Cameras": ["other/home/pet-care"],
    "Home Appliances > Pet Care > Pet Care & Hygiene": ["other/home/pet-care"],
    "Home Appliances > Pet Care > Pet Feeders & Drinkers": ["other/home/pet-care"],
    "Home Appliances > Small Household Appliances > Air Conditioners": ["other/home/climate"],
    "Home Appliances > Small Household Appliances > Ash Vacuums": ["other/home/cleaning/floor-care"],
    "Home Appliances > Small Household Appliances > Carpet Cleaning Machines": ["other/home/cleaning/floor-care"],
    "Home Appliances > Small Household Appliances > Electric Patio Cleaners": ["other/home/cleaning/floor-care"],
    "Home Appliances > Small Household Appliances > Garment Steamers": ["other/home/garment"],
    "Home Appliances > Small Household Appliances > Handheld Vacuums": ["other/home/cleaning/floor-care"],
    "Home Appliances > Small Household Appliances > Irons": ["other/home/garment"],
    "Home Appliances > Small Household Appliances > Mops": ["other/home/cleaning/floor-care"],
    "Home Appliances > Small Household Appliances > Other Appliances": ["other/home/household/other"],
    "Home Appliances > Small Household Appliances > Portable lamps": ["other/home/household/lamps"],
    "Home Appliances > Small Household Appliances > Shoe & Clothes Care": ["other/home/garment"],
    "Home Appliances > Small Household Appliances > Smart Light Fixtures": ["smart-home/lighting", "other/home/household/lamps"],
    "Home Appliances > Small Household Appliances > Steam Ironing Stations": ["other/home/garment"],
    "Home Appliances > Small Household Appliances > Stick Vacuums &Electric Brooms": ["other/home/cleaning/floor-care"],
    "Home Appliances > Small Household Appliances > Vacuum Cleaner Accessories": ["other/home/cleaning/accessories"],
    "Home Appliances > Small Household Appliances > Vacuum Cleaners": ["other/home/cleaning/floor-care"],
    "Home Appliances > Small Household Appliances > Vacuum Cleaners Robots": ["other/home/cleaning/robots"],
    "Home Appliances > Small Household Appliances > Vacuum Robot Accessories": ["other/home/cleaning/robots"],

    # Networking (elko)
    "Networking > Wired devices > Bridges & Repeaters": ["networking/routers"],
    "Networking > Wired devices > Gateways/Controllers": ["networking/wireless/standard"],
    "Networking > Wired devices > InfiniBand &Fiber Optic Cables": ["networking/cables"],
    "Networking > Wired devices > KVM Switches": ["peripherals/kvm"],
    "Networking > Wired devices > Media Convertors &Modules": ["networking/switches/media-converters"],
    "Networking > Wired devices > Net Switch Components": ["networking/switches"],
    "Networking > Wired devices > Net Switch Modules": ["networking/switches"],
    "Networking > Wired devices > Net Transceiver Modules": ["networking/switches/transceivers"],
    "Networking > Wired devices > POE Devices": ["networking/switches/poe"],
    "Networking > Wired devices > Powerline": ["networking/powerline"],
    "Networking > Wired devices > Routers": ["networking/routers"],
    "Networking > Wired devices > Switches": ["networking/switches"],
    "Networking > Wired devices > Wired Network Adapters": ["networking/cards"],
    "Networking > Wireless equipment > 3G/4G Routers": ["networking/routers/cellular"],
    "Networking > Wireless equipment > Antennas And Accessories": ["networking/wireless/antennas"],
    "Networking > Wireless equipment > Celluar Network Devices": ["networking/routers/cellular", "networking/wireless/standard"],
    "Networking > Wireless equipment > Mesh Wi-Fi Systems": ["networking/wireless/mesh"],
    "Networking > Wireless equipment > Modems": ["networking/modems/standard"],
    "Networking > Wireless equipment > Network Cards & Adapters": ["networking/cards"],
    "Networking > Wireless equipment > Network Equipmment Spare Parts": ["networking/accessories"],
    "Networking > Wireless equipment > Outdoor Networking": ["networking/wireless/outdoor"],
    "Networking > Wireless equipment > Wireless Access Points": ["networking/wireless/standard"],
    "Networking > Wireless equipment > Wireless Network Controllers": ["networking/wireless/standard"],
    "Networking > Wireless equipment > Wireless Range Extenders": ["networking/wireless/extenders"],
    "Networking > Wireless equipment > Wireless Routers": ["networking/routers"],

    # Notebooks, PC & Accessories (elko)
    "Notebooks, PC & Accessories > Desktop Computers > All-in-One PCs": ["computers/desktops/aio"],
    "Notebooks, PC & Accessories > Desktop Computers > Desktop Computers": ["computers/desktops/standard"],
    "Notebooks, PC & Accessories > Desktop Computers > Mini Desktop Computers": ["computers/desktops/mini"],
    "Notebooks, PC & Accessories > Desktop Computers > NUC": ["computers/desktops/mini"],
    "Notebooks, PC & Accessories > Notebooks > Backpacks": ["peripherals/bags", "computers/accessories/bags"],
    "Notebooks, PC & Accessories > Notebooks > Notebook Accessories": ["computers/accessories/other", "computers/accessories"],
    "Notebooks, PC & Accessories > Notebooks > Notebook Bags": ["peripherals/bags", "computers/accessories/bags"],
    "Notebooks, PC & Accessories > Notebooks > Notebook Docks": ["computers/accessories/docks", "peripherals/docks"],
    "Notebooks, PC & Accessories > Notebooks > Notebooks": ["computers/notebooks/standard"],
    "Notebooks, PC & Accessories > Notebooks > Rugged Notebook Accessories": ["computers/accessories/other", "computers/accessories"],
    "Notebooks, PC & Accessories > Notebooks > Rugged Notebooks": ["computers/notebooks/rugged"],

    # PC Components (elko)
    "PC Components > Accessories & Peripherals > Internal PC Cables": ["components/accessories/cables", "components/accessories"],
    "PC Components > Accessories & Peripherals > PC Mounts & Accessories": ["components/accessories/other", "components/accessories"],
    "PC Components > Accessories & Peripherals > Trusted Platform Modules (TPM)": ["components/accessories/tpm", "components/accessories"],
    "PC Components > Cases & PSU > Case Mods & Parts": ["components/cases"],
    "PC Components > Cases & PSU > Cases": ["components/cases"],
    "PC Components > Cooling > Cooling Accessories": ["components/cooling"],
    "PC Components > Cooling > CPU Coolers": ["components/cooling"],
    "PC Components > Cooling > System & VGA Coolers": ["components/cooling"],
    "PC Components > Mainboards > Mainboards for AMD CPUs": ["components/motherboards"],
    "PC Components > Mainboards > Mainboards for Intel CPUs": ["components/motherboards"],
    "PC Components > PC Power Supplies > Desktop Computer PSU": ["components/psu"],
    "PC Components > Processors > CPU": ["components/cpu/desktop"],
    "PC Components > RAM > Memory DIMM": ["components/memory/desktop"],
    "PC Components > RAM > Memory SODIMM": ["components/memory/notebook"],
    "PC Components > Video & Sound Cards > Sound Cards": ["components/sound-cards"],
    "PC Components > Video & Sound Cards > Video Cards": ["components/gpu"],

    # Peripherals & Office Products (elko)
    "Peripherals & Office Products > Accessories > Cable Organizers": ["peripherals/cables-adapters"],
    "Peripherals & Office Products > Accessories > Cleaning Products": ["peripherals/cleaning"],
    "Peripherals & Office Products > Accessories > I/O Cards & Adapters": ["peripherals/io-cards"],
    "Peripherals & Office Products > Accessories > Interface Hubs": ["peripherals/hubs"],
    "Peripherals & Office Products > Accessories > USB Hubs": ["peripherals/hubs"],
    "Peripherals & Office Products > Keyboards & Mouse > Desk Pads": ["peripherals/mousepads"],
    "Peripherals & Office Products > Keyboards & Mouse > Input Device Accessories": ["peripherals/mousepads"],
    "Peripherals & Office Products > Keyboards & Mouse > Keyboards": ["peripherals/keyboards"],
    "Peripherals & Office Products > Keyboards & Mouse > Mouse Devices": ["peripherals/mice"],
    "Peripherals & Office Products > Keyboards & Mouse > Mouse Pads": ["peripherals/mousepads"],
    "Peripherals & Office Products > Keyboards & Mouse > Numeric Keypads": ["peripherals/keyboards/numeric"],
    "Peripherals & Office Products > Keyboards & Mouse > Wrist Rests": ["peripherals/mousepads", "other/office/ergonomics"],
    "Peripherals & Office Products > Monitors > Monitor Accessories": ["peripherals/monitors/accessories"],
    "Peripherals & Office Products > Monitors > Monitor Mount Accessories": ["peripherals/monitors/accessories/mounts"],
    "Peripherals & Office Products > Monitors > USB Graphics Adapters": ["peripherals/monitors/accessories/usb-adapters"],
    "Peripherals & Office Products > Multimedia > Alarm clocks": ["other/home/household/clocks", "other/home/household"],
    "Peripherals & Office Products > Multimedia > Digitizers": ["peripherals/digitizers"],
    "Peripherals & Office Products > Office Products > Binding Machines": ["other/office/binding"],
    "Peripherals & Office Products > Office Products > Computer Desks": ["other/office/furniture"],
    "Peripherals & Office Products > Office Products > Conference Systems": ["communication/conferencing/audio-video"],
    "Peripherals & Office Products > Office Products > Dehumidifiers": ["other/office/air-quality"],
    "Peripherals & Office Products > Office Products > Humidifiers": ["other/office/air-quality"],
    "Peripherals & Office Products > Office Products > Other Office Products": ["other/office/other"],
    "Peripherals & Office Products > Office Products > Shredder Accessories": ["other/office/shredders"],
    "Peripherals & Office Products > Office Products > Shredders": ["other/office/shredders"],
    "Peripherals & Office Products > Office Products > Sneeze Guards": ["other/office/sneeze-guards"],
    "Peripherals & Office Products > Office Products > Standing Desk Frames": ["other/office/standing-desks", "other/office/furniture"],
    "Peripherals & Office Products > Office Products > VoIP": ["communication/desk-phones"],
    "Peripherals & Office Products > Office Products > Wired Telephones": ["communication/desk-phones"],
    "Peripherals & Office Products > Office Products > Workspace Ergonomics": ["other/office/ergonomics"],
    "Peripherals & Office Products > Printers, Scanners & Supplies > All In One": ["print-scan/mfp"],
    "Peripherals & Office Products > Printers, Scanners & Supplies > Ink Cartridges": ["print-scan/supplies/ink", "print-scan/supplies"],
    "Peripherals & Office Products > Printers, Scanners & Supplies > Laser Printer Supplies": ["print-scan/supplies/toner", "print-scan/supplies"],
    "Peripherals & Office Products > Printers, Scanners & Supplies > Laser Printers": ["print-scan/printers/standard"],
    "Peripherals & Office Products > Printers, Scanners & Supplies > Printer Drums": ["print-scan/supplies/drums", "print-scan/supplies"],
    "Peripherals & Office Products > Printers, Scanners & Supplies > Scanners": ["print-scan/scanners/standard"],
    "Peripherals & Office Products > Projectors > Presenters": ["peripherals/presenters"],
    "Peripherals & Office Products > Projectors > Projector Mounts": ["av/projectors/mounting"],
    "Peripherals & Office Products > Projectors > Projectors & Screens": ["av/projectors"],

    # POS Solutions
    "POS Solutions > Desktop POS": ["other/pos/terminals"],
    "POS Solutions > Handheld PDA": ["other/pos/terminals"],
    "POS Solutions > Kiosk SCO": ["other/pos/kiosks"],
    "POS Solutions > Mobile POS": ["other/pos/terminals"],
    "POS Solutions > POS Accessories": ["other/pos/accessories"],
    "POS Solutions > POS Printers": ["other/pos/printers"],
    "POS Solutions > POS Products": ["other/pos/other"],

    # Power Supplies & UPS
    "Power Supplies & UPS > Batteries For UPS": ["power/ups/accessories"],
    "Power Supplies & UPS > Notebook Chargers": ["power/chargers/notebook", "computers/accessories/chargers"],
    "Power Supplies & UPS > PC Power Cables": ["power/cables"],
    "Power Supplies & UPS > Power Adapters & Invertors": ["power/chargers"],
    "Power Supplies & UPS > Power Strips": ["power/surge"],
    "Power Supplies & UPS > Smart Plugs": ["power/smart-plugs", "smart-home/energy"],
    "Power Supplies & UPS > Surge Protectors": ["power/surge"],
    "Power Supplies & UPS > UPS For Workstations": ["power/ups/tower"],
    "Power Supplies & UPS > UPS Options": ["power/ups/accessories"],

    # Renewable Power
    "Renewable Power > Electric Car Charging": ["power/renewable/ev", "power/renewable"],
    "Renewable Power > Power Station Accessories": ["power/renewable/accessories"],
    "Renewable Power > Power Stations": ["power/renewable/stations", "power/renewable"],
    "Renewable Power > Solar Inverters": ["power/renewable/inverters", "power/renewable"],
    "Renewable Power > Solar Panels": ["power/renewable/panels", "power/renewable"],

    # Security Solutions
    "Security Solutions > Access Control Systems > Access Cards": ["cameras/access-control"],
    "Security Solutions > Access Control Systems > Card Readers": ["cameras/access-control"],
    "Security Solutions > Access Control Systems > Door Controllers": ["cameras/access-control"],
    "Security Solutions > Access Control Systems > RFID Tags": ["cameras/access-control"],
    "Security Solutions > Access Control Systems > Security Screening": ["cameras/access-control"],
    "Security Solutions > Door Entry Systems > DES Accessories": ["cameras/door-entry"],
    "Security Solutions > Door Entry Systems > Doorphone Mounting Accessories": ["cameras/door-entry"],
    "Security Solutions > Door Entry Systems > Doorphone Systems": ["cameras/door-entry"],
    "Security Solutions > Door Entry Systems > Network Doorphones": ["cameras/door-entry"],
    "Security Solutions > Door Entry Systems > Standalone Locks": ["cameras/door-entry"],
    "Security Solutions > Fire Alarm Systems > Fire Alarm Accessories": ["cameras/alarms"],
    "Security Solutions > Intruder Alarm Systems > Additional Modules": ["cameras/alarms"],
    "Security Solutions > Intruder Alarm Systems > Batteries": ["cameras/alarms"],
    "Security Solutions > Intruder Alarm Systems > Control Panels": ["cameras/alarms"],
    "Security Solutions > Intruder Alarm Systems > Detectors": ["cameras/alarms"],
    "Security Solutions > Intruder Alarm Systems > Keypads": ["cameras/alarms"],
    "Security Solutions > Intruder Alarm Systems > Power Supplies": ["cameras/alarms"],
    "Security Solutions > Intruder Alarm Systems > Remote Controllers": ["cameras/alarms"],
    "Security Solutions > Intruder Alarm Systems > Security Accessories": ["cameras/alarms"],
    "Security Solutions > Intruder Alarm Systems > Sirens": ["cameras/alarms"],
    "Security Solutions > Video Surveillance > AccessoriesCCTV IP": ["cameras/surveillance/accessories"],
    "Security Solutions > Video Surveillance > Analog CCTV Accessories": ["cameras/surveillance/accessories"],
    "Security Solutions > Video Surveillance > CCTV Lenses": ["cameras/surveillance/lenses"],
    "Security Solutions > Video Surveillance > DVR": ["cameras/nvr-dvr"],
    "Security Solutions > Video Surveillance > HDCVI Cameras": ["cameras/surveillance"],
    "Security Solutions > Video Surveillance > IP Cameras": ["cameras/surveillance"],
    "Security Solutions > Video Surveillance > NVR": ["cameras/nvr-dvr"],
    "Security Solutions > Video Surveillance > Video Decoders": ["cameras/nvr-dvr"],
    "Security Solutions > Video Surveillance > Video Surveillance Software": ["cameras/software"],
    "Security Solutions > Video Surveillance > Warranty Extensions": ["cameras/warranty", "software/warranty"],

    # Servers & Components (elko)
    "Servers & Components > Server Components > Cooling Parts": ["servers/components/cooling"],
    "Servers & Components > Server Components > Mainboards": ["servers/components/motherboards", "components/motherboards"],
    "Servers & Components > Server Components > Memory": ["servers/components/memory", "components/memory/server"],
    "Servers & Components > Server Components > Server Cables": ["servers/components/cables"],
    "Servers & Components > Server Components > Server CPU": ["servers/components/cpu"],
    "Servers & Components > Server Components > Server Disk Drive Controllers": ["servers/components/controllers", "components/controllers"],
    "Servers & Components > Server Components > Server Parts": ["servers/components/other"],
    "Servers & Components > Server Components > Server PSU": ["servers/components/psu"],
    "Servers & Components > Servers & Chassis > Servers": ["servers/rack-tower"],

    # Smartphones & Tablets (elko)
    "Smartphones & Tablets > Smartphones > Feature Phones": ["communication/smartphones/feature", "communication/smartphones"],
    "Smartphones & Tablets > Smartphones > Phone Accessories": ["communication/smartphones/accessories/other", "communication/smartphones/accessories"],
    "Smartphones & Tablets > Smartphones > Phone Car Mounts": ["communication/smartphones/accessories/holders", "communication/smartphones/accessories"],
    "Smartphones & Tablets > Smartphones > Powerbanks": ["communication/smartphones/accessories/chargers", "communication/smartphones/accessories"],
    "Smartphones & Tablets > Smartphones > Smartphone Covers & Cases": ["communication/smartphones/accessories/cases", "communication/smartphones/accessories"],
    "Smartphones & Tablets > Smartphones > Smartphones": ["communication/smartphones"],
    "Smartphones & Tablets > Tablets & E-Readers > Children's tablets": ["computers/tablets/standard"],
    "Smartphones & Tablets > Tablets & E-Readers > E-Reader Accessories": ["computers/accessories/tablet"],
    "Smartphones & Tablets > Tablets & E-Readers > E-Reader Cases": ["computers/accessories/tablet"],
    "Smartphones & Tablets > Tablets & E-Readers > E-Readers": ["computers/ereaders", "computers/tablets"],
    "Smartphones & Tablets > Tablets & E-Readers > Mobile Device Chargers": ["communication/smartphones/accessories/chargers", "computers/accessories/chargers"],
    "Smartphones & Tablets > Tablets & E-Readers > Mobile Device Keyboards": ["computers/accessories/tablet", "peripherals/keyboards"],
    "Smartphones & Tablets > Tablets & E-Readers > Rugged Tablet Accessories": ["computers/accessories/tablet", "computers/accessories"],
    "Smartphones & Tablets > Tablets & E-Readers > Rugged Tablets": ["computers/tablets/rugged"],
    "Smartphones & Tablets > Tablets & E-Readers > Tablet Accessories": ["computers/accessories/tablet", "peripherals/bags/tablet"],
    "Smartphones & Tablets > Tablets & E-Readers > Tablet Sleeves": ["peripherals/bags/tablet", "computers/accessories/tablet"],
    "Smartphones & Tablets > Tablets & E-Readers > Tablets": ["computers/tablets/standard"],
    "Smartphones & Tablets > Tablets & E-Readers > USB Cables": ["peripherals/cables-adapters", "communication/smartphones/accessories/cables"],

    # Software
    "Software > Office": ["software/office"],
    "Software > Server OS & Applications": ["software/server/standard"],
    "Software > Windows OEM": ["software/os/windows"],
    "Software > Windows Retail": ["software/os/windows"],

    # Storage & NAS Systems
    "Storage & NAS Systems > Storage External > Disk Arrays": ["servers/san-jbod"],
    'Storage & NAS Systems > Storage External > HDD External 2.5"': ["servers/external"],
    'Storage & NAS Systems > Storage External > HDD External 3.5"': ["servers/external"],
    "Storage & NAS Systems > Storage External > Memory Card Readers": ["peripherals/card-readers", "cameras/accessories/memory"],
    "Storage & NAS Systems > Storage External > SSD External": ["servers/external"],
    "Storage & NAS Systems > Storage External > USB Flash Drives": ["components/memory/usb"],
    "Storage & NAS Systems > Storage Internal > HDD Desktop": ["components/storage/hdd/internal"],
    "Storage & NAS Systems > Storage Internal > HDD Enterprise SAS": ["servers/enterprise-hdd"],
    "Storage & NAS Systems > Storage Internal > HDD Enterprise SATA": ["servers/enterprise-hdd"],
    "Storage & NAS Systems > Storage Internal > HDD Mobile SATA": ["components/storage/hdd/internal"],
    "Storage & NAS Systems > Storage Internal > HDD Video Surveillance": ["components/storage/hdd/internal", "av/surveillance/cameras"],
    "Storage & NAS Systems > Storage Internal > HDD/SSD Mounting": ["components/storage/accessories"],
    "Storage & NAS Systems > Storage Internal > Network Cables": ["networking/cables"],
    "Storage & NAS Systems > Storage Internal > Optical Disk Drives": ["components/storage/optical", "components/storage"],
    "Storage & NAS Systems > Storage Internal > SSD Enterprise PCI-E": ["servers/enterprise-ssd"],
    "Storage & NAS Systems > Storage Internal > SSD Enterprise SAS": ["servers/enterprise-ssd"],
    "Storage & NAS Systems > Storage Internal > SSD Enterprise SATA": ["servers/enterprise-ssd"],
    "Storage & NAS Systems > Storage Internal > SSD M.2": ["components/storage/ssd/internal"],
    "Storage & NAS Systems > Storage Internal > SSD SATA": ["components/storage/ssd/internal"],
    "Storage & NAS Systems > Storage Systems > JBOD": ["servers/san-jbod"],
    "Storage & NAS Systems > Storage Systems > Other Components": ["servers/components/other", "servers/components"],
    "Storage & NAS Systems > Storage Systems > Rack Mounting Parts": ["servers/racks/accessories"],
    "Storage & NAS Systems > Storage Systems > Rack Parts & Accessories": ["servers/racks/accessories"],
    "Storage & NAS Systems > Storage Systems > Storage": ["components/storage/arrays"],
    "Storage & NAS Systems > Storage Systems > Storage Memory": ["servers/storage-memory"],
    "Storage & NAS Systems > Storage Systems > Storage Software": ["servers/storage-software"],

    # TV, Audio & Video (elko)
    "TV, Audio & Video > Audio > Audio Cables": ["av/audio/cables"],
    "TV, Audio & Video > Audio > Car Audio Systems": ["av/audio/car"],
    "TV, Audio & Video > Audio > Headphone/Headset Accessories": ["peripherals/headsets/accessories"],
    "TV, Audio & Video > Audio > Headphones": ["peripherals/headsets"],
    "TV, Audio & Video > Audio > Headsets": ["peripherals/headsets"],
    "TV, Audio & Video > Audio > Home Audio": ["av/audio/home"],
    "TV, Audio & Video > Audio > Loudspeakers": ["av/audio/loudspeakers"],
    "TV, Audio & Video > Audio > Microphone stands": ["av/audio/microphones", "peripherals/microphones"],
    "TV, Audio & Video > Audio > Microphones": ["av/audio/microphones", "peripherals/microphones"],
    "TV, Audio & Video > Audio > MP3 Players": ["av/audio/mp3"],
    "TV, Audio & Video > Audio > Network Audio": ["av/audio/home"],
    "TV, Audio & Video > Audio > PA Microphones": ["av/audio/microphones", "peripherals/microphones"],
    "TV, Audio & Video > Audio > Portable Speakers": ["av/audio/portable-speakers"],
    "TV, Audio & Video > Audio > Speaker Mounts": ["av/audio/speaker-mounts"],
    "TV, Audio & Video > Audio > Speaker Sets": ["av/audio/loudspeakers"],
    "TV, Audio & Video > Camera & Photo > Action Cameras": ["cameras/photo/action"],
    "TV, Audio & Video > Camera & Photo > Car Video Recorders": ["cameras/car-recorders"],
    "TV, Audio & Video > Camera & Photo > Drone Accessories": ["cameras/drones"],
    "TV, Audio & Video > Camera & Photo > Drones": ["cameras/drones"],
    "TV, Audio & Video > Camera & Photo > Flash memory Cards & Readers": ["cameras/accessories/memory", "peripherals/card-readers"],
    "TV, Audio & Video > Camera & Photo > Gimbal Accessories": ["cameras/gimbals"],
    "TV, Audio & Video > Camera & Photo > Gimbals": ["cameras/gimbals"],
    "TV, Audio & Video > Camera & Photo > Instant Cameras": ["cameras/photo/instant"],
    "TV, Audio & Video > Camera & Photo > Net Cameras": ["cameras/surveillance"],
    "TV, Audio & Video > Camera & Photo > Photo/Video Cam. Accessories": ["cameras/accessories/other"],
    "TV, Audio & Video > Camera & Photo > Web Cameras": ["peripherals/webcams"],
    "TV, Audio & Video > Gaming > Consoles": ["other/gaming/consoles"],
    "TV, Audio & Video > Gaming > Games": ["av/games/games"],
    "TV, Audio & Video > Gaming > Gaming Accessories": ["other/gaming/peripherals"],
    "TV, Audio & Video > Gaming > Gaming Chairs": ["other/gaming/furniture", "other/office/furniture"],
    "TV, Audio & Video > Gaming > Gaming Controllers": ["other/gaming/peripherals/controllers", "other/gaming/peripherals"],
    "TV, Audio & Video > Gaming > Head-Mounted Displays": ["other/gaming/vr"],
    "TV, Audio & Video > Gaming > Portable Game Consoles": ["other/gaming/consoles"],
    "TV, Audio & Video > Monitors > Digital Signage Displays": ["peripherals/signage"],
    "TV, Audio & Video > Monitors > DisplayPort Cables": ["av/av-cables"],
    "TV, Audio & Video > Monitors > DVI Cables": ["av/av-cables"],
    "TV, Audio & Video > Monitors > HDMI Cables": ["av/av-cables"],
    "TV, Audio & Video > Monitors > Monitors": ["peripherals/monitors"],
    "TV, Audio & Video > Monitors > Signage Display Mounts": ["peripherals/monitors/accessories/mounts", "peripherals/signage"],
    "TV, Audio & Video > Monitors > VGA Cables": ["av/av-cables"],
    "TV, Audio & Video > Monitors > Video Cable Adapters": ["av/av-cables/adapters", "av/av-cables"],
    "TV, Audio & Video > Monitors > Video Wall Displays": ["peripherals/signage/video-wall", "peripherals/signage"],
    "TV, Audio & Video > TV > Hospitality  TVs": ["av/tvs/hotel"],
    "TV, Audio & Video > TV > Media Players": ["av/tvs/media-players"],
    "TV, Audio & Video > TV > Mounting Kits": ["av/tvs/mounts"],
    "TV, Audio & Video > TV > Portable TVs & Monitors": ["av/tvs/portable"],
    "TV, Audio & Video > TV > Smart TV Boxes": ["av/tvs/media-players"],
    "TV, Audio & Video > TV > Smart TV Dongles": ["av/tvs/media-players"],
    "TV, Audio & Video > TV > Soundbar Speakers": ["av/speakers"],
    "TV, Audio & Video > TV > TV & Video Equipment": ["av/tvs/standard"],
    "TV, Audio & Video > TV > TV Mount Accessories": ["av/tvs/mounts"],
    "TV, Audio & Video > TV > TV Mounts & Stands": ["av/tvs/mounts"],
    "TV, Audio & Video > TV > TV Sets": ["av/tvs/standard"],
}


# Codes that existed in earlier drafts of the mapping but were collapsed.
# Any mapping entry pointing to a key here is redirected to the value.
# This lets us keep the huge MAPPING dict intact while still removing splits.
COLLAPSE: dict[str, str] = {
    # ---------- Computers ----------
    "computers/desktops/refurbished":              "computers/desktops/standard",
    "computers/desktops/thin-client":              "computers/desktops/mini",
    "computers/notebooks/refurbished":             "computers/notebooks/standard",
    "computers/notebooks/bags":                    "computers/notebook-accessories/bags",
    "computers/notebooks/batteries":               "computers/notebook-accessories/batteries",
    "computers/notebooks/chargers":                "computers/notebook-accessories/chargers",
    "computers/notebooks/docks":                   "computers/notebook-accessories/docks",
    "computers/notebooks/other":                   "computers/notebook-accessories/other",
    "computers/accessories":                       "computers/notebook-accessories/other",
    "computers/accessories/docks":                 "computers/notebook-accessories/docks",
    "computers/accessories/bags":                  "computers/notebook-accessories/bags",
    "computers/accessories/batteries":             "computers/notebook-accessories/batteries",
    "computers/accessories/chargers":              "computers/notebook-accessories/chargers",
    "computers/accessories/tablet":                "computers/tablet-accessories",
    "computers/accessories/other":                 "computers/notebook-accessories/other",
    "computers/accessories/pc":                    "components/cases-accessories/other",
    "computers/tablet-accessories":                     "computers/tablet-accessories",

    # ---------- Components (memory/storage now under components/storage) ----------
    "components/memory":                           "components/storage/ram",
    "components/memory/desktop":                   "components/storage/ram/desktop",
    "components/memory/notebook":                  "components/storage/ram/notebook",
    "components/memory/server":                    "components/storage/ram/server",
    "components/memory/usb":                       "components/storage/flash",
    "components/memory/flash":                     "components/storage/flash",
    "components/gpu/server":                       "components/gpu",
    "components/gpu/workstation":                  "components/gpu",
    # components/storage/* are now real nodes, so no collapse needed except for the
    # old "accessories" leaf which still folds into the generic cases-accessories bucket.
    "components/storage/accessories":              "components/cases-accessories/other",
    "components/accessories":                      "components/cases-accessories",
    "components/accessories/cables":               "components/cases-accessories/internal-cables",
    "components/accessories/tpm":                  "components/cases-accessories/tpm",
    "components/accessories/other":                "components/cases-accessories/other",

    # ---------- Peripherals -> Components & Accessories (Markit 16) ----------
    "peripherals/keyboards":                       "components/keyboards-mice",
    "peripherals/keyboards/numeric":               "components/keyboards-mice/numeric",
    "peripherals/mice":                            "components/keyboards-mice",
    "peripherals/mousepads":                       "components/keyboards-mice/mousepads",
    "peripherals/presenters":                      "components/keyboards-mice/presenters",
    "peripherals/digitizers":                      "components/keyboards-mice/digitizers",
    "peripherals/combos":                          "components/keyboards-mice",
    "peripherals/headsets":                        "av/headsets/standard",
    "peripherals/headsets/accessories":            "av/headsets/accessories",
    "peripherals/microphones":                     "av/accessories/microphones",
    "peripherals/webcams":                         "components/webcams",
    "peripherals/speakers-pc":                     "av/speakers",
    "peripherals/cables-adapters":                 "components/cables/data",
    "peripherals/hubs":                            "components/cables/hubs",
    "peripherals/card-readers":                    "components/cables/card-readers",
    "peripherals/docks":                           "computers/notebook-accessories/docks",
    "peripherals/bags":                            "computers/notebook-accessories/bags",
    "peripherals/bags/tablet":                     "computers/tablet-accessories",
    "peripherals/kvm":                             "components/kvm",
    "peripherals/io-cards":                        "components/cables/io-cards",
    "peripherals/cleaning":                        "components/cases-accessories/other",
    "peripherals/accessories":                     "components/cases-accessories/other",
    # Monitors & Signage -> Displays & Projectors (Markit 12)
    "peripherals/monitors":                        "displays/monitors/standard",
    "peripherals/monitors/portable":               "displays/monitors/standard",
    "peripherals/monitors/accessories":            "displays/monitors/accessories/other",
    "peripherals/monitors/accessories/mounts":     "displays/monitors/accessories/mounts",
    "peripherals/monitors/accessories/privacy":    "displays/monitors/accessories/privacy",
    "peripherals/monitors/accessories/usb-adapters":"displays/monitors/accessories/usb-adapters",
    "peripherals/signage":                         "displays/large-format/standard",
    "peripherals/signage/outdoor":                 "displays/large-format/standard",
    "peripherals/signage/touch":                   "displays/large-format/standard",
    "peripherals/signage/video-wall":              "displays/large-format/video-wall",

    # ---------- Print-scan (Markit 13 restructure) ----------
    "print-scan/mfp":                              "print-scan/printers/mfp",
    "print-scan/mfp/inkjet":                       "print-scan/printers/mfp",
    "print-scan/mfp/laser":                        "print-scan/printers/mfp",
    "print-scan/printers/inkjet":                  "print-scan/printers/standard",
    "print-scan/printers/laser":                   "print-scan/printers/standard",
    "print-scan/printers/label":                   "print-scan/printers/standard",
    "print-scan/printers/matrix":                  "print-scan/printers/standard",
    "print-scan/printers/photo":                   "print-scan/printers/standard",
    "print-scan/lfp":                              "print-scan/printers/lfp",
    "print-scan/lfp/accessories":                  "print-scan/printers/lfp/accessories",
    "print-scan/3d":                               "print-scan/printers/3d",
    "print-scan/supplies":                         "print-scan/consumables",
    "print-scan/supplies/ink":                     "print-scan/consumables/ink",
    "print-scan/supplies/toner":                   "print-scan/consumables/toner",
    "print-scan/supplies/drums":                   "print-scan/consumables/drums",
    "print-scan/supplies/fuser":                   "print-scan/consumables/other",
    "print-scan/supplies/ribbons":                 "print-scan/consumables/other",
    "print-scan/supplies/other":                   "print-scan/consumables/other",
    "print-scan/paper":                            "print-scan/consumables/paper",
    "print-scan/accessories":                      "print-scan/trays",

    # ---------- Networking ----------
    "networking/switches/transceivers":            "networking/transceivers/standard",
    "networking/switches/media-converters":        "networking/transceivers/media-converters",
    "networking/firewalls":                        "networking/security/firewalls",
    "networking/powerline":                        "networking/modems/powerline",
    "networking/bridges":                          "networking/routers",
    "networking/cables":                           "networking/cabling",
    "networking/cards":                            "networking/adapters",
    "networking/accessories":                      "networking/adapters",

    # ---------- Servers -> computers/servers + storage ----------
    "servers/rack-tower":                          "computers/servers/rack-tower",
    "servers/components":                          "computers/servers/components",
    "servers/components/cpu":                      "computers/servers/components/cpu",
    "servers/components/memory":                   "computers/servers/components/memory",
    "servers/components/motherboards":             "computers/servers/components/motherboards",
    "servers/components/psu":                      "computers/servers/components/psu",
    "servers/components/controllers":              "computers/servers/components/controllers",
    "servers/components/cooling":                  "computers/servers/components/other",
    "servers/components/cases":                    "computers/servers/components/other",
    "servers/components/cables":                   "computers/servers/components/other",
    "servers/components/gpu":                      "computers/servers/components/other",
    "servers/components/other":                    "computers/servers/components/other",
    "servers/racks":                               "computers/servers/racks",
    "servers/racks/standard":                      "computers/servers/racks/standard",
    "servers/racks/accessories":                   "computers/servers/racks/accessories",
    "servers/accessories":                         "computers/servers/components/other",
    "servers/nas":                                 "components/storage/arrays",
    "servers/san-jbod":                            "components/storage/arrays",
    "servers/external":                            "components/storage/hdd/external",
    "servers/enterprise-hdd":                      "components/storage/hdd/enterprise",
    "servers/enterprise-ssd":                      "components/storage/ssd/enterprise",
    "servers/tape":                                "components/storage/tape",
    "servers/storage-software":                    "software-apps/business/backup",
    "servers/storage-memory":                      "components/storage/ram/server",

    # ---------- Power -> components/power-protection + other/energy + components/batteries + components/cables ----------
    "power/ups":                                   "components/power-protection/ups",
    "power/ups/workstation":                       "components/power-protection/ups",
    "power/ups/rack":                              "components/power-protection/ups",
    "power/ups/tower":                             "components/power-protection/ups",
    "power/pdu/managed":                           "components/power-protection/pdu",
    "power/pdu/standard":                          "components/power-protection/pdu",
    "power/ups/accessories":                       "components/power-protection/accessories",
    "power/pdu":                                   "components/power-protection/pdu",
    "power/pdu/accessories":                       "components/power-protection/accessories",
    "power/surge":                                 "components/power-protection/accessories",
    # flatten sub-nodes that were removed from TREE
    "components/power-protection/ups/rack":        "components/power-protection/ups",
    "components/power-protection/ups/tower":       "components/power-protection/ups",
    "components/power-protection/pdu/managed":     "components/power-protection/pdu",
    "components/power-protection/pdu/standard":    "components/power-protection/pdu",
    "components/power-protection/surge":           "components/power-protection/accessories",
    "power/smart-plugs":                           "other/smart-home/energy",
    "power/chargers":                              "components/batteries/chargers",
    "power/chargers/notebook":                     "components/batteries/notebook",
    "power/chargers/batteries":                    "components/batteries",
    "power/cables":                                "components/cables/power",
    "power/renewable":                             "other/energy",
    "power/renewable/panels":                      "other/energy/panels",
    "power/renewable/inverters":                   "other/energy/inverters",
    "power/renewable/battery":                     "other/energy/batteries",
    "power/renewable/stations":                    "other/energy/stations",
    "power/renewable/ev":                          "other/energy/ev",
    "power/renewable/accessories":                 "other/energy/accessories",

    # ---------- AV reorganization ----------
    "av/monitors":                                 "displays/monitors/standard",
    "av/monitors/accessories":                     "displays/monitors/accessories",
    "av/monitors/accessories/mounts":              "displays/monitors/accessories/mounts",
    "av/monitors/accessories/privacy":             "displays/monitors/accessories/privacy",
    "av/monitors/accessories/usb-adapters":        "displays/monitors/accessories/usb-adapters",
    "av/signage":                                  "displays/large-format/standard",
    "av/signage/video-wall":                       "displays/large-format/video-wall",
    "av/projectors":                               "displays/projectors/standard",
    "av/projectors/lamps":                         "displays/projectors/lamps",
    # projector screens merged into the main "Projectors & Screens" leaf
    "av/projectors/screens":                       "displays/projectors/standard",
    "displays/projectors/screens":                 "displays/projectors/standard",
    "av/projectors/mounting":                      "displays/projectors/mounting",
    "av/projectors/other":                         "displays/projectors/other",
    "av/projectors/accessories":                   "displays/projectors/other",
    "av/audio":                                    "av/home/audio",
    "av/audio/home":                               "av/home/audio",
    "av/audio/network":                            "av/home/audio",
    "av/audio/soundbars":                          "av/home/soundbars",
    "av/audio/portable-speakers":                  "av/portable/speakers",
    "av/audio/loudspeakers":                       "av/speakers",
    "av/audio/speaker-mounts":                     "av/speakers",
    "av/audio/headphones":                         "av/portable/headphones",
    "av/audio/mp3":                                "av/portable/mp3",
    "av/audio/microphones":                        "av/accessories/microphones",
    "av/audio/microphone-stands":                  "av/accessories/microphones",
    "av/audio/pa":                                 "av/accessories/microphones",
    "av/audio/car":                                "av/car/audio",
    "av/audio/cables":                             "av/accessories/cables",
    "av/av-cables":                                "av/accessories/cables",
    "av/av-cables/adapters":                       "av/accessories/cables",
    "av/av-systems":                               "av/home/audio",
    "av/radios":                                   "navigation/radios",
    "av/home/radios":                              "navigation/radios",
    "av/tvs/other":                                "av/tvs/accessories",
    "av/tvs/hotel":                                "av/tvs/specialty",
    "av/tvs/portable":                             "av/tvs/specialty",
    "av/tvs/mounts-accessories":                   "av/tvs/mounts",
    "av/tvs/mounting-kits":                        "av/tvs/mounts",

    # ---------- Cameras reorganization ----------
    "cameras/photo":                               "cameras/digital/standard",
    "cameras/photo/instant":                       "cameras/digital/instant",
    "cameras/photo/action":                        "cameras/digital/action",
    "cameras/drones":                              "cameras/camera-accessories/drones",
    "cameras/gimbals":                             "cameras/camera-accessories/gimbals",
    "cameras/car-recorders":                       "av/car/dashcams",
    "cameras/optical":                             "cameras/camera-accessories/optical",
    "cameras/accessories":                         "cameras/camera-accessories",
    "cameras/accessories/memory":                  "cameras/camera-accessories/memory",
    "cameras/accessories/other":                   "cameras/camera-accessories/other",
    "cameras/surveillance":                        "av/surveillance/cameras",
    "cameras/surveillance/accessories":            "av/surveillance/accessories",
    "cameras/surveillance/lenses":                 "av/surveillance/accessories",
    "cameras/nvr-dvr":                             "av/surveillance/nvr-dvr",
    "cameras/software":                            "av/surveillance/software",
    "cameras/access-control":                      "av/surveillance/access-control",
    "cameras/door-entry":                          "av/surveillance/door-entry",
    "cameras/alarms":                              "av/surveillance/alarms",
    "cameras/warranty":                            "service-support/hardware",

    # ---------- Smart-home -> other/smart-home + navigation/wearable ----------
    "smart-home/lighting":                         "other/smart-home/lighting",
    "smart-home/energy":                           "other/smart-home/energy",
    "smart-home/security-living":                  "other/smart-home/security",
    "smart-home/accessories":                      "other/smart-home/accessories",
    "smart-home/iot-devices":                      "other/smart-home/iot",
    "smart-home/iot-wearables":                    "navigation/wearable/fitness",
    "smart-home/iot-accessories":                  "other/smart-home/iot",
    "smart-home/iot-services":                     "other/smart-home/iot",

    # ---------- Communication -> phones-radios + navigation/wearable ----------
    "communication/smartphones":                   "phones-radios/mobile",
    "communication/smartphones/feature":           "phones-radios/mobile",
    "communication/smartphones/accessories":       "phones-radios/mobile/accessories",
    "communication/smartphones/accessories/cases": "phones-radios/mobile/accessories/cases",
    "communication/smartphones/accessories/chargers":"phones-radios/mobile/accessories/chargers",
    "communication/smartphones/accessories/cables":"phones-radios/mobile/accessories/cables",
    "communication/smartphones/accessories/holders":"phones-radios/mobile/accessories/holders",
    "communication/smartphones/accessories/protectors":"phones-radios/mobile/accessories/protectors",
    "communication/smartphones/accessories/headsets":"phones-radios/mobile/accessories/headsets",
    "communication/smartphones/accessories/other": "phones-radios/mobile/accessories/other",
    "communication/wearables":                     "navigation/wearable",
    "communication/wearables/smartwatches":        "phones-radios/wearables/smartwatches",
    "communication/wearables/fitness":             "navigation/wearable/fitness",
    "communication/wearables/accessories":         "navigation/wearable/accessories",
    "communication/desk-phones":                   "phones-radios/telephones/standard",
    "communication/desk-phones/accessories":       "phones-radios/telephones/accessories",
    "communication/conferencing":                  "phones-radios/telephones/conferencing",
    "communication/conferencing/audio-video":      "phones-radios/telephones/conferencing",
    "communication/conferencing/pc":               "phones-radios/telephones/conferencing",
    "communication/conferencing/accessories":      "phones-radios/telephones/conferencing",
    "communication/pro-radio":                     "navigation/two-way",
    "communication/pro-radio/portable":            "navigation/two-way/portable",
    "communication/pro-radio/accessories":         "navigation/two-way/accessories",

    # ---------- Software -> software-apps + os + service-support ----------
    "software/os":                                 "software-apps/os",
    "software/os/windows":                         "software-apps/os/windows",
    "software/os/linux":                           "software-apps/os/linux",
    "software/office":                             "software-apps/office",
    "software/security":                           "software-apps/antivirus",
    "software/security/antivirus":                 "software-apps/antivirus",
    "software/security/vpn":                       "software-apps/antivirus/vpn",
    "software/security/firewall":                  "software-apps/antivirus/firewall",
    "software/security/auth":                      "software-apps/antivirus/auth",
    "software/server":                             "software-apps/business/server",
    "software/server/standard":                    "software-apps/business/server",
    "software/server/cal":                         "software-apps/business/server",
    "software/network":                            "software-apps/network",
    "software/network/management":                 "software-apps/network/management",
    "software/network/webconf":                    "software-apps/network/webconf",
    "software/utilities":                          "software-apps/business/backup",
    "software/utilities/cloud":                    "software-apps/business/cloud",
    "software/utilities/backup":                   "software-apps/business/backup",
    "software/utilities/virtualization":           "software-apps/business/virtualization",
    "software/warranty":                           "service-support/hardware",

    # ---------- Other/gaming -> av/games (or appropriate destination) ----------
    "other/gaming":                                "av/games",
    "other/gaming/notebooks":                      "computers/notebooks/gaming",
    "other/gaming/pcs":                            "computers/desktops/gaming",
    "other/gaming/monitors":                       "displays/monitors/gaming",
    "other/gaming/peripherals":                    "av/games/peripherals",
    "other/gaming/peripherals/headsets":           "av/games/peripherals",
    "other/gaming/peripherals/keyboards-mice":     "av/games/peripherals",
    "other/gaming/peripherals/mousepads":          "av/games/peripherals",
    "other/gaming/peripherals/controllers":        "av/games/peripherals",
    "other/gaming/furniture":                      "av/games/furniture",
    "other/gaming/consoles":                       "av/games/consoles",
    "other/gaming/vr":                             "av/games/consoles",
    # State migration: old av/games sub-nodes that no longer exist
    "av/games/notebooks":                          "computers/notebooks/gaming",
    "av/games/desktops":                           "computers/desktops/gaming",
    "av/games/monitors":                           "displays/monitors/gaming",
    "av/games/vr":                                 "av/games/consoles",

    # ---------- Other/pos -> computers/pos ----------
    "other/pos":                                   "computers/pos",
    "other/pos/terminals":                         "computers/pos/terminals",
    "other/pos/kiosks":                            "computers/pos/kiosks",
    "other/pos/printers":                          "computers/pos/printers",
    "other/pos/accessories":                       "computers/pos/accessories",
    "other/pos/other":                             "computers/pos/other",

    # ---------- Other/office (shredders, binding, media moved into print-scan/storage) ----------
    "other/office/shredders":                      "print-scan/office-products/shredders",
    "other/office/binding":                        "print-scan/office-products/binding",
    "other/office/media":                          "components/storage/media",

    # ---------- Other/gadgets -> av/games + navigation + other/car ----------
    "other/gadgets":                               "av/games",
    "other/gadgets/e-mobility":                    "other/home/sports/e-mobility",
    "other/gadgets/navigation":                    "navigation/accessories",
    "other/gadgets/car-accessories":               "navigation/accessories",

    # ---------- Other/home misc collapses ----------
    "other/home/cleaning/chemical":                "other/home/cleaning/accessories",
    "other/home/kitchen/other":                    "other/home/kitchen/cookware",

    # ---------- storage/* -> components/storage/* (nested under Components) ----------
    "storage":                                     "components/storage",
    "storage/hdd":                                 "components/storage/hdd",
    "storage/hdd/internal":                        "components/storage/hdd/internal",
    "storage/hdd/external":                        "components/storage/hdd/external",
    "storage/hdd/enterprise":                      "components/storage/hdd/enterprise",
    "storage/ram":                                 "components/storage/ram",
    "storage/ram/desktop":                         "components/storage/ram/desktop",
    "storage/ram/notebook":                        "components/storage/ram/notebook",
    "storage/ram/server":                          "components/storage/ram/server",
    "storage/ssd":                                 "components/storage/ssd",
    "storage/ssd/internal":                        "components/storage/ssd/internal",
    "storage/ssd/enterprise":                      "components/storage/ssd/enterprise",
    "storage/enclosures":                          "components/storage/enclosures",
    "storage/flash":                               "components/storage/flash",
    "storage/optical":                             "components/storage/optical",
    "storage/nas":                                 "components/storage/arrays",
    "storage/tape":                                "components/storage/tape",
    "storage/duplicators":                         "components/storage/duplicators",
    "storage/arrays":                              "components/storage/arrays",
    "storage/legacy":                              "components/storage/legacy",
    "storage/media":                               "components/storage/media",
    "storage/cables":                              "components/storage/cables",

    # ---------- os/* -> software-apps/os/* (nested under Software Applications) ----------
    "os":                                          "software-apps/os",
    "os/windows":                                  "software-apps/os/windows",
    "os/linux":                                    "software-apps/os/linux",

    # ---------- Headsets moved out from under "AV Accessories" ----------
    "av/accessories/headsets":                     "av/headsets",
    "av/accessories/headsets/accessories":         "av/headsets/accessories",

    # ---------- Headphones merged into Headsets & Headphones ----------
    "av/portable/headphones":                      "av/headsets",
    "av/audio/headphones":                         "av/headsets",

    # ---------- Soundbars moved from Home Audio into Speakers ----------
    "av/home/soundbars":                           "av/speakers",
    "av/audio/soundbars":                          "av/speakers",

    # ---------- E-Scooters moved from Gaming to Sports/Outdoor ----------
    "av/games/e-mobility":                         "other/home/sports/e-mobility",
    "other/gadgets/e-mobility":                    "other/home/sports/e-mobility",

    # ---------- Service Robots moved from Sports to Smart Home ----------
    "other/home/sports/robots":                    "other/smart-home/robots",

    # ---------- Server-specific components now only under Servers ----------
    "components/storage/ram/server":               "computers/servers/components/memory",
    "components/cpu/server":                       "computers/servers/components/cpu",

    # ---------- Notebook Chargers unified under Notebooks ----------
    "computers/notebooks/chargers":                "computers/notebook-accessories/chargers",
    "components/batteries/notebook":               "computers/notebook-accessories/chargers",

    # ---------- Removed redundant nodes ----------
    "software-apps/utilities":                     "software-apps/business/backup",
    "other/car":                                   "navigation/accessories",

    # ---------- Antivirus sub-nodes collapsed into parent ----------
    "software-apps/antivirus/vpn":                 "software-apps/antivirus",
    "software-apps/antivirus/firewall":            "software-apps/antivirus",
    "software-apps/antivirus/auth":                "software-apps/antivirus",

    # ---------- Service & Support moved under Other ----------
    "service-support":                             "other/service-support",
    "service-support/hardware":                    "other/service-support/hardware",
    "service-support/training":                    "other/service-support/training",

    # ---------- Radios moved under Navigation ----------
    "phones-radios/two-way":                       "navigation/two-way",
    "phones-radios/two-way/portable":              "navigation/two-way/portable",
    "phones-radios/two-way/accessories":           "navigation/two-way/accessories",

    # ---------- Wearables moved under Phones & Devices ----------
    "navigation/wearable":                         "phones-radios/wearables",
    "navigation/wearable/smartwatches":            "phones-radios/wearables/smartwatches",
    "navigation/wearable/fitness":                 "phones-radios/wearables/fitness",
    "navigation/wearable/accessories":             "phones-radios/wearables/accessories",

    # ---------- v3 reduction pass ----------
    "navigation/radios":                             "navigation/accessories",
    "other/education/presentation":                  "other/education/accessories",
    "other/smart-home/accessories":                  "other/smart-home/iot",
    "other/smart-home/robots":                       "other/smart-home/iot",
    "other/office/sneeze-guards":                    "other/office/furniture",
    "other/office/other":                            "other/office/furniture",
    "print-scan/printers/lfp/accessories":           "print-scan/printers/lfp",
    "print-scan/scanners/barcode":                   "print-scan/scanners/standard",
    "peripherals/combos":                            "components/keyboards-mice",
    "power/chargers/batteries":                      "components/batteries/chargers",

    # ---------- flatten single-child MB node ----------
    "components/motherboards/desktop":               "components/motherboards",
    # Enterprise HDDs → Internal HDDs (two HDD children: External / Internal)
    "components/storage/hdd/enterprise":             "components/storage/hdd/internal",

    # ---------- v4 reduction pass ----------
    # POS: kiosks/other/printers → related leaf nodes
    "computers/pos/kiosks":                          "computers/pos/terminals",
    "computers/pos/other":                           "computers/pos/accessories",
    "computers/pos/printers":                        "computers/pos/accessories",

    # Office: standing desks + air quality → furniture leaf
    "other/office/standing-desks":                   "other/office/furniture",
    "other/office/air-quality":                      "other/office/furniture",

    # I/O cards → cases-accessories/other (leaf)
    "components/cables/io-cards":                    "components/cases-accessories/other",

    # ---------- v5 reduction pass ----------
    # Drop same-label / single-provider / dual-mapped sibling leaves.
    # Any stale tree_state.json reference is redirected to the surviving bucket.

    # Single-provider attribute variants — collapse into parent device node.
    "computers/desktops/gaming":                     "computers/desktops/standard",
    "computers/notebooks/standard":                  "computers/notebooks",
    "computers/notebooks/gaming":                    "computers/notebooks",
    "computers/notebooks/rugged":                    "computers/notebooks",
    "computers/tablets/standard":                    "computers/tablets",
    "computers/tablets/rugged":                      "computers/tablets",
    "displays/monitors/standard":                    "displays/monitors",
    "displays/monitors/gaming":                      "displays/monitors",
    "displays/large-format/standard":                "displays/large-format",
    "displays/large-format/video-wall":              "displays/large-format",
    "print-scan/printers/standard":                  "print-scan/printers",
    "networking/modems/standard":                    "networking/modems",
    "av/tvs/standard":                               "av/tvs",
    "av/headsets/standard":                          "av/headsets",
    "cameras/digital/standard":                      "cameras/digital",

    # Pattern B merges — sibling pairs combined by at least one supplier.
    "components/keyboards-mice/keyboards":           "components/keyboards-mice",
    "components/keyboards-mice/mice":                "components/keyboards-mice",
    "phones-radios/mobile/smartphones":              "phones-radios/mobile",
    "phones-radios/mobile/feature":                  "phones-radios/mobile",
    "networking/routers/standard":                   "networking/routers",
    "networking/routers/bridges":                    "networking/routers",
    "networking/switches/standard":                  "networking/switches",
    "networking/switches/modules":                   "networking/switches",
    "av/speakers/pc":                                "av/speakers",
    "av/speakers/soundbars":                         "av/speakers",
    "av/speakers/loudspeakers":                      "av/speakers",
    "components/storage/nas":                        "components/storage/arrays",
    "other/tools/workwear":                          "other/tools/power-tools",

    # Merged Projectors & Screens leaf (previous session) — legacy /screens
    # sub-tree folds into /standard so confirmed state migrates.
    "displays/projectors/screens":                   "displays/projectors/standard",
    "displays/projectors/screens/electric":          "displays/projectors/standard",
    "displays/projectors/screens/manual":            "displays/projectors/standard",
    "displays/projectors/screens/options":           "displays/projectors/standard",
    "displays/projectors/screens/portable":          "displays/projectors/standard",

    # Single-provider server sub-components → Other Server Parts.
    # Rule: single-provider leaves don't stand alone; they fold into a
    # sibling /other or /accessories bucket.
    "computers/servers/components/cooling":          "computers/servers/components/other",
    "computers/servers/components/cases":            "computers/servers/components/other",
    "computers/servers/components/cables":           "computers/servers/components/other",
    "computers/servers/components/gpu":              "computers/servers/components/other",
    "computers/servers/accessories":                 "computers/servers/components/other",

    # Notebook Accessories lifted out of the notebooks leaf (notebooks carries
    # products directly, so it can't also have children). Old codes migrate
    # into the new sibling branch.
    "computers/notebooks/accessories":               "computers/notebook-accessories",
    "computers/notebooks/accessories/bags":          "computers/notebook-accessories/bags",
    "computers/notebooks/accessories/batteries":     "computers/notebook-accessories/batteries",
    "computers/notebooks/accessories/chargers":      "computers/notebook-accessories/chargers",
    "computers/notebooks/accessories/docks":         "computers/notebook-accessories/docks",
    "computers/notebooks/accessories/other":         "computers/notebook-accessories/other",

    # Tablets is also a product-bearing leaf — E-Readers and Tablet Accessories
    # become their own sibling branches (same rule as Notebooks).
    "computers/tablets/ereaders":                    "computers/ereaders",
    "computers/tablets/accessories":                 "computers/tablet-accessories",
    "computers/tablets/cases":                       "computers/tablet-accessories",

}


def normalise(code: str) -> str:
    # Follow the COLLAPSE chain (in case of multi-hop) and return final code.
    seen = set()
    while code in COLLAPSE and code not in seen:
        seen.add(code)
        code = COLLAPSE[code]
    return code


def path_label(code: str) -> str:
    parts = []
    cur = code
    while cur is not None:
        label, parent = TREE[cur]
        parts.append(label)
        cur = parent
    return " > ".join(reversed(parts))


IN_DIR = Path(__file__).parent / "output"
OUT_DIR = Path(__file__).parent / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

IN_FILES = [
    "eduards@abian.lv_default.csv",
    "eduards@abian.lv_default (1).csv",
]

# Persisted edits from the HTML editor (survive rebuilds).
#   deleted   : [code, ...]                   — nodes removed from the tree
#   overrides : { supplier_category : [code, ...] }  — mapping overrides
#   confirmed : [code, ...]                   — categories reviewed & approved by the user
STATE_FILE = OUT_DIR / "tree_state.json"
DELETED_CODES: set[str] = set()
OVERRIDES: dict[str, list[str]] = {}
CONFIRMED_CODES: set[str] = set()
ORDER: dict[str, list[str]] = {}  # parent_code (or "__root__") -> [child_code, ...]
# Populated by main(); reused by the serve() POST /save handler to re-render
# the HTML so the persisted confirmed/deleted/order state shows up on reload.
_RENDER_CTX: dict = {}
if STATE_FILE.exists():
    try:
        _state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        DELETED_CODES = set(_state.get("deleted", []))
        OVERRIDES = dict(_state.get("overrides", {}))
        CONFIRMED_CODES = set(_state.get("confirmed", []))
        ORDER = dict(_state.get("order", {}))
    except Exception:
        pass


# Migrate any stale codes in the loaded state through the current COLLAPSE map
# so user confirmations / order / deletions survive tree restructures
# (e.g. moving `storage/*` under `components/storage/*`).
CONFIRMED_CODES = {normalise(c) for c in CONFIRMED_CODES}
DELETED_CODES = {normalise(c) for c in DELETED_CODES}
ORDER = {
    normalise(parent) if parent != "__root__" else "__root__":
        [normalise(c) for c in children]
    for parent, children in ORDER.items()
}

# Remove deleted codes from TREE before downstream processing.
for _code in list(TREE):
    if _code in DELETED_CODES:
        del TREE[_code]

# Apply mapping overrides on top of the base MAPPING.
for _cat, _codes in OVERRIDES.items():
    MAPPING[_cat] = list(_codes)


# ---------------------------------------------------------------------------
# Prune empty categories: remove any TREE node that no MAPPING entry reaches
# (neither directly nor as an ancestor). Empty top-level roots are pruned too.
# User-confirmed codes are kept so "approved" leaves don't vanish if a
# supplier temporarily lacks coverage.
# ---------------------------------------------------------------------------
def _prune_empty():
    used: set[str] = set()
    # Keep user-confirmed codes (and their ancestors).
    for _code in CONFIRMED_CODES:
        if _code in TREE:
            used.add(_code)
            _c = _code
            while "/" in _c:
                _c = _c.rsplit("/", 1)[0]
                used.add(_c)
    # Keep every code reachable from MAPPING (after COLLAPSE) + ancestors.
    for _codes in MAPPING.values():
        for _code in _codes:
            _c = normalise(_code)
            if _c in TREE:
                used.add(_c)
                while "/" in _c:
                    _c = _c.rsplit("/", 1)[0]
                    used.add(_c)
    for _code in list(TREE):
        if _code not in used:
            del TREE[_code]

_prune_empty()


def process_file(filename: str):
    in_path = IN_DIR / filename
    out_path = OUT_DIR / filename
    unmapped, out_rows = [], []
    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            supplier = row["supplier_name"]
            cat = row["supplier_category"]
            codes = MAPPING.get(cat)
            if not codes:
                unmapped.append(cat)
                out_rows.append([supplier, cat, "", ""])
                continue
            # 1. Apply COLLAPSE normalisation + dedupe + skip deleted codes.
            seen = set(); norm_codes = []
            for code in codes:
                c = normalise(code)
                if c not in TREE:
                    continue  # code was deleted in HTML editor
                if c in seen: continue
                seen.add(c); norm_codes.append(c)
            # 2. Ancestor-dedupe: drop code X if the list also contains X/sub.
            code_set = set(norm_codes)
            final_codes = []
            for c in norm_codes:
                is_ancestor = any(o != c and o.startswith(c + "/") for o in code_set)
                if not is_ancestor:
                    final_codes.append(c)
            if not final_codes:
                out_rows.append([supplier, cat, "", ""])
                continue
            for code in final_codes:
                out_rows.append([supplier, cat, code, path_label(code)])
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(["supplier_name", "supplier_category", "client_category_code", "client_category_label"])
        w.writerows(out_rows)
    return out_rows, unmapped


def build_tree_json():
    children = defaultdict(list)
    for code, (_, parent) in TREE.items():
        children[parent].append(code)

    def sort_key(code):
        label = TREE[code][0].lower()
        # "Other" nodes (top-level "Other" or "Other X Accessories" leaves) sort last.
        is_other = code == "other" or code.endswith("/other") or label.startswith("other ")
        return (1 if is_other else 0, label)

    # Apply persisted user order where available; fall back to default sort for
    # any children not listed (new codes) or when no order is saved.
    for parent, lst in children.items():
        key = "__root__" if parent is None else parent
        saved = ORDER.get(key) or []
        if saved:
            pos = {c: i for i, c in enumerate(saved)}
            # Unknown (new) codes go after known ones, alphabetical with "Other" last.
            lst.sort(key=lambda c: (0, pos[c]) if c in pos else (1, *sort_key(c)))
        else:
            lst.sort(key=sort_key)

    def build(code):
        return [{"code": c, "label": TREE[c][0], "children": build(c)}
                for c in children[code] if c not in DELETED_CODES]
    return {"tree": build(None)}


def build_map_idx(rows):
    idx = defaultdict(list)
    for supplier, sup_cat, code, _ in rows:
        if code:
            idx[code].append({"supplier": supplier, "category": sup_cat})
    return idx


def coverage_diagnostic(rows):
    """For every leaf with mappings, list which suppliers cover it."""
    leaf_suppliers = defaultdict(set)
    for supplier, _, code, _ in rows:
        if code:
            leaf_suppliers[code].add(supplier)
    only_also = sorted([c for c, s in leaf_suppliers.items() if s == {"also_data"}])
    only_elko = sorted([c for c, s in leaf_suppliers.items() if s == {"elko"}])
    both = sorted([c for c, s in leaf_suppliers.items() if len(s) >= 2])
    return only_also, only_elko, both


def render_html(tree, map_idx, stats, coverage, sources, sup_mapping, path_labels, confirmed, deleted=None):
    tree_json = json.dumps(tree, ensure_ascii=False)
    map_json  = json.dumps(map_idx, ensure_ascii=False)
    stats_json = json.dumps(stats, ensure_ascii=False)
    cov_json = json.dumps(coverage, ensure_ascii=False)
    sources_json = json.dumps(sources, ensure_ascii=False)
    supmap_json = json.dumps(sup_mapping, ensure_ascii=False)
    paths_json = json.dumps(path_labels, ensure_ascii=False)
    confirmed_json = json.dumps(sorted(confirmed), ensure_ascii=False)
    deleted_json = json.dumps(sorted(deleted or []), ensure_ascii=False)
    tpl = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>B2B Unified Category Tree (v2)</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
         margin: 0; background: #f6f7fb; color: #1f2937; }
  header { background: #1e3a8a; color: #fff; padding: 16px 24px; box-shadow: 0 2px 4px rgba(0,0,0,.1);
           display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap; }
  header h1 { margin: 0; font-size: 20px; font-weight: 600; }
  header .sub { opacity: .85; font-size: 13px; margin-top: 4px; }
  header .actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  header button { background: #fff; color: #1e3a8a; border: none; padding: 8px 14px;
                  border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; }
  header button:hover { background: #e0e7ff; }
  header button.primary { background: #10b981; color: #fff; }
  header button.primary:hover { background: #059669; }
  header button.warn { background: #f59e0b; color: #fff; }
  header button.warn:hover { background: #d97706; }
  header button:disabled { opacity: .5; cursor: not-allowed; }
  .edit-badge { background: #10b981; color: #fff; padding: 4px 10px; border-radius: 999px;
                font-size: 12px; font-weight: 600; display: none; }
  .edit-on .edit-badge { display: inline-block; }
  .edit-on .label { cursor: copy; }
  .wrap { max-width: 1500px; margin: 0 auto; padding: 24px;
          display: grid; grid-template-columns: 400px 1fr; gap: 24px; }
  @media (max-width: 960px) { .wrap { grid-template-columns: 1fr; } }
  .panel { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,.06); padding: 16px; }
  .stats { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
  .stat { background: #eef2ff; color: #3730a3; padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }
  .stat.warn { background: #fef3c7; color: #92400e; }
  input[type=search] { width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; margin-bottom: 12px; }
  input[type=search]:focus { outline: none; border-color: #1e3a8a; box-shadow: 0 0 0 3px rgba(30,58,138,.15); }
  .tree { max-height: 75vh; overflow-y: auto; padding-right: 8px; }
  .tree ul { list-style: none; padding-left: 18px; margin: 0; }
  .tree > ul { padding-left: 0; }
  .node { padding: 3px 0; user-select: none; line-height: 1.45; }
  .toggle { display: inline-block; width: 16px; text-align: center; cursor: pointer;
            color: #6b7280; font-size: 10px; margin-right: 2px;
            vertical-align: top; line-height: 1.55; }
  .toggle.leaf { cursor: default; color: transparent; }
  .label { cursor: pointer; padding: 2px 6px; border-radius: 4px; font-size: 13.5px;
           display: inline; word-break: break-word; overflow-wrap: anywhere;
           -webkit-box-decoration-break: clone; box-decoration-break: clone; }
  .label:hover { background: #eef2ff; }
  .label.selected { background: #1e3a8a; color: #fff; }
  .label.match { background: #fef08a; }
  .label.only-one { border-left: 3px solid #f59e0b; padding-left: 4px; }
  .count { color: #6b7280; font-size: 11.5px; margin-left: 4px; }
  .dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; margin-left: 4px; vertical-align: middle; }
  .dot.also { background: #2563eb; }
  .dot.elko { background: #16a34a; }
  .hidden { display: none; }
  .detail h2 { margin: 0 0 4px; font-size: 18px; }
  .detail .crumbs { color: #6b7280; font-size: 13px; margin-bottom: 16px; }
  .detail .code { color: #6b7280; font-size: 12px; font-family: monospace; margin-bottom: 16px; }
  .subs { margin-bottom: 24px; }
  .subs a { color: #1e3a8a; text-decoration: none; margin-right: 12px; font-size: 13px; }
  .subs a:hover { text-decoration: underline; }
  table { border-collapse: collapse; width: 100%; font-size: 13px; }
  th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }
  th { background: #f9fafb; font-weight: 600; }
  .supplier-tag { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600; }
  .supplier-tag.also_data { background: #dbeafe; color: #1e40af; }
  .supplier-tag.elko { background: #dcfce7; color: #166534; }
  .empty { color: #9ca3af; font-style: italic; padding: 16px 0; }
  .controls { margin-bottom: 8px; display: flex; gap: 8px; flex-wrap: wrap; }
  .controls button { background: #e5e7eb; border: none; padding: 5px 10px; border-radius: 4px;
                     font-size: 12px; cursor: pointer; color: #374151; }
  .controls button:hover { background: #d1d5db; }
  .legend { font-size: 12px; color: #6b7280; margin-bottom: 8px; }

  /* ---- Edit mode ---- */
  .edit-on tr.drag-row { cursor: grab; }
  .edit-on tr.drag-row:active { cursor: grabbing; }
  tr.drag-row.dragging { opacity: .4; }
  .label.drop-hover { outline: 2px dashed #10b981; outline-offset: 2px; background: #d1fae5 !important; }
  .row-actions { display: none; }
  .edit-on .row-actions { display: inline-flex; gap: 4px; }
  .row-actions button { background: none; border: 1px solid #d1d5db; padding: 2px 8px;
                        font-size: 11px; border-radius: 4px; cursor: pointer; color: #6b7280; }
  .row-actions button:hover { background: #fee2e2; border-color: #f87171; color: #b91c1c; }
  .pending { color: #d97706; font-weight: 600; }
  .saved { color: #10b981; font-weight: 600; }
  .help { background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; padding: 10px 14px;
          margin-bottom: 12px; font-size: 12.5px; color: #78350f; display: none; }
  .edit-on .help { display: block; }
  .node-del { display: none; background: #fee2e2; border: 1px solid #f87171; color: #b91c1c;
              font-size: 10.5px; padding: 1px 6px; border-radius: 4px; margin-left: 8px;
              cursor: pointer; font-weight: 600; line-height: 1.2; vertical-align: middle; }
  .edit-on .node-del.visible { display: inline-block; }
  .node-del:hover { background: #fecaca; border-color: #ef4444; }
  /* Up/Down reorder buttons (edit mode only) */
  .node-move { display: none; background: #eef2ff; border: 1px solid #c7d2fe; color: #4338ca;
               font-size: 11px; padding: 0 5px; border-radius: 3px; margin-left: 3px;
               cursor: pointer; font-weight: 700; line-height: 1.4; vertical-align: middle; }
  .edit-on .node-move { display: inline-block; }
  .node-move:hover { background: #c7d2fe; border-color: #6366f1; }
  .node-move:disabled { opacity: .3; cursor: not-allowed; }

  /* Confirmation checkbox */
  .node-chk { display: inline-block; width: 14px; height: 14px; margin-right: 4px;
              vertical-align: top; margin-top: 3px; cursor: pointer; accent-color: #10b981; }
  .label.confirmed { background: #ecfdf5; border-left: 3px solid #10b981; padding-left: 4px; }
  .label.confirmed:hover { background: #d1fae5; }
  /* Selected always wins over confirmed so white text stays readable. */
  .label.selected,
  .label.selected.confirmed,
  .label.selected.confirmed:hover { background: #1e3a8a; color: #fff; }
  .label.selected.confirmed { border-left-color: #10b981; }
  .confirm-badge { color: #059669; font-size: 10px; margin-left: 4px; vertical-align: middle; }
  /* Hide-confirmed filter */
  .hide-confirmed li.node.confirmed-node { display: none; }
</style>
</head>
<body>
<header>
  <div>
    <h1>B2B Unified Category Tree <span class="edit-badge" id="editBadge">EDIT MODE</span></h1>
    <div class="sub">also_data + elko mapped to unified leaves. Toggle edit mode to drag supplier categories between nodes, then hit Save to write the CSVs in place.</div>
  </div>
  <div class="actions">
    <span id="pendingCounter" style="color:#fde68a; font-size:12px;"></span>
    <button id="toggleEdit">Enable edit mode</button>
    <button id="resetBtn" class="warn" style="display:none;">Reset changes</button>
    <button id="saveBtn" class="primary">Save</button>
    <button id="downloadBtn">Download CSVs</button>
  </div>
</header>
<div class="wrap">
  <aside class="panel">
    <div class="stats" id="stats"></div>
    <div class="legend"><span class="dot also"></span> also_data <span class="dot elko"></span> elko &nbsp; | &nbsp; orange bar = only one supplier</div>
    <input type="search" id="q" placeholder="Search categories..." autocomplete="off">
    <div class="controls">
      <button id="expand-all">Expand all</button>
      <button id="collapse-all">Collapse all</button>
      <button id="show-roots">Show only roots</button>
      <button id="hide-confirmed-btn">Hide confirmed</button>
    </div>
    <div class="tree" id="tree"></div>
  </aside>
  <main class="panel detail" id="detail">
    <div class="help">
      <strong>Edit mode active.</strong>
      Drag any supplier row from the detail pane onto a category in the tree to <strong>move</strong> it there.
      Hold <kbd>Ctrl</kbd> while dropping to <strong>copy</strong> (add as cross-mapping) instead of moving.
      Use the <strong>&times;</strong> button to remove a mapping from the current category. When done, click <strong>Download CSVs</strong>.
    </div>
    <div class="empty">Click any category on the left to see supplier mappings.</div>
  </main>
</div>
<script>
const TREE_DATA = __TREE__;
const STATS = __STATS__;
const COV = __COV__;
const SOURCES = __SOURCES__;       // filename -> [[supplier, supplier_category], ...]
const PATHS = __PATHS__;           // code -> full breadcrumb label
let   SUPMAP = __SUPMAP__;         // "supplier||category" -> [code, ...]
const INITIAL_SUPMAP = JSON.parse(JSON.stringify(SUPMAP));
const INITIAL_TREE = JSON.parse(JSON.stringify(TREE_DATA));
let   MAP = {};                    // code -> [{supplier, category}, ...]  (derived)
let   editMode = false;
let   pendingChanges = 0;
const deletedCodes = new Set(__DELETED__);
const confirmedCodes = new Set(__CONFIRMED__);
const INITIAL_CONFIRMED = new Set(confirmedCodes);
// Server detection: if this page is served over http(s):// we can Save to disk.
const hasServer = location.protocol.startsWith('http');

function deriveMap() {
  MAP = {};
  for (const key of Object.keys(SUPMAP)) {
    const sep = key.indexOf("||");
    const supplier = key.slice(0, sep);
    const category = key.slice(sep + 2);
    for (const code of SUPMAP[key]) {
      (MAP[code] = MAP[code] || []).push({supplier, category, key});
    }
  }
}
deriveMap();

function updateStats() {
  const leafSups = {};
  for (const key of Object.keys(SUPMAP)) {
    const sup = key.slice(0, key.indexOf("||"));
    for (const c of SUPMAP[key]) (leafSups[c] = leafSups[c] || new Set()).add(sup);
  }
  let both=0, only_also=0, only_elko=0;
  for (const c in leafSups) {
    const s = leafSups[c];
    if (s.size >= 2) both++;
    else if (s.has("also_data")) only_also++;
    else only_elko++;
  }
  const rows = Object.values(MAP).reduce((a,v) => a+v.length, 0);
  // Total (non-deleted) categories in tree = live entries of nodeIdx, fall back to STATS.
  const total = nodeIdx.size || STATS.categories;
  const confirmed = [...confirmedCodes].filter(c => nodeIdx.has(c)).length;
  const pct = total ? Math.round(100 * confirmed / total) : 0;
  document.getElementById('stats').innerHTML =
    '<span class="stat">'+total+' categories</span>' +
    '<span class="stat" style="background:#d1fae5;color:#065f46;">\u2713 '+confirmed+' / '+total+' confirmed ('+pct+'%)</span>' +
    '<span class="stat">'+rows+' supplier mappings</span>' +
    '<span class="stat">'+both+' leaves covered by BOTH</span>' +
    '<span class="stat warn">'+only_also+' also-only</span>' +
    '<span class="stat warn">'+only_elko+' elko-only</span>';
}

const nodeIdx = new Map();
function hasDescendantMapping(node) {
  if ((MAP[node.code] || []).length) return true;
  for (const c of (node.children || [])) if (hasDescendantMapping(c)) return true;
  return false;
}
function collectSuppliers(node) {
  const set = new Set();
  for (const m of (MAP[node.code] || [])) set.add(m.supplier);
  for (const c of (node.children || [])) for (const s of collectSuppliers(c)) set.add(s);
  return set;
}

function refreshLabel(code) {
  const entry = nodeIdx.get(code);
  if (!entry) return;
  const node = entry.node;
  const sups = collectSuppliers(node);
  const mapped = (MAP[code] || []).length;
  // Re-render label contents (preserve the delete button element)
  entry.labelEl.innerHTML = '';
  entry.labelEl.appendChild(document.createTextNode(node.label));
  if (sups.size === 1 && hasDescendantMapping(node)) entry.labelEl.classList.add('only-one');
  else entry.labelEl.classList.remove('only-one');
  if (sups.has('also_data')) { const d=document.createElement('span'); d.className='dot also'; entry.labelEl.appendChild(d); }
  if (sups.has('elko'))      { const d=document.createElement('span'); d.className='dot elko'; entry.labelEl.appendChild(d); }
  if (mapped) { const c=document.createElement('span'); c.className='count'; c.textContent='('+mapped+')'; entry.labelEl.appendChild(c); }
  // Re-append persistent delete button (it was wiped by innerHTML reset)
  entry.labelEl.appendChild(entry.delBtn);
}
function refreshLabelsRecursively(code) {
  refreshLabel(code);
  // Walk up ancestors
  const entry = nodeIdx.get(code);
  if (entry) for (const a of entry.ancestors) refreshLabel(a.code);
}

function render(parentEl, nodes, ancestors) {
  const ul = document.createElement('ul');
  for (const node of nodes) {
    const li = document.createElement('li'); li.className = 'node'; li.dataset.code = node.code;
    if (confirmedCodes.has(node.code)) li.classList.add('confirmed-node');
    const hasCh = node.children && node.children.length > 0;
    const tog = document.createElement('span'); tog.className = 'toggle' + (hasCh ? '' : ' leaf');
    tog.textContent = hasCh ? '\u25B6' : '\u2022'; li.appendChild(tog);

    // Confirmation checkbox (always visible, independent of edit mode)
    const chk = document.createElement('input');
    chk.type = 'checkbox'; chk.className = 'node-chk';
    chk.title = 'Mark this category as reviewed & confirmed';
    chk.checked = confirmedCodes.has(node.code);
    chk.onclick = ev => { ev.stopPropagation(); toggleConfirmed(node.code, chk.checked); };
    li.appendChild(chk);

    const lbl = document.createElement('span'); lbl.className = 'label'; lbl.dataset.code = node.code;
    if (confirmedCodes.has(node.code)) lbl.classList.add('confirmed');
    lbl.textContent = node.label;
    // Drop target
    lbl.addEventListener('dragover', ev => { if (!editMode) return; ev.preventDefault(); lbl.classList.add('drop-hover'); ev.dataTransfer.dropEffect = ev.ctrlKey ? 'copy' : 'move'; });
    lbl.addEventListener('dragleave', () => lbl.classList.remove('drop-hover'));
    lbl.addEventListener('drop', ev => {
      if (!editMode) return;
      ev.preventDefault(); lbl.classList.remove('drop-hover');
      const data = ev.dataTransfer.getData('application/json');
      if (!data) return;
      const {key, fromCode} = JSON.parse(data);
      const targetCode = node.code;
      if (ev.ctrlKey) addMapping(key, targetCode);
      else moveMapping(key, fromCode, targetCode);
    });
    lbl.onclick = () => selectNode(node, ancestors);
    li.appendChild(lbl);
    const sups = collectSuppliers(node);
    if (sups.size === 1 && hasDescendantMapping(node)) lbl.classList.add('only-one');
    if (sups.has('also_data')) { const d=document.createElement('span'); d.className='dot also'; lbl.appendChild(d); }
    if (sups.has('elko'))      { const d=document.createElement('span'); d.className='dot elko'; lbl.appendChild(d); }
    const mapped = (MAP[node.code] || []).length;
    if (mapped) { const c=document.createElement('span'); c.className='count'; c.textContent='('+mapped+')'; lbl.appendChild(c); }
    // Delete button (only visible when node AND descendants are empty, in edit mode).
    const del = document.createElement('button'); del.className = 'node-del'; del.textContent = 'delete'; del.title = 'Delete this empty category';
    del.onclick = ev => { ev.stopPropagation(); deleteNode(node); };
    lbl.appendChild(del);
    // Up/Down reorder buttons (visible in edit mode)
    const upBtn = document.createElement('button'); upBtn.className = 'node-move'; upBtn.textContent = '\u25B2'; upBtn.title = 'Move up among siblings';
    upBtn.onclick = ev => { ev.stopPropagation(); moveSibling(node.code, -1); };
    const dnBtn = document.createElement('button'); dnBtn.className = 'node-move'; dnBtn.textContent = '\u25BC'; dnBtn.title = 'Move down among siblings';
    dnBtn.onclick = ev => { ev.stopPropagation(); moveSibling(node.code, +1); };
    lbl.appendChild(upBtn); lbl.appendChild(dnBtn);
    let childUl = null;
    if (hasCh) {
      childUl = render(li, node.children, [...ancestors, node]);
      childUl.classList.add('hidden');
      tog.onclick = () => { const h = childUl.classList.toggle('hidden'); tog.textContent = h ? '\u25B6' : '\u25BC'; };
    }
    nodeIdx.set(node.code, { node, labelEl: lbl, li, toggle: tog, childUl, ancestors: [...ancestors], delBtn: del, chkEl: chk, upBtn, dnBtn });
    ul.appendChild(li);
  }
  parentEl.appendChild(ul); return ul;
}

function toggleConfirmed(code, isChecked) {
  if (isChecked) confirmedCodes.add(code); else confirmedCodes.delete(code);
  const entry = nodeIdx.get(code);
  if (entry) {
    entry.labelEl.classList.toggle('confirmed', isChecked);
    entry.li.classList.toggle('confirmed-node', isChecked);
  }
  pendingChanges++;
  markPending();
  updateStats();
}

function updateDeletableBadges() {
  // A node is deletable if: has no direct mappings, has no descendants with mappings.
  nodeIdx.forEach((entry, code) => {
    const node = entry.node;
    const deletable = !hasDescendantMapping(node);
    entry.delBtn.classList.toggle('visible', deletable);
  });
}

function moveSibling(code, dir) {
  // dir: -1 = up, +1 = down. Reorders `code` among its siblings.
  const entry = nodeIdx.get(code);
  if (!entry) return;
  const parentNode = entry.ancestors.length > 0
    ? nodeIdx.get(entry.ancestors[entry.ancestors.length - 1].code).node
    : null;
  const siblings = parentNode ? parentNode.children : TREE_DATA.tree;
  const idx = siblings.findIndex(c => c.code === code);
  const newIdx = idx + dir;
  if (idx < 0 || newIdx < 0 || newIdx >= siblings.length) return;
  const [moved] = siblings.splice(idx, 1);
  siblings.splice(newIdx, 0, moved);
  // Redraw this subtree: re-insert <li> elements in new order.
  const parentLi = parentNode ? nodeIdx.get(parentNode.code).li : null;
  const ul = parentLi ? parentLi.querySelector(':scope > ul') : document.querySelector('#tree > ul');
  if (ul) {
    for (const child of siblings) {
      const childEntry = nodeIdx.get(child.code);
      if (childEntry) ul.appendChild(childEntry.li);  // appendChild moves existing nodes
    }
  }
  pendingChanges++;
  markPending();
}

function deleteNode(node) {
  if ((MAP[node.code] || []).length > 0 || hasDescendantMapping(node)) {
    alert('Cannot delete: category (or its descendants) still has supplier mappings.');
    return;
  }
  if (!confirm('Delete category "' + node.label + '"? This will remove it from the tree.')) return;
  const entry = nodeIdx.get(node.code);
  if (!entry) return;
  // Remove from parent's children array.
  const parentNode = entry.ancestors.length > 0
      ? nodeIdx.get(entry.ancestors[entry.ancestors.length - 1].code).node
      : null;
  if (parentNode) {
    parentNode.children = parentNode.children.filter(c => c.code !== node.code);
  } else {
    TREE_DATA.tree = TREE_DATA.tree.filter(c => c.code !== node.code);
  }
  // Remove descendants from nodeIdx.
  function removeFromIdx(n) {
    nodeIdx.delete(n.code);
    (n.children || []).forEach(removeFromIdx);
  }
  removeFromIdx(node);
  entry.li.remove();
  deletedCodes.add(node.code);
  pendingChanges++;
  markPending();
  // Refresh parent label so it re-checks descendant count.
  if (parentNode) refreshLabelsRecursively(parentNode.code);
  updateDeletableBadges();
}

let selected = null;
let currentNode = null, currentAncestors = null;
function selectNode(node, ancestors) {
  if (selected) selected.classList.remove('selected');
  const entry = nodeIdx.get(node.code); entry.labelEl.classList.add('selected'); selected = entry.labelEl;
  for (const a of ancestors) { const e = nodeIdx.get(a.code);
    if (e && e.childUl && e.childUl.classList.contains('hidden')) { e.childUl.classList.remove('hidden'); e.toggle.textContent = '\u25BC'; } }
  currentNode = node; currentAncestors = ancestors;
  showDetail(node, ancestors);
}

function escapeHtml(s) { return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

function showDetail(node, ancestors) {
  const d = document.getElementById('detail');
  const breadcrumbs = [...ancestors, node].map(a => a.label).join(' \u203A ');
  const mappings = MAP[node.code] || [];
  const subs = (node.children || []).map(c => '<a href="#" data-code="'+c.code+'">'+escapeHtml(c.label)+'</a>').join('');
  const rowsHtml = mappings.map((m, i) =>
    '<tr class="drag-row" draggable="true" data-key="'+escapeHtml(m.key)+'" data-idx="'+i+'">' +
      '<td><span class="supplier-tag '+m.supplier+'">'+m.supplier+'</span></td>' +
      '<td>'+escapeHtml(m.category)+'</td>' +
      '<td><span class="row-actions"><button class="rm" title="Remove from this category">&times;</button></span></td>' +
    '</tr>').join('');
  const helpHtml = document.querySelector('.help') ? document.querySelector('.help').outerHTML : '';
  d.innerHTML = helpHtml +
    '<h2>'+escapeHtml(node.label)+'</h2>' +
    '<div class="crumbs">'+escapeHtml(breadcrumbs)+'</div>' +
    '<div class="code">code: '+node.code+'</div>' +
    (subs ? '<div class="subs"><strong>Subcategories:</strong> '+subs+'</div>' : '') +
    (mappings.length
       ? '<table><thead><tr><th>Supplier</th><th>Supplier category</th><th></th></tr></thead><tbody>'+rowsHtml+'</tbody></table>'
       : '<div class="empty">No direct supplier mappings at this level (see subcategories).</div>');

  // Subcategory links
  d.querySelectorAll('.subs a').forEach(a => { a.onclick = e => {
    e.preventDefault(); const code = a.getAttribute('data-code'); const entry = nodeIdx.get(code);
    if (entry) selectNode(entry.node, entry.ancestors); }; });

  // Drag handlers on rows
  d.querySelectorAll('tr.drag-row').forEach(tr => {
    tr.addEventListener('dragstart', ev => {
      if (!editMode) { ev.preventDefault(); return; }
      const key = tr.dataset.key;
      ev.dataTransfer.setData('application/json', JSON.stringify({key, fromCode: node.code}));
      ev.dataTransfer.effectAllowed = 'copyMove';
      tr.classList.add('dragging');
    });
    tr.addEventListener('dragend', () => tr.classList.remove('dragging'));
    tr.querySelector('.rm').onclick = ev => {
      ev.stopPropagation();
      const key = tr.dataset.key;
      removeMapping(key, node.code);
    };
  });
}

function moveMapping(key, fromCode, toCode) {
  const codes = SUPMAP[key] || [];
  if (codes.includes(toCode) && codes.includes(fromCode)) {
    // Already in target AND source — just remove from source (move dedup)
    SUPMAP[key] = codes.filter(c => c !== fromCode);
  } else {
    SUPMAP[key] = codes.filter(c => c !== fromCode).concat(codes.includes(toCode) ? [] : [toCode]);
  }
  onMappingChanged([fromCode, toCode]);
}
function addMapping(key, toCode) {
  const codes = SUPMAP[key] || [];
  if (!codes.includes(toCode)) SUPMAP[key] = codes.concat([toCode]);
  onMappingChanged([toCode]);
}
function removeMapping(key, fromCode) {
  SUPMAP[key] = (SUPMAP[key] || []).filter(c => c !== fromCode);
  onMappingChanged([fromCode]);
}
function markPending() {
  document.getElementById('pendingCounter').innerHTML = pendingChanges > 0 ? '<span class="pending">'+pendingChanges+' change'+(pendingChanges===1?'':'s')+' pending</span>' : '';
  document.getElementById('resetBtn').style.display = pendingChanges > 0 ? 'inline-block' : 'none';
}
function onMappingChanged(affectedCodes) {
  pendingChanges++;
  markPending();
  deriveMap();
  updateStats();
  for (const c of affectedCodes) refreshLabelsRecursively(c);
  if (currentNode) showDetail(currentNode, currentAncestors);
  updateDeletableBadges();
}

render(document.getElementById('tree'), TREE_DATA.tree, []);
updateStats();
updateDeletableBadges();

// Toggle Save button label depending on whether we have a server
const saveBtn = document.getElementById('saveBtn');
if (!hasServer) {
  saveBtn.title = 'Run "python build_categories.py" and open the URL it prints (http://127.0.0.1:8765/category_tree.html) to save in place.';
}

const q = document.getElementById('q');
q.oninput = () => {
  const t = q.value.trim().toLowerCase();
  nodeIdx.forEach(e => { e.labelEl.classList.remove('match'); e.li.classList.remove('hidden'); });
  if (!t) { nodeIdx.forEach(e => { if (e.childUl) { e.childUl.classList.add('hidden'); e.toggle.textContent='\u25B6'; }}); return; }
  const m = new Set();
  nodeIdx.forEach((e, c) => { if (e.node.label.toLowerCase().includes(t) || c.includes(t)) { m.add(c); e.labelEl.classList.add('match'); for (const a of e.ancestors) m.add(a.code); } });
  nodeIdx.forEach((e, c) => { if (!m.has(c)) e.li.classList.add('hidden'); else if (e.childUl) { e.childUl.classList.remove('hidden'); e.toggle.textContent='\u25BC'; } });
};
document.getElementById('expand-all').onclick = () => nodeIdx.forEach(e => { if (e.childUl) { e.childUl.classList.remove('hidden'); e.toggle.textContent='\u25BC'; } });
document.getElementById('collapse-all').onclick = () => nodeIdx.forEach(e => { if (e.childUl) { e.childUl.classList.add('hidden'); e.toggle.textContent='\u25B6'; } });
document.getElementById('show-roots').onclick = () => nodeIdx.forEach(e => { if (e.childUl) { e.childUl.classList.add('hidden'); e.toggle.textContent='\u25B6'; } });
const hideConfBtn = document.getElementById('hide-confirmed-btn');
hideConfBtn.onclick = () => {
  const tree = document.getElementById('tree');
  const hiding = !tree.classList.contains('hide-confirmed');
  tree.classList.toggle('hide-confirmed', hiding);
  hideConfBtn.textContent = hiding ? 'Show confirmed' : 'Hide confirmed';
};

// Edit mode toggle
const toggleBtn = document.getElementById('toggleEdit');
toggleBtn.onclick = () => {
  editMode = !editMode;
  document.body.classList.toggle('edit-on', editMode);
  toggleBtn.textContent = editMode ? 'Exit edit mode' : 'Enable edit mode';
  updateDeletableBadges();
  if (currentNode) showDetail(currentNode, currentAncestors);
};

// Reset
document.getElementById('resetBtn').onclick = () => {
  if (!confirm('Discard all pending changes?')) return;
  SUPMAP = JSON.parse(JSON.stringify(INITIAL_SUPMAP));
  // Restore confirmations
  confirmedCodes.clear();
  INITIAL_CONFIRMED.forEach(c => confirmedCodes.add(c));
  // Restore tree (deleted nodes come back).
  if (deletedCodes.size > 0) {
    deletedCodes.clear();
    Object.assign(TREE_DATA, JSON.parse(JSON.stringify(INITIAL_TREE)));
    document.getElementById('tree').innerHTML = '';
    nodeIdx.clear();
    render(document.getElementById('tree'), TREE_DATA.tree, []);
  }
  // Re-sync checkboxes & classes for nodes that still exist
  nodeIdx.forEach((entry, code) => {
    const on = confirmedCodes.has(code);
    entry.chkEl.checked = on;
    entry.labelEl.classList.toggle('confirmed', on);
    entry.li.classList.toggle('confirmed-node', on);
  });
  pendingChanges = 0;
  document.getElementById('pendingCounter').innerHTML = '';
  document.getElementById('resetBtn').style.display = 'none';
  deriveMap();
  updateStats();
  nodeIdx.forEach((_, c) => refreshLabel(c));
  updateDeletableBadges();
  if (currentNode) {
    // currentNode may have been deleted; try to keep selection if node still exists
    if (nodeIdx.has(currentNode.code)) showDetail(currentNode, currentAncestors);
    else document.getElementById('detail').innerHTML = '<div class="empty">Click any category on the left to see supplier mappings.</div>';
  }
};

// CSV download — regenerate each file preserving original input order & multi-mapping
function csvEscape(s) {
  return '"' + String(s).replace(/"/g, '""') + '"';
}
function buildCsv(filename) {
  const rows = SOURCES[filename] || [];
  const out = ['"supplier_name","supplier_category","client_category_code","client_category_label"'];
  for (const [supplier, category] of rows) {
    const key = supplier + '||' + category;
    const codes = SUPMAP[key] || [];
    if (codes.length === 0) {
      out.push([supplier, category, '', ''].map(csvEscape).join(','));
    } else {
      for (const code of codes) {
        out.push([supplier, category, code, PATHS[code] || ''].map(csvEscape).join(','));
      }
    }
  }
  return out.join('\r\n') + '\r\n';
}
function downloadFile(name, content) {
  const blob = new Blob([content], {type: 'text/csv;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = name;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
document.getElementById('downloadBtn').onclick = () => {
  for (const fn of Object.keys(SOURCES)) downloadFile(fn, buildCsv(fn));
};

// Compute per-supplier-category override delta (only categories whose codes
// differ from the initial state). Keyed by supplier_category (no supplier prefix)
// so the Python script can apply it against its MAPPING dict.
function computeOverrides() {
  const out = {};
  const byCat = {};       // category -> final code list (union across files, but same supplier)
  const initByCat = {};
  for (const key of Object.keys(SUPMAP)) {
    const cat = key.slice(key.indexOf('||') + 2);
    byCat[cat] = SUPMAP[key].slice();
  }
  for (const key of Object.keys(INITIAL_SUPMAP)) {
    const cat = key.slice(key.indexOf('||') + 2);
    initByCat[cat] = INITIAL_SUPMAP[key].slice();
  }
  for (const cat of Object.keys(byCat)) {
    const a = byCat[cat].slice().sort();
    const b = (initByCat[cat] || []).slice().sort();
    if (a.length !== b.length || a.some((v, i) => v !== b[i])) {
      out[cat] = byCat[cat];
    }
  }
  return out;
}

// Walk the current TREE_DATA and emit a { parent_code | "__root__": [child_code, ...] } map.
function computeOrder() {
  const order = {};
  function walk(nodes, parentCode) {
    order[parentCode] = nodes.map(n => n.code);
    for (const n of nodes) if (n.children && n.children.length) walk(n.children, n.code);
  }
  walk(TREE_DATA.tree, '__root__');
  return order;
}

// Save — POSTs to local server if available, else falls back to download.
async function saveToDisk() {
  const csvPayload = {};
  for (const fn of Object.keys(SOURCES)) csvPayload[fn] = buildCsv(fn);
  const payload = {
    csv: csvPayload,
    deleted: Array.from(deletedCodes),
    overrides: computeOverrides(),
    confirmed: Array.from(confirmedCodes),
    order: computeOrder(),
  };
  const pc = document.getElementById('pendingCounter');
  if (!hasServer) {
    pc.innerHTML = '<span style="color:#fca5a5;">Save needs the local server. Run <code>python build_categories.py</code> and open the page it prints (http://127.0.0.1:8765/category_tree.html). Use “Download CSVs” for a one-off export.</span>';
    return;
  }
  pc.innerHTML = '<span style="color:#fde68a;">Saving…</span>';
  try {
    const r = await fetch('/save', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    if (!r.ok) throw new Error(r.status + ' ' + r.statusText);
    const result = await r.json();
    pendingChanges = 0;
    pc.innerHTML = '<span class="saved">\u2713 Saved ' + (result.files || []).length + ' file(s), ' +
                   (result.overrides || 0) + ' move(s), ' +
                   (result.deleted || 0) + ' deletion(s), ' +
                   (result.confirmed || 0) + ' confirmed</span>';
    document.getElementById('resetBtn').style.display = 'none';
    setTimeout(() => { if (pendingChanges === 0) pc.innerHTML = ''; }, 4000);
  } catch (e) {
    pc.innerHTML = '<span style="color:#fca5a5;">Save failed: ' + e.message + '</span>';
  }
}
document.getElementById('saveBtn').onclick = saveToDisk;
</script>
</body></html>
"""
    return (tpl.replace("__TREE__", tree_json)
               .replace("__MAP__", map_json)
               .replace("__STATS__", stats_json)
               .replace("__COV__", cov_json)
               .replace("__SOURCES__", sources_json)
               .replace("__SUPMAP__", supmap_json)
               .replace("__PATHS__", paths_json)
               .replace("__CONFIRMED__", confirmed_json)
               .replace("__DELETED__", deleted_json))


def main():
    all_rows, all_unmapped = [], []
    per_file = []
    for fn in IN_FILES:
        rows, un = process_file(fn)
        all_rows.extend(rows); all_unmapped.extend(un)
        per_file.append((fn, len(rows), len(un)))

    seen = set(); dedup = []
    for r in all_rows:
        key = tuple(r)
        if key in seen: continue
        seen.add(key); dedup.append(r)

    map_idx = build_map_idx(dedup)
    only_also, only_elko, both = coverage_diagnostic(dedup)
    coverage = {"only_also": only_also, "only_elko": only_elko, "both": both}

    stats = {"categories": len(TREE),
             "supplier_rows": sum(len(v) for v in map_idx.values()),
             "suppliers": len({r[0] for r in dedup})}

    # Build per-file source rows so the HTML can regenerate CSVs after edits.
    sources = {}
    for fn in IN_FILES:
        file_rows = []
        with (IN_DIR / fn).open("r", encoding="utf-8-sig", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                file_rows.append([row["supplier_name"], row["supplier_category"]])
        sources[fn] = file_rows

    # Build editable supplier→codes mapping (keyed "supplier||category").
    sup_mapping = {}
    for file_rows in sources.values():
        for supplier, cat in file_rows:
            key = f"{supplier}||{cat}"
            if key in sup_mapping:
                continue
            codes = MAPPING.get(cat, [])
            seen = set(); norm = []
            for c in codes:
                c = normalise(c)
                if c in seen: continue
                seen.add(c); norm.append(c)
            code_set = set(norm)
            final = [c for c in norm if not any(o != c and o.startswith(c + "/") for o in code_set)]
            sup_mapping[key] = final

    # Precomputed breadcrumb labels for every code (used by CSV export).
    path_labels = {code: path_label(code) for code in TREE}

    # Cache render context so the server's POST /save handler can re-render the
    # HTML after persisting edits (otherwise the next page reload serves a stale
    # file whose __CONFIRMED__ / tree state predates the save).
    global _RENDER_CTX
    _RENDER_CTX = {
        "tree_json": build_tree_json(),
        "map_idx": map_idx,
        "stats": stats,
        "coverage": coverage,
        "sources": sources,
        "sup_mapping": sup_mapping,
        "path_labels": path_labels,
    }

    html = render_html(_RENDER_CTX["tree_json"], map_idx, stats, coverage, sources, sup_mapping, path_labels, CONFIRMED_CODES, DELETED_CODES)
    (OUT_DIR / "category_tree.html").write_text(html, encoding="utf-8")

    print("=== v2 DONE ===")
    for fn, nrows, nun in per_file:
        print(f"  {fn}: {nrows} rows, {nun} unmapped")
    print(f"  Unique unmapped: {len(set(all_unmapped))}")
    for u in sorted(set(all_unmapped)): print("    -", u)
    print(f"  Tree nodes: {len(TREE)}  |  roots: {sum(1 for _,(_,p) in TREE.items() if p is None)}")
    print(f"  Leaves covered by BOTH: {len(both)}")
    print(f"  also-only leaves: {len(only_also)}")
    print(f"  elko-only leaves: {len(only_elko)}")
    print(f"\n  also-only leaves (review whether elko has a match):")
    for c in only_also: print(f"    * {c}  —  {path_label(c)}")
    print(f"\n  elko-only leaves (review whether also has a match):")
    for c in only_elko: print(f"    * {c}  —  {path_label(c)}")


def serve(port: int = 8765):
    """Local HTTP server that serves the HTML tree editor and persists edits.

    POST /save accepts JSON { csv: {filename: content}, deleted: [code, ...] }
    and writes the CSV files + tree_state.json into OUT_DIR.
    """
    import http.server
    import socketserver
    import webbrowser

    out_dir_str = str(OUT_DIR)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=out_dir_str, **kw)

        def log_message(self, fmt, *args):
            # Less chatty than default.
            sys.stderr.write("[server] " + (fmt % args) + "\n")

        def do_POST(self):
            if self.path != "/save":
                self.send_error(404); return
            length = int(self.headers.get("Content-Length") or 0)
            try:
                data = json.loads(self.rfile.read(length).decode("utf-8"))
            except Exception as e:
                self.send_error(400, f"Bad JSON: {e}"); return
            try:
                # Save CSV files
                for fn, content in (data.get("csv") or {}).items():
                    safe = Path(fn).name  # prevent traversal
                    (OUT_DIR / safe).open("w", encoding="utf-8", newline="").write(content)
                # Save tree state (deletions, overrides, confirmed, order all persist)
                # Safety: drop deleted codes that no longer exist in the current
                # TREE (stale deletions from old server sessions would silently
                # remove nodes that the Python script never defined).
                deleted = sorted(
                    c for c in set(data.get("deleted") or []) if c in TREE
                )
                # Safety: drop overrides whose target codes are all absent from
                # TREE — they are stale drags from an old session.
                raw_overrides = data.get("overrides") or {}
                overrides = {
                    cat: codes
                    for cat, codes in raw_overrides.items()
                    if any(normalise(c) in TREE for c in codes)
                }
                confirmed = sorted(set(data.get("confirmed") or []))
                order = data.get("order") or {}
                STATE_FILE.write_text(
                    json.dumps({"deleted": deleted, "overrides": overrides,
                                "confirmed": confirmed, "order": order},
                               indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                # Refresh in-memory state and re-render the HTML so the next
                # reload reflects what the user just confirmed/moved/deleted.
                global CONFIRMED_CODES, DELETED_CODES, OVERRIDES, ORDER
                CONFIRMED_CODES = set(confirmed)
                DELETED_CODES = set(deleted)
                OVERRIDES = dict(overrides)
                ORDER = dict(order)
                try:
                    if _RENDER_CTX:
                        # Rebuild tree JSON so the new ORDER is reflected in the HTML.
                        _RENDER_CTX["tree_json"] = build_tree_json()
                        html = render_html(
                            _RENDER_CTX["tree_json"],
                            _RENDER_CTX["map_idx"],
                            _RENDER_CTX["stats"],
                            _RENDER_CTX["coverage"],
                            _RENDER_CTX["sources"],
                            _RENDER_CTX["sup_mapping"],
                            _RENDER_CTX["path_labels"],
                            CONFIRMED_CODES,
                            DELETED_CODES,
                        )
                        (OUT_DIR / "category_tree.html").write_text(html, encoding="utf-8")
                except Exception as _re:
                    sys.stderr.write(f"[server] re-render failed: {_re}\n")
                body = json.dumps({
                    "ok": True,
                    "files": list((data.get("csv") or {}).keys()),
                    "deleted": len(deleted),
                    "overrides": len(overrides),
                    "confirmed": len(confirmed),
                    "order": len(order),
                }).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_error(500, f"Save failed: {e}")

    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        url = f"http://127.0.0.1:{port}/category_tree.html"
        print(f"Serving {out_dir_str} at {url}")
        print("Save button in the HTML will now write back to this directory.")
        print("Press Ctrl+C to stop.")
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutdown.")


if __name__ == "__main__":
    # Default: build + start local server so the HTML "Save" button writes
    # directly back into the CSVs and tree_state.json. Pass --no-serve to
    # build only (just regenerate HTML + CSVs and exit).
    main()
    if "--no-serve" not in sys.argv:
        serve()
