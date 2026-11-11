# Which GCC sources name companies? (checked 2026-11-01)

## FCSC open data does NOT name companies
- Datasets seen via the Arab Development Portal mirror: annual non-oil exports / re-exports by HS section x country (AED, 2017-2024, updated Dec 2025), monthly imports by country, Dubai Customs tariff lists. No company fields.
- opendata.fcsc.gov.ae sits behind a Cloudflare bot check (curl 403, browser pane challenge). Not bypassed. Open it in your own browser.
- UAE customs bills of lading are not public. No free source lists UAE importers by shipment.

## Sources that do name companies
| Source | Names | Notes |
|---|---|---|
| SFDA Saudi registered drugs list | Manufacturer name, manufacturer country, marketing company, local agents, price | Best pharma source. Page: sfda.gov.sa/en/news/updated-list-sfda-registered-drugs. curl was rejected by a web firewall; use a browser. Filter manufacturer country = India / EU members, count products per firm |
| UAE MOHAP drug search | Registered products and holders | Not reachable from my shell |
| Indian Embassy UAE commercial page | Indian investors and contractors in UAE (Taj, Ashok Leyland, Mahindra, Dabur, L&T, Essar, Punj Lloyd, EIL) | Investment/contracts, not export volume |
| Export councils (APEDA, Pharmexcil, EEPC, FIEO) | Registered exporters by sector | APEDA exporters-directory URL I tried was 404; Pharmexcil directory found was 2008 (stale). Check live sites |
| Saudi Etimad, UAE tender portals | Awarded contractors | Login-heavy, mostly Arabic |
| MEED project contract awards | EPC contractors (European, Korean, Indian) | Paywalled; headlines free. Saudi $144bn, UAE $81bn contracts in 2024 |
| Company annual reports / BSE-NSE filings / EU company filings | Middle East revenue by segment | Free, authoritative, per company |
| JAFZA / DMCC / Dubai Chamber directories | Free-zone and member firms (JAFZA: 2,300+ Indian firms per search result) | Directories, not trade volumes |

## Unverified claims to avoid
- A blog named Allanasons (exporter) and Golden Star Tobacco Trading FZ LLC (importer) as top 2024-25 names. No method given. Treat as a lead only.
- Paid aggregators (TradeInt, Volza) show UAE/Saudi names behind paywalls; TradeInt returned 403.

## EU side
EU-GCC trade: Saudi is over 50% of EU-GCC imports, UAE 16.7% (EU Council infographic). Company names come from filings and contract-award news, not trade statistics.
