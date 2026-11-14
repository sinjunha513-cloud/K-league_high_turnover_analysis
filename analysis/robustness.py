from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import sys
out=Path(sys.argv[1] if len(sys.argv)>1 else 'results_revalidated')
s=pd.read_csv(out/'sequences.csv');a=json.loads((out/'audit.json').read_text())
rng=np.random.default_rng(20261114);games=np.sort(s.game_id.unique());ix=rng.integers(0,len(games),(2000,len(games)))
counts=s.groupby('game_id').is_shot.agg(['sum','size']).reindex(games).to_numpy();c=counts[ix].sum(1);rate=c[:,0]/c[:,1]
cent=s[s.zone.eq('Central')].groupby('game_id').is_shot.agg(['sum','size']).reindex(games,fill_value=0).to_numpy()[ix].sum(1)
flank=s[s.zone.eq('Flank')].groupby('game_id').is_shot.agg(['sum','size']).reindex(games,fill_value=0).to_numpy()[ix].sum(1)
diff=cent[:,0]/cent[:,1]-flank[:,0]/flank[:,1]
form=a['model']['formula']
rows=[]
for label,data,f in [('main',s,form),('nonlinear_x',s,form+' + I(x10 ** 2)'),('without_duel',s[s.turnover_type.ne('Duel')],form),('without_block',s[s.turnover_type.ne('Block')],form)]:
    fit=smf.glm(f,data,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':data.game_id})
    for term in fit.params.index:
        if 'zone' in term:
            rows.append(dict(model=label,n=len(data),term=term,OR=np.exp(fit.params[term]),low=np.exp(fit.conf_int().loc[term,0]),high=np.exp(fit.conf_int().loc[term,1]),converged=fit.converged))
pd.DataFrame(rows).to_csv(out/'model_sensitivity.csv',index=False)
tied=s.time_to_shot.eq(0)
r=dict(overall_shot_ci=[float(x*100) for x in np.quantile(rate,[.025,.975])],
       central_flank_difference_ci_pp=[float(x*100) for x in np.quantile(diff,[.025,.975])],
       zero_time_shots=int(tied.sum()),positive_time_shots=int((s.time_to_shot>0).sum()),
       positive_time_shot_pct=100*float((s.time_to_shot>0).sum())/len(s))
(out/'supplement.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
print(pd.DataFrame(rows).to_string(index=False))
