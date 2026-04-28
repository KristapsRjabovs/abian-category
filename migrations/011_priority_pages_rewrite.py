"""
Editorial review pass 1.5: hand-written rewrites for the 4 pages where
the editor gave detailed page-specific feedback.

Pages and what was wrong before this migration:

1. computers-servers (root)
   - meta "plus the docks ... spare components that fit them" makes no
     sense; LV "kopā ar dokstacijām ... rezerves komponentēm" same.
   - bottom_seo first H2 was just the category name.
   - Decision framework was rigid (developer = desktop tower; said
     notebooks could not drive two monitors).
   - Did not reflect that modern offices favour notebooks as the default
     for everyone.
   - Mentioned warranty (the site does not issue warranties).

2. computers-servers/notebooks
   - LV used "Notebook" as the primary noun; should be "Portatīvais dators"
     with "(notebook)" as secondary.
   - bottom_seo first H2 was bare ("Notebooks").
   - First paragraph of bottom_seo duplicated the seo_desc; second
     paragraph was a near-copy of the first.
   - Had a "what this category does NOT include" block.

3. computers-servers/notebook-accessories
   - LV used "Notebook" as primary noun.
   - Contained the illogical phrase "kas pabeidz datoru parka izvietošanu".
   - Mentioned "products live in subcategories below" / "Faktiskie
     produkti dzīvo četrās apakškategorijās zemāk".

4. computers-servers/notebook-accessories/bags-sleeves-backpacks
   - bottom_seo first H2 was bare.
   - LV name_lv adjusted per editor preference: "Somas, Mugursomas un
     Sleeve apvalki".
   - LV body should mix "Portatīvo datoru somas" with "notebook somas".

Safe-update: replaces fields outright; the editor will manually re-edit
through the UI if they touch these pages between deploy and review.
"""

