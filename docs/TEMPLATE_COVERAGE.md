# Template coverage: other sources and engines for the CFI titles tag matching missed

Generated from `catalog/curated_alternatives.json` (2026-10-24). These are the 149 CFI dashboard titles that the model-type tag rules in `finmodel.alternatives` could not match (accounting one-pagers, calculators, Excel-function demos, documents). For each: free sources of the same template, graded `same` / `close` / `partial`, and the `finmodel` function that reproduces the calculation where one applies.

- Best available match: **84 same**, **56 close**, 9 partial only.
- 99 titles name a `finmodel` engine function; the rest are Excel how-tos, documents or soft-skills material.
- Verification: Per-title search for free sources of the same template; every URL checked with curl (status, content type, and file magic bytes for direct downloads). 'page-exists, curl-blocked' = confirmed via web search but the site refuses scripted requests.

Most-used source sites: openstax.org (76), exceljet.net (28), support.microsoft.com (28), vertex42.com (20), wallstreetprep.com (19), pages.stern.nyu.edu (19), omnicalculator.com (18), accountingcoach.com (14), github.com (11), sec.gov (8), portfoliovisualizer.com (8), calculator.net (7).

Paid titles have no downloaded CFI file to inspect, so they were matched on title and CFI's page description; the `what it computes` line says so where relevant. Wall Street Prep and some Microsoft pages refuse scripted requests and are marked `page-exists, curl-blocked`; Wall Street Prep's Excel files need an email sign-up.

## Accounting & financial statements (51)

