# Learning guide: what each tool does, and where to learn it properly

Each section summarises one engine in this toolkit (the method, the formulas the code actually
runs, the judgement calls that matter), then points to **books** and **open university material**
that teach it, and to the **public templates** in `catalog/` that implement it in Excel.
All course links were checked live on 2026-09-06.

---

## 0. The reading stack (in the order practitioners recommend)

| Book | Author(s) | Edition | Use it for |
|---|---|---|---|
| *Financial Modeling and Valuation: A Practical Guide to Investment Banking and Private Equity* | Paul Pignataro | 2nd ed. (Wiley, 2022) | Build the 3-statement model line by line; the closest book to the CFI case study |
| *Investment Banking: Valuation, LBOs, M&A, and IPOs* | Joshua Rosenbaum, Joshua Pearl | 3rd ed. (Wiley, 2020/2022 with model templates) | Comps, precedents, DCF, LBO, merger and IPO models the way banks build them |
| *Valuation: Measuring and Managing the Value of Companies* | Tim Koller, Marc Goedhart, David Wessels (McKinsey) | 8th ed. (Wiley, 2025) | Value drivers (ROIC, growth), continuing value, enterprise DCF vs economic profit |
| *Investment Valuation* / *Damodaran on Valuation* / *The Little Book of Valuation* / *Narrative and Numbers* | Aswath Damodaran | 3rd ed. 2012 / 2nd ed. 2006 / 2011 / 2017 | DCF inputs (cost of capital, growth, terminal value), relative valuation, real options |
| *Applied Corporate Finance* | Aswath Damodaran | 4th ed. (Wiley, 2014) | WACC, capital structure, dividend policy, project analysis |
| *Financial Statement Analysis and Security Valuation* | Stephen Penman | 5th ed. (McGraw-Hill, 2013) | Accounting-based valuation, reformulated statements, ratio decomposition |
| *Financial Modeling* | Simon Benninga | 4th ed. (MIT Press, 2014) | Excel implementation: pro-forma models, cost of capital, options, Monte Carlo |
| *Building Financial Models* | John Tjia | 3rd ed. (McGraw-Hill, 2018) | Model architecture, balancing the balance sheet, circularity, error checks |
| *Principles of Financial Modelling* | Michael Rees | Wiley, 2018 | Design principles, sensitivity, scenario and risk modelling |
| *Corporate Finance* | Berk & DeMarzo / Brealey, Myers & Allen | 5th ed. 2019 / 14th ed. 2022 | The underlying theory; either is the standard MBA text |
| CFA Program Curriculum — Level I FSA, Level II Equity (FCFF/FCFE, residual income, multiples) | CFA Institute | current | Rigorous definitions of every ratio and DCF variant |

**Free college-level textbooks**
- OpenStax *Principles of Finance* (Rice University, CC-BY): https://openstax.org/details/books/principles-finance — TVM, statements, ratios, capital budgeting, cost of capital.
- Saylor Academy BUS202 *Principles of Finance* (full course, free): https://learn.saylor.org/course/view.php?id=1252
- *Introduction to Financial Analysis* (Open Textbook Library): https://open.umn.edu/opentextbooks/textbooks/1221

**Open university courses**
- NYU Stern, Damodaran — MBA *Valuation* class: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/equity.html ; lecture notes index: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/eqlect.htm ; Spring-2025 syllabus: https://pages.stern.nyu.edu/~adamodar/pdfiles/eqnotes/eqsyllspr25.pdf ; lecture packet 1: https://pages.stern.nyu.edu/~adamodar/pdfiles/eqnotes/packet1a.pdf ; topic notes: `basics.pdf`, `dcfinput.pdf`, `fcff.pdf`, `fcfe.pdf`, `ddm.pdf`, `pe.pdf`, `eva.pdf`, `option.pdf` under https://pages.stern.nyu.edu/~adamodar/pdfiles/
- NYU Stern, Damodaran — *Corporate Finance* class: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/corpfin.html ; lecture notes index: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/cflect.htm ; Spring-2025 syllabus: https://pages.stern.nyu.edu/~adamodar/pdfiles/cfovhds/cfsyllspr25.pdf ; packet 1: https://pages.stern.nyu.edu/~adamodar/pdfiles/cfovhds/cfpacket1.pdf ; YouTube playlist linked from the page
- NYU Stern, Damodaran — Executive valuation class: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/execvaln.html
- MIT OCW 15.401 *Finance Theory I* (video + slides): https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/
- MIT OCW 15.402 *Finance Theory II* (corporate finance, capital structure, valuation cases): https://ocw.mit.edu/courses/15-402-finance-theory-ii-spring-2003/
- MIT OCW 15.414 *Financial Management*: https://ocw.mit.edu/courses/15-414-financial-management-summer-2003/
- MIT OCW 15.535 *Business Analysis Using Financial Statements* (ratios, DCF foundations, earnings quality): https://ocw.mit.edu/courses/15-535-business-analysis-using-financial-statements-spring-2003/
- MIT OCW 15.501 *Introduction to Financial and Managerial Accounting*: https://ocw.mit.edu/courses/15-501-introduction-to-financial-and-managerial-accounting-spring-2004/
- MIT OCW 15.433 *Investments*: https://ocw.mit.edu/courses/15-433-investments-spring-2003/
- Open Yale ECON 252 *Financial Markets* (Shiller): https://oyc.yale.edu/economics/econ-252

