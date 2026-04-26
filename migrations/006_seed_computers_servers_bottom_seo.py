"""
Seed the bottom_seo_en HTML for the Computers & Servers root category.

Hand-written long-form copy modelled on the Notebooks example. Idempotent:
only writes if bottom_seo_en is empty for that node, so manual edits made
through the UI after the migration runs are not overwritten on re-run.
"""

CODE = "computers-servers"

CONTENT_EN = """\
<h2>Computers &amp; Servers</h2>
<p>Computers and servers are the core hardware that powers every part of a modern business: portable notebooks for daily mobile work, desktop and workstation PCs for fixed offices, rack-mounted servers for shared infrastructure, and point-of-sale terminals for retail and hospitality checkouts. This top-level category brings all of those device families together in one place.</p>
<p>This category includes notebooks, notebook accessories, desktops and workstations, all-in-one and mini PC formats, rack and tower servers, server components, racks and cabinets, and point-of-sale (POS) equipment. Most of the actual products live in the subcategories underneath. Peripherals like keyboards, mice and monitors, networking equipment, software licences and printers belong in their own separate top-level sections.</p>
<h2>Computers &amp; Servers overview</h2>
<h3>What this category includes</h3>
<p>The Computers &amp; Servers category groups every type of computing hardware sold to businesses, schools and home users. It covers personal computers in every form factor, workstation-grade machines for demanding professional software, point-of-sale terminals for shop-floor use and infrastructure servers that run shared services for many users at once.</p>
<p>Main groups in this category:</p>
<ul>
  <li>Notebooks (business, consumer, gaming, workstation, rugged, refurbished)</li>
  <li>Notebook accessories (bags, chargers, docking stations, replacement batteries and miscellaneous add-ons)</li>
  <li>Desktops &amp; workstations (tower desktops, all-in-one PCs, mini PCs and NUC-style systems)</li>
  <li>Servers (rack and tower units plus the components that go inside them)</li>
  <li>Racks, cabinets and mounting hardware for server-room and data-centre installs</li>
  <li>Point-of-sale (POS) equipment for retail, hospitality and warehouse checkouts</li>
</ul>
<p>Each group serves a different purpose. Notebooks focus on portability, desktops on fixed-position performance and easy upgradeability, servers on uptime and shared services, and POS on retail and hospitality checkouts.</p>
<h3>What this category does not include</h3>
<p>This category does not include broader peripherals such as keyboards, mice, monitors, headsets or external storage; those live in the Peripherals &amp; Office Products section. It also does not include networking hardware (switches, routers, access points, cabling), printers or scanners, or software licences and operating systems, all of which have their own top-level categories.</p>
<p>Keeping core computing hardware in one place makes it easier to compare notebooks, desktops, workstations, servers and POS terminals without mixing in add-ons, peripherals or service items.</p>
<h2>Categories in this group</h2>
<h3>Notebooks</h3>
<p>Notebooks are portable personal computers with a built-in display, keyboard, touchpad and battery. They are designed for users who move between desks, sites or homes: students, mobile professionals, sales teams, field engineers and anyone who values portability over upgradeability.</p>
<p>The Notebooks subcategory groups business, consumer, gaming, workstation and rugged notebook models, plus refurbished units sold at lower prices. Chargers, bags, docking stations and replacement batteries are listed separately in Notebook Accessories so the listings stay focused on actual computers.</p>
<h3>Notebook accessories</h3>
<p>Notebook accessories are the parts and add-ons that extend a laptop beyond what comes in the original box. The section covers bags and sleeves for transport, replacement chargers and power adapters, docking stations that turn a laptop into a desktop workstation, and a smaller miscellaneous group for charging trolleys, security locks, replacement batteries and similar items.</p>
<p>This subcategory exists separately so a buyer browsing notebook computers is not flooded with accessory SKUs, and a buyer refreshing accessories does not need to scroll past every laptop in the catalog.</p>
<h3>Desktops &amp; workstations</h3>
<p>Desktops and workstations are non-portable personal computers built around a tower, all-in-one display or compact mini PC form factor, powered from a wall outlet rather than a battery. They are the right choice for a user who works from one place every day.</p>
<p>The subcategory covers:</p>
<ul>
  <li>Standard desktop towers for general office and home use, with easy access to memory, storage and graphics upgrades</li>
  <li>All-in-one PCs that hide the computer hardware behind the display, common at receptions, classrooms and tidy office desks</li>
  <li>Mini PCs and NUC-style systems for low-footprint installations, signage, thin clients and meeting rooms</li>
  <li>Workstation-grade desktops certified for engineering, video, 3D and other demanding professional software</li>
</ul>
<p>Compared with notebooks, desktops generally give more performance per euro, are easier to upgrade and last longer in service. The trade-off is that they are tied to one location.</p>
<h3>Servers</h3>
<p>A server is a computer dedicated to running shared services like databases, websites, file storage or backups for many users at once, instead of one personal user. Servers sit at the heart of business IT infrastructure and are typically owned and operated by IT teams, system integrators and businesses running their own applications.</p>
<p>This branch covers complete rack and tower server units, the spare and upgrade components that go inside them (CPUs, server memory, motherboards, power supplies, storage controllers and other internal parts), and the racks, cabinets and mounting hardware they live in. The components are split into separate subcategories so a maintenance team can replace a single failed module rather than swapping the whole machine.</p>
<h3>Point-of-sale (POS) equipment</h3>
<p>POS equipment is the hardware used at retail, hospitality and warehouse checkouts to ring up sales, scan items, accept card payments and print receipts. The section is split into POS terminals (the touchscreen all-in-one devices that run the till software, plus mobile POS units carried around the store and self-checkout kiosks) and POS accessories (printers, scanners, cash drawers, mounting arms and customer-facing displays).</p>
<p>This subcategory is intended for retailers, hospitality operators, warehouse and logistics teams and the resellers who fit out their checkout points.</p>
<h2>How to choose between these categories</h2>
<h3>Start with the use case</h3>
<p>The easiest way to navigate this section is to start with what the computer needs to do every day. The same buyer might need different hardware for different roles in the business.</p>
<p>Quick direction:</p>
<ul>
  <li>Mobile work, study or travel: choose a Notebook</li>
  <li>Fixed office or home desk with easy upgradeability: choose a Desktop</li>
  <li>Single-piece machine for receptions, classrooms or tidy desks: choose an All-in-One PC</li>
  <li>Compact deployment, digital signage or thin clients: choose a Mini PC</li>
  <li>Demanding professional software (CAD, video, 3D, data): choose a Workstation</li>
  <li>Shared services for many users at once: choose a Server</li>
  <li>Retail, hospitality or warehouse checkout: choose POS Equipment</li>
</ul>
<h3>Choose by environment</h3>
<p>For office and business use, business-grade notebooks or desktops are the most balanced choice. They focus on reliability, security, manageability, warranty terms and docking-station compatibility over raw performance.</p>
<p>For home and study, consumer notebooks, all-in-one PCs and entry-level desktops are usually enough. Price, screen size, battery life and ease of use matter more than enterprise features.</p>
<p>For industrial, warehouse or field work, rugged notebooks and mobile POS units are designed to survive drops, dust, vibration and outdoor conditions where standard office hardware would fail too quickly.</p>
<p>For data centres and server rooms, rack-mounted servers with redundant power supplies, hot-swap drive bays and remote management are the right starting point. They are designed for 24/7 operation in shared infrastructure.</p>
<h3>Choose by performance needs</h3>
<p>For basic use (browsing, documents, email and video calls), entry-level consumer notebooks, all-in-ones or mini PCs cover the workload comfortably. 8 to 16 GB of RAM (Random Access Memory) and a small SSD (Solid State Drive) are usually enough.</p>
<p>For business work and study, 16 GB of RAM with 256 to 512 GB of SSD storage gives a more comfortable multitasking experience and longer useful life. This is a practical starting point for most office users.</p>
<p>For workstation, gaming or content-creation use, dedicated graphics cards, more memory and faster storage become the deciding factors. 32 GB of RAM and 1 TB or more of SSD storage is more typical.</p>
<p>For server workloads, the priorities shift to ECC (Error-Correcting Code) memory, multiple CPU sockets, redundant PSUs (Power Supply Units), hot-swap storage, RAID (Redundant Array of Independent Disks) controllers and remote management features.</p>
<h2>Key specifications across this category</h2>
<h3>Form factor</h3>
<p>Form factor decides where and how the computer can be installed. A 1U, 2U or 4U rack server fits into a 19-inch cabinet alongside others; a tower server sits on the floor in a small server room; an all-in-one PC mounts behind a screen on a reception desk; a mini PC hides behind a monitor on a VESA bracket; a notebook fits in a bag.</p>
<h3>Processor (CPU)</h3>
<p>CPU choice depends on the workload. Desktop and notebook chips are tuned for general-purpose work and balanced power consumption. Server CPUs (Central Processing Units), such as the Intel Xeon and AMD EPYC families, bring more cores, larger memory bandwidth and ECC support, all of which matter for shared, multi-user workloads.</p>
<h3>Memory (RAM)</h3>
<p>Notebooks and desktops use standard DDR memory. Servers use server-grade RAM with ECC and registered or load-reduced buffering for stability under heavy multi-core load. POS terminals and mini PCs usually ship with smaller, fixed memory configurations that are not user-upgradable.</p>
<h3>Storage</h3>
<p>SSD storage is now the norm across this category. Servers can be configured with hot-swap drive bays plus dedicated RAID controllers and HBA (Host Bus Adapter) cards for resilience and capacity. Workstations may add NVMe storage for very fast project-file access. Notebooks rely on a single internal SSD plus optional external storage.</p>
<h3>Connectivity</h3>
<p>Notebooks and mini PCs rely on USB-C, Thunderbolt and HDMI plus Wi-Fi and Bluetooth. Desktops add more PCIe and storage slots for upgrades. Servers add IPMI/BMC (Baseboard Management Controller) remote management, multiple network interfaces and rack-mount cable management. POS terminals add specialised ports for receipt printers, cash drawers and barcode scanners.</p>
<h2>Accessories and related categories</h2>
<p>Notebook-specific accessories (bags, chargers, docking stations, batteries) live in the Notebook Accessories subcategory inside this group. POS-specific accessories (receipt printers, scanners, cash drawers, customer displays) live in POS Accessories. Server-specific spare parts (CPUs, memory, motherboards, PSUs, storage controllers) live under Server Components.</p>
<p>For broader peripherals (keyboards, mice, monitors, headsets) and for networking equipment (switches, routers, access points, cabling), use the dedicated Peripherals &amp; Office Products and Networking sections of the catalog.</p>
<h2>Frequently asked questions</h2>
<h3>What is the difference between a notebook, a desktop and a workstation?</h3>
<p>A notebook is a portable computer with a built-in screen, keyboard and battery. A desktop is fixed in place, powered from a wall outlet and easier to upgrade. A workstation is a more powerful desktop or notebook certified for demanding professional software. The choice depends on whether mobility, upgradability or raw performance matters most.</p>
<h3>When should I choose a server instead of a desktop?</h3>
<p>Choose a server when the machine has to run shared services for many users at once: databases, file storage, virtualisation, web applications, email, backup targets or other always-on workloads. A desktop is built for one personal user; a server is built to keep running 24/7 with redundancy and remote management.</p>
<h3>What is the difference between a rack server and a tower server?</h3>
<p>A rack server is a flat 1U, 2U or 4U chassis designed to be screwed into a 19-inch rack alongside others. A tower server looks like a tall desktop case and sits on the floor. Rack format suits data centres and structured server rooms; tower format suits offices and small server rooms without a rack cabinet.</p>
<h3>What does POS equipment cover?</h3>
<p>POS (Point of Sale) equipment covers the hardware used at the checkout: fixed and mobile POS terminals, handheld PDAs (Personal Digital Assistants) for stock-take, self-checkout kiosks operated by the customer, barcode scanners, receipt printers, cash drawers and customer-facing displays. It is intended for retail, hospitality and warehouse checkouts.</p>
<h3>Are accessories included in this category?</h3>
<p>No. Notebook-specific accessories sit in the Notebook Accessories subcategory inside this group. POS-specific accessories sit in POS Accessories. Server-specific spares sit under Server Components. Broader peripherals (keyboards, mice, monitors, networking gear) live in their own sections of the catalog.</p>
<h3>Do you sell refurbished computers?</h3>
<p>Refurbished business notebooks are listed within the Notebooks subcategory. They are previously used devices that have been prepared for resale and can be a cost-efficient option for cost-conscious businesses, education customers and general office use. Always check the warranty terms, condition grade and battery health before ordering.</p>
<h3>Is software included in this category?</h3>
<p>No. Operating systems, server software licences, antivirus, business productivity tools and similar items live in the dedicated Software section of the catalog, separate from the hardware listed here.</p>
"""


def apply(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT bottom_seo_en FROM tree_nodes WHERE code = %s", (CODE,))
        row = cur.fetchone()
        if not row:
            print(f"  no tree_node {CODE!r}, skipping")
            return
        if (row[0] or "").strip():
            print(f"  bottom_seo_en already set on {CODE!r}, leaving alone")
            return
        cur.execute("UPDATE tree_nodes SET bottom_seo_en = %s WHERE code = %s",
                    (CONTENT_EN, CODE))
    print(f"  seeded bottom_seo_en on {CODE} ({len(CONTENT_EN)} chars)")
