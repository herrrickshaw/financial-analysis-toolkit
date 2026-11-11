import json,copy
def model(c,mult=None):
    mult=mult or {}
    fixed=sum(c['capex'].values()); util=c['util']; n=len(util)
    sub=c.get('subsidy',0.0)
    L=c['loan']
    rows=[];
    def lines(y,m):
        u=util[y]; esc=1.0
        rev=[ (l['qty']*u*l['price']*m.get('rev'+str(i),1)/1e7) for i,l in enumerate(c['rev'])]
        var=[ (l['qty']*u*l['price']*m.get('var'+str(i),1)/1e7) for i,l in enumerate(c['var'])]
        return u,rev,var
    # steady working capital at year5
    u,rev,var=lines(4,mult); fx=c['fixed']
    def fixed_cost(y,u): return fx['manpower']*1.05**y+fx['admin']*1.05**y+fx['maint']*(c['plant_pct']*fixed)+fx['insurance']*fixed+fx['other']*u+ fx.get('power',0)*u
    cost5=sum(var)+fixed_cost(4,u)
    wc5=sum(var[:c.get('rm_n',1)])*c['wc']['rm']/365+cost5*c['wc']['fg']/365+sum(rev)*c['wc']['rec']/365-sum(var[:c.get('rm_n',1)])*c['wc']['pay']/365
    wc_margin=round(0.25*wc5,2)
    total=fixed+wc_margin
    TL=round(L['share']*fixed,2); EQ=round(total-TL-sub,2)
    debt=TL; fl=[-(fixed+0)]; out=[]
    sched=[]
    dep_y=sum(v*c['dep'][k] for k,v in c['capex_groups'].items())
    for y in range(10):
        u=util[min(y,n-1)]
        _,rev,var=lines(min(y,n-1),mult)
        R=sum(rev); V=sum(var); F=fixed_cost(y,u); cost=V+F; ebitda=R-cost
        mor=L['moratorium']; rep_years=L['tenor']-mor
        rp=0
        if y>=mor and y<L['tenor']: rp=min(TL/rep_years,debt)
        intr=debt*L['rate']; open_=debt; debt-=rp
        wc=sum(var[:c.get('rm_n',1)])*c['wc']['rm']/365+cost*c['wc']['fg']/365+R*c['wc']['rec']/365-sum(var[:c.get('rm_n',1)])*c['wc']['pay']/365
        wi=max(wc-wc_margin,0)*L['wc_rate']
        pbt=ebitda-dep_y-intr-wi; tax=max(pbt,0)*0.2517; pat=pbt-tax
        dscr=(ebitda-tax)/(intr+rp+wi) if (intr+rp+wi)>0 else 0
        out.append(dict(year=y+1,util=u,rev=R,cost=cost,ebitda=ebitda,dep=dep_y,intr=intr+wi,pat=pat,dscr=dscr,wc=wc,rev_l=rev,var_l=var))
        sched.append(dict(year=y+1,open=open_,intr=intr,rp=rp,close=debt,ds=intr+rp,cfads=ebitda-tax,dscr=(ebitda-tax)/(intr+rp) if intr+rp>0 else 0))
        fl.append(ebitda-tax)
    fl[0]-=out[0]['wc']; fl[-1]+=out[-1]['wc']+0.2*fixed; fl[0]+=sub
    lo,hi=-.9,6
    for _ in range(200):
        m=(lo+hi)/2
        if sum(f/(1+m)**i for i,f in enumerate(fl))>0: lo=m
        else: hi=m
    cum=0;pb=None
    for i,f in enumerate(fl):
        prev=cum;cum+=f
        if cum>=0 and pb is None and i>0: pb=i-1+(-prev/f)
    ds=[s['dscr'] for s in sched if s['ds']>0]
    return dict(fixed=fixed,wc_margin=wc_margin,total=total,TL=TL,EQ=EQ,sub=sub,rows=out,sched=sched,irr=lo,pb=pb,avg_dscr=sum(ds)/len(ds) if ds else 0,min_dscr=min(ds) if ds else 0,wc5=wc5)
def sens(c):
    b=model(c);res=[]
    for lab,mm in (("Main product price -10%",{'rev0':.9}),("Main product price +10%",{'rev0':1.1}),("Main feedstock cost +10%",{'var0':1.1}),("Main feedstock cost +20%",{'var0':1.2}),("Both: price -10% and feedstock +10%",{'rev0':.9,'var0':1.1})):
        m=model(c,mm);res.append(dict(label=lab,ebitda=m['rows'][4]['ebitda'],dscr=m['rows'][4]['dscr'],irr=m['irr'],avg=m['avg_dscr']))
    return dict(base=dict(ebitda=b['rows'][4]['ebitda'],dscr=b['rows'][4]['dscr'],irr=b['irr']),rows=res)