**Practitioner knowledge bases (free tutorials with Excel files)**
- Breaking Into Wall Street KB: https://breakingintowallstreet.com/kb/ (direct S3 spreadsheet links; catalogued as source `biws`)
- Macabacus Learn: https://macabacus.com/learn (free demo models catalogued as source `macabacus`)
- Wall Street Prep knowledge: https://www.wallstreetprep.com/knowledge/financial-modeling/ (files behind an email form)
- A Simple Model: https://www.asimplemodel.com (source `asimplemodel`)

---

## 1. Three-statement model  (`finmodel.three_statement`)

**What it is.** One integrated workbook where the income statement, balance sheet and cash-flow
statement are linked so that a change in any assumption flows through all three and the balance
sheet still balances. It is the base layer under every DCF, LBO and merger model.

**How the engine works (CFI structure).**
- Revenue_t = Revenue_{t-1} × (1 + g); COGS and salaries as % of revenue; rent as an amount.
- D&A_t = opening PP&E × rate; PP&E_close = open + capex − D&A.
- Interest_t = average(debt_open, debt_close) × rate; debt_close = open + issuance.
- AR = revenue × days/365; inventory and AP = COGS × days/365; ΔNWC = NWC_t − NWC_{t-1}.
- Net earnings = (gross profit − expenses) × (1 − tax rate); retained earnings roll forward.
- Cash_t = cash_{t-1} + (NI + D&A − ΔNWC) − capex + debt issued + equity issued, and the check
  `Total L&E − Total assets = 0` proves the links.

