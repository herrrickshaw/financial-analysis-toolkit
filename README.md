# financial-analysis-toolkit

Financial modelling engines distilled from Corporate Finance Institute (CFI) Excel templates,
re-implemented in dependency-free Python and reconciled to the spreadsheets cell-for-cell.

| Engine | Source template | What it does |
|---|---|---|
| `finmodel.three_statement` | CFI Case Study – 3-Statement Model | Linked IS / BS / CF with working-capital, PP&E and debt schedules; N historical + N forecast years driven by ratio assumptions; balance check |
| `finmodel.dcf` | CFI DCF Model Template (Updated) | Unlevered FCF, stub-period `YEARFRAC`, `XNPV` enterprise value, perpetuity-growth + EV/EBITDA terminal value (average / either), equity bridge, `XIRR`, WACC × g sensitivity |
| `finmodel.projection` | CFI Financial Projection Template | Bottom-up: products × units, employees × hours (NETWORKDAYS), opex by category → IS → BS → CF → ratios, 1 monthly base year + N forecast years |
| `finmodel.ratios` | CFI Financial Ratio Analysis | Profitability, efficiency (turnover + days + funding gap), liquidity, leverage, coverage |
| `finmodel.fin` | — | Excel-exact `YEARFRAC` (basis 0–4), `XNPV`, `XIRR`, `NPV`, `IRR`, `NETWORKDAYS`, `EOMONTH`, `PMT` |
| `finmodel.excel` | — | Writes the 3-statement and DCF models as **live-formula** workbooks in the CFI layout (blue inputs / black formulas); LibreOffice headless recalc for verification |
| `finmodel.extract` | — | Turns any `.xlsx`/`.xls` template into a JSON + Markdown spec (labels, inputs, formulas, R1C1 patterns, cross-sheet links) |
| `finmodel.catalog` | — | Catalog / verify / fetch template sources: CFI dashboard (login), Damodaran, A Simple Model, exinfm |

## Install

```bash
git clone https://github.com/herrrickshaw/financial-analysis-toolkit && cd financial-analysis-toolkit
pip install -e ".[test]"          # only openpyxl is required at runtime
pytest -q                         # 25 tests; the LibreOffice recalc test auto-skips if soffice is absent
```

## Quick start

```bash
finmodel demo                                                   # runs all engines on the bundled examples -> out/*.xlsx
finmodel three-statement examples/cfi_three_statement.json --table all --xlsx out/3s.xlsx
finmodel dcf examples/cfi_dcf.json --sensitivity --xlsx out/dcf.xlsx
finmodel projection examples/projection_demo.json --xlsx out/proj.xlsx
finmodel ratios examples/ratios_demo.json
finmodel extract path/to/AnyTemplate.xlsx -o extracted/         # JSON + Markdown spec of the workbook
finmodel catalog list --source damodaran                        # 59 verified public spreadsheets
finmodel catalog fetch --source damodaran asimplemodel exinfm   # downloads/<source>/ (git-ignored)
finmodel catalog fetch --source cfi --auth "Cookie: ..."        # CFI dashboard needs your logged-in session
```

Python:

```python
from finmodel import three_statement as ts, dcf
r = ts.from_dict(json.load(open("examples/cfi_three_statement.json")))
print(r.table("balance_sheet")); assert r.balanced

v = dcf.run(dcf.DCFInputs(ebit=[...], da=[...], change_nwc=[...], capex=15000, discount_rate=0.12,
                          perpetual_growth=0.03, ev_ebitda_multiple=7, transaction_date="2017-12-31",
                          fiscal_year_end="2018-06-30", current_price=25, shares_outstanding=20000, debt=30000, cash=0))
v["equity_value_per_share"], v["irr"]
```

## Reconciliation to the CFI workbooks

`tests/test_three_statement.py` and `tests/test_dcf.py` assert the engines against the cached values in the
CFI files (forecast rows to ±0.01, DCF outputs to 1e-9). `tests/test_excel.py` writes the formula workbooks,
recalculates them with LibreOffice and checks every year's net earnings, total assets, closing cash, the
balance check, and the DCF EV / per-share / IRR against the engine.

The projection template ships with empty inputs (every cached value is 0), so `finmodel.projection` is
verified through accounting identities instead, and it **corrects four template bugs**:

1. forecast wages omit the hours-per-day factor (`avg wage × headcount × workdays`) — restored;
2. the D&A-rate cell points at interest ÷ opening debt (copy-paste) — uses base D&A ÷ opening PP&E;
3. employee bonuses are shown but never deducted from EBT — deducted;
4. prepaid and accrued expenses grow but are excluded from working capital, so the balance sheet cannot balance — included.

Also: wage expense defaults to gross wages (`wage_expense_basis="gross"`); pass `"net_pay"` to reproduce the template.

## Template sources

`catalog/catalog.md` lists 323 CFI dashboard items (196 free-tier downloads, 127 paid) and 82 verified public
spreadsheets from Damodaran (NYU Stern), A Simple Model and exinfm.com with sizes and HTTP status.
`docs/OPEN_SOURCE_MODULES.md` surveys the Python packages that overlap with this toolkit (FinanceToolkit,
pyxirr, numpy-financial, OpenBB, …) and `finmodel/integrations.py` has lazy bridges to them.

Downloaded templates are copyrighted by their publishers and stay in the git-ignored `downloads/` and
`extracted/` folders. The example JSON files carry only the illustrative figures printed in the free CFI
educational templates.

## Layout

```
finmodel/          engines + tools (fin, three_statement, dcf, projection, ratios, excel, extract, catalog, integrations, cli)
examples/          JSON inputs (CFI 3-statement, CFI DCF, projection demo, ratios demo)
catalog/           source lists (cfi_dashboard_raw.txt, open_sources_verified.txt) -> catalog.json / catalog.md
docs/              OPEN_SOURCE_MODULES.md
tests/             pytest suite (reconciliation, identities, LibreOffice recalc, CLI)
```

## Roadmap

- LBO engine (from A Simple Model's free LBO files) and mid-year-convention DCF
- Damodaran-style WACC / synthetic-rating inputs feeding `dcf.DCFInputs`
- Monthly roll-forward of the projection (the CFI base-year sheets are monthly)