| CFI title | Engine | Best source | Match |
|---|---|---|---|
| Accounting for Diluted Shares & Earnings per Share | `eps_calculation.diluted_eps` | [Treasury Stock Method (TSM)](https://www.wallstreetprep.com/knowledge/treasury-stock-method/) (Wall Street Prep, web) | same |
| Accounting for Inventory | `inventory_costing.compare_costing_methods` | [10.1 Inventory valuation methods (FIFO/LIFO/WAC/specific ID)](https://openstax.org/books/principles-financial-accounting/pages/10-1-describe-and-demonstrate-the-basic-inventory-valuation-methods-and-their-cost-flow-assumptions) (OpenStax, web) | same |
| Accounting for Leases | `lease_accounting.initial_measurement` | [Converting operating leases into debt (oplease.xls)](https://pages.stern.nyu.edu/~adamodar/pc/oplease.xls) (Damodaran, xls) | close |
| Accounts Receivable Aging Report Template | `warranty_and_receivables_allowance.receivables_allowance_aging_method` | [9.2 Uncollectible accounts: balance-sheet aging method](https://openstax.org/books/principles-financial-accounting/pages/9-2-account-for-uncollectible-accounts-using-the-balance-sheet-and-income-statement-approaches) (OpenStax, web) | close |
| Additional Paid-in Capital Template | `capital_bridges.additional_paid_in_capital` | [14.2 Issuance and repurchase of stock](https://openstax.org/books/principles-financial-accounting/pages/14-2-analyze-and-record-transactions-for-the-issuance-and-repurchase-of-stock) (OpenStax, web) | same |
| Adjusted EBITDA | `earnings_bridges.adjusted_ebitda` | [Non-GAAP Financial Measures (Corp Fin C&DIs)](https://www.sec.gov/rules-regulations/staff-guidance/corporation-finance-interpretations/non-gaap-financial-measures) (SEC, web) | partial |
| Balance-Sheet-Current-Assets-Template | `three_statement.run` | [Balance Sheet Template](https://www.vertex42.com/ExcelTemplates/balance-sheet.html) (Vertex42, xlsx via download page) | close |
| Balance-Sheet-Current-Liabilities-Template | `three_statement.run` | [Balance Sheet Template](https://www.vertex42.com/ExcelTemplates/balance-sheet.html) (Vertex42, xlsx via download page) | close |
| Balance-Sheet-Template | `three_statement.run` | [Balance Sheet Template](https://www.vertex42.com/ExcelTemplates/balance-sheet.html) (Vertex42, xlsx via download page) | same |
| Beneish M-Score Template | `scores.beneish_m` | [M-Score calculator](https://apps.kelley.iu.edu/Beneish/MScore/MScoreInput) (Indiana University Kelley School (Beneish), web) | same |
| BV vs MV of Equity Template | `capital_bridges.book_vs_market_equity` | [6.5 Market Value Ratios (market-to-book)](https://openstax.org/books/principles-finance/pages/6-5-market-value-ratios) (OpenStax, web) | close |
| Cash EPS | `earnings_bridges.cash_eps` | [14.5 Earnings per Share](https://openstax.org/books/principles-financial-accounting/pages/14-5-discuss-the-applicability-of-earnings-per-share-as-a-method-to-measure-performance) (OpenStax, web) | partial |
| Cash Flow Reconciliation | `accrual_bridges.cash_flow_reconciliation` | [16.3 Statement of cash flows, indirect method](https://openstax.org/books/principles-financial-accounting/pages/16-3-prepare-the-statement-of-cash-flows-using-the-indirect-method) (OpenStax, web) | same |
| Cash Flow Statement | `three_statement.run` | [Cash Flow Statement Template](https://www.vertex42.com/ExcelTemplates/cash-flow-statement.html) (Vertex42, xlsx via download page) | same |
| Cash to Accrual (Complete) | `accrual_bridges.cash_to_accrual_statement` | [4.1 Cash versus accrual accounting](https://openstax.org/books/principles-finance/pages/4-1-cash-versus-accrual-accounting) (OpenStax, web) | close |
| Diluted EPS Formula | `eps_calculation.diluted_eps` | [Treasury Stock Method (TSM)](https://www.wallstreetprep.com/knowledge/treasury-stock-method/) (Wall Street Prep, web) | close |
| Dilution Example | `eps_calculation.treasury_stock_method_incremental_shares` | [Treasury Stock Method (TSM)](https://www.wallstreetprep.com/knowledge/treasury-stock-method/) (Wall Street Prep, web) | same |
| Earnings Per Share | `eps_calculation.basic_eps` | [14.5 Earnings per Share](https://openstax.org/books/principles-financial-accounting/pages/14-5-discuss-the-applicability-of-earnings-per-share-as-a-method-to-measure-performance) (OpenStax, web) | same |
| EBIT Example | `earnings_bridges.income_statement_subtotals` | [Firm value multiples (firmmult.xls)](https://pages.stern.nyu.edu/~adamodar/pc/firmmult.xls) (Damodaran, xls) | close |
| EBIT vs EBITDA | `earnings_bridges.income_statement_subtotals` | [5.1 The Income Statement](https://openstax.org/books/principles-finance/pages/5-1-the-income-statement) (OpenStax, web) | close |
| EBITDA Template | `earnings_bridges.income_statement_subtotals` | [5.1 The Income Statement](https://openstax.org/books/principles-finance/pages/5-1-the-income-statement) (OpenStax, web) | close |
| EBT Example | `earnings_bridges.income_statement_subtotals` | [5.1 The Income Statement](https://openstax.org/books/principles-finance/pages/5-1-the-income-statement) (OpenStax, web) | close |
| Enterprise Value to EBITDA | `comps.multiple` | [EV/EBITDA Multiple](https://www.wallstreetprep.com/knowledge/ev-ebitda-enterprise-value/) (Wall Street Prep, web) | same |
| Enterprise Value vs Equity Value Calculator | `capital_bridges.enterprise_value_bridge` | [Gross debt vs net debt approaches (GrossvsNet.xls)](https://pages.stern.nyu.edu/~adamodar/pc/GrossvsNet.xls) (Damodaran, xls) | close |
| FFO Example | `earnings_bridges.ffo` | [Nareit Funds From Operations White Paper (2018 restatement)](https://www.reit.com/sites/default/files/2018-FFO-white-paper-(11-27-18).pdf) (Nareit, pdf) | same |
| Financial Analysis Fundamentals Template | `ratios.compute` | [Chapter 6: Measures of financial health (ratios)](https://openstax.org/books/principles-finance/pages/6-1-ratios-condensing-information-into-smaller-pieces) (OpenStax, web) | close |
| FP&A Monthly Rollforward Template | `fpa_planning.rolling_forecast` | [12-Month Profit and Loss Projection](https://www.score.org/templates/12-month-profit-and-loss-projection/) (SCORE, xlsx) | partial |
| Free Cash Flow (FCF) Example | `earnings_bridges.free_cash_flow` | [5.6 Operating cash flow and FCFF](https://openstax.org/books/principles-finance/pages/5-6-operating-cash-flow-and-free-cash-flow-to-the-firm-fcff) (OpenStax, web) | same |
| Journal Entries Template | — | [3.5 Journal entries and T-accounts](https://openstax.org/books/principles-financial-accounting/pages/3-5-use-journal-entries-to-record-transactions-and-post-to-t-accounts) (OpenStax, web) | same |
| LTM Revenue Example | `calculators.ltm` | [Last Twelve Months (LTM)](https://www.wallstreetprep.com/knowledge/last-twelve-months-ltm/) (Wall Street Prep, web) | same |
| Market Capitalization Template | `capital_bridges.market_cap` | [Treasury Stock Method (TSM)](https://www.wallstreetprep.com/knowledge/treasury-stock-method/) (Wall Street Prep, web) | close |
| Market Value of Debt Template | `capital_bridges.market_value_of_debt_estimate` | [Cost of capital worksheet (wacccalc.xls)](https://pages.stern.nyu.edu/~adamodar/pc/wacccalc.xls) (Damodaran, xls) | same |
| Monthly Cash Flow Model | `cash_flow_forecast.rolling_forecast` | [12 Month Cash Flow Statement](https://www.score.org/templates/12-month-cash-flow-statement/) (SCORE, xlsx) | same |
| Net Debt Calulator | `capital_bridges.net_debt` | [Net Debt](https://www.wallstreetprep.com/knowledge/net-debt/) (Wall Street Prep, web) | same |
| Net Identifiable Assets Template | `ppa_valuation.allocate` | [Merger model (merger-model.xlsx)](https://macabacus.com/assets/2023/02/merger-model.xlsx) (Macabacus, xlsx) | partial |
| Net Working Capital Template | `nwc_peg.trailing_average_peg` | [5.3 Current ratio and working capital](https://openstax.org/books/principles-financial-accounting/pages/5-3-apply-the-results-from-the-adjusted-trial-balance-to-compute-current-ratio-and-working-capital-balance-and-explain-how-these-measures-represent-liquidity) (OpenStax, web) | close |
| Net Working Capital Template (2) | `nwc_peg.trailing_average_peg` | [5.3 Current ratio and working capital](https://openstax.org/books/principles-financial-accounting/pages/5-3-apply-the-results-from-the-adjusted-trial-balance-to-compute-current-ratio-and-working-capital-balance-and-explain-how-these-measures-represent-liquidity) (OpenStax, web) | close |
| NOPAT Template | `earnings_bridges.nopat` | [5.6 Operating cash flow and FCFF](https://openstax.org/books/principles-finance/pages/5-6-operating-cash-flow-and-free-cash-flow-to-the-firm-fcff) (OpenStax, web) | close |
| Normalizing Income Statements | `earnings_bridges.normalize_net_income` | [Normalized earnings (normearn.xls)](https://pages.stern.nyu.edu/~adamodar/pc/normearn.xls) (Damodaran, xls) | close |
| Personal Financial Statement | `personal_finance.personal_financial_statement` | [SBA Form 413 Personal Financial Statement](https://legacy.sba.gov/sites/default/files/2025-02/SBAForm413.pdf) (U.S. SBA, pdf) | same |
| Profit and Loss Statement | `three_statement.run` | [Profit and Loss Statement](https://www.vertex42.com/ExcelTemplates/profit-and-loss.html) (Vertex42, xlsx via download page) | same |
| Proforma Earnings Per Share Template | `merger.from_dict` | [Merger model (merger-model.xlsx)](https://macabacus.com/assets/2023/02/merger-model.xlsx) (Macabacus, xlsx) | close |
| Research and Development Capitalization | `rd_capitalization.capitalize_rd` | [R&D converter (R&DConv.xls)](https://pages.stern.nyu.edu/~adamodar/pc/R%26DConv.xls) (Damodaran, xls) | same |
| Revenue Variance Analysis | `variance_analysis.sales_mix_and_volume_variance` | [8.2 Materials price and quantity variances](https://openstax.org/books/principles-managerial-accounting/pages/8-2-compute-and-evaluate-materials-variances) (OpenStax, web) | partial |
| SME Lending - Owner's Net Worth Adjustment Template | `personal_finance.owner_net_worth_adjustment` | [SBA Form 413 Personal Financial Statement](https://legacy.sba.gov/sites/default/files/2025-02/SBAForm413.pdf) (U.S. SBA, pdf) | partial |
| Tax-Shield Template | `capital_bridges.tax_shield` | [17.2 Costs of debt and equity capital](https://openstax.org/books/principles-finance/pages/17-2-the-costs-of-debt-and-equity-capital) (OpenStax, web) | close |
| Treasury Stock Method Calculator | `eps_calculation.treasury_stock_method_incremental_shares` | [Treasury Stock Method (TSM)](https://www.wallstreetprep.com/knowledge/treasury-stock-method/) (Wall Street Prep, web) | same |
| Variance Analysis | `variance_analysis.budget_vs_actual_variance` | [Business budget planner (gallery)](https://excel.cloud.microsoft/create/en/business-budgeting/) (Microsoft Create, web) | close |
| Weighted Average Shares Outstanding Template | `capital_bridges.weighted_average_shares` | [Weighted Average Shares Outstanding](https://www.wallstreetprep.com/knowledge/weighted-average-shares-outstanding/) (Wall Street Prep, web) | same |
| Working Capital Cycle | `accrual_bridges.working_capital_cycle` | [Cash Conversion Cycle](https://www.wallstreetprep.com/knowledge/cash-conversion-cycle-ccc/) (Wall Street Prep, web) | same |
| Working Capital Cycle Template | `accrual_bridges.working_capital_cycle` | [Cash Conversion Cycle](https://www.wallstreetprep.com/knowledge/cash-conversion-cycle-ccc/) (Wall Street Prep, web) | same |

## Time value, rates & growth calculators (23)

| CFI title | Engine | Best source | Match |
|---|---|---|---|
| Annual Income Calculator | `calculators.annual_income` | [Salary Calculator](https://www.calculator.net/salary-calculator.html) (Calculator.net, web) | same |
| CAGR Calculator | `fin.cagr` | [CAGR Calculator](https://www.vertex42.com/Calculators/cagr-calculator.html) (Vertex42, xlsx via download page) | same |
| Capital Gains Yield Calculator | `calculators.capital_gains_yield` | [Principles of Finance, 15.1 Risk and Return to an Individual Asset](https://openstax.org/books/principles-finance/pages/15-1-risk-and-return-to-an-individual-asset) (OpenStax, web) | same |
| Compound Monthly Growth Rate (CMGR) | `calculators.cmgr` | [Compound Monthly Growth Rate (CMGR)](https://www.wallstreetprep.com/knowledge/compound-monthly-growth-rate-cmgr/) (Wall Street Prep, web) | same |
| Cost of Preferred Stock Calculator | `calculators.cost_of_preferred_stock` | [Cost of Preferred Stock](https://www.wallstreetprep.com/knowledge/cost-of-preferred-stock/) (Wall Street Prep, web) | same |
| Coupon Rate | `calculators.coupon_rate` | [Coupon Rate Calculator](https://www.omnicalculator.com/finance/coupon-rate) (Omni Calculator, web) | same |
| CUMIPMT Template | `calculators.cumulative_interest_and_principal` | [CUMIPMT function](https://support.microsoft.com/en-us/excel/functions/cumipmt-function) (Microsoft Support, web) | same |
| Effective Annual Interest Rate Calculator | `calculators.effective_annual_rate` | [EFFECT function](https://support.microsoft.com/en-us/excel/functions/effect-function) (Microsoft Support, web) | same |
| Future Value Calculator | `calculators.future_value` | [FV function](https://support.microsoft.com/en-us/excel/functions/fv-function) (Microsoft Support, web) | same |
| Geometric Mean Example | `calculators.geometric_mean_return` | [Principles of Finance, 15.1 Risk and Return to an Individual Asset](https://openstax.org/books/principles-finance/pages/15-1-risk-and-return-to-an-individual-asset) (OpenStax, web) | same |
| HELOC Calculator | `calculators.heloc` | [HELOC Calculator](https://www.omnicalculator.com/finance/heloc) (Omni Calculator, web) | same |
| Interest Calculator | `calculators.interest` | [Interest Calculator](https://www.calculator.net/interest-calculator.html) (Calculator.net, web) | same |
| Interest Rate Parity (IRP) Calculator | `carry_trade.covered_interest_rate_parity` | [Interest Rate Parity Calculator](https://www.omnicalculator.com/finance/interest-rate-parity) (Omni Calculator, web) | same |
| Loan Payment Calculator | `retail_loans.amortization_schedule` | [Loan Amortization Schedule and Calculator](https://www.vertex42.com/ExcelTemplates/loan-amortization-schedule.html) (Vertex42, xlsx via download page) | same |
| Markup Calculator | `calculators.markup` | [Markup Calculator](https://www.omnicalculator.com/finance/markup) (Omni Calculator, web) | same |
| Net Present Value Template | `fin.npv` | [NPV Calculator - IRR and Net Present Value](https://www.vertex42.com/Calculators/npv-irr-calculator.html) (Vertex42, xlsx via download page) | same |
| Percentage Change Calculator | `calculators.percentage_change` | [Get percent change](https://exceljet.net/formulas/get-percent-change) (Exceljet, web) | same |
| Perpetuity Calculator | `calculators.perpetuity` | [Principles of Finance, 8.1 Perpetuities](https://openstax.org/books/principles-finance/pages/8-1-perpetuities) (OpenStax, web) | same |
| Present Value of Growth Opportunities (PVGO) Template | `calculators.pvgo` | [PVGO Calculator](https://www.omnicalculator.com/finance/pvgo) (Omni Calculator, web) | same |
| Revenue Run Rate | `calculators.revenue_run_rate` | [Revenue Run Rate Calculator](https://userjot.com/tools/revenue-run-rate-calculator) (UserJot, web) | close |
| Sales Tax Decalculator | `calculators.sales_tax_decalculator` | [Sales Tax Calculator](https://www.calculator.net/sales-tax-calculator.html) (Calculator.net, web) | same |
| Year over Year (YoY) Analysis | `calculators.year_over_year` | [Year-over-Year Growth Calculator](https://www.omnicalculator.com/finance/year-over-year-growth) (Omni Calculator, web) | same |
| Year to Date YTD Template | `calculators.year_to_date` | [YTD Return Calculator](https://www.ytdreturn.com/calculator/) (YTDReturn.com, web) | close |

## Cost & managerial accounting (8)

| CFI title | Engine | Best source | Match |
|---|---|---|---|
| Activity Based Costing Template | `managerial_costing.activity_based_costing` | [Principles of Accounting Vol 2, 6.3 Calculate Activity-Based Product Costs](https://openstax.org/books/principles-managerial-accounting/pages/6-3-calculate-activity-based-product-costs) (OpenStax, web) | same |
| Cost Behavior Analysis | `managerial_costing.cost_behavior` | [Principles of Accounting Vol 2, 2.3 Estimate a Variable and Fixed Cost Equation and Predict Future Costs](https://openstax.org/books/principles-managerial-accounting/pages/2-3-estimate-a-variable-and-fixed-cost-equation-and-predict-future-costs) (OpenStax, web) | same |
| Cost of Goods Manufactured | `managerial_costing.cost_of_goods_manufactured` | [Principles of Accounting Vol 2, 2.1 Distinguish between Merchandising, Manufacturing, and Service Organizations](https://openstax.org/books/principles-managerial-accounting/pages/2-1-distinguish-between-merchandising-manufacturing-and-service-organizations) (OpenStax, web) | same |
| Cost of Goods Sold | `managerial_costing.cost_of_goods_sold` | [Principles of Accounting Vol 1, 10.2 Calculate COGS and Ending Inventory Using the Periodic Method](https://openstax.org/books/principles-financial-accounting/pages/10-2-calculate-the-cost-of-goods-sold-and-ending-inventory-using-the-periodic-method) (OpenStax, web) | same |
| Cost Volume Profit Analysis Template | `breakeven.break_even_point` | [Principles of Accounting Vol 2, 3.2 Calculate a Break-Even Point in Units and Dollars](https://openstax.org/books/principles-managerial-accounting/pages/3-2-calculate-a-break-even-point-in-units-and-dollars) (OpenStax, web) | same |
| Economic Order Quantity | `managerial_costing.economic_order_quantity` | [EOQ Calculator (Economic Order Quantity)](https://www.omnicalculator.com/finance/eoq) (Omni Calculator, web) | same |
| Product Costs Template | `managerial_costing.product_costs` | [Principles of Accounting Vol 2, 4.2 The Three Major Components of Product Costs under Job Order Costing](https://openstax.org/books/principles-managerial-accounting/pages/4-2-describe-and-identify-the-three-major-components-of-product-costs-under-job-order-costing) (OpenStax, web) | same |
| Target Costing Example | `managerial_costing.target_costing` | [Target Costing](https://www.wallstreetprep.com/knowledge/target-costing/) (Wall Street Prep, web) | same |

## Portfolio, trading & risk (15)

| CFI title | Engine | Best source | Match |
|---|---|---|---|
| Alpha Calculator | `market_tools.jensens_alpha` | [Principles of Finance 15.4 Applications in Performance Measurement](https://openstax.org/books/principles-finance/pages/15-4-applications-in-performance-measurement) (OpenStax, web) | close |
| Cohort Analysis | `cohort_analysis.cohort_retention_curve` | [Customer Retention Cohort Analysis Template for SaaS](https://pages.visible.vc/customer-retention-cohort-analysis-template-for-saas-companies) (Visible.vc, google-sheet) | close |
| Collateralized Mortgage Obligations (CMO) Models | `cmo.cmo_deal` | [cmoseqcf - sequential CMO cash flows (Financial Instruments Toolbox)](https://www.mathworks.com/help/fininst/cmoseqcf.html) (MathWorks, web) | close |
| Directional Trading Strategies | `market_tools.strategy_payoff` | [Bull Call Spread (Debit Call Spread)](https://www.optionseducation.org/strategies/all-strategies/bull-call-spread-debit-call-spread) (Options Industry Council (OIC), web) | close |
| Efficient Frontier and CAL Template | `portfolio_optimization.efficient_frontier` | [Efficient Frontier](https://www.portfoliovisualizer.com/efficient-frontier) (Portfolio Visualizer, web) | close |
| ETF Allocator Model | `portfolio_optimization.tangency_portfolio` | [PyPortfolioOpt (6.1k stars, pushed 2026-07)](https://github.com/PyPortfolio/PyPortfolioOpt) (GitHub, py) | same |
| Expected Return Example | `market_tools.expected_return_scenarios` | [Principles of Finance 15.1 Risk and Return to an Individual Asset](https://openstax.org/books/principles-finance/pages/15-1-risk-and-return-to-an-individual-asset) (OpenStax, web) | same |
| Individual Equity Allocation Model | `portfolio_optimization.portfolio_stats` | [PyPortfolioOpt (6.1k stars, pushed 2026-07)](https://github.com/PyPortfolio/PyPortfolioOpt) (GitHub, py) | close |
| InsurTech Pricer Model | `insurance_pricing.rate_making_premium` | [Basic Ratemaking (Werner & Modlin, 5th ed.)](https://casact.org/library/studynotes/Werner_Modlin_Ratemaking.pdf) (Casualty Actuarial Society, pdf) | close |
| Market Risk Fundamentals | `market_tools.value_at_risk` | [Value at Risk (VaR) paper](https://pages.stern.nyu.edu/~adamodar/pdfiles/papers/VAR.pdf) (Damodaran, pdf) | close |
| Moving Averages Template | `market_tools.moving_average` | [Moving average formula](https://exceljet.net/formulas/moving-average-formula) (Exceljet, web) | same |
| Non-directional Trading Strategies | `market_tools.strategy_payoff` | [Long Straddle](https://www.optionseducation.org/strategies/all-strategies/long-straddle) (Options Industry Council (OIC), web) | close |
| NVDA Moving Average Algorithmic Trading Model | `market_tools.ma_crossover_backtest` | [Quick Start User Guide (SmaCross strategy)](https://kernc.github.io/backtesting.py/doc/examples/Quick%20Start%20User%20Guide.html) (backtesting.py docs, web) | same |
| Robo-Advisor Model | `three_statement.run` | [Investor Questionnaire](https://investor.vanguard.com/tools-calculators/investor-questionnaire) (Vanguard, web) | close |
| Simplified Robo-Advisor Model | `three_statement.run` | [Investor Questionnaire](https://investor.vanguard.com/tools-calculators/investor-questionnaire) (Vanguard, web) | close |

## Strategy frameworks (3)

| CFI title | Engine | Best source | Match |
|---|---|---|---|
| Competitive Forces Model | `strategy_frameworks.five_forces` | [Porter's Five Forces Template](https://www.cascade.app/resources/porters-5-forces-template) (Cascade, xlsx via download page) | same |
| Making Effective Business Decisions Template | `strategy_frameworks.weighted_decision_matrix` | [Weighted Decision Matrix Template](https://spreadsheetdaddy.com/wp-content/uploads/2026/01/Weighted-Decision-Matrix-Template.xlsx) (Spreadsheet Daddy, xlsx) | close |
| Multi-Criteria Analysis Balance Scorecard | `strategy_frameworks.weighted_decision_matrix` | [Multi-criteria analysis: a manual (DCLG 2009)](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/7612/1132618.pdf) (GOV.UK, pdf) | close |

## Excel functions & learning material (29)

| CFI title | Engine | Best source | Match |
|---|---|---|---|
| Accounting Fact Sheet | — | [Financial Statements (explanation)](https://www.accountingcoach.com/financial-statements/explanation) (AccountingCoach, web) | close |
| AutoSum Example | — | [AutoSum selected cells (shortcut)](https://exceljet.net/shortcuts/autosum-selected-cells) (Exceljet, web) | same |
| CFI Accounting eBook | — | [Principles of Accounting, Volume 1: Financial Accounting](https://openstax.org/details/books/principles-financial-accounting) (OpenStax, pdf via download page) | close |
| CFI Advanced Excel Formulas & Functions | — | [Excel Functions (500+ function guide)](https://exceljet.net/functions) (Exceljet, web) | close |
| CFI Essential Guide to Breaking into FP&A | — | [Principles of Finance Ch.18 Financial Forecasting](https://openstax.org/books/principles-finance/pages/18-1-the-importance-of-forecasting) (OpenStax, web) | partial |
| CFI Excel eBook | — | [Excel Functions (500+ function guide)](https://exceljet.net/functions) (Exceljet, web) | close |
| CFI Financial Analysis Glossary | — | [Harvey's Hypertextual Finance Glossary](https://people.duke.edu/~charvey/Classes/wpg/glossary.htm) (Duke University (Campbell R. Harvey), web) | close |
| Corporate Finance Fundamentals: Capital Financing | — | [Principles of Finance Ch.17 How Firms Raise Capital / capital structure](https://openstax.org/books/principles-finance/pages/17-1-the-concept-of-capital-structure) (OpenStax, web) | close |
| Corporate Finance Fundamentals: Capital Return | — | [dividends.xls (dividend policy / FCFE payout)](https://pages.stern.nyu.edu/~adamodar/pc/dividends.xls) (Damodaran, xls) | close |
| COUNTIFS Template | — | [COUNTIFS function](https://support.microsoft.com/en-us/excel/functions/countifs-function) (Microsoft Support, web) | same |
| COVARIANCE.P Template | — | [COVARIANCE.P function](https://support.microsoft.com/en-us/excel/functions/covariance-p-function) (Microsoft Support, web) | same |
| Excel for Finance Functions | — | [Financial functions (reference)](https://support.microsoft.com/en-us/office/financial-functions-reference-5658d81e-6035-4f24-89c1-fbf124c2b1d8) (Microsoft Support, web) | close |
| Excel Fundamentals - Formulas for Finance | — | [Financial functions (reference)](https://support.microsoft.com/en-us/office/financial-functions-reference-5658d81e-6035-4f24-89c1-fbf124c2b1d8) (Microsoft Support, web) | close |
| Excel Fundamentals - Formulas for Finance (Summary) | — | [Financial functions (reference)](https://support.microsoft.com/en-us/office/financial-functions-reference-5658d81e-6035-4f24-89c1-fbf124c2b1d8) (Microsoft Support, web) | close |
| Excel Fundamentals - Quick Start Guide (Summary) | — | [Principles of Finance 18.6 Using Excel to Create the Long-Term Forecast](https://openstax.org/books/principles-finance/pages/18-6-using-excel-to-create-the-long-term-forecast) (OpenStax, web) | close |
| Excel Fundamentals - Quick Start Guide Analysis | — | [Principles of Finance 18.6 Using Excel to Create the Long-Term Forecast](https://openstax.org/books/principles-finance/pages/18-6-using-excel-to-create-the-long-term-forecast) (OpenStax, web) | close |
| Excel shortcuts - Mac | — | [Keyboard shortcuts in Excel](https://support.microsoft.com/en-us/office/keyboard-shortcuts-in-excel-1798d9d5-842a-42b8-9c99-9b7213f0040f) (Microsoft Support, web) | same |
| Excel shortcuts - PC | — | [Keyboard shortcuts in Excel](https://support.microsoft.com/en-us/office/keyboard-shortcuts-in-excel-1798d9d5-842a-42b8-9c99-9b7213f0040f) (Microsoft Support, web) | same |
| Financial Analysis Glossary | — | [Harvey's Hypertextual Finance Glossary](https://people.duke.edu/~charvey/Classes/wpg/glossary.htm) (Duke University (Campbell R. Harvey), web) | close |
| Macabacus Quick Start Guide | — | [Macabacus Quick Start Guide (PDF, 12 pp.)](https://lseg.com/content/dam/marketing/en_us/documents/learning-centre/macabacus-start-guide.pdf) (LSEG (Macabacus guide, client-branded copy), pdf) | same |
| Macabacus Quick Start Guide (2) | — | [Macabacus Quick Start Guide (PDF, 12 pp.)](https://lseg.com/content/dam/marketing/en_us/documents/learning-centre/macabacus-start-guide.pdf) (LSEG (Macabacus guide, client-branded copy), pdf) | same |
| MAX Template | — | [MAX function](https://support.microsoft.com/en-us/excel/functions/max-function) (Microsoft Support, web) | same |
| NORMDIST Template | — | [NORMDIST function](https://support.microsoft.com/en-us/excel/functions/normdist-function) (Microsoft Support, web) | same |
| OR Template | — | [OR function](https://support.microsoft.com/en-us/excel/functions/or-function) (Microsoft Support, web) | same |
| ROUNDUP Template | — | [ROUNDUP function](https://support.microsoft.com/en-us/excel/functions/roundup-function) (Microsoft Support, web) | same |
| SEARCH Template | — | [SEARCH, SEARCHB functions](https://support.microsoft.com/en-us/excel/functions/search-function) (Microsoft Support, web) | same |
| Sheet Name Formula Template | — | [Get sheet name only](https://exceljet.net/formulas/get-sheet-name-only) (Exceljet, web) | same |
| SUBTOTAL Template | — | [SUBTOTAL function](https://support.microsoft.com/en-us/excel/functions/subtotal-function) (Microsoft Support, web) | same |
| Variance Formula | — | [Get percent change](https://exceljet.net/formulas/get-percent-change) (Exceljet, web) | same |

## Deal, legal & business documents (12)

| CFI title | Engine | Best source | Match |
|---|---|---|---|
| Appraisal Checklist | — | [Commercial Real Estate Lending, Appendix E: Appraisal Review Worksheet (plus Internal Control Questionnaire)](https://www.occ.gov/publications-and-resources/publications/comptrollers-handbook/files/commercial-real-estate-lending/pub-ch-commercial-real-estate.pdf) (OCC Comptroller's Handbook, pdf) | same |
| Business Letter Format Template | — | [Business Letter Template](https://www.vertex42.com/WordTemplates/business-letter.html) (Vertex42, docx via download page) | same |
| Clean Cover Letter Template | — | [Cover letter templates](https://create.microsoft.com/en-us/templates/cover-letters) (Microsoft Create, docx via download page) | close |
| Clean Resignation Letter Template | — | [Letter of Resignation Template](https://www.vertex42.com/WordTemplates/resignation-letter.html) (Vertex42, docx via download page) | same |
| Confidential Information Memorandum Template | — | [CIM sample template (PDF)](https://biws-support.s3.amazonaws.com/CIM/CIM-07-Sample-Template.pdf) (Mergers & Inquisitions (BIWS), pdf) | same |
| Creative Cover Letter | — | [Cover letter templates (creative designs)](https://create.microsoft.com/en-us/templates/cover-letters) (Microsoft Create, docx via download page) | close |
| ECM Deals Committee Memo Template | — | [Lehman Brothers High Grade / Commitment / Equity Commitment Committee memorandum (2007, 31 pp)](https://web.stanford.edu/~jbulow/lehmandocs/docs/DEBTORS/LBEX-AM%20112872-112902.pdf) (Stanford (Lehman examiner documents, J. Bulow), pdf) | close |
| General Cover Letter Template | — | [Resume Cover Letter Template](https://www.vertex42.com/WordTemplates/cover-letter-template.html) (Vertex42, docx via download page) | same |
| Letter of Intent Template | — | [Profusa, Inc. / Bio Insights LLC Non-Binding Letter of Intent (EX-99.1, 8-K, Apr 2026)](https://www.sec.gov/Archives/edgar/data/1859807/000121390026040111/ea028515101ex99-1.htm) (SEC EDGAR, web) | same |
| Line Cover Letter Template | — | [Cover letter templates](https://create.microsoft.com/en-us/templates/cover-letters) (Microsoft Create, docx via download page) | close |
| NDA Confidentiality Agreement Sample | — | [CECO Environmental / Profire Energy Mutual Confidentiality Agreement (EX-99.(d)(2), SC TO, Aug 2024)](https://www.sec.gov/Archives/edgar/data/1289636/000110465924124892/tm2426882d6_ex99-d2.htm) (SEC EDGAR, web) | same |
| Term Sheet Template | — | [Standard Series A Term Sheet (docx)](https://bookface-static.ycombinator.com/assets/ycdc/Standard_Series_A_TS-da51af523a01165d6514a085678c50c8514fce6acd5ab83553c3f47ce0dffacb.docx) (Y Combinator, docx) | same |

## Soft-skills diagnostics (outside the toolkit's finance scope) (8)

| CFI title | Engine | Best source | Match |
|---|---|---|---|
| Active Listening Diagnostic | — | [Listening Skills Self-Evaluation](https://www.pugetsound.edu/sites/default/files/2022-11/listen-skills-eval.pdf) (University of Puget Sound, pdf) | same |
| Coaching for Workplace Performance Assessment | — | [Coaching Skills for Managers Workbook](https://www.dsc.org.uk/wp-content/uploads/2024/03/Coaching-Skills-for-Managers-Workbook.pdf) (Directory of Social Change, pdf) | close |
| Communication Styles Diagnostic | — | [Assert Yourself module 1: What is Assertiveness](https://www.cci.health.wa.gov.au/-/media/CCI/Consumer-Modules/Assert-Yourself/Assert-Yourself---01---What-is-Assertiveness.pdf) (Centre for Clinical Interventions (WA Health), pdf) | close |
| Conflict Styles Questionnaire | — | [Basics of Conflict Management (TKI-style 30-item instrument with scoring grid)](https://www.sandiego.gov/sites/default/files/2025-07/basics-of-conflict-management.pdf) (City of San Diego, pdf) | same |
| Giving Feedback | — | [Performance Management & Accountability Playbook: Monitoring and Developing](https://www.opm.gov/policy-data-oversight/performance-management/performance-management-and-accountability-playbook/monitoring-and-developing/) (US OPM, web) | partial |
| Hybrid Team Self-Reflection | — | [Support for remote and hybrid work (team question set and checklist)](https://sites.tuni.fi/digitaltoolkit/teamwork-and-collaboration/support-for-remote-and-hybrid-work/) (Tampere University Digital Toolkit, web) | close |
| Managing Relationships at Work | — | [Your Employeeship Questionnaire: a survey of the relationships at your workplace (short v1.2)](https://www.lunduniversity.lu.se/lup/publication/4f507b32-f107-4e14-a8d5-ec5941a64b5d) (Lund University, web) | partial |
| Team Development Diagnostic | — | [Team Development Questionnaire (Tuckman stages)](http://www.nwlink.com/~donclark/leader/teamsuv.html) (Donald Clark (Big Dog & Little Dog), web) | same |

## Partial matches only

No free source reproduces these templates. Where an engine is named, it is the free equivalent.

- **Adjusted EBITDA** — No free calculator found; SEC sources define what adjustments are permissible and the required reconciliation format. Engine: `finmodel.earnings_bridges.adjusted_ebitda`.
- **CFI Essential Guide to Breaking into FP&A** — No free, non-signup third-party FP&A career eBook verified; web search surfaced Teachable/Gumroad sign-up products only. The CFI guide itself is free with a CFI login.
- **Cash EPS** — Cash EPS is a non-standard metric; no free dedicated template found. Engine: `finmodel.earnings_bridges.cash_eps`.
- **FP&A Monthly Rollforward Template** — Paid CFI template not inspected (no spec); matches inferred from title/engine (rolling forecast). Engine: `finmodel.fpa_planning.rolling_forecast`.
- **Giving Feedback** — No free stand-alone feedback-giving diagnostic was found. Only guidance and broader supervisor checklists.
- **Managing Relationships at Work** — No free same/close equivalent was found. The available options are adjacent research questionnaires and quizzes.
- **Net Identifiable Assets Template** — No free standalone PPA / net identifiable assets template found. Engine: `finmodel.ppa_valuation.allocate`.
- **Revenue Variance Analysis** — No free sales price/volume/mix workbook found from a reputable source. Engine: `finmodel.variance_analysis.sales_mix_and_volume_variance`.
- **SME Lending - Owner's Net Worth Adjustment Template** — Bank-specific credit worksheet; no free equivalent found. Engine: `finmodel.personal_finance.owner_net_worth_adjustment`.