**Judgement calls.** Days-based working capital vs % of revenue; whether interest uses average
or opening debt (average creates circularity in Excel, not here); which historical years to
average for the forecast ratios; a revolver / cash sweep if cash can go negative (not in CFI's version).

**Learn it.** Pignataro ch. 1–8 (build), Tjia ch. 4–11 (architecture and balancing), Rosenbaum & Pearl
ch. 3 (financial projections inside a DCF), Damodaran corporate-finance packet 1 (statements as inputs),
MIT 15.501 (accounting foundations), MIT 15.535 (reading statements for valuation), OpenStax ch. 5–6.

**Templates.** `asimplemodel/IFS_Simple Three Statement Model.xlsx`, `…/IFS_PPE Schedule.xlsx`,
`macabacus/operating-model.xlsx`, `exinfm/statmnts.xls`, `exinfm/Financial Projections Model v6.8.4.xls`.

---

## 2. Discounted cash flow  (`finmodel.dcf`)

**What it is.** Enterprise value = present value of unlevered free cash flows + present value of a
terminal value; equity value = EV + cash − debt; per-share value vs market price gives the upside.

**How the engine works (CFI structure).**
- UFCF = EBIT × (1 − t) + D&A − capex − ΔNWC.
- Stub period: first flow is scaled by `YEARFRAC(transaction date, first FYE)` (Excel basis 0, US 30/360).
- Terminal value: perpetuity `UFCF_n × (1+g)/(r−g)` and exit multiple `EV/EBITDA × EBITDA_n`; CFI averages them.
- EV = `XNPV(r, [0, UFCF_1·yf_1 … UFCF_n·yf_n, TV], dates)`; IRR from `XIRR` on (−market EV, flows, TV).
- Sensitivity grid over discount rate × growth (`dcf.sensitivity`).

**Judgement calls.** WACC inputs (see §5); g must be below the long-run nominal growth of the economy;
mid-year convention (A Simple Model file) vs end-of-period; reconciling the two terminal methods —
the implied exit multiple of the perpetuity TV is the sanity check; treatment of leases, options,
minority interests and non-operating assets in the bridge.

**Learn it.** Damodaran `basics.pdf`, `dcfinput.pdf`, `fcff.pdf`; *Investment Valuation* ch. 12–15;
Koller ch. 8–12 (enterprise DCF, continuing value); Rosenbaum & Pearl ch. 3; Pignataro ch. 9–10;
MIT 15.401 lectures on capital budgeting and equities; MIT 15.402 valuation cases; OpenStax ch. 16–17.

**Templates.** `damodaran/fcffsimpleginzu.xlsx` (the full ginzu), `damodaran/fcffginzu.xlsx`,
`damodaran/fcff2st.xls`, `fcff3st.xls`, `fcffgen.xls`; `asimplemodel/DCF_Discounted Cash Flow Model.xlsx`
and `DCF_MidYear Convention.xlsx`; `exinfm/LBO_DCF_Model.xls`; BIWS DCF case files (see `catalog/catalog.md`).

---

## 3. Bottom-up projection  (`finmodel.projection`)

**What it is.** An FP&A-style operating model: revenue built from units × price per product,
payroll from headcount × hours × wage, opex by category, then rolled into the three statements and a
ratio dashboard. This is the "budget and forecast" model rather than the valuation model.

**How the engine works (CFI structure).** Monthly base year (NETWORKDAYS drives hours), annual
forecast years with growth rates per product / employee type / expense line; bonus pool = 10% of
positive EBIT; taxes only on positive EBT; AR/inventory/AP by days, prepaid and accrued by growth;
PP&E and debt schedules as in §1; 20+ ratios per year.

**Judgement calls.** Driver choice (units vs price vs mix), seasonality, headcount timing, whether
wage expense is gross or net pay (the CFI sheet books net pay — see README), capex as % of revenue vs
a plan, and the four template corrections listed in the README.

**Learn it.** Benninga part I (pro-forma models), Rees ch. 2–6, Tjia; CFI *FP&A Fundamentals* and the
free *Financial Modeling Guidelines* PDF on your dashboard; Saylor BUS202 units on pro-forma statements
and forecasting; MIT 15.414 lecture notes on financial planning.

**Templates.** `exinfm/Financial_model_1.xls`, `exinfm/CashModel1.4.xls` (not downloaded, on the exinfm page),
`macabacus/operating-model.xlsx`, `exinfm/Box IPO Financial Model.xls` (a real-company operating model).

---

## 4. Ratio analysis  (`finmodel.ratios`)

**What it is.** Profitability (margins, ROA, ROE), efficiency (turnover and days: DSO, DIO, DPO,
working-capital funding gap), liquidity (current, quick), leverage (D/E, liabilities/equity,
assets/equity), coverage (EBIT/interest).

**Judgement calls.** Average vs closing balances in turnover ratios; which "debt" (gross, net,
including leases); DuPont decomposition (ROE = margin × turnover × leverage) is the standard extension;
compare against sector benchmarks (Damodaran's industry averages, updated each January).

**Learn it.** Penman ch. 9–12 (reformulation and ratio analysis), MIT 15.535 classes 1–8, CFA Level I
*Financial Statement Analysis* readings, OpenStax ch. 6, CFI *Financial Ratios Definitive Guide* (free download on your dashboard).

**Templates.** `exinfm/Ratio_Tree.xls`, `damodaran/returncalculator.xls`, Damodaran industry datasets
(`betas.xls`, `wacc.xls`).

---

## 5. Cost of capital (inputs to the DCF)

**What it is.** WACC = E/(D+E) × k_e + D/(D+E) × k_d × (1 − t); k_e from CAPM = r_f + β × ERP (+ country risk);
β from regression or bottom-up (unlever peers, relever at target D/E); k_d from a synthetic rating
(interest-coverage → rating → spread).

**Learn it.** Damodaran *Applied Corporate Finance* ch. 4, corporate-finance packet 1; `dcfinput.pdf`;
Koller ch. 15; MIT 15.401 CAPM lectures; OpenStax ch. 15–17.

**Templates.** `damodaran/wacccalc.xls`, `ratings.xls` (synthetic rating), `levbeta.xls`, `risk.xls`,
`implprem.xls` (implied ERP), `ctryprem.xlsx` (country premia), `exinfm/betawacc.xls`. Free CFI dashboard
items: *WACC Calculator*, *Beta Calculator*, *Cost of Debt*, *CAPM Formula*, *Market Risk Premium*.

---

## 6. Leveraged buyout  (`finmodel.lbo`)

**What it is.** Buy a company with mostly debt, run the operating model for 5–7 years, pay debt down
from free cash flow, exit at a multiple, and solve for the sponsor's IRR / MOIC. Core mechanics:
sources & uses, purchase-price allocation and goodwill, tranched debt schedule with cash sweep,
PIK interest, management rollover, returns attribution.

**How the engine works.** Tranches sized as EBITDA multiples (or amounts) with rate, scheduled amortisation, PIK share, sweep share and warrant equity; closing balance sheet with goodwill = seller proceeds − book equity, fees capitalised, transaction expenses through retained earnings; depreciation waves per capex vintage; revolver against a minimum cash balance; exit at a multiple; XIRR on dated flows for the sponsor and each lender; scenario × exit-multiple table. Reconciled to the A Simple Model workbook.

**Learn it.** Rosenbaum & Pearl ch. 4–5, Pignataro part III, BIWS "Simple LBO model" tutorial
(https://breakingintowallstreet.com/kb/leveraged-buyouts-and-lbo-models/simple-lbo-model-excel/),
Macabacus LBO tutorials (https://macabacus.com/learn), Damodaran `lboval.xls` for the valuation view.

**Templates.** `macabacus/lbo-model-long-form.xlsx` and `lbo-model-short-form.xlsx`,
`asimplemodel/LBO_Simple LBO Scenarios and Data Tables.xlsx`, `LBO II Common_Preferred.xlsx`,
`exinfm/LBO Model Template.xls`, `damodaran/lboval.xls`.

---

## 7. Merger / M&A model  (`finmodel.merger`)

**What it is.** Combine acquirer and target statements, fund the deal (cash / debt / stock),
adjust for purchase accounting (asset write-ups, goodwill, new D&A), synergies and transaction fees,
then test accretion / dilution of EPS and the pro-forma leverage.

**How the engine works.** Deal level: purchase equity = target market cap × (1 + premium); funding split cash / debt / stock; combined NI = (EBT_A + EBT_B − cash × foregone rate − debt × cost of debt + synergies − fees) × (1 − t); new shares = stock consideration ÷ acquirer price; accretion = combined EPS − standalone EPS. Multi-year: PPA (write-ups, new DTL, goodwill), synergies with realisation, integration costs, new-debt interest and amortisation, adjusted EPS. Reconciled to the BIWS workbook.

**Learn it.** Rosenbaum & Pearl ch. 6–7, Damodaran `synergyvaluation.xls` and *The Value of Synergy* paper,
BIWS merger-model tutorial (https://breakingintowallstreet.com/kb/ma-and-merger-models/merger-model/),
Koller ch. 31 (mergers and acquisitions).

**Templates.** `macabacus/merger-model.xlsx`, `exinfm/Combination Template.xls`, `damodaran/synergyvaluation.xls`,
`damodaran/controlvalue.xls`.

---

## 8. Comparable companies and precedent transactions  (roadmap)

**What it is.** Relative valuation: pick peers, spread their EV/EBITDA, EV/Revenue, P/E and growth
metrics, apply the range (25th–75th percentile) to the target; precedents do the same with control
premia from past deals; a football-field chart lays the ranges side by side with the DCF and LBO values.

**Learn it.** Rosenbaum & Pearl ch. 1–2, Damodaran `pe.pdf` and *Investment Valuation* ch. 17–20
(what drives each multiple), BIWS comps tutorial (https://breakingintowallstreet.com/kb/valuation/comparable-company-analysis/)
and precedent-transactions tutorial (…/kb/valuation/precedent-transaction-analysis/) with S3 Excel files.

**Templates.** `exinfm/Comparable Companies (NON-FDS).xls`, `damodaran/eqmult.xls`, `firmmult.xls`,
BIWS `107-21-Comparable-Company-Analysis.xlsx` and precedent files; free CFI dashboard items
*Comparable Company Analysis*, *Football Field Chart*, *Pharmaceuticals / Retail Industry Comps*.

---

## 9. Capital budgeting (NPV / IRR / payback) and options

Project appraisal is the same maths as the DCF applied to one project: `finmodel.fin.npv/irr/xnpv/xirr/pmt`.
Learn it from OpenStax ch. 16, MIT 15.401 capital-budgeting lectures, Damodaran corporate-finance packet 2,
Brealey–Myers ch. 5–10. Templates: `damodaran/capbudg.xls`, `exinfm/npv_irr.xls`, `damodaran/apv.xls`.
Option pricing (Black–Scholes, binomial, real options): Damodaran `option.pdf`, templates `optst.xls`,
`optlt.xls`, `warrant.xls`, `expand.xls`, `delay.xls`, `abandon.xls`, `natres.xls`.

---

## 10. Where the industry-standard titles on the CFI paid tier are covered elsewhere

`catalog/alternatives.md` (generated by `finmodel catalog alternatives`) maps every one of the 127
paid-only CFI titles — LBO Model, M&A Model, Trading/Transaction Comps, Bank & FIG model, REIT model,
SaaS model, Debt Capacity, Scenario & Sensitivity, Dividend Discount Model, FCFF vs FCFE, … — to the
closest public files from Damodaran, A Simple Model, Macabacus, BIWS and exinfm, using model-type tags.