UT=[.5,.65,.75,.8,.85,.85,.85,.85,.85,.85]
cfgs={}
# ---------- Biodiesel ----------
cfgs['biodiesel']=dict(title='Biodiesel (B100) Manufacturing Plant',cap='6,000 KL/yr (20 KLPD)',unit='KL',
 capex={"Land & site development":0.40,"Building & civil works":1.00,"Plant & machinery":2.50,"Storage tanks":1.10,"Utilities (thermopack, DG, electrical, fire-fighting)":0.40,"Pollution control & EMP":0.18,"Pre-operative expenses":0.35,"Contingency (~6%)":0.34},
 capex_groups={"mach":4.18,"bldg":1.00},dep={"mach":.10,"bldg":.0334},plant_pct=0.667,
 util=UT,rev=[dict(name='Biodiesel (₹/L)',qty=6000*1000,price=88.0,unit='L'),dict(name='Freight received (₹/KL)',qty=6000,price=649.25,unit='KL'),dict(name='Crude glycerol (₹/kg)',qty=528000,price=20,unit='kg')],
 var=[dict(name='UCO/non-edible oil incl. freight (₹/kg)',qty=5500000,price=82.5,unit='kg'),dict(name='Methanol incl. freight (₹/kg)',qty=581000,price=36,unit='kg'),dict(name='Catalyst (₹/kg)',qty=52800,price=90,unit='kg'),dict(name='Outbound freight cost (₹/KL)',qty=6000,price=584,unit='KL'),dict(name='Winter cold-flow treatment (₹/L on 1/3 output)',qty=2000000,price=1.0,unit='L')],
 rm_n=3,fixed=dict(manpower=.55,admin=.28,maint=.02,insurance=.009/7.5*7.5/6.27*0+.0014,other=.17,power=.15),
 wc=dict(rm=20,fg=7,rec=21,pay=15),loan=dict(share=.60,rate=.105,tenor=8,moratorium=1,wc_rate=.105),subsidy=0.0)
# ---------- CBG ----------
cap_cbg=dict({"Land & site development":3.0,"Civil, structures & feedstock yard":10.0,"Digesters, gas holders & CBG purification/compression":38.0,"Feed handling, FOM section & utilities":10.0,"Cascade filling / grid connectivity":3.0,"Pollution control, safety & EMP":1.5,"Pre-operative & financing costs":3.0,"Contingency (~5%)":3.5})
cfgs['cbg']=dict(title='Compressed Biogas (CBG) Plant',cap='10 TPD CBG; about 160 TPD mixed feedstock',unit='tonnes',
 capex=cap_cbg,capex_groups={"mach":sum(cap_cbg.values())-3.0-10.0,"bldg":10.0},dep={"mach":.10,"bldg":.0334},plant_pct=.7,
 util=[.5,.65,.75,.8,.85,.85,.85,.85,.85,.85],
 rev=[dict(name='CBG (₹/kg, GOBARdhan administered price)',qty=3300*1000,price=98.0,unit='kg'),dict(name='Fermented organic manure (₹/t)',qty=18000,price=3500,unit='t')],
 var=[dict(name='Feedstock (press mud, agri residue, napier) delivered (₹/t)',qty=52800,price=1500,unit='t'),dict(name='Power, chemicals, consumables',qty=1,price=45000000,unit='lump'),dict(name='Transport of CBG and FOM',qty=1,price=25000000,unit='lump')],
 rm_n=1,fixed=dict(manpower=1.8,admin=.8,maint=.03,insurance=.002,other=.0,power=0),
 wc=dict(rm=20,fg=10,rec=30,pay=10),loan=dict(share=.60,rate=.10,tenor=11,moratorium=2,wc_rate=.105),subsidy=20.0)
# ---------- Ethanol ----------
cap_e=dict({"Land & site development":6.0,"Civil, structures & storage":22.0,"Process plant (milling, fermentation, distillation, dehydration)":62.0,"DDGS dryer & evaporation":14.0,"Boiler, power & utilities":14.0,"Effluent treatment (zero liquid discharge)":8.0,"Pre-operative & financing costs":6.0,"Contingency (~5%)":8.0})
cfgs['ethanol']=dict(title='Grain-based Ethanol (1G) Distillery',cap='100 KLPD (about 33,000 KL/yr at 330 days)',unit='KL',
 capex=cap_e,capex_groups={"mach":sum(cap_e.values())-6-22,"bldg":22.0},dep={"mach":.10,"bldg":.0334},plant_pct=.75,
 util=[.55,.65,.70,.70,.70,.70,.70,.70,.70,.70],
 rev=[dict(name='Ethanol (₹/L, ex-depot; verify against OMC tender)',qty=33000*1000,price=71.0,unit='L'),dict(name='DDGS (₹/t)',qty=26000,price=20000,unit='t')],
 var=[dict(name='Maize/FCI rice (₹/t delivered)',qty=86800,price=22500,unit='t'),dict(name='Enzymes, chemicals, yeast',qty=1,price=90000000,unit='lump'),dict(name='Steam fuel and power',qty=1,price=140000000,unit='lump')],
 rm_n=1,fixed=dict(manpower=3.0,admin=1.2,maint=.02,insurance=.002,other=.0,power=0),
 wc=dict(rm=20,fg=10,rec=21,pay=10),loan=dict(share=.65,rate=.095,tenor=12,moratorium=2,wc_rate=.10),subsidy=0.0)
