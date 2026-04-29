"""
Hand-rewrite the 8 pages flagged by migration 012's audit as having a
duplicated opening structure.

The agent that wrote the other/* branch used a template that:
  - duplicated seo_desc into the bottom_seo first paragraph
  - echoed the subcategory list in the next paragraph
  - added "use the subcategory navigation to drill down" boilerplate
  - mentioned "B2B team", "volume tier pricing", "VAT invoicing" repeatedly
  - mixed warranty language outside manufacturer context

This migration replaces bottom_seo on those 8 pages with category-specific
content: distinct intros, brief subcategory descriptions, real buying
considerations and 3-4 page-specific FAQs.

Safe-update: replaces fields outright; the editor will manually re-edit
through the UI if they touch any of these between deploy and review.
"""

PAGES = {
    # ─────────────────── 1. personal-care ─────────────────────────────────
    "other/home-lifestyle/personal-care": {
        "bottom_seo_en": """\
<h2>Personal care appliances for daily routines, salons and hospitality buyers</h2>
<p>Personal care covers the small electrical appliances people use directly on the body: brushing teeth, drying and styling hair, shaving and trimming, and a long tail of specialist beauty devices. The buying drivers are skin contact (so hygiene of replaceable heads matters), travel suitability (size, voltage, plug type) and consumables availability over the device's life. This subcategory groups four product groups so a household, a salon or a hotel housekeeping team can compare like for like.</p>
<h3>Subcategories at a glance</h3>
<p>Dental care covers electric toothbrushes, water flossers and the replacement heads they consume. Hair care covers dryers, straighteners and curling tools by wattage and barrel size. Shavers and trimmers split between wet/dry electric razors, beard trimmers and body groomers. Other beauty appliances bundle facial cleansing, IPL hair removal and similar specialist devices that do not fit the first three groups.</p>
<h3>What actually matters when buying</h3>
<p>Replaceable head availability is the single biggest cost driver after the device itself; a brush whose heads cost more than the brush after two years is a poor choice. For travel, dual-voltage and a folding handle are practical wins. For salons and hotels, look at duty cycle (how long the device runs continuously before needing a cool-down) and IP rating where it sits near sinks.</p>
<h3>Frequently asked questions</h3>
<h4>What is included in the Personal Care subcategory?</h4>
<p>Electric toothbrushes and water flossers, hair dryers and styling tools, electric shavers and trimmers, and a smaller group of specialist beauty appliances such as facial cleansing brushes and IPL hair removal devices.</p>
<h4>How long do replacement heads typically last?</h4>
<p>Toothbrush heads three months under daily use, shaver foils and blades 12 to 18 months depending on hair coarseness, hair styling tools have no consumables but will need replacement after a few thousand uses depending on heat setting habits.</p>
<h4>Are these appliances suitable for hotel rooms?</h4>
<p>Hair dryers and shavers are commonly fitted in hotel rooms; specifications worth checking are wattage, attachment storage and the noise rating for late-night use. Toothbrushes and personal grooming tools are normally guest-supplied rather than room-supplied.</p>
""",
        "bottom_seo_lv": """\
<h2>Personīgās kopšanas ierīces ikdienai, saloniem un viesnīcu pircējiem</h2>
<p>Personīgā kopšana aptver mazās elektriskās ierīces, ko cilvēki lieto tieši uz ķermeņa: zobu tīrīšana, matu žāvēšana un veidošana, skūšanās un trimmēšana, un garš specializēto skaistumkopšanas ierīču saraksts. Iegādes virzītāji ir saskare ar ādu (tāpēc nomaināmo galviņu higiēna ir svarīga), piemērotība ceļojumiem (izmērs, spriegums, kontaktdakšas tips) un izejmateriālu pieejamība ierīces darbības laikā. Šī apakškategorija sakārto četras produktu grupas, lai mājsaimniecība, salons vai viesnīcas apkalpošanas komanda varētu salīdzināt līdzīgu ar līdzīgu.</p>
<h3>Apakškategorijas īsumā</h3>
<p>Zobu kopšana aptver elektriskās zobu birstes, ūdens flosus un nomaināmās galviņas, ko tās patērē. Matu kopšana aptver fēnus, taisnotājus un lokšķēres pēc jaudas un cilindra izmēra. Skuvekļi un trimmeri sadalās starp slapjiem un sausiem elektriskajiem skuvekļiem, bārdas trimmeriem un ķermeņa kopšanas ierīcēm. Citas skaistumkopšanas ierīces apvieno sejas tīrīšanu, IPL matu noņemšanu un līdzīgas specializētās ierīces, kas neietilpst pirmajās trijās grupās.</p>
<h3>Kas patiesībā ir svarīgi pirkšanas brīdī</h3>
<p>Nomaināmo galviņu pieejamība ir lielākais izmaksu virzītājs pēc pašas ierīces; birste, kuras galviņas pēc diviem gadiem maksā vairāk nekā pati birste, ir slikta izvēle. Ceļošanai praktiskas priekšrocības ir divi spriegumi un salokāms rokturis. Saloniem un viesnīcām vērā ņemams ir darba cikls (cik ilgi ierīce darbojas nepārtraukti pirms atdzesēšanas) un IP klase tur, kur tā atrodas pie izlietnes.</p>
<h3>Biežāk uzdotie jautājumi</h3>
<h4>Kas iekļauts personīgās kopšanas apakškategorijā?</h4>
<p>Elektriskās zobu birstes un ūdens flosi, matu fēni un veidošanas rīki, elektriskie skuvekļi un trimmeri un mazāka specializēto skaistumkopšanas ierīču grupa, piemēram, sejas tīrīšanas birstes un IPL matu noņemšanas ierīces.</p>
<h4>Cik ilgi parasti kalpo nomaināmās galviņas?</h4>
<p>Zobu birstes galviņas trīs mēnešus ikdienas lietošanā, skuvekļa tīkliņi un asmeņi 12 līdz 18 mēnešus atkarībā no apmatojuma raupjuma, matu veidošanas rīkiem nav izejmateriālu, bet tie būs jānomaina pēc dažiem tūkstošiem lietojumu atkarībā no karstuma iestatījumu paradumiem.</p>
<h4>Vai šīs ierīces ir piemērotas viesnīcu numuriem?</h4>
<p>Matu fēni un skuvekļi parasti tiek uzstādīti viesnīcu numuros; specifikācijas, kuras vērts pārbaudīt, ir jauda, piederumu glabāšana un trokšņa līmenis vēlās stundās. Zobu birstes un personīgās kopšanas rīki parasti ir viesa līdzpaņemti, ne numura piederums.</p>
""",
    },

    # ─────────────────── 2. small-household-lamps ─────────────────────────
    "other/home-lifestyle/small-household-lamps": {
        "bottom_seo_en": """\
<h2>Small household appliances and lighting for homes, offices and short-stay venues</h2>
<p>This subcategory groups the small electricals that sit on tables, counters and floors rather than in the kitchen or bathroom proper: clocks and alarm clocks for bedside and reception, light bulbs, lamps and fixtures for ambient and task lighting, and a wider group of small household devices like irons, fans and dehumidifiers. Buying decisions usually centre on energy use, expected operating life and replacement-bulb compatibility for fixtures.</p>
<h3>Subcategories at a glance</h3>
<p>Clocks and alarm clocks split between traditional analog, digital LED and smart variants with phone integration. Light bulbs, lamps and fixtures run from individual LED bulbs by socket type to complete table and floor lamps with integrated drivers. Other small appliances cover irons, fans, dehumidifiers and the smaller assorted devices that do not have their own dedicated subcategory yet.</p>
<h3>What actually matters when buying</h3>
<p>For lighting, lumen output and colour temperature (Kelvins) are more useful than wattage for comparing modern LED products. Socket type (E27, E14, GU10) decides which bulbs fit the fixture. For irons and fans look at wattage, water tank size for steam irons, and noise level for fans used in bedrooms. Small household appliances rarely sit unused, so duty cycle and warranty terms matter.</p>
<h3>Frequently asked questions</h3>
<h4>How do I compare LED bulbs?</h4>
<p>Compare lumens (brightness), colour temperature in Kelvins (2700K is warm white, 4000K is neutral, 6500K is daylight), beam angle for spotlights and dimming compatibility. Wattage is a secondary measure for LED products; lumens carry more useful information.</p>
<h4>Are these products covered by manufacturer warranty?</h4>
<p>Yes; manufacturer warranty terms vary by brand and product class. Lighting products typically carry one to three years, small household appliances one to two years. Specific terms appear on each product listing.</p>
<h4>Which products fit short-stay rentals best?</h4>
<p>For short-stay rentals look at robust standard formats (E27 LED bulbs, simple bedside alarm clocks, basic irons and fans) over premium or smart variants. Replacement availability and price matter more than feature depth at this scale.</p>
""",
        "bottom_seo_lv": """\
<h2>Mazās sadzīves ierīces un apgaismojums mājām, birojiem un īstermiņa īres vietām</h2>
<p>Šī apakškategorija sakārto mazos elektriskos priekšmetus, kas atrodas uz galdiem, leticēm un grīdām, ne tieši virtuvē vai vannas istabā: pulksteņi un modinātāji gultas malai un reģistratūrai, spuldzes, lampas un gaismekļi vispārīgam un darba apgaismojumam, kā arī plašāka mazo mājsaimniecības ierīču grupa, piemēram, gludekļi, ventilatori un mitruma savācēji. Pirkšanas lēmumus parasti virza enerģijas patēriņš, paredzamais darbības laiks un nomaināmo spuldžu saderība gaismekļiem.</p>
<h3>Apakškategorijas īsumā</h3>
<p>Pulksteņi un modinātāji sadalās starp tradicionālajiem analogiem, digitāliem LED un viediem variantiem ar telefona integrāciju. Spuldzes, lampas un gaismekļi sniedzas no atsevišķām LED spuldzēm pēc cokola tipa līdz pilnām galda un grīdas lampām ar integrētiem draiveriem. Citas mazās sadzīves ierīces aptver gludekļus, ventilatorus, mitruma savācējus un mazāku dažādu ierīču grupu, kurām vēl nav atsevišķas apakškategorijas.</p>
<h3>Kas patiesībā ir svarīgi pirkšanas brīdī</h3>
<p>Apgaismojumam lūmena izvade un krāsu temperatūra (Kelvinos) ir noderīgāka par jaudu modernās LED produktu salīdzināšanai. Cokola tips (E27, E14, GU10) nosaka, kuras spuldzes der gaismeklim. Gludekļiem un ventilatoriem skatieties uz jaudu, ūdens tvertnes izmēru tvaika gludekļiem un trokšņa līmeni guļamistabā lietotiem ventilatoriem. Mazās sadzīves ierīces reti stāv neizmantotas, tāpēc darba cikls un ražotāja garantijas nosacījumi ir svarīgi.</p>
<h3>Biežāk uzdotie jautājumi</h3>
<h4>Kā salīdzināt LED spuldzes?</h4>
<p>Salīdziniet lūmenus (spilgtumu), krāsu temperatūru Kelvinos (2700K ir silti balta, 4000K neitrāla, 6500K dienasgaisma), staru leņķi prožektoriem un dimmēšanas saderību. Jauda ir sekundārs mērs LED produktiem; lūmeni nes noderīgāku informāciju.</p>
<h4>Vai šie produkti ir nodrošināti ar ražotāja garantiju?</h4>
<p>Jā; ražotāja garantijas nosacījumi atšķiras pēc zīmola un produktu klases. Apgaismojuma produktiem parasti ir viens līdz trīs gadi, mazajām sadzīves ierīcēm viens līdz divi gadi. Konkrēti nosacījumi parādās katra produkta lapā.</p>
<h4>Kuri produkti vislabāk der īstermiņa īrēm?</h4>
<p>Īstermiņa īrēm skatieties uz izturīgiem standarta formātiem (E27 LED spuldzes, vienkārši gultas modinātāji, pamata gludekļi un ventilatori), nevis uz premium vai viediem variantiem. Nomaiņas pieejamība un cena ir svarīgāka par funkciju dziļumu šajā mērogā.</p>
""",
    },

    # ─────────────────── 3. sport-outdoor-hobbies ─────────────────────────
    "other/home-lifestyle/sport-outdoor-hobbies": {
        "bottom_seo_en": """\
<h2>Sport, outdoor and hobby gear from short trips to seasonal venues</h2>
<p>This subcategory covers personal mobility, outdoor lighting, swimming pool gear and a broader group of sport and hobby accessories. Buyers range from individual users equipping a hobby to seasonal venues kitting out a rental fleet, so the practical concerns are battery life and charging logistics for mobility devices, IP ratings for anything that lives outdoors, and durability of consumables for gear that gets daily use over a short season.</p>
<h3>Subcategories at a glance</h3>
<p>E-scooters and mobility covers electric scooters, e-bikes accessories and similar short-distance personal transport. Lanterns and illumination cover camping lights, outdoor torches and rechargeable area lamps. Other sport and hobby accessories pull together the long tail of mid-volume gear that does not have a dedicated home yet. Swimming pool accessories cover above-ground pools, robotic and manual cleaners, and chemical kits.</p>
<h3>What actually matters when buying</h3>
<p>For e-scooters, range claims under load are more useful than peak range; check rider weight ratings against actual users. For outdoor lighting, IP rating (IP65 for occasional rain, IP67 for full immersion) and run-time at full brightness matter more than maximum lumens. For pool gear match the cleaner type to pool size and bottom material.</p>
<h3>Frequently asked questions</h3>
<h4>What e-scooter range is realistic?</h4>
<p>Manufacturer range numbers assume a single light rider, smooth flat road and conservative speed. Real-world range with a heavier rider, hills and stop-start traffic is usually 40 to 60 percent of the headline figure. Pick a model rated 50 to 70 percent above the longest commute.</p>
<h4>Are these products warranted by the manufacturer?</h4>
<p>Yes; manufacturer warranty cover is on each product listing. E-scooters and e-bikes typically carry one to two years on the frame and shorter cover on battery and consumables. Outdoor lighting commonly two years.</p>
<h4>Do you stock seasonal pool gear year-round?</h4>
<p>Pool stock peaks before summer and tails off in autumn; chemicals and replacement parts are usually available year-round. For seasonal venues placing volume orders, plan a few weeks ahead of opening.</p>
""",
        "bottom_seo_lv": """\
<h2>Sporta, brīvā laika un āra preces no īsiem braucieniem līdz sezonas vietām</h2>
<p>Šī apakškategorija aptver personīgo mobilitāti, āra apgaismojumu, peldbaseinu aprīkojumu un plašāku sporta un brīvā laika piederumu grupu. Pircēji svārstās no individuāliem lietotājiem, kas aprīko hobiju, līdz sezonas vietām, kas komplektē nomas parku, tāpēc praktiskie aspekti ir akumulatora darbības laiks un uzlādes loģistika mobilajām ierīcēm, IP klases visam, kas dzīvo ārā, un izejmateriālu izturība aprīkojumam, ko izmanto ikdienā īsā sezonā.</p>
<h3>Apakškategorijas īsumā</h3>
<p>Elektriskie skūteri un mobilitāte aptver elektriskos skūterus, e-velosipēdu piederumus un līdzīgu īsa attāluma personīgo transportu. Laternas un apgaismojums aptver tūrisma gaismas, āra lukturus un lādējamas teritorijas lampas. Citi sporta un brīvā laika piederumi apkopo plašu vidējā apjoma aprīkojumu, kam vēl nav atsevišķa miteklis. Peldbaseinu piederumi aptver virszemes baseinus, robotizētus un manuālus tīrītājus un ķīmijas komplektus.</p>
<h3>Kas patiesībā ir svarīgi pirkšanas brīdī</h3>
<p>Elektriskajiem skūteriem brauciena attāluma deklarācijas zem slodzes ir noderīgākas par maksimālo attālumu; pārbaudiet braucēja svara reitingus pret reāliem lietotājiem. Āra apgaismojumam IP klase (IP65 dažreizējam lietum, IP67 pilnai iegremdēšanai) un darbības laiks pilnā spilgtumā ir svarīgāki par maksimālajiem lūmeniem. Baseinu aprīkojumam saskaņojiet tīrītāja tipu ar baseina izmēru un dibena materiālu.</p>
<h3>Biežāk uzdotie jautājumi</h3>
<h4>Kāds elektriskā skūtera attālums ir reālistisks?</h4>
<p>Ražotāja attāluma skaitļi pieņem vienu vieglu braucēju, līdzenu gludu ceļu un konservatīvu ātrumu. Reāls attālums ar smagāku braucēju, kalniem un pārtraucamu plūsmu parasti ir 40 līdz 60 procenti no virsraksta skaitļa. Izvēlieties modeli, kas reitingots par 50 līdz 70 procentiem virs garākā brauciena.</p>
<h4>Vai šie produkti ir nodrošināti ar ražotāja garantiju?</h4>
<p>Jā; ražotāja garantijas segums ir katrā produkta sarakstā. Elektriskajiem skūteriem un e-velosipēdiem parasti ir viens līdz divi gadi rāmim un īsāks segums akumulatoriem un izejmateriāliem. Āra apgaismojumam parasti divi gadi.</p>
<h4>Vai sezonas baseinu aprīkojums ir pieejams visu gadu?</h4>
<p>Baseinu krājumi sasniedz maksimumu pirms vasaras un samazinās rudenī; ķīmiskās vielas un nomaiņas daļas parasti ir pieejamas visu gadu. Sezonas vietām, kas veic apjoma pasūtījumus, plānojiet dažas nedēļas pirms atvēršanas.</p>
""",
    },

    # ─────────────────── 4. vacuums-cleaning ──────────────────────────────
    "other/home-lifestyle/vacuums-cleaning": {
        "bottom_seo_en": """\
<h2>Vacuums and cleaning equipment for households, rentals and facility teams</h2>
<p>Cleaning equipment splits cleanly along two axes: who uses it (consumer vs facility team) and what is being cleaned (floors only vs upholstery, vehicle interiors, outdoor surfaces). This subcategory groups vacuum accessories that consume in daily use, robot vacuums that automate routine floor care, and a broader cleaning group covering mops, carpet cleaners and patio washers. Each subcategory carries its own buyer mix, from individual households to short-stay rentals and small commercial sites.</p>
<h3>Subcategories at a glance</h3>
<p>Vacuum accessories cover replacement bags, filters, brush heads and battery packs that vacuums need on a recurring schedule. Robot vacuums and accessories cover the autonomous floor cleaners and the docking stations, replacement brushes and bin liners they consume. Mops, carpet and patio cleaners cover wet/dry floor cleaning, carpet shampoo machines and pressure-style patio washers for outdoor surfaces.</p>
<h3>What actually matters when buying</h3>
<p>For vacuums, suction in air watts is more useful than nominal motor wattage; bag-vs-bagless decides ongoing consumable cost; battery vacuums beat corded only past a certain rental size. For robots, mapping accuracy and floor-type detection matter more than maximum suction. For carpet and patio cleaners, water/solution capacity decides how much surface a single tank covers.</p>
<h3>Frequently asked questions</h3>
<h4>Bag or bagless vacuum?</h4>
<p>Bagless is cheaper to run (no bag refills) but messier to empty and the pre-filter needs cleaning more often. Bagged is hygienic and convenient but ongoing bag cost adds up over the life of the device. For households with allergies, bagged with HEPA filtration usually wins.</p>
<h4>Are robot vacuums good enough to replace a regular vacuum?</h4>
<p>For routine floor maintenance on hard floors and short-pile carpet, yes. For deep cleaning, edges, stairs and upholstery a regular vacuum is still needed. Most homes use both: the robot handles daily upkeep, the regular vacuum handles weekly deep clean.</p>
<h4>Are these products covered by manufacturer warranty?</h4>
<p>Yes; manufacturer warranty terms are on each product page. Vacuums and robot vacuums commonly carry two years; consumables (bags, filters, brushes) are not covered as they are wear items.</p>
""",
        "bottom_seo_lv": """\
<h2>Putekļsūcēji un tīrīšanas aprīkojums mājsaimniecībām, īrēm un objektu komandām</h2>
<p>Tīrīšanas aprīkojums sadalās pa divām asīm: kas to lieto (patērētājs vai objekta komanda) un kas tiek tīrīts (tikai grīdas vai mīkstās mēbeles, automobiļu salons, āra virsmas). Šī apakškategorija sakārto putekļsūcēju piederumus, kas tiek patērēti ikdienā, robotu putekļsūcējus, kas automatizē regulāru grīdas kopšanu, un plašāku tīrīšanas grupu, kas aptver mopus, paklāju tīrītājus un terašu mazgātājus. Katrai apakškategorijai ir savs pircēju sastāvs, no individuālām mājsaimniecībām līdz īstermiņa īrēm un maziem komerciāliem objektiem.</p>
<h3>Apakškategorijas īsumā</h3>
<p>Putekļsūcēju piederumi aptver nomaiņas maisus, filtrus, sukas galviņas un akumulatoru blokus, kas putekļsūcējiem nepieciešami regulāri. Robotu putekļsūcēji un piederumi aptver autonomos grīdas tīrītājus un dokstacijas, nomaiņas sukas un tvertņu maisus, ko tie patērē. Mopi, paklāju un terašu tīrītāji aptver slapju un sausu grīdas tīrīšanu, paklāju šampūna mašīnas un spiediena tipa terašu mazgātājus āra virsmām.</p>
<h3>Kas patiesībā ir svarīgi pirkšanas brīdī</h3>
<p>Putekļsūcējiem sūkšana gaisa vatos ir noderīgāka par nominālo motora jaudu; maisa pret bezmaisa izvēle nosaka pastāvīgās izejmateriālu izmaksas; akumulatoru putekļsūcēji pārspēj vada modeļus tikai pēc noteikta īres izmēra. Robotiem kartēšanas precizitāte un grīdas tipa noteikšana ir svarīgāka par maksimālo sūkšanu. Paklāju un terašu tīrītājiem ūdens vai šķīduma ietilpība nosaka, cik daudz virsmas viena tvertne aptver.</p>
<h3>Biežāk uzdotie jautājumi</h3>
<h4>Maisa vai bezmaisa putekļsūcējs?</h4>
<p>Bezmaisa ir lētāks darbībā (nav maisa papildinājumu), bet netīrāks iztukšošanā, un priekšfiltrs jātīra biežāk. Maisa modelis ir higiēnisks un ērts, bet pastāvīgās maisa izmaksas summējas ierīces darbības laikā. Mājsaimniecībām ar alerģijām maisa modelis ar HEPA filtrāciju parasti uzvar.</p>
<h4>Vai robotu putekļsūcēji ir pietiekami labi, lai aizvietotu parasto putekļsūcēju?</h4>
<p>Regulārai grīdas uzturēšanai uz cietām grīdām un īsa pūka paklājiem jā. Dziļai tīrīšanai, malām, kāpnēm un mīkstajām mēbelēm joprojām nepieciešams parasts putekļsūcējs. Lielākā daļa māju izmanto abus: robots veic ikdienas uzturēšanu, parastais putekļsūcējs veic iknedēļas dziļo tīrīšanu.</p>
<h4>Vai šie produkti ir nodrošināti ar ražotāja garantiju?</h4>
<p>Jā; ražotāja garantijas nosacījumi ir katrā produkta lapā. Putekļsūcējiem un robotu putekļsūcējiem parasti ir divi gadi; izejmateriāli (maisi, filtri, sukas) nav segti, jo tie ir nolietojuma daļas.</p>
""",
    },

    # ─────────────────── 5. office-equipment-furniture ────────────────────
    "other/office-equipment-furniture": {
        "bottom_seo_en": """\
<h2>Office equipment and furniture from single-room setups to multi-floor fit-outs</h2>
<p>Office equipment and furniture is the part of the catalog where the buying stops being about technology and starts being about how people will sit and work for eight hours a day. This category covers the desks and chairs that hold the monitors, the ergonomic add-ons that soften long sitting hours, and the everyday office stationery that the IT side rarely thinks about. The buying scale ranges from a single home office to a whole floor of identical workstations.</p>
<h3>Subcategories at a glance</h3>
<p>Desks, trolleys and chairs cover the structural pieces: standing and fixed-height desks, mobile trolleys for hot-desking, ergonomic and basic task chairs. Workspace ergonomics covers the upgrade layer: monitor arms, keyboard trays, footrests, anti-fatigue mats. Office stationery covers the consumable layer: pens, paper, organisers and the small items every office reorders monthly.</p>
<h3>What actually matters when buying</h3>
<p>For desks the practical specs are working surface area, cable routing, and (for height-adjustable) lift speed and weight capacity with monitors loaded. For chairs the long-day comfort drivers are seat depth adjustment, lumbar support shape and armrest mobility, not headline marketing. For ergonomics, monitor arm reach and weight capacity decide which monitors fit.</p>
<h3>Frequently asked questions</h3>
<h4>Standing or sitting desk for a typical office?</h4>
<p>Height-adjustable desks have become the default for new offices because they let one desk fit different users and different parts of the day. Pure standing desks are rarer; pure sitting desks are still common where desk height never needs to change.</p>
<h4>Are these products warranted by the manufacturer?</h4>
<p>Yes; manufacturer warranty terms are on each product page. Office furniture commonly carries five to ten years on the structure (desk frame, chair base) and shorter cover on textile and fabric components.</p>
<h4>How many monitors fit a typical desk?</h4>
<p>Most 140 cm desks fit two 27 inch monitors comfortably, three with monitor arms positioned over the desk back. 160 cm desks fit three 27 inch monitors directly. Triple-monitor setups usually need monitor arms rather than feet to free up the working surface.</p>
""",
        "bottom_seo_lv": """\
<h2>Biroja aprīkojums un mēbeles no vienas telpas uzstādījumiem līdz vairāku stāvu iekārtošanai</h2>
<p>Biroja aprīkojums un mēbeles ir kataloga daļa, kur iegāde vairs nav par tehnoloģijām un kļūst par to, kā cilvēki sēdēs un strādās astoņas stundas dienā. Šī kategorija aptver galdus un krēslus, kas tur monitorus, ergonomiskos papildinājumus, kas padara garas sēdēšanas stundas vieglākas, un ikdienas biroja kancelejas preces, par ko IT puse reti domā. Iegādes mērogs svārstās no vienas mājas biroja līdz veselai stāvu identisku darbavietu klāstam.</p>
<h3>Apakškategorijas īsumā</h3>
<p>Galdi, ratiņi un krēsli aptver strukturālās daļas: augstuma regulējami un fiksētu augstumu galdi, mobilie ratiņi koplietojamām darbavietām, ergonomiskie un pamata darba krēsli. Darbavietas ergonomika aptver uzlabojumu slāni: monitora rokas, tastatūras paplātes, kāju balsti, pretnoguruma paklāji. Biroja kancelejas preces aptver patērējamo slāni: pildspalvas, papīrs, organizatori un mazie priekšmeti, ko katrs birojs pārpasūta katru mēnesi.</p>
<h3>Kas patiesībā ir svarīgi pirkšanas brīdī</h3>
<p>Galdiem praktiskās specifikācijas ir darba virsmas laukums, kabeļu vadīšana un (augstuma regulējamiem) celšanas ātrums un svara ietilpība ar monitoriem. Krēsliem garas dienas komforta virzītāji ir sēdekļa dziļuma regulēšana, jostas balsta forma un roku balstu kustīgums, ne virsraksta mārketings. Ergonomikai monitora rokas sniedzamība un svara ietilpība nosaka, kuri monitori ietilpst.</p>
<h3>Biežāk uzdotie jautājumi</h3>
<h4>Stāvošs vai sēdošs galds tipiskam birojam?</h4>
<p>Augstuma regulējami galdi ir kļuvuši par jauno biroju noklusējumu, jo tie ļauj vienam galdam derēt dažādiem lietotājiem un dažādām dienas daļām. Tīri stāvoši galdi ir retāki; tīri sēdoši galdi joprojām ir izplatīti tur, kur galda augstumam nav jāmainās.</p>
<h4>Vai šie produkti ir nodrošināti ar ražotāja garantiju?</h4>
<p>Jā; ražotāja garantijas nosacījumi ir katrā produkta lapā. Biroja mēbelēm parasti ir piecu līdz desmit gadu segums struktūrai (galda rāmis, krēsla pamatne) un īsāks segums tekstila un auduma komponentiem.</p>
<h4>Cik monitoru ietilpst tipiskā galdā?</h4>
<p>Lielākā daļa 140 cm galdu ērti ietilpina divus 27 collu monitorus, trīs ar monitora rokām, kas novietotas pāri galda aizmugurei. 160 cm galdi ietilpina trīs 27 collu monitorus tieši. Trīs monitoru uzstādījumiem parasti nepieciešamas monitora rokas, ne pamatnes, lai atbrīvotu darba virsmu.</p>
""",
    },

    # ─────────────────── 6. power-tools-garden ────────────────────────────
    "other/power-tools-garden": {
        "bottom_seo_en": """\
<h2>Power tools and garden equipment for trades, hobbyists and grounds maintenance</h2>
<p>Power tools and garden equipment is the catalog section where the buyer profile shifts hardest from individual hobbyist to professional trade, with prosumer in between. The same drill, saw or trimmer in different price tiers serves a homeowner doing a once-a-year project, a serious DIYer, and a tradesperson using it daily. This category groups workshop tools and outdoor garden equipment so a single buyer can compare across both branches.</p>
<h3>Subcategories at a glance</h3>
<p>Power tools and workwear cover drills, drivers, saws, sanders, the safety wear that goes with them and the workshop accessories that support them. Garden equipment covers everything that maintains outdoor spaces: lawn mowers, grass trimmers, leaf blowers, pressure washers and water pumps. Each branch carries its own consumable layer (drill bits, saw blades, line for trimmers).</p>
<h3>What actually matters when buying</h3>
<p>For battery tools, the battery platform decides total cost more than the individual tool: a buyer building up a kit on one battery family pays much less per added tool than a buyer mixing brands. For garden equipment, work area decides everything: cordless tools beat corded above garden size X, ride-on mowers beat walk-behind above lawn size Y. Match power source to hours of use per session.</p>
<h3>Frequently asked questions</h3>
<h4>Should I buy corded or cordless power tools?</h4>
<p>For occasional household use, cordless is more practical: no extension lead drama, faster setup. For workshop use where a single point of work has constant mains nearby, corded is cheaper at the same power level and never runs out. Trades commonly carry both.</p>
<h4>Which battery platform should a homeowner pick?</h4>
<p>Pick the platform that has the tools you actually use most often, not the one with the longest catalog. A buyer who needs a drill, a circular saw and a hedge trimmer should buy whichever brand makes the best version of those three; the rest of the catalog is irrelevant.</p>
<h4>Are these products covered by manufacturer warranty?</h4>
<p>Yes; manufacturer warranty terms are on each product listing. Power tools commonly carry two to three years (longer with brand registration), garden equipment two years, batteries shorter cover than the tool. Trade-grade products often carry longer terms.</p>
""",
        "bottom_seo_lv": """\
<h2>Elektriskie instrumenti un dārza aprīkojums amatniekiem, hobistiem un teritorijas uzturētājiem</h2>
<p>Elektriskie instrumenti un dārza aprīkojums ir kataloga sadaļa, kur pircēja profils visstraujāk pāriet no individuāla hobista uz profesionālu amatnieku, ar prosumer pa vidu. Tāds pats urbis, zāģis vai trimmeris dažādos cenu līmeņos kalpo māju īpašniekam, kas dara reizi gadā projektu, nopietnam DIY entuziastam un amatniekam, kas to lieto ikdienā. Šī kategorija sakārto darbnīcas instrumentus un āra dārza aprīkojumu, lai viens pircējs varētu salīdzināt abās zaros.</p>
<h3>Apakškategorijas īsumā</h3>
<p>Elektriskie instrumenti un darba apģērbs aptver urbjus, skrūvgriežus, zāģus, slīpmašīnas, drošības apģērbu, kas tiem paredzēts, un darbnīcas piederumus, kas tos atbalsta. Dārza aprīkojums aptver visu, kas uztur āra telpas: zāles pļāvēji, zāles trimmeri, lapu pūtēji, augstspiediena mazgātāji un ūdens sūkņi. Katram zaram ir savs izejmateriālu slānis (urbja gali, zāģa asmeņi, līnija trimmeriem).</p>
<h3>Kas patiesībā ir svarīgi pirkšanas brīdī</h3>
<p>Akumulatoru instrumentiem akumulatora platforma nosaka kopējās izmaksas vairāk nekā atsevišķs instruments: pircējs, kas veido komplektu uz vienas akumulatora saimes, maksā daudz mazāk par katru pievienoto instrumentu nekā tas, kas jauc zīmolus. Dārza aprīkojumam darba laukums nosaka visu: bezvada instrumenti pārspēj vada modeļus virs noteikta dārza izmēra, brauktuvēs ar pļāvējiem pārspēj staigāšanas pļāvējus virs noteikta zālāja izmēra. Saskaņojiet enerģijas avotu ar darba stundām vienā sesijā.</p>
<h3>Biežāk uzdotie jautājumi</h3>
<h4>Vai pirkt vada vai bezvada elektriskos instrumentus?</h4>
<p>Reizēm mājsaimniecības lietošanai bezvada ir praktiskāks: nav pagarinātāja drāmas, ātrāka iestatīšana. Darbnīcas lietošanai, kur viens darba punkts ir blakus tīklam, vada modelis ir lētāks tādā pašā jaudas līmenī un nekad neizsīkst. Amatnieki parasti nēsā abus.</p>
<h4>Kuru akumulatoru platformu izvēlēties māju īpašniekam?</h4>
<p>Izvēlieties platformu, kurai ir instrumenti, ko jūs patiesi visbiežāk lietojat, ne to ar garāko katalogu. Pircējam, kuram nepieciešams urbis, ripzāģis un dzīvžoga trimmeris, jāpērk tā zīmola, kas izgatavo labāko versiju šiem trim; pārējais katalogs nav būtisks.</p>
<h4>Vai šie produkti ir nodrošināti ar ražotāja garantiju?</h4>
<p>Jā; ražotāja garantijas nosacījumi ir katrā produkta sarakstā. Elektriskajiem instrumentiem parasti ir divi līdz trīs gadi (ilgāks ar zīmola reģistrāciju), dārza aprīkojumam divi gadi, akumulatoriem īsāks segums nekā instrumentam. Amatniecības klases produktiem bieži ir garāki nosacījumi.</p>
""",
    },

    # ─────────────────── 7. renewable-energy ──────────────────────────────
    "other/renewable-energy": {
        "bottom_seo_en": """\
<h2>Renewable energy hardware: solar, batteries, EV charging and portable power</h2>
<p>Renewable energy is one of the more demanding categories in this catalog because the components have to work as a system, not as standalone purchases. A solar panel without an inverter produces nothing useful, an inverter without batteries is useless after sunset, and an EV charger without an adequate supply contract trips the breaker. This category groups every piece a homeowner or small commercial site needs to plan a coherent installation rather than a pile of incompatible parts.</p>
<h3>Subcategories at a glance</h3>
<p>Battery storage covers the home and commercial battery banks that hold solar energy for evening use and grid backup. EV charging covers wallboxes and portable chargers for residential and small fleet use. Power stations cover portable battery generators for camping, off-grid sites and emergency backup. Solar accessories and tools cover installation and maintenance equipment. Solar inverters and optimizers convert and condition the panel output. Solar panels cover the panels themselves by wattage, dimensions and mounting type.</p>
<h3>What actually matters when buying</h3>
<p>The most common mistake is sizing the panels and skipping the battery, then being surprised that excess solar is exported to grid for very little money. Match battery capacity to evening household load. The second most common mistake is choosing an inverter without checking compatibility with the chosen panel and battery brands. The third is installing an EV charger without confirming the property's mains supply can deliver the chosen charging speed.</p>
<h3>Frequently asked questions</h3>
<h4>Can I install solar without batteries?</h4>
<p>Technically yes; the inverter exports excess solar to grid during the day and the property buys electricity back at night. Financially the case for batteries depends heavily on the local export tariff: where export pays poorly, batteries pay back faster.</p>
<h4>Are these products covered by manufacturer warranty?</h4>
<p>Yes; manufacturer warranty terms are on each product page. Solar panels typically carry 20 to 25 year performance warranties and 10 to 12 year product warranties. Inverters carry 5 to 10 years extendable. Batteries carry 7 to 10 years or a stated cycle count.</p>
<h4>Do you supply complete kits or individual components?</h4>
<p>Both. Individual components are available for installers building bespoke systems, complete kits are available for homeowners and small commercial buyers who want a tested combination of panels, inverter, mounting and (optionally) battery storage.</p>
""",
        "bottom_seo_lv": """\
<h2>Atjaunojamās enerģijas aparatūra: saule, baterijas, EV uzlāde un pārnēsājama enerģija</h2>
<p>Atjaunojamā enerģija ir viena no prasīgākajām kategorijām šajā katalogā, jo komponentiem jāstrādā kā sistēmai, ne kā atsevišķiem pirkumiem. Saules panelis bez invertora neražo neko noderīgu, invertors bez baterijām ir bezjēdzīgs pēc saulrieta, un EV lādētājs bez atbilstoša piegādes līguma nosit drošinātāju. Šī kategorija sakārto katru daļu, kas māju īpašniekam vai mazam komerciālam objektam nepieciešama, lai plānotu saskaņotu uzstādīšanu, nevis nesaderīgu detaļu kaudzi.</p>
<h3>Apakškategorijas īsumā</h3>
<p>Bateriju uzkrāšana aptver mājas un komerciālās bateriju bankas, kas tur saules enerģiju vakara lietošanai un tīkla rezervei. EV uzlāde aptver sienas lādētājus un pārnēsājamus lādētājus dzīvojamai un nelielai parka lietošanai. Enerģijas stacijas aptver pārnēsājamos bateriju ģeneratorus tūrismam, ārpus tīkla objektiem un avārijas rezervei. Saules piederumi un rīki aptver uzstādīšanas un apkopes aprīkojumu. Saules invertori un optimizatori pārveido un apstrādā paneļa izvadi. Saules paneļi aptver pašus paneļus pēc jaudas, izmēriem un stiprināšanas tipa.</p>
<h3>Kas patiesībā ir svarīgi pirkšanas brīdī</h3>
<p>Visbiežākā kļūda ir paneļu izmēra noteikšana un baterijas izlaišana, pēc tam pārsteigums, ka liekā saules enerģija tiek eksportēta uz tīklu par ļoti mazu naudu. Saskaņojiet baterijas kapacitāti ar vakara mājsaimniecības slodzi. Otrā biežākā kļūda ir invertora izvēle, nepārbaudot saderību ar izvēlēto paneļu un bateriju zīmoliem. Trešā ir EV lādētāja uzstādīšana, neapstiprinot, ka īpašuma tīkla piegāde var nodrošināt izvēlēto uzlādes ātrumu.</p>
<h3>Biežāk uzdotie jautājumi</h3>
<h4>Vai varu uzstādīt saules sistēmu bez baterijām?</h4>
<p>Tehniski jā; invertors dienas laikā eksportē lieko saules enerģiju uz tīklu, un īpašums vakarā pērk elektrību atpakaļ. Finansiāli bateriju gadījums lielā mērā ir atkarīgs no vietējā eksporta tarifa: tur, kur eksports maksā maz, baterijas atmaksājas ātrāk.</p>
<h4>Vai šie produkti ir nodrošināti ar ražotāja garantiju?</h4>
<p>Jā; ražotāja garantijas nosacījumi ir katrā produkta lapā. Saules paneļiem parasti ir 20 līdz 25 gadu veiktspējas garantijas un 10 līdz 12 gadu produkta garantijas. Invertoriem ir 5 līdz 10 gadu pagarināmas. Baterijām ir 7 līdz 10 gadi vai noteikts ciklu skaits.</p>
<h4>Vai jūs piegādājat pilnus komplektus vai atsevišķas komponentes?</h4>
<p>Abus. Atsevišķas komponentes ir pieejamas uzstādītājiem, kas veido pielāgotas sistēmas, pilni komplekti ir pieejami māju īpašniekiem un nelieliem komerciāliem pircējiem, kas vēlas pārbaudītu paneļu, invertora, stiprinājumu un (pēc izvēles) bateriju uzkrāšanas kombināciju.</p>
""",
    },

    # ─────────────────── 8. smart-home-iot ────────────────────────────────
    "other/smart-home-iot": {
        "bottom_seo_en": """\
<h2>Smart home and IoT hardware: lights, plugs, sensors and connected devices</h2>
<p>Smart home and IoT hardware is the part of the catalog where the platform decision matters more than the device decision. A smart bulb that does not talk to the platform a household already runs is just an expensive bulb. A motion sensor that does not feed an automation runs flat in months and gets ignored. This category groups smart lighting, smart energy and a broader IoT device group so a buyer can plan a coherent installation around one ecosystem before adding more devices.</p>
<h3>Subcategories at a glance</h3>
<p>IoT devices, sensors and services cover the connected sensors and gateways that feed home automation: motion, door, temperature, water leak, plus the hubs that bring them together. Smart energy and plugs cover the smart plugs and energy monitors that turn ordinary devices into scheduled or remote-controlled appliances. Smart lighting and bulbs cover the smart bulbs, light strips and switch replacements that bring lighting under app and voice control.</p>
<h3>What actually matters when buying</h3>
<p>Pick the platform first. Most current households default to one of three: a major voice-assistant ecosystem, a Matter-over-Thread mesh, or a vendor-specific app. Once the platform is fixed, every new device decision narrows: only buy products that work natively with the chosen platform. Mixing ecosystems is technically possible but fragments automations and makes the household harder to maintain after a year.</p>
<h3>Frequently asked questions</h3>
<h4>Do I need a hub?</h4>
<p>Depends on the protocol. Wi-Fi smart devices work without a hub but flood the home network. Zigbee and Z-Wave devices need a hub, and the hub is what makes the network reliable. Matter-over-Thread reduces hub dependence but does not eliminate it for most households.</p>
<h4>Are these products covered by manufacturer warranty?</h4>
<p>Yes; manufacturer warranty terms are on each product listing. Smart lighting and plugs commonly carry one to three years; sensors and hubs two years; some pro-grade devices longer.</p>
<h4>Will smart bulbs work in any fixture?</h4>
<p>Mostly yes, by socket type (E27, E14, GU10). Watch out for fixtures with built-in dimmers (a smart bulb plus an analog dimmer fights the dimmer protocol), and for enclosed fixtures where the smart bulb's electronics overheat. The product page lists compatible fixture types.</p>
""",
        "bottom_seo_lv": """\
<h2>Viedo māju un IoT aparatūra: gaismas, kontaktspraudņi, sensori un savienotas ierīces</h2>
<p>Viedās mājas un IoT aparatūra ir kataloga daļa, kur platformas lēmums ir svarīgāks par ierīces lēmumu. Vieda spuldze, kas nerunā ar platformu, ko mājsaimniecība jau lieto, ir tikai dārga spuldze. Kustības sensors, kas nepadod datus automatizācijai, mēnešos izlādējas un tiek ignorēts. Šī kategorija sakārto viedo apgaismojumu, vieda enerģija un plašāku IoT ierīču grupu, lai pircējs varētu plānot saskaņotu uzstādīšanu ap vienu ekosistēmu, pirms pievienot vairāk ierīču.</p>
<h3>Apakškategorijas īsumā</h3>
<p>IoT ierīces, sensori un pakalpojumi aptver savienotos sensorus un vārtejus, kas baro mājas automatizāciju: kustība, durvis, temperatūra, ūdens noplūde, plus centrmezglus, kas tos apvieno. Vieda enerģija un kontaktspraudņi aptver viedos kontaktspraudņus un enerģijas monitorus, kas pārvērš parastās ierīces par plānotām vai attālināti kontrolētām ierīcēm. Vieds apgaismojums un spuldzes aptver viedās spuldzes, gaismas lentes un slēdžu nomaiņas, kas apgaismojumu pakļauj lietotnes un balss kontrolei.</p>
<h3>Kas patiesībā ir svarīgi pirkšanas brīdī</h3>
<p>Vispirms izvēlieties platformu. Lielākā daļa pašreizējo mājsaimniecību noklusē pie vienas no trim: lielas balss asistenta ekosistēmas, Matter-over-Thread režģa vai pārdevēja specifiskas lietotnes. Kad platforma ir fiksēta, katrs jauns ierīces lēmums sašaurinās: pērciet tikai produktus, kas dabīgi strādā ar izvēlēto platformu. Ekosistēmu jaukšana ir tehniski iespējama, bet sadrumstalo automatizāciju un padara mājsaimniecību grūtāk uzturamu pēc gada.</p>
<h3>Biežāk uzdotie jautājumi</h3>
<h4>Vai man vajadzīgs centrmezgls?</h4>
<p>Atkarīgs no protokola. Wi-Fi viedās ierīces strādā bez centrmezgla, bet pārplūdina mājas tīklu. Zigbee un Z-Wave ierīcēm nepieciešams centrmezgls, un centrmezgls ir tas, kas padara tīklu uzticamu. Matter-over-Thread samazina atkarību no centrmezgla, bet to neizslēdz lielākajai daļai mājsaimniecību.</p>
<h4>Vai šie produkti ir nodrošināti ar ražotāja garantiju?</h4>
<p>Jā; ražotāja garantijas nosacījumi ir katrā produkta sarakstā. Viedam apgaismojumam un kontaktspraudņiem parasti ir viens līdz trīs gadi; sensoriem un centrmezgliem divi gadi; dažām profesionālas klases ierīcēm ilgāk.</p>
<h4>Vai viedās spuldzes strādās jebkurā gaismeklī?</h4>
<p>Galvenokārt jā, pēc cokola tipa (E27, E14, GU10). Uzmanieties no gaismekļiem ar iebūvētiem dimmeriem (vieda spuldze plus analogais dimmers konfliktē ar dimmera protokolu) un no slēgtiem gaismekļiem, kur viedās spuldzes elektronika pārkarst. Produkta lapā uzskaitīti saderīgie gaismekļu tipi.</p>
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
    print(f"  rewrote bottom_seo on {len(PAGES)} pages under other/*")
