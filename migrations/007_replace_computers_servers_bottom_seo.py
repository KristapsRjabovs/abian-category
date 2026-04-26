"""
Replace the bottom_seo_en for computers-servers with content that does a
proper parent-category job: device-class selection, fleet planning,
lifecycle, procurement and TCO. The first version overlapped too much
with the per-child SEO descriptions (notebooks, servers, POS), which
hurts SEO and reads as duplicate content.

Safe-update: only overwrites if the current value matches what migration
006 wrote (the seed text). If a human has edited the field through the
UI, this migration leaves their version alone.
"""

CODE = "computers-servers"

# First sentence of the seed written by migration 006. If it matches, we
# know the field still holds the auto-generated version and is safe to
# replace. Any UI edit would change this and trip the guard.
SEED_FINGERPRINT = "Computers and servers are the core hardware that powers every part of a modern business"

CONTENT_EN = """\
<h2>Computers &amp; Servers</h2>
<p>Buying business computing hardware rarely starts with one device. It starts with a question: which device class fits each role, how do those devices fit together, and how often do they need replacing? This top-level category is where that planning happens. Underneath sit the actual product subcategories: Notebooks, Notebook Accessories, Desktops &amp; Workstations, Servers and Point-of-Sale Equipment, each with its own buyer guide.</p>
<p>A notebook covers individual mobility. A desktop covers fixed-position productivity. A server covers shared services for everyone at once. A POS terminal covers the checkout floor. Knowing which to use where, and which to combine, is the difference between a coherent IT estate and a tangled inventory of single-purpose purchases.</p>
<h2>When to use which device class</h2>
<h3>Match the device to the role, not to the person</h3>
<p>A finance lead working in spreadsheets all day usually needs a desktop with two monitors, even if they would prefer a laptop. A salesperson on the road needs a lightweight notebook with long battery life, even if the company standard is a tower. A developer compiling large projects needs workstation-class memory and CPU, regardless of whether they sit at a desk all week.</p>
<p>Practical role-to-device mapping:</p>
<ul>
  <li>Office knowledge worker (documents, email, video calls): business notebook, or mid-range desktop with monitor</li>
  <li>Mobile salesperson, consultant or field engineer: business notebook with a docking station at the home base</li>
  <li>Reception, classroom, kiosk, exhibition: all-in-one PC or mini PC behind a monitor</li>
  <li>Developer, engineer, video editor, 3D designer: workstation desktop or workstation notebook</li>
  <li>Retail cashier, hospitality till, warehouse stock-take: POS terminal, mobile POS or rugged PDA</li>
  <li>Server administrator, infrastructure team: rack or tower server with remote management</li>
</ul>
<h3>Match the device to the workspace</h3>
<p>The same person often needs different hardware in different settings. A field engineer might need a rugged notebook on site and a docking station with monitors at the depot. A retail manager might need a back-office desktop and a mobile POS unit on the shop floor. The right answer is usually a small kit, not a single device.</p>
<p>Workspace-to-device guidance:</p>
<ul>
  <li>Permanent office desk, single user: desktop tower, all-in-one PC or business notebook with dock</li>
  <li>Hot desk or shared workspace: business notebook plus a docking station per desk</li>
  <li>Reception, classroom, exhibition counter: all-in-one PC or mini PC plus monitor</li>
  <li>Field service, construction, agriculture: rugged notebook or rugged tablet</li>
  <li>Warehouse, logistics, stock control: mobile POS, handheld PDA or rugged tablet</li>
  <li>Server room or data centre: rack server in a 19-inch cabinet</li>
  <li>Small office without a server room: tower server on the floor</li>
</ul>
<h2>Typical setups by business size and sector</h2>
<h3>Sole trader or small office, 1 to 10 users</h3>
<p>A single tower server is usually unnecessary at this scale. Shared workloads run comfortably in cloud services or on a network-attached storage (NAS) box, so the focus is end-user devices: business notebooks for mobile staff, desktops for fixed roles, all-in-ones for reception, and a POS terminal if there is a checkout. Standardising on one notebook and one desktop model keeps spare parts, imaging and support simple.</p>
<h3>Mid-sized office, 10 to 100 users</h3>
<p>This is the size where mixed estates start to appear. Notebooks for staff who travel, desktops for staff who do not, workstations for design and engineering teams, and a small tower or rack server for shared file storage and backups. A common docking-station standard becomes important so any laptop can plug into any desk without driver chaos.</p>
<h3>Multi-site retail or hospitality</h3>
<p>Every store needs identical POS terminals, receipt printers and barcode scanners so staff can move between locations without retraining. The back office benefits from a shared rack server (or its cloud equivalent) for inventory, ordering and reporting. Mobile POS units cover seasonal counters, pop-up events and queue-busting at peak times.</p>
<h3>Workshop, manufacturing or industrial site</h3>
<p>Rugged notebooks or rugged tablets in the production area, standard desktops in the back office, and often a tower server in a ventilated cabinet for production data and quality control. Spare parts (power supplies, drives, batteries, ruggedised charging cables) are typically bought up front because production downtime costs more than the spare itself.</p>
<h3>Education</h3>
<p>A mix of notebooks for teaching staff, desktops or all-in-one PCs in student labs, charging trolleys for tablet fleets, and frequently a small server for shared file storage and authentication. Refurbished business notebooks often fit education budgets without compromising build quality, and the resulting savings buy more devices per classroom.</p>
<h3>IT services or consultancy</h3>
<p>Engineers usually run workstation-class notebooks supplemented by lab servers (rack or tower) for testing customer environments before deploying. POS equipment is rarely needed unless the consultancy resells it. Fleet management, remote-access tools and warranty depth matter more than peak performance for individual machines.</p>
<h2>Lifecycle, refresh and total cost of ownership</h2>
<h3>Different devices age at different rates</h3>
<p>Notebooks live the hardest life: daily transport, battery degradation, screen impacts and connector wear. Most business fleets refresh notebooks every 3 to 4 years. Desktops and all-in-ones, sitting still on a desk, comfortably last 5 to 6. Servers are typically refreshed on a 4 to 5 year cycle driven by warranty expiry, not raw performance. POS terminals run reliably for 6 to 8 years if the till software supports the operating system that long.</p>
<p>Plan refresh cycles per device class:</p>
<ul>
  <li>Notebooks: 3 to 4 years (battery life and physical wear lead the decision)</li>
  <li>Desktops and all-in-ones: 5 to 6 years (performance leads)</li>
  <li>Workstations: 4 to 5 years (driven by software certification, not hardware)</li>
  <li>Servers: 4 to 5 years (warranty and support contract end is the real trigger)</li>
  <li>POS terminals: 6 to 8 years (software compatibility leads)</li>
</ul>
<h3>Spare parts vs whole-device replacement</h3>
<p>For notebooks, replacing the whole device is usually faster and cheaper than chasing spare parts, although replacement batteries, chargers and docks remain routine. For desktops and workstations, individual upgrades extend useful life: more memory, larger SSD (Solid State Drive), sometimes a new graphics card. Servers are designed for component-level repair: hot-swap PSUs (Power Supply Units), hot-swap drives, BMC-managed parts. POS gear sits in the middle: receipt printers and cash drawers usually outlive the terminal they attach to.</p>
<h3>Warranty terms worth checking before you buy</h3>
<p>For end-user devices, a 3-year next-business-day on-site warranty is the practical office standard. For servers, a 5-year warranty with 24x7 4-hour response is more typical and usually mandatory for production workloads. POS hardware often ships with 1 to 3 years standard and an extended option for the full till estate. Account for this gap in the per-device cost when comparing across categories.</p>
<h2>Standardisation and fleet management</h2>
<h3>One brand line, or several?</h3>
<p>Standardising on a single notebook line and a single desktop line makes spare parts, warranty handling, imaging and helpdesk support cheaper and faster. Mixing brands feels cheaper at the per-unit level but usually costs more once tickets, driver mismatches and image sprawl are counted. The break-even point is roughly 10 devices: above that, picking one line per category pays back quickly.</p>
<h3>Manageability features that pay back at scale</h3>
<p>Business notebooks and desktops support remote-management features designed for IT departments: Intel vPro / AMT, AMD equivalents, TPM (Trusted Platform Module) chips for disk encryption, and out-of-band BIOS update tools. These are typically skipped on consumer-grade devices, which is one practical reason business hardware is worth the price gap for fleets above 10 devices.</p>
<h3>One docking-station standard</h3>
<p>If staff move between desks or work from home with a single notebook, picking one docking-station standard (USB-C Power Delivery, Thunderbolt 4 or a single proprietary OEM dock family) lets any laptop plug in anywhere. Mixing dock types fragments the office into incompatible islands within a year or two and adds friction to every desk move.</p>
<h2>Procurement essentials</h2>
<h3>Lead times by device class</h3>
<p>Stock business notebook and desktop configurations usually ship within a few days. Configure-to-order workstations, servers with non-default storage and POS terminals with custom imaging can take 2 to 6 weeks. Plan accordingly when refreshing a whole fleet rather than a single device, particularly across a fiscal year-end.</p>
<h3>Configuration tiers</h3>
<p>Most business hardware ships in three tiers: entry, mid and high. Entry covers basic productivity. Mid is the volume sweet spot for most office staff. High is for power users, workstation buyers and infrastructure roles. Picking one mid-tier configuration and ordering it in volume is usually cheaper per device and faster to deploy than mixing tiers across roles.</p>
<h3>Long-term SKU availability</h3>
<p>Business-grade hardware is typically sold for 12 to 24 months on a single SKU before being replaced with a successor. Consumer hardware refreshes much more often. For fleet purchases, business SKUs make it easier to buy more units 12 months later without re-imaging or re-testing the entire setup.</p>
<h2>Frequently asked questions</h2>
<h3>Should every employee get the same device?</h3>
<p>No. Standardise within roles, not across the company. All office staff on the same business notebook makes sense; forcing the engineering or design team onto the same device usually slows them down. A small portfolio of three or four approved configurations is the right middle ground for most companies.</p>
<h3>Do small businesses need their own server?</h3>
<p>Often no. Cloud services (file storage, email, line-of-business apps) and a good NAS box cover most needs up to roughly 20 users. A dedicated server starts to make sense when there are workloads that must stay on-premises for compliance, cost or latency reasons, or when shared file storage outgrows what a NAS can serve.</p>
<h3>Can a notebook replace a desktop for daily office work?</h3>
<p>Yes for most office staff, paired with a docking station, external monitor, keyboard and mouse. The notebook then doubles as a portable device when needed. The trade-off is a higher cost per machine and a shorter useful life than an equivalent desktop, plus battery wear that the desktop never sees.</p>
<h3>When are rugged notebooks worth the extra cost?</h3>
<p>When the device routinely leaves a normal office. Field service, construction, manufacturing, logistics and outdoor work destroy standard laptops far faster than rugged units. The price premium typically pays back through fewer warranty claims, fewer replacements and less downtime over the device lifecycle.</p>
<h3>How do POS terminals fit alongside the rest of the IT estate?</h3>
<p>Treat them as separate from office IT. POS hardware runs purpose-built till software, has its own warranty and refresh cycle and rarely belongs on the same management platform as office laptops. The shared touchpoints are usually the network and the integration with back-office systems for stock and reporting.</p>
<h3>What is the smallest IT setup that justifies a server?</h3>
<p>Around 10 to 20 active users, or earlier if the workload involves shared databases, line-of-business applications, large file shares or compliance constraints that prevent cloud storage. Below that threshold, a NAS plus cloud services usually works out simpler, cheaper and easier to maintain.</p>
<h3>How does refurbished hardware fit into a business plan?</h3>
<p>Refurbished business notebooks and desktops are a sensible option for cost-conscious refresh cycles, secondary workstations for occasional users, remote workers and education. The key checks are warranty, condition grade, battery health, processor generation and storage size. A well-graded business notebook one generation behind often outperforms a brand-new entry consumer model at the same price.</p>
<h3>How long should a hardware procurement plan look ahead?</h3>
<p>Three years is the practical horizon for end-user devices, matching most business warranty terms. Five years is the right horizon for servers and infrastructure, matching service contracts and tax-depreciation cycles. POS estates often plan over 5 to 8 years because the underlying till software refreshes more slowly than office IT.</p>
"""


def apply(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT bottom_seo_en FROM tree_nodes WHERE code = %s", (CODE,))
        row = cur.fetchone()
        if not row:
            print(f"  no tree_node {CODE!r}, skipping")
            return
        current = row[0] or ""
        # Only overwrite if the current value is the auto-seed from migration 006
        # (or empty). A human edit through the UI would not start with the
        # seed fingerprint.
        if current and SEED_FINGERPRINT not in current:
            print(f"  bottom_seo_en on {CODE!r} looks user-edited, leaving alone")
            return
        cur.execute("UPDATE tree_nodes SET bottom_seo_en = %s WHERE code = %s",
                    (CONTENT_EN, CODE))
    print(f"  replaced bottom_seo_en on {CODE} ({len(CONTENT_EN)} chars)")