PAGES = {

    # ────────────────────────── 1. computers-servers ──────────────────────
    "computers-servers": {
        "name_lv": "Datori un serveri",
        "meta_desc_en": "Notebooks, desktops, all-in-ones, mini PCs, tablets and rack servers, alongside the components and accessories that keep them running.",
        "meta_desc_lv": "Portatīvie datori, galddatori, viss-vienā, mini PC, planšetes un rack serveri, kopā ar komponentēm un piederumiem, kas tos uztur darbā.",
        "seo_desc_en": "This top-level group brings together every kind of computer in the catalog: notebooks for mobile work, desktops and all-in-ones for fixed workstations, mini PCs for compact installs, tablets for shop floor and field use, rack and tower servers for shared infrastructure, plus the components and accessories that keep the whole estate running through its refresh cycle.",
        "seo_desc_lv": "Šī augšējā līmeņa grupa apvieno visus datoru veidus katalogā: portatīvie datori mobilam darbam, galddatori un viss-vienā fiksētām darbstacijām, mini PC kompaktiem uzstādījumiem, planšetes lauka un veikalu zonām, rack un tower serveri kopīgai infrastruktūrai, kā arī komponentes un piederumi, kas uztur visu IT vidi darba kārtībā ikdienā un atjaunināšanas ciklā.",
        "bottom_seo_en": """\
<h2>Computers and servers for business, retail and home environments</h2>
<p>Outfitting an office, a shop or a workshop with computing hardware is rarely a single decision. Each role gets a different device, the devices need to work together, and the whole estate refreshes on a rolling cycle. This top-level category groups every option side by side: notebooks for mobility, desktops and all-in-ones for fixed positions, mini PCs for compact installs, tablets for the shop floor or warehouse, rack and tower servers for shared infrastructure, and POS (Point of Sale) terminals for checkout zones.</p>
<h2>Choosing devices for the people who actually use them</h2>
<h3>Notebooks as the default for most office staff</h3>
<p>Modern offices increasingly default to notebook computers for almost every role, not just travelling staff. A notebook on a docking station with two external monitors, a separate keyboard and a mouse delivers the same desk experience as a desktop tower, with the option of taking it home, into a meeting room or to a customer site. The trade-off is a higher per-device cost and a shorter useful life because of battery wear.</p>
<h3>Two-monitor setups, multiple paths</h3>
<p>Two-monitor work does not require a desktop. A docked notebook with one external monitor gives a two-screen layout (laptop screen plus external). A docked notebook with two external monitors gives three screens. A desktop with two external monitors gives a true two-screen setup without a third. Pick the path that matches the user's mobility need, not what the spec sheet says is "standard".</p>
<h3>When a desktop or workstation is still the better fit</h3>
<p>Fixed-position roles where the user never carries the device, sustained heavy workloads (CAD, 3D rendering, large code compilations, long video exports) where a desktop's better thermals and upgrade headroom translate into faster runs, and shared kiosks where battery wear has no value, all map naturally to desktops or workstations. Notebooks can do the same work, just at a higher unit cost and shorter useful life.</p>
<h3>All-in-ones, mini PCs and tablets in supporting roles</h3>
<p>All-in-one PCs are tidy at receptions, classrooms and counter spaces where a tower would dominate. Mini PCs hide on a VESA (mounting standard) bracket behind a monitor for digital signage and clean office desks. Tablets cover stock-take, customer-facing demos, restaurant ordering and field service where a laptop would be too heavy.</p>
<h2>When does an in-house server make sense?</h2>
<p>For most companies under about 20 active users, cloud services and a NAS (Network Attached Storage) box cover shared workloads cheaper than buying, racking and maintaining a dedicated server. A server starts to pay back when the workload requires on-premise data for compliance, latency or dataset size, or when shared file storage outgrows what a NAS can serve smoothly. Above twenty users with custom line-of-business applications, a small tower or rack server becomes the cleaner answer.</p>
<h2>Standardisation: one configuration, simpler ordering</h2>
<p>Picking one notebook configuration and one desktop configuration for the bulk of the company makes ordering straightforward, simplifies imaging and helpdesk support, and lets repeat purchases land predictably. Mixing brands and configurations feels cheaper at the per-unit level but usually costs more once support load and image sprawl are counted. Reserve one or two power configurations for engineering, design and infrastructure roles; everyone else gets the standard.</p>
<h2>Refresh cycles by device class</h2>
<p>Different devices age at different rates. Plan refresh windows by class, not by device:</p>
<ul>
<li>Notebooks: 3 to 4 years (battery life and physical wear drive the decision)</li>
<li>Desktops and all-in-ones: 5 to 6 years (performance drives the decision)</li>
<li>Workstations: 4 to 5 years (software certification, not hardware, drives it)</li>
<li>Servers: 4 to 5 years (support contract end is the practical trigger)</li>
<li>POS terminals: 6 to 8 years (till software compatibility drives it)</li>
</ul>
<h2>Frequently asked questions</h2>
<h3>Should every employee get the same notebook?</h3>
<p>Standardise within roles, not across the whole company. All office staff on one business notebook works; forcing engineering or design teams onto the same device usually slows them down. Three or four approved configurations is the practical middle ground.</p>
<h3>Do small businesses need a server?</h3>
<p>Often no. Cloud services and a NAS cover most needs up to roughly twenty users. A dedicated server starts to make sense when workloads must stay on-premise or when shared storage outgrows what a NAS can serve.</p>
<h3>Can a notebook replace a desktop for daily office work?</h3>
<p>Yes for almost every role, paired with a docking station, external monitor, keyboard and mouse. The notebook then doubles as a portable device when needed.</p>
<h3>How does POS hardware fit alongside the rest of the estate?</h3>
<p>Treat POS as a separate stack. POS hardware runs purpose-built till software, has its own refresh cycle, and rarely belongs on the same management platform as office laptops. The shared touchpoints are the network and the integration with back-office systems for stock and reporting.</p>
<h3>Mini PC behind the monitor or a full desktop?</h3>
<p>For browsing, documents, video calls and most office software a mini PC on a VESA bracket gives the same experience as a desktop with no tower on the desk. For heavy graphics, large file work or upgrade headroom, a full desktop is still the better fit.</p>
""",
        "bottom_seo_lv": """\
<h2>Datori un serveri biznesam, mazumtirdzniecībai un mājas darbam</h2>
<p>Biroja, veikala vai darbnīcas datortehnikas iegāde reti ir viens lēmums. Katrai lomai paredzēta atšķirīga ierīce, ierīcēm jāstrādā kopā, un viss IT parks atjaunojas ritošā ciklā. Šī augšējā līmeņa kategorija sakārto visas iespējas blakus: portatīvie datori mobilitātei, galddatori un viss-vienā fiksētām vietām, mini PC kompaktiem uzstādījumiem, planšetes veikala zālei vai noliktavai, rack un tower serveri kopīgai infrastruktūrai, kā arī POS (Point of Sale) termināļi kases zonām.</p>
<h2>Ierīces izvēle pēc cilvēka, kas tās lieto</h2>
<h3>Portatīvie datori kā biroja darbinieku noklusējuma izvēle</h3>
<p>Mūsdienu birojos portatīvais dators arvien biežāk kļūst par noklusējuma izvēli gandrīz visām lomām, ne tikai ceļojošajiem darbiniekiem. Portatīvais dators uz dokstacijas ar diviem ārējiem monitoriem, atsevišķu tastatūru un peli sniedz to pašu galda pieredzi kā galddatora tornis, ar iespēju to paņemt uz mājām, sapulču telpu vai pie klienta. Cena par ierīci ir augstāka un kalpošanas laiks īsāks akumulatora nolietojuma dēļ.</p>
<h3>Divu monitoru darbavieta, vairākas pieejas</h3>
<p>Diviem monitoriem nav vajadzīgs galddators. Pieslēgts portatīvais ar vienu ārējo monitoru dod divu ekrānu izkārtojumu (klēpjdatora ekrāns plus ārējais). Pieslēgts portatīvais ar diviem ārējiem monitoriem dod trīs ekrānus. Galddators ar diviem ārējiem monitoriem dod tīru divu ekrānu darbvietu bez trešā. Izvēlieties to, kas atbilst mobilitātes vajadzībai, nevis to, ko specifikācija sauc par "standartu".</p>
<h3>Kad galddators vai workstation joprojām ir labākā izvēle</h3>
<p>Fiksētas vietas lomas, kur lietotājs ierīci nekad nepārvieto, ilgstošas smagas darba slodzes (CAD, 3D rendēšana, lielas koda kompilācijas, gari video eksporti), kur galddatora labāka dzesēšana un paplašināšanas iespējas pārvēršas ātrākos rezultātos, kā arī koplietošanas kioski, kur akumulators nav vērtība, dabiski atbilst galddatoram vai workstation. Portatīvais var darīt to pašu, tikai par augstāku cenu un īsāku kalpošanas laiku.</p>
<h3>Viss-vienā, mini PC un planšetes atbalsta lomās</h3>
<p>Viss-vienā datori sakārto reģistratūras, klases un letes telpu, kur tornis būtu pārāk liels. Mini PC paslēpjas uz VESA (mounting standard) stiprinājuma aiz monitora digitālajai signalizācijai un sakārtotām biroja darbavietām. Planšetes apkalpo inventarizāciju, klientu prezentācijas, restorānu pasūtījumus un lauka servisu, kur portatīvais būtu pārāk smags.</p>
<h2>Kad iekšējais serveris ir vērts ieguldījuma?</h2>
<p>Lielākajai daļai uzņēmumu ar mazāk kā ap 20 aktīviem lietotājiem mākoņa pakalpojumi un NAS (Network Attached Storage) iekārta apmierina kopīgās darba slodzes lētāk, nekā iegādāties, izvietot un apkopt atsevišķu serveri. Serveris sāk atmaksāties, kad darba slodzei jāpaliek lokāli atbilstības, latentuma vai datu apjoma dēļ vai kad kopīgā failu glabāšana pāraug to, ko NAS var nodrošināt raiti. Virs divdesmit lietotājiem ar specifiskām biznesa lietojumprogrammām neliels tower vai rack serveris kļūst par tīrāku risinājumu.</p>
<h2>Standartizācija: viena konfigurācija, vienkāršāka pasūtīšana</h2>
<p>Vienas portatīvā un vienas galddatora konfigurācijas izvēle uzņēmuma lielākajai daļai padara pasūtīšanu vienkāršu, vienkāršo attēlu sagatavošanu un palīdzības dienestu, un ļauj atkārtotiem pirkumiem ienākt paredzami. Zīmolu un konfigurāciju jaukšana šķiet lētāka uz vienības, bet parasti izmaksā vairāk, kad tiek saskaitīta atbalsta slodze un attēlu sazarojums. Atstājiet vienu vai divas jaudīgas konfigurācijas inženierijai, dizainam un infrastruktūras lomām; pārējie saņem standartu.</p>
<h2>Atjaunināšanas cikli pēc ierīču klases</h2>
<p>Dažādas ierīces noveco dažādā ātrumā. Plānojiet atjaunināšanas logus pēc klases, ne pēc ierīces:</p>
<ul>
<li>Portatīvie datori: 3 līdz 4 gadi (akumulatora darbības laiks un fiziskais nolietojums vada lēmumu)</li>
<li>Galddatori un viss-vienā: 5 līdz 6 gadi (veiktspēja vada lēmumu)</li>
<li>Workstation: 4 līdz 5 gadi (programmatūras sertifikācija, ne aparatūra, vada to)</li>
<li>Serveri: 4 līdz 5 gadi (atbalsta līguma beigas ir praktiskais aktivizētājs)</li>
<li>POS termināļi: 6 līdz 8 gadi (kases programmatūras saderība vada to)</li>
</ul>
<h2>Biežāk uzdotie jautājumi</h2>
<h3>Vai katram darbiniekam vajadzētu būt vienam un tam pašam portatīvajam?</h3>
<p>Standartizējiet lomu ietvaros, ne visā uzņēmumā. Visi biroja darbinieki ar vienu Business portatīvo strādā labi; piespiest inženierijas vai dizaina komandu uz vienas ierīces parasti palēnina darbu. Trīs vai četras apstiprinātas konfigurācijas ir praktiskais vidusceļš.</p>
<h3>Vai maziem uzņēmumiem ir vajadzīgs serveris?</h3>
<p>Bieži nē. Mākoņa pakalpojumi un NAS apmierina lielāko daļu vajadzību līdz aptuveni divdesmit lietotājiem. Atsevišķs serveris kļūst lietderīgs, ja darba slodzēm jāpaliek lokāli vai kopīgā glabāšana pāraug to, ko NAS var nodrošināt.</p>
<h3>Vai portatīvais var aizstāt galddatoru ikdienas biroja darbam?</h3>
<p>Jā, gandrīz visām lomām, kombinācijā ar dokstaciju, ārējo monitoru, tastatūru un peli. Portatīvais tad kalpo arī kā pārnēsājama ierīce, kad nepieciešams.</p>
<h3>Kā POS aparatūra sader ar pārējo IT vidi?</h3>
<p>Uzskatiet POS par atsevišķu pakāpienu. POS aparatūra darbina mērķim veidotu kases programmatūru, tai ir savs atjaunināšanas cikls, un tā reti pieder vienai un tai pašai pārvaldības platformai kā biroja klēpjdatori. Kopīgie saskares punkti ir tīkls un integrācija ar aizmugures sistēmām krājumiem un atskaitēm.</p>
<h3>Mini PC aiz monitora vai pilns galddators?</h3>
<p>Pārlūkošanai, dokumentiem, video zvaniem un lielākajai daļai biroja programmatūras mini PC uz VESA stiprinājuma sniedz to pašu pieredzi kā galddators bez torņa uz galda. Smagai grafikai, lielu failu darbam vai paplašināšanas rezerves jaudai pilns galddators joprojām ir labākā izvēle.</p>
""",
    },

    # ────────────────────────── 2. notebooks ──────────────────────────────
    "computers-servers/notebooks": {
        "name_lv": "Portatīvie datori",
        "meta_desc_en": "Portable computers (notebooks): Business, Consumer, Gaming, Workstation and Rugged models for office, home, study, field and industrial use.",
        "meta_desc_lv": "Portatīvie datori (notebook): Business, Consumer, Gaming, Workstation un Rugged modeļi birojam, mājām, mācībām, lauka un rūpnieciskai lietošanai.",
        "seo_desc_en": "Portable computers (notebooks) combine screen, keyboard and battery in one foldable case. This category covers Business, Consumer, Gaming, Workstation and Rugged models, plus refurbished business notebooks. Specifications focus on processor generation, memory, storage, screen size, weight and battery rating so buyers can match the device to mobility needs and the daily workload it has to handle without slowing the user down.",
        "seo_desc_lv": "Portatīvais dators (notebook) vienā salokāmā korpusā apvieno ekrānu, tastatūru un akumulatoru. Sadaļa aptver Business, Consumer, Gaming, Workstation un Rugged modeļus, kā arī atjaunotus biznesa portatīvos. Specifikācijās uzsvērti procesora paaudze, atmiņa, datu nesēji, ekrāna izmērs, svars un akumulatora reitings, lai pircējs ierīci varētu saskaņot ar mobilitātes vajadzību un ikdienas darba slodzi.",
        "bottom_seo_en": """\
<h2>Notebook computers for work, study and travel</h2>
<p>A notebook is a personal computer designed to leave the desk. The screen, keyboard, touchpad and battery share one foldable case, which is what makes the same machine usable on a kitchen table, a meeting room and a customer site without a separate setup. Different roles need different priorities from that case, which is why this category sorts notebooks into Business, Consumer, Gaming, Workstation and Rugged ranges, plus refurbished business stock for cost-conscious buyers.</p>
<h2>Notebook ranges in this category</h2>
<h3>Business notebooks</h3>
<p>Business notebooks are built for daily professional use: managers, sales, support, remote employees, administrative staff. They favour reliable build quality, comfortable keyboards, long battery life, security features (TPM (Trusted Platform Module), fingerprint readers, vPro/AMT remote management) and consistent docking-station support across model generations. The trade-off vs a similarly priced consumer model is design polish: business chassis prioritise repairability and standard parts.</p>
<h3>Consumer notebooks</h3>
<p>Consumer notebooks cover everyday personal use, study and general productivity: browsing, documents, video calls, online learning, streaming. They balance price, portability, screen size and everyday performance, without the security stack or ruggedisation a business or industrial buyer would pay for. Many household notebooks fall here.</p>
<h3>Gaming notebooks</h3>
<p>Gaming notebooks pair a stronger processor with a dedicated GPU (Graphics Processing Unit) and faster displays inside a portable case. Beyond games they are routinely used for video editing, 3D applications and other GPU-heavy creative work. They tend to be heavier, hotter and shorter on battery than a business notebook of similar size.</p>
<h3>Workstation notebooks</h3>
<p>Workstation notebooks carry certified components for engineering and creative software: CAD, 3D modelling, video production, data analysis, large project files. They prioritise CPU speed, RAM (Random Access Memory) capacity, professional graphics and display calibration, with battery life and weight as secondary concerns.</p>
<h3>Rugged notebooks</h3>
<p>Rugged notebooks are built for environments that destroy regular laptops: warehouses, transport, construction, manufacturing, field service. Reinforced casings, sealed ports, dust and moisture resistance and outdoor-readable displays mean the device survives drops, vibration and weather. The premium pays back through fewer warranty claims and less downtime over the device's life.</p>
<h3>Refurbished notebooks</h3>
<p>Refurbished notebooks are previously deployed devices reconditioned for resale. A well-graded business refurb often outperforms a brand-new entry-level consumer model at the same price. Look at condition grade, battery health, processor generation, RAM, SSD (Solid State Drive) size and screen condition before buying.</p>
<h2>How to choose the right notebook</h2>
<h3>Start with the daily workload</h3>
<p>Match the notebook to what it actually has to run every day, not to a top-of-spec dream. Browsing and documents need very different hardware to CAD or video editing. Gaming and creative work need dedicated graphics; office work does not. Field and warehouse use need ruggedisation; office work does not.</p>
<h3>Pick the screen size that fits the routine</h3>
<p>13 to 14 inch notebooks are the easiest to carry: travel, classrooms, hot-desking. 15 to 16 inch is the balanced default for daily home and office work, with enough screen real estate without becoming a brick. 17 inch is for gaming, design and workstation use where screen space outweighs portability. Most users save weight by adding an external monitor at the desk instead of buying the biggest screen the spec sheet offers.</p>
<h3>Specifications worth checking</h3>
<ul>
<li>Processor generation and tier (basic vs business vs creative vs workstation)</li>
<li>RAM: 8 GB for light use, 16 GB for business and study, 32 GB or more for creative and workstation work</li>
<li>SSD storage: 256 GB for cloud-first work, 512 GB for the practical default, 1 TB or more for creative and gaming use</li>
<li>Display: brightness in nits (300+ for office, 400+ for outdoor), colour gamut for creative work, refresh rate for gaming</li>
<li>Keyboard layout, touchpad accuracy, webcam quality, weight, battery life, charger size</li>
<li>Ports: USB-C (Universal Serial Bus Type-C), USB-A, HDMI, Ethernet (or adapter support), card reader, docking-station compatibility</li>
</ul>
<h2>Frequently asked questions</h2>
<h3>Is a notebook the same as a laptop?</h3>
<p>In everyday use yes; both names describe the same portable foldable computer. "Notebook" is more common in business product naming, "laptop" in consumer marketing.</p>
<h3>Which notebook is best for a small office or remote team?</h3>
<p>A business notebook is usually the right answer. Reliable build, security features, comfortable keyboard, predictable battery life and consistent docking-station support across model generations matter more than peak performance for office workloads.</p>
<h3>Which notebook for students?</h3>
<p>A 13 to 15 inch consumer or entry business notebook with SSD storage and 16 GB RAM covers documents, video calls, online learning and most coursework comfortably for several years.</p>
<h3>Do I need a dedicated graphics card?</h3>
<p>Not for office work, browsing or video calls. Yes for gaming, CAD, 3D modelling, video editing, rendering and other GPU-heavy workflows.</p>
<h3>How long should a business notebook last?</h3>
<p>Three to four years is the practical refresh cycle for daily-use business notebooks, driven mostly by battery wear and physical condition rather than raw performance.</p>
<h3>When does a rugged notebook pay back the price premium?</h3>
<p>When the device routinely leaves a normal office: field service, construction, manufacturing, logistics, outdoor work. Fewer replacements and less downtime cover the gap.</p>
""",
        "bottom_seo_lv": """\
<h2>Portatīvie datori darbam, mācībām un ceļošanai</h2>
<p>Portatīvais dators ir personālais dators, kas paredzēts atstāt darbgaldu. Ekrāns, tastatūra, skārienjutīgais panelis un akumulators ir vienā salokāmā korpusā, un tieši tas padara to pašu mašīnu lietojamu uz virtuves galda, sapulču telpā un pie klienta bez atsevišķa uzstādījuma. Dažādām lomām no šī korpusa nepieciešami atšķirīgi prioritāšu salikumi, tāpēc šī sadaļa portatīvos sakārto Business, Consumer, Gaming, Workstation un Rugged segmentos, plus atjaunoti biznesa modeļi izmaksu apzinīgajiem pircējiem.</p>
<h2>Portatīvo datoru segmenti šajā sadaļā</h2>
<h3>Business portatīvie datori</h3>
<p>Business portatīvie ir veidoti ikdienas profesionālam darbam: vadītāji, tirdzniecība, atbalsts, attālie darbinieki, administratīvais personāls. Tie izceļas ar uzticamu izgatavošanas kvalitāti, ērtu tastatūru, ilgu akumulatora darbības laiku, drošības funkcijām (TPM (Trusted Platform Module), pirkstu nospiedumu lasītāji, vPro/AMT attālā pārvaldība) un konsekventu dokstaciju atbalstu modeļu paaudzēs. Salīdzinot ar līdzīgas cenas Consumer modeli, tie upurē dizainu par labu remontējamībai un standarta detaļām.</p>
<h3>Consumer portatīvie datori</h3>
<p>Consumer portatīvie aptver ikdienas personisko lietošanu, mācības un vispārēju produktivitāti: pārlūkošana, dokumenti, video zvani, tiešsaistes mācības, straumēšana. Tie līdzsvaro cenu, pārnēsājamību, ekrāna izmēru un ikdienas veiktspēju, bez drošības funkcijām vai izturības, par ko maksātu Business vai rūpniecības pircējs. Daudzi mājsaimniecības portatīvie ietilpst šeit.</p>
<h3>Gaming portatīvie datori</h3>
<p>Gaming portatīvie apvieno spēcīgāku procesoru ar atsevišķu GPU (Graphics Processing Unit) un ātrākiem displejiem pārnēsājamā korpusā. Bez spēlēm tos regulāri izmanto video apstrādei, 3D lietojumiem un citam GPU smagam radošam darbam. Parasti tie ir smagāki, karstāki un ar īsāku akumulatora darbības laiku nekā līdzīga izmēra Business portatīvais.</p>
<h3>Workstation portatīvie datori</h3>
<p>Workstation portatīvie nes sertificētas komponentes inženierijas un radošajai programmatūrai: CAD, 3D modelēšana, video produkcija, datu analīze, lieli projektu faili. Prioritātē procesora ātrums, RAM (Random Access Memory) ietilpība, profesionāla grafika un displeja kalibrācija, kamēr akumulatora darbības laiks un svars ir sekundāri.</p>
<h3>Rugged portatīvie datori</h3>
<p>Rugged portatīvie ir veidoti vidēm, kas iznīcina parastus klēpjdatorus: noliktavas, transports, būvniecība, ražošana, lauka serviss. Pastiprināts korpuss, hermētiski porti, putekļu un mitruma izturība un āra apstākļiem lasāmi displeji nodrošina, ka ierīce iztur kritienus, vibrāciju un laikapstākļus. Cenas piemaksa atmaksājas mazāk pretenziju un mazāk dīkstāves dēļ visā ierīces dzīves laikā.</p>
<h3>Atjaunoti portatīvie datori</h3>
<p>Atjaunoti portatīvie ir iepriekš lietotas ierīces, kas atjauninātas pārdošanai. Labi novērtēts atjaunots Business notebook bieži pārspēj jaunu ievada Consumer modeli par to pašu cenu. Pirms iegādes pārbaudiet stāvokļa novērtējumu, akumulatora veselību, procesora paaudzi, RAM, SSD (Solid State Drive) ietilpību un ekrāna stāvokli.</p>
<h2>Kā izvēlēties piemērotu portatīvo</h2>
<h3>Sāciet no ikdienas darba slodzes</h3>
<p>Saskaņojiet portatīvo ar to, kas tam patiešām jādara katru dienu, ne ar augstākās klases sapni. Pārlūkošanai un dokumentiem vajadzīga ļoti atšķirīga aparatūra nekā CAD vai video apstrādei. Spēlēm un radošam darbam vajadzīga atsevišķa grafika; biroja darbam nē. Lauka un noliktavas darbam vajadzīga izturība; biroja darbam nē.</p>
<h3>Izvēlieties ekrāna izmēru pēc rutīnas</h3>
<p>13 līdz 14 collu portatīvie ir vieglāk nēsājami: ceļojumiem, klasēm, koplietojamām darba vietām. 15 līdz 16 collu ir līdzsvarotā noklusējuma izvēle ikdienas mājas un biroja darbam, ar pietiekami daudz ekrāna laukuma bez ķieģeļa svara. 17 collu ir paredzēts spēlēm, dizainam un Workstation darbam, kur ekrāna platība pārsver pārnēsājamību. Lielākā daļa lietotāju ietaupa svaru, pievienojot ārējo monitoru pie galda, nevis pērkot lielāko ekrānu specifikācijā.</p>
<h3>Specifikācijas, kuras vērts pārbaudīt</h3>
<ul>
<li>Procesora paaudze un līmenis (pamata, biznesa, radošajiem, Workstation)</li>
<li>RAM: 8 GB vieglai lietošanai, 16 GB biznesam un mācībām, 32 GB vai vairāk radošam un Workstation darbam</li>
<li>SSD glabāšana: 256 GB mākonim balstītam darbam, 512 GB praktiskajā noklusējumā, 1 TB vai vairāk radošam un Gaming darbam</li>
<li>Displejs: spilgtums nitos (300+ birojam, 400+ ārā), krāsu gamuts radošam darbam, atsvaidzes frekvence Gaming vajadzībām</li>
<li>Tastatūras izkārtojums, skārienjutīgā paneļa precizitāte, web kameras kvalitāte, svars, akumulatora darbības laiks, lādētāja izmērs</li>
<li>Porti: USB-C (Universal Serial Bus Type-C), USB-A, HDMI, Ethernet (vai adapteru atbalsts), karšu lasītājs, dokstaciju saderība</li>
</ul>
<h2>Biežāk uzdotie jautājumi</h2>
<h3>Vai portatīvais ir tas pats kas klēpjdators?</h3>
<p>Ikdienas lietošanā jā; abi nosaukumi apzīmē vienu un to pašu pārnēsājamo salokāmo datoru. "Portatīvais" un "notebook" ir vairāk lietoti biznesa kontekstā, "klēpjdators" patērētāju mārketingā.</p>
<h3>Kurš portatīvais der mazam birojam vai attālinātajai komandai?</h3>
<p>Business portatīvais parasti ir pareizā atbilde. Uzticama izgatavošana, drošības funkcijas, ērta tastatūra, paredzams akumulatora laiks un konsekvents dokstaciju atbalsts modeļu paaudzēs ir svarīgāki par maksimālo veiktspēju biroja darba slodzēm.</p>
<h3>Kurš portatīvais der studentiem?</h3>
<p>13 līdz 15 collu Consumer vai ievada Business portatīvais ar SSD glabāšanu un 16 GB RAM ērti aptver dokumentus, video zvanus, tiešsaistes mācības un lielāko daļu kursa darbu vairākus gadus.</p>
<h3>Vai man vajadzīga atsevišķa grafikas karte?</h3>
<p>Biroja darbam, pārlūkošanai vai video zvaniem nē. Spēlēm, CAD, 3D modelēšanai, video apstrādei, rendēšanai un citām GPU smagām darba plūsmām jā.</p>
<h3>Cik ilgi kalpos Business portatīvais?</h3>
<p>Trīs līdz četri gadi ir praktiskais atjaunināšanas cikls ikdienas Business portatīvajiem, ko galvenokārt nosaka akumulatora nolietojums un fiziskais stāvoklis, ne raw veiktspēja.</p>
<h3>Kad Rugged portatīvais atmaksājas?</h3>
<p>Kad ierīce regulāri pamet parasto biroju: lauka serviss, būvniecība, ražošana, loģistika, āra darbs. Mazāk nomaiņu un mazāk dīkstāves sedz cenu starpību.</p>
""",
    },

    # ─────────────────────── 3. notebook-accessories ──────────────────────
    "computers-servers/notebook-accessories": {
        "name_lv": "Portatīvo datoru piederumi",
        "meta_desc_en": "Bags, chargers, docking stations, replacement batteries, charging trolleys and security locks for portable computers (notebooks).",
        "meta_desc_lv": "Somas, lādētāji, dokstacijas, rezerves akumulatori, uzlādes ratiņi un drošības slēdzenes portatīvajiem datoriem (notebook).",
        "seo_desc_en": "Portable computer (notebook) accessories: bags and sleeves for transport, chargers and power adapters for replacements and travel kits, docking stations for desk-style use with external monitors, plus a smaller miscellaneous group covering charging trolleys, replacement batteries, security locks and cleaning supplies. Each subcategory specifies the laptop families it fits so an order does not bring back the wrong dock.",
        "seo_desc_lv": "Portatīvo datoru (notebook) piederumi: somas un sleeve apvalki pārnēsāšanai, lādētāji un strāvas adapteri rezerves un ceļojuma komplektiem, dokstacijas galda lietošanai ar ārējiem monitoriem, kā arī mazāka grupa, kas aptver uzlādes ratiņus, rezerves akumulatorus, drošības slēdzenes un tīrīšanas līdzekļus. Katra apakšsadaļa norāda saderīgās klēpjdatoru saimes, lai pasūtījums neatnestu nepareizu dokstaciju.",
        "bottom_seo_en": """\
<h2>Notebook accessories for daily mobility, replacement and workspace setup</h2>
<p>An accessory category exists because the box a notebook ships in covers basic use only. The moment a user wants to dock at a desk, charge in a second location, carry the device safely or run several units from one charging station, the supporting hardware lives outside the laptop itself. This section gathers that supporting hardware: transport, power, docking and the smaller workspace items that surround a portable computer.</p>
<h2>Subcategory at a glance</h2>
<h3>Bags, sleeves and backpacks</h3>
<p>Padded sleeves for slot-in protection, shoulder bags for the office commute, and backpacks with dedicated padded sections for daily carry. Sized to the screen diagonal stated by the laptop manufacturer.</p>
<h3>Chargers and power adapters</h3>
<p>Original notebook power adapters and USB-C (Universal Serial Bus Type-C) Power Delivery chargers. The adapter category covers replacement units, travel chargers and shared-desk spares so a single user can charge in office, home and meeting room without unplugging anything.</p>
<h3>Docking stations</h3>
<p>USB-C, Thunderbolt and proprietary mechanical docks that turn a portable computer into a desk-style workstation: external monitors, USB ports, wired Ethernet and power through one cable. Compatibility is by host interface and PD wattage, not laptop model.</p>
<h3>Other accessories</h3>
<p>Charging trolleys for school and office fleets, replacement batteries listed by manufacturer part number, security cable locks, cleaning kits, privacy filters, port adapters and small spare parts that do not warrant their own subcategory.</p>
<h2>Choosing accessories that fit the deployment</h2>
<h3>Standardise the dock first</h3>
<p>If staff move between desks or work from home occasionally, picking one docking-station family (USB-C PD, Thunderbolt 4 or one OEM mechanical dock) lets every laptop plug in anywhere. Mixing dock types fragments the office into incompatible islands within a year. Buy a few extra docks for the meeting rooms while standardising.</p>
<h3>Match charger spec to the device, not the cable</h3>
<p>Notebook chargers vary in wattage (45 W, 65 W, 90 W, 100 W and higher) and connector. A USB-C cable does not guarantee compatibility: the charger has to deliver the wattage the laptop expects and use a connector the laptop accepts. Read the spec on both ends before ordering replacements in volume.</p>
<h3>Bag size by screen diagonal, not "looks about right"</h3>
<p>Sleeves and bags are sized to the laptop diagonal stated by the manufacturer (13.3", 14", 15.6", 17.3"). A 15.6" notebook will not safely fit a 14" sleeve even if it visually looks close. Order by inches, not by appearance.</p>
<h2>Frequently asked questions</h2>
<h3>Are these accessories included with a new notebook?</h3>
<p>The box typically contains the device, a charger and basic documentation. Bags, docking stations, replacement batteries, security locks, charging trolleys and similar items are accessories bought separately as the deployment grows.</p>
<h3>Can a USB-C dock work with any laptop?</h3>
<p>Only with a laptop that supports USB-C with Power Delivery and DisplayPort Alt Mode. Older USB-C ports without these capabilities cannot drive a docking station. Check the laptop's port specification before ordering.</p>
<h3>How many spare chargers should an office stock?</h3>
<p>The pragmatic ratio is one extra charger per five active notebooks for hot-desk and travel use, plus one per meeting room and one per shared workspace. Cheaper than dealing with dead-laptop tickets in middle of meetings.</p>
<h3>Do replacement batteries fit any laptop of the same brand?</h3>
<p>No. Batteries are matched by manufacturer part number, not brand or model line. A replacement battery for one model often will not fit a closely-related sibling model. Always order by part number.</p>
""",
        "bottom_seo_lv": """\
<h2>Portatīvo datoru piederumi ikdienas mobilitātei, nomaiņai un darbavietas iekārtošanai</h2>
<p>Piederumu sadaļa pastāv tāpēc, ka komplektā iekļautie elementi sedz tikai pamata lietošanu. Brīdī, kad lietotājs vēlas pieslēgties pie galda, lādēties otrā vietā, pārnēsāt ierīci droši vai darbināt vairākas vienības no vienas uzlādes stacijas, atbalsta aparatūra dzīvo ārpus paša klēpjdatora. Šī sadaļa apkopo to atbalsta aparatūru: pārnēsāšana, barošana, dokstacijas un mazākie darbavietas elementi ap portatīvo datoru.</p>
<h2>Apakšsadaļas īsumā</h2>
<h3>Somas, sleeve apvalki un mugursomas</h3>
<p>Polsterēti sleeve apvalki iebīdāmai aizsardzībai, pleca somas biroja braucieniem un mugursomas ar polsterētu datora nodalījumu ikdienas nēsāšanai. Izmērs saskaņots ar ražotāja norādīto ekrāna diagonāli.</p>
<h3>Lādētāji un strāvas adapteri</h3>
<p>Oriģinālie portatīvo datoru strāvas adapteri un USB-C (Universal Serial Bus Type-C) Power Delivery lādētāji. Adapteru sadaļa aptver nomaiņas vienības, ceļojuma lādētājus un koplietojamo galdu rezerves, lai viens lietotājs varētu lādēties birojā, mājās un sapulču telpā bez atvienošanas.</p>
<h3>Dokstacijas</h3>
<p>USB-C, Thunderbolt un patentētas mehāniskās dokstacijas, kas pārvērš portatīvo datoru par galda darbstaciju: ārējie monitori, USB porti, vadu Ethernet un strāva caur vienu kabeli. Saderība ir pēc saimnieka interfeisa un PD jaudas, ne pēc klēpjdatora modeļa.</p>
<h3>Citi piederumi</h3>
<p>Uzlādes ratiņi skolu un biroju parkiem, rezerves akumulatori pēc ražotāja artikula numura, drošības kabeļa slēdzenes, tīrīšanas komplekti, privātuma filtri, portu adapteri un sīkas rezerves daļas, kam nav atsevišķas apakšsadaļas.</p>
<h2>Kā izvēlēties piederumus, kas iekļaujas izvietojumā</h2>
<h3>Vispirms standartizējiet dokstaciju</h3>
<p>Ja darbinieki pārvietojas starp galdiem vai dažkārt strādā no mājām, vienas dokstaciju saimes izvēle (USB-C PD, Thunderbolt 4 vai viena OEM mehāniskā dokstacija) ļauj jebkuru klēpjdatoru pievienot jebkur. Dokstaciju tipu jaukšana sadala biroju nesaderīgās salās gada laikā. Pērciet pāris papildu dokstacijas sapulču telpām, kamēr standartizējat.</p>
<h3>Saskaņojiet lādētāja parametrus ar ierīci, ne ar kabeli</h3>
<p>Portatīvo datoru lādētāji atšķiras pēc jaudas (45 W, 65 W, 90 W, 100 W un augstāk) un savienotāja. USB-C kabelis negarantē saderību: lādētājam jānodrošina jauda, ko klēpjdators sagaida, un jāizmanto savienotājs, ko klēpjdators pieņem. Pirms apjoma pasūtīšanas izlasiet specifikāciju abos galos.</p>
<h3>Somas izmērs pēc ekrāna diagonāles, ne pēc "izskatās piemēroti"</h3>
<p>Apvalki un somas ir izmērā saskaņoti ar ražotāja norādīto klēpjdatora diagonāli (13,3", 14", 15,6", 17,3"). 15,6 collu klēpjdators droši neiederēsies 14 collu apvalkā, pat ja vizuāli izskatās tuvu. Pasūtiet pēc collām, ne pēc izskata.</p>
<h2>Biežāk uzdotie jautājumi</h2>
<h3>Vai šie piederumi ir iekļauti komplektā ar jaunu portatīvo?</h3>
<p>Komplektā parasti ir ierīce, lādētājs un pamata dokumentācija. Somas, dokstacijas, rezerves akumulatori, drošības slēdzenes, uzlādes ratiņi un līdzīgi priekšmeti ir piederumi, ko pērk atsevišķi, parkam pieaugot.</p>
<h3>Vai USB-C dokstacija strādās ar jebkuru klēpjdatoru?</h3>
<p>Tikai ar tādu, kas atbalsta USB-C ar Power Delivery un DisplayPort Alt Mode. Vecāki USB-C porti bez šīm iespējām nevar darbināt dokstaciju. Pirms pasūtīšanas pārbaudiet klēpjdatora porta specifikāciju.</p>
<h3>Cik daudz rezerves lādētāju biroju vajadzētu uzturēt?</h3>
<p>Praktiskā attiecība ir viens papildu lādētājs uz pieciem aktīviem portatīvajiem koplietojamai un ceļojuma lietošanai, plus viens uz katru sapulču telpu un viens uz katru koplietošanas darbavietu. Lētāk nekā risināt mirušas baterijas problēmu sapulču vidū.</p>
<h3>Vai rezerves akumulatori der jebkuram tā paša zīmola klēpjdatoram?</h3>
<p>Nē. Akumulatori tiek saskaņoti pēc ražotāja artikula numura, ne pēc zīmola vai modeļu līnijas. Rezerves akumulators vienam modelim bieži neder cieši saistītam māsas modelim. Vienmēr pasūtiet pēc artikula numura.</p>
""",
    },

    # ──────────────── 4. notebook-accessories/bags-sleeves-backpacks ──────
    "computers-servers/notebook-accessories/bags-sleeves-backpacks": {
        "name_lv": "Somas, mugursomas un sleeve apvalki",
        "meta_desc_en": "Padded sleeves, shoulder bags and backpacks for portable computers (notebooks), sized to the screen diagonal stated by the manufacturer.",
        "meta_desc_lv": "Polsterēti sleeve apvalki, pleca somas un mugursomas portatīvajiem datoriem (notebook somām), izmēros pēc ražotāja norādītās ekrāna diagonāles.",
        "seo_desc_en": "Carrying gear for portable computers (notebooks): padded sleeves for slot-in protection, shoulder bags and briefcases for the office commute, and backpacks with a dedicated padded laptop section for daily transport. Sized to the screen diagonal stated by the laptop manufacturer in inches, with separate compartments for chargers, cables and small accessories so a kit travels together without sliding around.",
        "seo_desc_lv": "Pārnēsāšanas piederumi portatīvajiem datoriem (notebook somām): polsterēti sleeve apvalki iebīdāmai aizsardzībai, pleca somas un portfeļi biroja braucieniem, kā arī mugursomas ar atsevišķu polsterētu klēpjdatora nodalījumu ikdienas pārnēsāšanai. Izmērs saskaņots ar ražotāja norādīto ekrāna diagonāli collās, ar nodalījumiem lādētājiem, kabeļiem un mazākiem piederumiem, lai komplekts ceļo kopā.",
        "bottom_seo_en": """\
<h2>Notebook bags, sleeves and backpacks for daily transport and travel</h2>
<p>A laptop spends as much time being carried as it does being used, which is why the carrying format is part of the daily experience and not a checkout afterthought. Three formats cover almost everyone: a slim sleeve that lives inside another bag, a shoulder bag or briefcase for the desk-to-desk commute, and a backpack for daily travel and longer routes. Each protects the screen and case in a different way and suits a different routine.</p>
<h2>Carrying formats in this category</h2>
<h3>Slim sleeves</h3>
<p>A sleeve is a soft padded pouch sized exactly to the laptop's screen diagonal. Its job is shock and abrasion protection while the laptop sits inside another bag, a backpack or even a tote. Sleeves shine when the user already has a preferred carry bag and just wants the laptop protected inside it. Look for memory-foam padding, a snug fit and a soft inner lining that does not scuff the lid.</p>
<h3>Shoulder bags and briefcases</h3>
<p>Shoulder bags, messenger bags and briefcases place the laptop in a structured padded compartment with separate sleeves for charger, cables, documents and small accessories. They suit short office commutes and meetings, where the laptop comes out and goes back in several times a day. Pick by closure type (zip, magnetic flap, clip), strap comfort and front-pocket layout.</p>
<h3>Backpacks</h3>
<p>Backpacks distribute weight across both shoulders and free both hands, which makes them the practical choice for cycling, public transport, longer walks and travel days. The padded laptop section is usually a separate back-of-bag pocket with its own zip; better designs keep the laptop close to the spine for balance. Look for padded straps, a sternum clip, a luggage pass-through strap for travel and water-resistant fabric.</p>
<h2>Choosing the right size and format</h2>
<h3>Match the size to the laptop, not the bag</h3>
<p>Bags and sleeves are sized in inches: 13.3, 14, 15.6, 17.3. A bag labelled for a 15-inch notebook will fit most 14-inch and 15.6-inch laptops, but a 17-inch laptop will not fit a 15-inch bag even if it looks close. Always check the laptop's screen diagonal in the manufacturer specification, not the marketing name.</p>
<h3>Match the format to the routine</h3>
<p>Five days a week sitting at the same office: a sleeve inside an existing tote is enough. Daily commute by car or short walk: a shoulder bag with one or two laptops and a few accessories. Cycling, public transport, longer travel: a backpack with sternum clip and a luggage pass-through strap. Two-laptop carry (work plus personal) is usually the moment to switch to a backpack regardless.</p>
<h3>Padding, water resistance and cabin compatibility</h3>
<p>Padding matters most where the laptop sits closest to the outer wall, which is why backpack laptop sleeves are usually positioned against the back panel rather than the outer face. Water-resistant outer fabric and a covered zip on the laptop section keep light rain out; full waterproof material is rare and expensive. For travel, check the bag against the cabin baggage size limits of the airlines used most.</p>
<h2>Frequently asked questions</h2>
<h3>Sleeve, bag or backpack — which one to start with?</h3>
<p>If the laptop already travels in another bag, a sleeve is enough. If most days are office-to-office with a short commute, a shoulder bag or briefcase is the practical default. If the route involves cycling, walking, public transport or carrying anything else, a backpack is the better daily option.</p>
<h3>Will a 15-inch bag fit a 14-inch laptop?</h3>
<p>Usually yes, but the laptop will move around inside the padded compartment. For long carry routes that movement causes wear; for short commutes it does not matter much. A snug-fit sleeve plus a roomier outer bag is the safer combination if the carry distance is long.</p>
<h3>Can a backpack laptop section be skipped if the laptop already has a sleeve?</h3>
<p>It can; many backpacks treat the laptop section as just a padded pocket and a sleeve adds a second layer of protection. The combination is common for daily commute users carrying expensive or sensitive devices.</p>
<h3>How does a notebook bag protect against drops?</h3>
<p>Most laptop bags protect against impacts during normal handling: dropping the bag from desk height onto a hard floor, knocking it against doorframes, or bumping it on public transport. Severe drops (multi-floor falls, hard impacts onto corners) exceed what a normal padded bag can absorb. Rugged laptop cases with reinforced corners are a separate product class for that level of protection.</p>
""",
        "bottom_seo_lv": """\
<h2>Portatīvo datoru somas, sleeve apvalki un mugursomas ikdienas pārnēsāšanai un ceļošanai</h2>
<p>Klēpjdators vienlīdz ilgu laiku pavada nēsāts kā arī lietots, tāpēc pārnēsāšanas formāts ir daļa no ikdienas pieredzes, ne pēkšņs lēmums kasē. Trīs formāti aptver gandrīz visus: plāns sleeve apvalks, kas dzīvo citas somas iekšpusē, pleca soma vai portfelis biroja braucieniem, un mugursoma ikdienas ceļojumiem un garākiem maršrutiem. Katrs aizsargā ekrānu un korpusu atšķirīgi un atbilst atšķirīgai rutīnai.</p>
<h2>Pārnēsāšanas formāti šajā sadaļā</h2>
<h3>Plānie sleeve apvalki</h3>
<p>Sleeve apvalks (notebook somām dažkārt saukts par notebook ietvaru) ir mīksts polsterēts maks, kura izmērs precīzi atbilst klēpjdatora ekrāna diagonālei. Tā uzdevums ir aizsardzība pret triecieniem un nodilumu, kamēr klēpjdators atrodas citas somas, mugursomas vai pat tirzniecības somas iekšpusē. Sleeve apvalki ir noderīgi, kad lietotājam jau ir iemīļota soma un viņš vienkārši vēlas tajā aizsargāt klēpjdatoru. Meklējiet memory-foam polsterējumu, ciešu pieguļumu un mīkstu iekšpusi, kas neskrāpē vāku.</p>
<h3>Pleca somas un portfeļi</h3>
<p>Pleca somas, kuriera somas un portfeļi (klasiskās notebook somas) ievieto klēpjdatoru strukturētā polsterētā nodalījumā ar atsevišķām kabatiņām lādētājam, kabeļiem, dokumentiem un sīkiem piederumiem. Tās der īsiem biroja braucieniem un sapulcēm, kur klēpjdators dienā tiek izņemts un nolikts atpakaļ vairākas reizes. Izvēlieties pēc aizdares (rāvējslēdzējs, magnētiskā atloka, klipša), siksnas ērtuma un priekšējās kabatas izkārtojuma.</p>
<h3>Mugursomas</h3>
<p>Mugursomas (klēpjdatoru mugursomas, notebook somas mugursomas formātā) sadala svaru pa abiem pleciem un atbrīvo abas rokas, kas tās padara par praktisku izvēli riteņbraukšanai, sabiedriskajam transportam, garākiem gājieniem un ceļojumu dienām. Polsterētais klēpjdatora nodalījums parasti ir atsevišķa aizmugures kabata ar savu rāvējslēdzēju; labākajos dizainos klēpjdators atrodas tuvu mugurkaulam līdzsvaram. Meklējiet polsterētas siksnas, krūšu klipsi, bagāžas siksnas caurumu ceļojumiem un ūdens izturīgu audumu.</p>
<h2>Pareizā izmēra un formāta izvēle</h2>
<h3>Saskaņojiet izmēru ar klēpjdatoru, ne ar somu</h3>
<p>Somas un sleeve apvalki ir mērīti collās: 13,3, 14, 15,6, 17,3. Soma, kas marķēta 15 collu klēpjdatoram, iederēsies lielākajai daļai 14 un 15,6 collu klēpjdatoru, bet 17 collu klēpjdators neiederēsies 15 collu somā, pat ja izskatās tuvu. Vienmēr pārbaudiet klēpjdatora ekrāna diagonāli ražotāja specifikācijā, ne pēc mārketinga nosaukuma.</p>
<h3>Saskaņojiet formātu ar rutīnu</h3>
<p>Piecas dienas nedēļā vienā birojā: sleeve apvalks esošās somas iekšpusē ir pietiekams. Ikdienas brauciens ar auto vai īss gājiens: pleca soma ar vienu vai diviem klēpjdatoriem un dažiem piederumiem. Riteņbraukšana, sabiedriskais transports, garāki ceļojumi: mugursoma ar krūšu klipsi un bagāžas siksnas caurumu. Divu klēpjdatoru pārnēsāšana (darba plus personīgais) parasti ir brīdis, kad pāriet uz mugursomu jebkurā gadījumā.</p>
<h3>Polsterējums, ūdens izturība un kabīnes saderība</h3>
<p>Polsterējums ir vissvarīgākais tur, kur klēpjdators atrodas tuvāk ārējai sienai, tāpēc mugursomas klēpjdatora nodalījumi parasti ir izvietoti pret mugurpaneli, ne pret ārējo virsmu. Ūdens izturīgs ārējais audums un nosegts rāvējslēdzējs uz klēpjdatora nodalījuma neielaiž vieglu lietu; pilnīgi ūdensnecaurlaidīgs materiāls ir reti un dārgs. Ceļojumiem pārbaudiet somu pret biežāk lietoto aviokompāniju kabīnes bagāžas izmēru ierobežojumiem.</p>
<h2>Biežāk uzdotie jautājumi</h2>
<h3>Sleeve apvalks, soma vai mugursoma — ar ko sākt?</h3>
<p>Ja klēpjdators jau ceļo citā somā, sleeve apvalks ir pietiekams. Ja lielākā daļa dienu ir biroja-uz-biroju ar īsu braucienu, pleca soma vai portfelis ir praktiskais noklusējums. Ja maršruts ietver riteņbraukšanu, gājienus, sabiedrisko transportu vai jebko citu nēsājamu, mugursoma ir labāka ikdienas izvēle.</p>
<h3>Vai 15 collu soma der 14 collu klēpjdatoram?</h3>
<p>Parasti jā, bet klēpjdators kustēsies polsterētā nodalījuma iekšpusē. Garos pārnēsāšanas maršrutos šī kustība rada nodilumu; īsiem braucieniem tas nav īpaši svarīgi. Cieši pieguļošs sleeve apvalks plus plašāka ārējā soma ir drošāka kombinācija garā maršrutā.</p>
<h3>Vai mugursomas klēpjdatora nodalījumu var izlaist, ja klēpjdatoram jau ir sleeve apvalks?</h3>
<p>Var; daudzas mugursomas klēpjdatora nodalījumu uzskata vienkārši par polsterētu kabatu, un sleeve apvalks pievieno otru aizsardzības slāni. Šī kombinācija ir bieža ikdienas braucienu lietotāju vidū, kas nēsā dārgas vai jutīgas ierīces.</p>
<h3>Kā notebook soma aizsargā pret kritieniem?</h3>
<p>Lielākā daļa klēpjdatoru somu aizsargā pret triecieniem normālas lietošanas laikā: somas nokrišana no galda augstuma uz cietas grīdas, sasišana pret durvju rāmjiem vai sabiedriskā transporta triecieniem. Smagi kritieni (vairāku stāvu kritieni, cieti triecieni stūros) pārsniedz to, ko parasta polsterēta soma var absorbēt. Šādam aizsardzības līmenim Rugged klēpjdatora futrāļi ar pastiprinātiem stūriem ir atsevišķa produktu klase.</p>
""",
    },
}


def apply(conn):
    with conn.cursor() as cur:
        for code, fields in PAGES.items():
            sets, vals = [], []
            for k, v in fields.items():
                sets.append(f"{k} = %s")
                vals.append(v)
            vals.append(code)
            cur.execute(
                f"UPDATE tree_nodes SET {', '.join(sets)} WHERE code = %s",
                vals,
            )
    print(f"  applied editor-feedback rewrites to {len(PAGES)} pages")
