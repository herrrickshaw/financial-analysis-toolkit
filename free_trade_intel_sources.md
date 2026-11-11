# Free alternatives to Volza: trade data, finance leads, export-ready items
Checked 2026-11-01. "Reachable" = my curl got HTTP 200 today. Reachable does not mean the data is complete.

## Key limit
Volza sells shipment-level records (named buyer, named supplier, price per shipment). Free sources give mostly
country x HS-code aggregates. Named-company shipment data free = US sea imports only. Use aggregates to find
WHERE demand is; use tenders, fairs and registries to find WHO.

## A. Aggregate flows (find demand gaps by HS code and country)
| Source | What you get | Access |
|---|---|---|
| DGCI&S TradeStat + NIRYAT (India) | India exports by country x HS8, monthly, ~2 mo lag | curl recipes in memory: reference_tradestat_niryat_programmatic_access |
| UN Comtrade public preview | Any reporter x partner x HS6, annual/monthly, 500-row cap/call | Keyless API, reachable. Loop per chapter |
| US Census intltrade API | US monthly imports/exports by HS and country | Keyless API, reachable (api.census.gov/data/timeseries/intltrade) |
| Eurostat Comext | EU reporter x partner at CN8, monthly | SDMX endpoint reachable (ec.europa.eu/eurostat/api/comext/dissemination); bulk monthly files as fallback |
| USITC DataWeb | US HTS10 by country | Free account, web query + export |
| ITC Trade Map / Export Potential Map | Mirror data, growth, unit values, export-potential scores | Trade Map reachable. Free for developing-country users (India qualifies); register. macmap.org returned 403 to curl, use a browser |
| Korea KCS / K-stat, Japan e-Stat, UK HMRC, Canada CIMT | National HS8/HS10 monthly | Free, per-country portals |

Mirror check: compare India's reported exports to a partner with that partner's reported imports. Gaps flag
transshipment via hubs (see memory: Swiss imports of Indian-origin goods are 2x India's direct exports).

## B. Named-company shipment data (free tiers)
- ImportYeti: US sea import bills of lading, searchable by importer/supplier. Free tier is limited; premium is paid. curl got 403, use a browser. Search results suggest exports and non-US data are not covered.
- Volza free tier: credits run out fast per reviews. Use for spot checks only.
- Indian shipment sites (Zauba, Seair etc.): I could not verify any current free India bill-of-lading service. Treat as unverified.
- Gap-filler: US importer names from ImportYeti for a given HS code, then match to Indian suppliers by name.

## C. Live buyer demand (opportunities, not history)
- UNGM (UN procurement notices): reachable. Good for pharma, food, medical devices, textiles.
- EU TED (api.ted.europa.eu, tenders.europa.eu): API exists (405 on GET means POST search). Public tenders open to non-EU suppliers.
- World Bank, ADB, AfDB, IDB procurement notices: free, filter by goods.
- GeM and state e-procurement are India-domestic; skip for export.
- Trade fair exhibitor lists (MEDICA, Anuga, Gulfood, Arab Health): free, show active buyers/importers.
- Alibaba/IndiaMART/TradeIndia buyer RFQs: free to read, noisy.

## D. Trade-finance opportunity signals
- EXIM Bank India lines of credit (eximbankindia.in/lines-of-credit, reachable): lists countries with Indian-funded credit lines. Projects there must source goods from India, which is a pull for export items. Also DEA-administered LoCs.
- ECGC (ecgc.in, reachable): country risk categories and cover limits. Low-risk, high-demand countries are best finance targets.
- Multilateral trade-finance programmes: ADB Trade and Supply Chain Finance, IFC Global Trade Finance Program, Afreximbank, ITFC. Confirming banks need LC volume, so rising imports into their member countries signal LC demand.
- Not verified: I found no 2026 announcements of new ECGC or EXIM terms. Check the sites directly.

## E. Screen for export-ready items (cheap, repeatable)
1. India exports to partner P in HS8 H are small (or zero) while P's world imports of H are large and growing (Comtrade/Comext/Census).
2. Tariff into P is not prohibitive (MAcMap or WTO tariff download; Swiss industrial tariffs are zero).
3. India has capacity: India world exports of H exist and unit value is competitive vs. P's current suppliers.
4. Compliance is attainable: CE/FDA/EU-GMP, FSSAI, phytosanitary, CH-REP for devices, EUDR, CBAM.
5. Finance fit: P in ECGC low-risk band, or in an EXIM LoC country, or tender on UNGM/TED.
Score each (H, P) pair. Already done for Switzerland pharma/devices: ~/Downloads/swiss_export/.

## Suggested monitoring setup
Weekly: Comtrade/Census/Comext pulls for a fixed HS watchlist, flag YoY import growth >25% and India share <2%.
Monthly: NIRYAT refresh; EXIM LoC page diff; UNGM/TED keyword alerts for watchlist HS terms.
Happy to script this against the existing TradeStat/NIRYAT recipes.
