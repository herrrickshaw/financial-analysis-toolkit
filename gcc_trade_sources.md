# GCC (Saudi, UAE, Qatar, Kuwait, Oman, Bahrain) trade data sources
Checked 2026-11-01. Reachable = curl HTTP 200 today.

## Best free route: UN Comtrade public preview (keyless)
All six GCC states returned data when India (699) was the partner. Imports from India, US$ bn, as reported by the GCC state:
| Reporter | 2023 | 2024 |
|---|---|---|
| UAE | 30.45 | not yet published |
| Saudi Arabia | 11.62 | 12.66 |
| Oman | 2.78 | 3.91 |
| Kuwait | 2.06 | 1.94 |
| Qatar | 1.77 | 1.92 |
| Bahrain | 0.74 | 0.82 |
Gotchas: the preview API returns HTTP 429 if called quickly (spaced ~6 s plus retries worked); 500-row cap per call, so loop per HS chapter (see memory: reference_tradestat_niryat_programmatic_access). UAE reports late. Compare with India's own exports to each country (TradeStat country codes) to find re-export hub gaps, especially via UAE.

## Official national / regional portals
| Source | Content | Status |
|---|---|---|
| GCC-Stat data portal (dp.marsa.gccstat.org) | Foreign trade, monthly from Jan 2016, GCC-wide, HS-linked; labelled beta | Reachable. Main site gccstat.org returned 406 to curl, use a browser |
| Saudi GASTAT (stats.gov.sa) | Monthly goods trade, HS 2022, origin/destination by country, CIF imports, from 2000 | Reachable. Open-data URL I guessed was 404; navigate from the site menu |
| Saudi ZATCA (zatca.gov.sa) | Tariff and customs rules | Reachable, tariff not trade stats |
| UAE FCSC open data (opendata.fcsc.gov.ae) | Monthly trade by partner (AED), annual non-oil exports and re-exports by HS section and country, Dubai Customs tariff/agreement lists, CC-BY 4.0 | curl got 403; use a browser. Coverage dates conflict between listings, verify |
| Qatar NPC (npc.qa), Oman NCSI (ncsi.gov.om), Kuwait CSB (csb.gov.kw), Bahrain (data.gov.bh) | National trade tables and bulletins | All reachable; I did not find the HS-by-country tables, so locate them manually |

## Secondary (not official)
- TrendEconomy mirrors monthly and annual HS-by-country data for Qatar, Oman, Bahrain, etc. (search results only; direct fetch failed). Fine for browsing, verify against Comtrade.
- ITC Trade Map and WITS (wits.worldbank.org reachable) repackage the same reporter data.

## Opportunity sources (GCC buyers)
- Saudi Etimad (etimad.sa) government tenders; reachable, portal is largely Arabic/login for details.
- Saudi SFDA, UAE MOHAP/ESMA and GCC conformity (G-Mark, GSO standards) set entry rules for pharma, food, devices.
- Trade fairs with exhibitor lists: Gulfood (Dubai), Arab Health/World Health Expo, Saudi Food Show, Big 5.
- India-side finance: EXIM lines of credit, ECGC country limits. India-GCC CEPA with UAE (in force 2022) gives preferential access; check the Dubai Customs preferential-agreement dataset.

## Not verified
Any free named-company shipment data for GCC. Volza/TradeInt-type sites sell it; I could not confirm a free source.