# ---------- SAF ----------
cap_s=dict({"Land & site development":20.0,"Civil, structures & tankage":70.0,"HEFA hydrotreating, isomerisation & fractionation units":330.0,"Hydrogen unit and utilities":120.0,"Feed pre-treatment (UCO cleaning)":35.0,"Effluent, safety & EMP":25.0,"Pre-operative & financing costs":45.0,"Contingency (~5%)":35.0})
cfgs['saf']=dict(title='Sustainable Aviation Fuel (HEFA from UCO) Plant',cap='30,000 t/yr feed (about 100 TPD); SAF about 24,000 t/yr',unit='t',
 capex=cap_s,capex_groups={"mach":sum(cap_s.values())-20-70,"bldg":70.0},dep={"mach":.10,"bldg":.0334},plant_pct=.8,
 util=[.45,.60,.70,.75,.80,.80,.80,.80,.80,.80],
 rev=[dict(name='SAF (₹/kg)',qty=24000*1000,price=165.0,unit='kg'),dict(name='Renewable diesel/naphtha co-products (₹/kg)',qty=4500*1000,price=85.0,unit='kg')],
 var=[dict(name='UCO delivered (₹/kg)',qty=30000*1000,price=72.0,unit='kg'),dict(name='Hydrogen, catalysts, utilities',qty=1,price=300000000,unit='lump'),dict(name='Logistics and certification',qty=1,price=60000000,unit='lump')],
 rm_n=1,fixed=dict(manpower=6.0,admin=2.5,maint=.02,insurance=.002,other=.0,power=0),
 wc=dict(rm=25,fg=15,rec=30,pay=10),loan=dict(share=.70,rate=.095,tenor=12,moratorium=2,wc_rate=.10),subsidy=0.0)
cap_f=dict({"Land & site development":2.5,"Civil, cold rooms & structures":7.0,"Pulping, blanching, aseptic filling & freezing lines":11.0,"Boiler, ETP & utilities":3.5,"Quality lab, safety & FSSAI compliance":0.8,"Pre-operative & financing costs":1.2,"Contingency (~5%)":1.4})
cfgs['food']=dict(title='Fruit and Vegetable Processing Unit (pulp, puree and frozen)',cap='10,000 t/yr raw input (about 50 TPD in season); 6,000 t/yr pulp and puree',unit='t',
 capex=cap_f,capex_groups={"mach":sum(cap_f.values())-2.5-7.0,"bldg":7.0},dep={"mach":.10,"bldg":.0334},plant_pct=.55,
 util=[.45,.60,.70,.75,.80,.80,.80,.80,.80,.80],
 rev=[dict(name='Pulp and puree (₹/kg)',qty=6000*1000,price=65.0,unit='kg'),dict(name='By-products: peel, stone, pomace (₹/kg)',qty=1500*1000,price=4.0,unit='kg')],
 var=[dict(name='Raw fruit and vegetables delivered (₹/kg)',qty=10000*1000,price=20.0,unit='kg'),dict(name='Packaging (aseptic bags, drums, cartons)',qty=1,price=40000000,unit='lump'),dict(name='Fuel, power, water and cold chain',qty=1,price=30000000,unit='lump')],
 rm_n=1,fixed=dict(manpower=1.8,admin=.7,maint=.03,insurance=.002,other=.0,power=0),
 wc=dict(rm=45,fg=30,rec=45,pay=10),loan=dict(share=.65,rate=.10,tenor=9,moratorium=1,wc_rate=.105),subsidy=0.0)
out={}
for k,c in cfgs.items():
    m=model(c); s=sens(c)
    out[k]=dict(cfg=c,m=m,s=s)
    r=m['rows'][4]
    print(k,'fixed',round(m['fixed'],1),'wc',round(m['wc_margin'],1),'TL',m['TL'],'EQ',m['EQ'],'| y5 rev',round(r['rev'],1),'ebitda',round(r['ebitda'],1),'dscr',round(r['dscr'],2),'irr',round(m['irr'],3),'pb',m['pb'],'avg dscr',round(m['avg_dscr'],2),'min',round(m['min_dscr'],2))
json.dump(out,open('models.json','w'))
