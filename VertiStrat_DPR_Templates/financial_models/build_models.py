import sys,json
sys.path.insert(0,'/Users/umashankar/financial-analysis-toolkit')
from finmodel import dcf, fin, project_finance as pf, india_corporate_tax_regimes as tx, india_depreciation_schedule as dep
from finmodel.excel import write_record_tables
MD=json.load(open('/tmp/dpr/t/models.json'))
NAMES={'biodiesel':'Biodiesel_B100_20KLPD','cbg':'CBG_10TPD','ethanol':'Ethanol_Grain_100KLPD','saf':'SAF_HEFA_100TPD','food':'FoodProcessing_FruitVeg_10000tpa'}
r2=lambda x:round(x,3) if isinstance(x,(int,float)) else x
summary_all=[]
for key,name in NAMES.items():
    cfg=MD[key]['cfg'];m=MD[key]['m'];s=MD[key]['s'];R=m['rows'];L=cfg['loan']
    tax=[max(r['ebitda']-r['dep']-r['intr'],0)*0.2517 for r in R]
    cfads=[r['ebitda']-t for r,t in zip(R,tax)]
    n=L['tenor']
    cf=cfads+[cfads[-1]]*max(0,n-10)
    # 1. debt structuring via toolkit
    cmp_=pf.compare_debt_structures(m['TL'],L['rate'],n,cf[:n],target_dscr=1.25)
    scl=pf.sculpted_amortization(cf[:n],m['TL'],1.25,L['rate'])
    size=pf.size_debt_by_dscr(cf[:n],1.25,L['rate'])
    llcr=pf.llcr(cf[1:n],m['TL'],L['rate'])
    ann=pf.level_annuity_schedule(m['TL'],L['rate'],n)
    # 2. DCF via toolkit
    wc=[0]+[r['wc'] for r in R]; dn=[wc[i+1]-wc[i] for i in range(10)]
    inp=dcf.DCFInputs(ebit=[r['ebitda']-r['dep'] for r in R],da=[r['dep'] for r in R],change_nwc=dn,capex=0.0,tax_rate=0.2517,discount_rate=0.12,perpetual_growth=0.0,transaction_date="2027-03-31",fiscal_year_end="2028-03-31",debt=m['TL'],cash=0.0,terminal_method="perpetuity",shares_outstanding=1,current_price=1)
    d=dcf.run(inp)
    sens=dcf.sensitivity(inp,[0.10,0.12,0.14,0.16],[0.0,0.02],metric='enterprise_value') if True else None
    npv=d['enterprise_value']-(m['fixed']+wc[1])+m['sub']
    # 3. tax & CGTMSE
    regimes={"115BAA (22% + 10% surcharge + 4% cess)":dict(base_rate=.22,surcharge_rate=.10,cess_rate=.04),"Old regime (30% + 4% cess)":dict(base_rate=.30,surcharge_rate=0.0,cess_rate=.04)}
    pre=R[4]['ebitda']-R[4]['dep']-R[4]['intr']+R[4]['dep']
    trc=tx.tax_regime_comparison(R[4]['ebitda'],m['fixed'],10,regimes)
    cg=tx.cgtmse_adjusted_dscr(cfads[4],m['TL'],L['rate'],n,0.01,1.25)
    mach=sum(v for k,v in cfg['capex'].items())*0.0+cfg['capex_groups']['mach']
    wdv=dep.multi_year_block_schedule(0.0,0.15,[[dict(amount=mach,used_180_days_or_more=True)]]+[[] for _ in range(9)])
    sh={}
    sh['Summary']=dict(headers=['Metric','Value'],rows=[
      ['Project',cfg['title']],['Capacity',cfg['cap']],['Total project cost (₹ cr)',r2(m['total'])],['Fixed capital (₹ cr)',r2(m['fixed'])],['Term loan (₹ cr)',r2(m['TL'])],['Capital subsidy (₹ cr)',r2(m['sub'])],['Promoter equity (₹ cr)',r2(m['EQ'])],
      ['Year-5 revenue (₹ cr)',r2(R[4]['rev'])],['Year-5 EBITDA (₹ cr)',r2(R[4]['ebitda'])],['Project IRR (model)',r2(m['irr'])],['Payback (years)',r2(m['pb']) if m['pb'] else 'n/a'],
      ['Average DSCR over loan (model)',r2(m['avg_dscr'])],['Minimum DSCR over loan (model)',r2(m['min_dscr'])],
      ['Unlevered DCF enterprise value @12%, g=0 (₹ cr) [finmodel.dcf]',r2(d['enterprise_value'])],['NPV = EV minus project cost net of subsidy (₹ cr)',r2(npv)],
      ['Max debt sized at DSCR 1.25 (₹ cr) [finmodel.project_finance]',r2(size['max_debt_sized'])],['LLCR at year 1 [finmodel.project_finance]',r2(llcr['llcr']) if 'llcr' in llcr else r2(list(llcr.values())[-1])],
      ['Year-5 DSCR incl. CGTMSE 1% fee [finmodel.india_corporate_tax_regimes]',r2(cg['dscr_with_cgtmse_fee'])],['Best tax regime',trc['best_regime']]])
    sh['Assumptions']=dict(headers=['Item','Value','Note'],rows=[['Capex: '+k,r2(v),'₹ crore, placeholder'] for k,v in cfg['capex'].items()]+[['Revenue: '+l['name'],f"{l['qty']:,.0f} {l['unit']} × ₹{l['price']}",'full capacity; placeholder'] for l in cfg['rev']]+[['Cost: '+l['name'],f"{l['qty']:,.0f} {l['unit']} × ₹{l['price']}",'full capacity; placeholder'] for l in cfg['var']]+[['Capacity ramp',', '.join(f'{u:.0%}' for u in cfg['util'][:5])+' then flat',''],['Loan',f"{L['share']:.0%} of fixed capital, {L['rate']:.1%}, {L['tenor']} yr incl {L['moratorium']} yr moratorium",''],['Working capital days',str(cfg['wc']),''],['Tax','25.17% (115BAA)','']])
    sh['Projections']=dict(headers=['Year','Utilisation','Revenue','Operating cost','EBITDA','Depreciation','Interest','Tax (derived)','PAT','CFADS','DSCR (term loan)','Working capital'],rows=[[r['year'],r2(r['util']),r2(r['rev']),r2(r['cost']),r2(r['ebitda']),r2(r['dep']),r2(r['intr']),r2(t),r2(r['pat']),r2(c),r2(r['dscr']),r2(r['wc'])] for r,t,c in zip(R,tax,cfads)])
    sh['Debt structures']=dict(headers=['Structure','Total interest','Year-1 debt service','Min DSCR','Average DSCR'],rows=[[k.replace('_',' '),r2(v['total_interest']),r2(v['year1_debt_service']),r2(v['min_dscr']),r2(v['average_dscr'])] for k,v in cmp_.items()]+[['',None,None,None,None],['Level annuity payment per year',r2(ann['level_payment']),None,None,None],['Max debt supportable at DSCR 1.25',r2(size['max_debt_sized']),None,None,None]])
    sh['Sculpted schedule']=dict(headers=['Year','Opening','Interest','Principal','Closing','CFADS','DSCR'],rows=[[i+1,r2(x['opening_balance']),r2(x['interest']),r2(x['principal']),r2(x['opening_balance']-x['principal']),r2(x['cfads']),r2(x.get('dscr',0)) if 'dscr' in x else ''] for i,x in enumerate(scl['schedule'])])
    sh['DCF']=dict(headers=['Year','EBIT','Cash tax','D&A','Change NWC','Unlevered FCF'],rows=[[d['years'][i],r2(d['ebit'][i]),r2(d['cash_taxes'][i]),r2(d['da'][i]),r2(d['change_nwc'][i]),r2(d['ufcf'][i])] for i in range(10)]+[['Terminal value (perpetuity, g=0)',None,None,None,None,r2(d['terminal_value']['used'])],['Enterprise value @12%',None,None,None,None,r2(d['enterprise_value'])],['Project cost net of subsidy (year 1)',None,None,None,None,r2(m['fixed']+wc[1]-m['sub'])],['NPV',None,None,None,None,r2(npv)]])
    sens_rows=[]
    if isinstance(sens,dict):
        tbl=sens.get('table') or sens.get('values') or sens.get('grid')
        dr=sens.get('rows');gr=sens.get('cols')
        if tbl and dr and gr:
            for i,a in enumerate(dr):
                sens_rows.append([f'discount {a:.0%}']+[r2(tbl[i][j]) for j in range(len(gr))])
            sh['DCF sensitivity (EV)']=dict(headers=['']+[f'g={g:.0%}' for g in gr],rows=sens_rows)
    sh['Tax and CGTMSE']=dict(headers=['Item','Value'],rows=[[f'Post-tax IRR: {k}',r2(v['irr_post_tax'])] for k,v in trc['regimes'].items()]+[['Best regime',trc['best_regime']],['Annual debt service (annuity, ₹ cr)',r2(cg['annual_debt_service'])],['CGTMSE annual fee at 1.0% (assumption, check current fee)',r2(cg['annual_guarantee_fee'])],['DSCR with fee',r2(cg['dscr_with_cgtmse_fee'])],['DSCR without fee',r2(cg['dscr_without_fee_for_comparison'])],['Compliant with 1.25',str(cg['compliant'])]])
    sh['Tax depreciation (WDV)']=dict(headers=['Year','Opening WDV','Depreciation (15% block)','Closing WDV'],rows=[[x['year'],r2(x['opening_wdv']),r2(x['depreciation']),r2(x['closing_wdv'])] for x in wdv['rows']])
    sh['Sensitivity']=dict(headers=['Case','Yr-5 EBITDA','Yr-5 DSCR','Avg DSCR','IRR'],rows=[['Base',r2(s['base']['ebitda']),r2(s['base']['dscr']),r2(m['avg_dscr']),r2(s['base']['irr'])]]+[[x['label'],r2(x['ebitda']),r2(x['dscr']),r2(x['avg']),r2(x['irr'])] for x in s['rows']])
    out=f'/tmp/dpr/fm/Model_{name}.xlsx'
    write_record_tables(out,sh,readme_lines=['VertiStrat illustrative financial model. All prices and costs are placeholders to replace with quotes. Units: ₹ crore.','Cash-flow projections come from the template model (engine.py). Debt structuring (finmodel.project_finance), DCF (finmodel.dcf), tax regimes and CGTMSE (finmodel.india_corporate_tax_regimes) and tax depreciation (finmodel.india_depreciation_schedule) come from the financial-analysis-toolkit engines.','CGTMSE fee 1.0% and DCF discount rate 12% are assumptions. Check lender terms.','The DCF treats the plant as a going concern with terminal value at zero growth, so it is more generous than the 10-year project IRR, which assumes 20% salvage. Loan tenors longer than 10 years use flat year-10 cash flow for the debt tests.'],workbook_title='VertiStrat model '+key)
    summary_all.append((key,round(m['irr'],3),round(d['irr'],3),round(npv,1),round(size['max_debt_sized'],1),round(m['TL'],1),round(cg['dscr_with_cgtmse_fee'],2),cg['compliant'],trc['best_regime']))
    print(key,'model IRR',round(m['irr'],3),'dcf irr',round(d['irr'],3),'NPV',round(npv,1),'maxdebt@1.25',round(size['max_debt_sized'],1),'TL',m['TL'],'cgtmse dscr',round(cg['dscr_with_cgtmse_fee'],2),'sens keys',list(sens.keys())[:5] if isinstance(sens,dict) else sens)
