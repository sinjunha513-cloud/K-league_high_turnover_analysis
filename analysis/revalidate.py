"""Revalidation of K League event-based high turnovers.
Usage: python revalidate.py --data raw_data.csv --matches match_info.csv --out results
Coordinates: 105 x 68. First subsequent shot outcome, not all eventual goals.
No raw data distributed. Event-derived possession is an operational estimate.
"""
import argparse, hashlib, json, platform
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
import statsmodels.api as sm
import statsmodels.formula.api as smf

SHOTS={'Shot','Shot_Freekick','Penalty Kick'}
STOPS={'Out','Foul','Offside','Pause','Handball_Foul','Foul_Throw','Goal','Own Goal'}
RESTARTS={'Throw-In','Goal Kick','Pass_Corner','Pass_Freekick','Shot_Freekick','Penalty Kick'}
TOUCHES={'Pass','Pass Received','Carry','Cross','Shot','Shot_Freekick','Penalty Kick',
         'Throw-In','Goal Kick','Pass_Corner','Pass_Freekick','Clearance','Aerial Clearance',
         'Ball Received','Catch','Take-On'}
DEFENSE={'Recovery','Interception','Tackle','Duel'}

def prepare(raw):
    d=raw.sort_values(['game_id','period_id','time_seconds','action_id'],kind='stable').reset_index(drop=True).copy()
    keys=['game_id','period_id','team_id']
    groups=d[keys].drop_duplicates()
    s=d[d.type_name.isin(SHOTS)].groupby(keys).start_x.mean().rename('shot_x')
    g=d[d.type_name.eq('Goal Kick')].groupby(keys).start_x.median().rename('gk_x')
    direction=groups.join(s,on=keys).join(g,on=keys)
    direction['right']=np.where(direction.shot_x.notna(),direction.shot_x.ge(52.5),np.nan)
    for ix,row in direction[direction.right.isna()].iterrows():
        opp=direction[(direction.game_id==row.game_id)&(direction.period_id==row.period_id)&(direction.team_id!=row.team_id)&direction.right.notna()]
        if len(opp)==1: direction.loc[ix,'right']=1-int(opp.iloc[0].right)
        elif pd.notna(row.gk_x): direction.loc[ix,'right']=int(row.gk_x<52.5)
        else: raise ValueError('Direction has no independent evidence')
    direction['gk_agrees']=np.where(direction.gk_x.notna(),(direction.gk_x<52.5)==direction.right.astype(bool),np.nan)
    assert direction.loc[direction.gk_x.notna(),'gk_agrees'].all()
    d=d.merge(direction[keys+['right']],on=keys,validate='many_to_one',sort=False)
    d['x']=np.where(d.right.eq(1),d.start_x,105-d.start_x)
    d['y']=np.where(d.right.eq(1),d.start_y,68-d.start_y)
    return d,direction

def iscontrol(typ,res,extended=True):
    return typ in TOUCHES if extended else typ in (TOUCHES-{'Ball Received','Catch','Take-On','Aerial Clearance'})

def run(d,threshold=70,window=15,block_seconds=5,extended=True,reset_restarts=True,credit_blocks=True):
    """One record per control transition. Block attribution occurs at confirmed control;
    time and location both refer to that control, not to earlier block contact."""
    rows=list(d.itertuples(index=False))
    n=len(rows)
    control=np.array([iscontrol(r.type_name,r.result_name,extended) or
        (r.type_name in {'Recovery','Interception'} and r.result_name!='Unsuccessful') or
        (r.type_name in {'Tackle','Duel'} and r.result_name=='Successful') for r in rows])
    boundary=np.array([r.type_name in STOPS or (r.type_name in SHOTS and r.result_name=='Goal') for r in rows])
    contexts=[(r.game_id,r.period_id) for r in rows]
    owner=None; context=None; pending=None; transitions=[]; poss=0; possession_records=[]
    for i,r in enumerate(rows):
        if contexts[i]!=context: owner=None;pending=None;context=contexts[i]
        if reset_restarts and r.type_name in RESTARTS: owner=None;pending=None
        if r.type_name=='Block' and owner is not None and owner!=r.team_id:
            pending=(i,r.team_id,r.time_seconds)
        if control[i]:
            previous=owner
            if owner!=r.team_id:
                poss+=1;possession_records.append((r.game_id,r.team_id,poss))
                typ=r.type_name if r.type_name in DEFENSE else None
                block_ix=None
                if credit_blocks and pending and pending[1]==r.team_id and 0<=r.time_seconds-pending[2]<=block_seconds:
                    typ='Block';block_ix=pending[0]
                if previous is not None and typ and r.x>=threshold:
                    transitions.append((i,typ,poss,block_ix))
                pending=None
            owner=r.team_id
        if boundary[i]:owner=None;pending=None
    records=[]
    for i,typ,pid,block_ix in transitions:
        r=rows[i]; shot=None; last=i;first=None; passes=0; carry=0
        for j in range(i+1,n):
            a=rows[j];dt=a.time_seconds-r.time_seconds
            if contexts[j]!=contexts[i] or dt>window:break
            if dt<0:continue
            if a.type_name in STOPS or (reset_restarts and a.type_name in RESTARTS):break
            if a.team_id!=r.team_id:
                if control[j]:break
                continue
            if control[j]: last=j
            if first is None and a.type_name in TOUCHES: first=a.type_name
            passes+=int(a.type_name=='Pass');carry+=int(a.type_name=='Carry')
            if a.type_name in SHOTS:shot=j;break
        endpoint=rows[last];duration=endpoint.time_seconds-r.time_seconds
        records.append(dict(game_id=r.game_id,period_id=r.period_id,team_id=r.team_id,team_name=r.team_name_ko,
            action_id=r.action_id,event_index=i,possession_id=pid,block_event_index=block_ix,
            turnover_type=typ,time_seconds=r.time_seconds,x=r.x,y=r.y,
            zone='Central' if 23<=r.y<=45 else ('Half-space' if 14<=r.y<23 or 45<r.y<=54 else 'Flank'),
            is_shot=int(shot is not None),is_goal=int(shot is not None and rows[shot].result_name=='Goal'),
            shot_event_index=shot,shot_action_id=rows[shot].action_id if shot is not None else None,
            time_to_shot=rows[shot].time_seconds-r.time_seconds if shot is not None else np.nan,
            first_action=first or 'None',pass_count=passes,carry_count=carry,
            observed_duration=duration,net_start_progress=endpoint.x-r.x,
            ball_progress_rate=(endpoint.x-r.x)/duration if duration>=1 else np.nan))
    s=pd.DataFrame(records)
    if s.empty: return s,pd.DataFrame(possession_records,columns=["game_id","team_id","possession_id"])
    assert not s.possession_id.duplicated().any()
    assert not s.loc[s.is_shot.eq(1),['game_id','shot_action_id']].duplicated().any()
    return s,pd.DataFrame(possession_records,columns=['game_id','team_id','possession_id'])

def summarize(s):
    return dict(turnovers=len(s),shots=int(s.is_shot.sum()),goals=int(s.is_goal.sum()),
                shot_pct=100*s.is_shot.mean(),goal_pct=100*s.is_goal.mean())

def bootstrap(s,groups='zone',seed=20261114,B=2000):
    rng=np.random.default_rng(seed);games=np.sort(s.game_id.unique());out=[]
    for label,sub in s.groupby(groups):
        a=sub.groupby('game_id').is_shot.agg(['sum','size']).reindex(games,fill_value=0).to_numpy()
        idx=rng.integers(0,len(games),(B,len(games)));v=a[idx].sum(axis=1);rate=v[:,0]/v[:,1]
        out.append(dict(group=label,n=len(sub),shots=int(sub.is_shot.sum()),goals=int(sub.is_goal.sum()),
                        shot_pct=100*sub.is_shot.mean(),ci_low=100*np.quantile(rate,.025),ci_high=100*np.quantile(rate,.975)))
    return pd.DataFrame(out)

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',required=True);p.add_argument('--matches',required=True);p.add_argument('--out',required=True);args=p.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(args.data);matches=pd.read_csv(args.matches)
    assert not raw.duplicated(['game_id','action_id']).any()
    assert raw[['game_id','action_id','period_id','time_seconds','team_id','start_x','start_y','end_x','end_y']].notna().all().all()
    assert set(raw.game_id)==set(matches.game_id)
    assert raw.start_x.between(0,105).all() and raw.start_y.between(0,68).all()
    d,direction=prepare(raw);direction.to_csv(out/'direction_checks.csv',index=False)
    # Reconstruct final score from shot results and own goals; Goal rows duplicate shot-result goals.
    goalrows=raw[(raw.type_name.isin(SHOTS)&raw.result_name.eq('Goal'))|raw.type_name.eq('Own Goal')].copy()
    goalrows=goalrows.merge(matches[['game_id','home_team_id','away_team_id']],on='game_id',validate='many_to_one')
    goalrows['beneficiary']=np.where(goalrows.type_name.eq('Own Goal'),np.where(goalrows.team_id==goalrows.home_team_id,goalrows.away_team_id,goalrows.home_team_id),goalrows.team_id)
    counts=goalrows.groupby(['game_id','beneficiary']).size()
    final=matches[['game_id','home_score','away_score']].copy()
    final['reconstructed_home']=[counts.get((r.game_id,r.home_team_id),0) for r in matches.itertuples()]
    final['reconstructed_away']=[counts.get((r.game_id,r.away_team_id),0) for r in matches.itertuples()]
    final['match']=final.home_score.eq(final.reconstructed_home)&final.away_score.eq(final.reconstructed_away)
    final.to_csv(out/'score_checks.csv',index=False)
    s,poss=run(d)
    s=s.merge(matches[['game_id','home_team_id','away_team_id','game_day']],on='game_id',validate='many_to_one')
    s['home']=(s.team_id==s.home_team_id).astype(int)
    s['opponent_id']=np.where(s.home.eq(1),s.away_team_id,s.home_team_id)
    # Pre-turnover score, strictly earlier timestamps, excludes same-time ambiguous goals.
    diffs=[]
    for r in s.itertuples():
        g=goalrows[(goalrows.game_id==r.game_id)&((goalrows.period_id<r.period_id)|((goalrows.period_id==r.period_id)&(goalrows.time_seconds<r.time_seconds)))]
        diffs.append(int((g.beneficiary==r.team_id).sum()-(g.beneficiary!=r.team_id).sum()))
    s['score_diff']=diffs;s['x10']=(s.x-70)/10;s['minute10']=s.time_seconds/600
    s.to_csv(out/'sequences.csv',index=False)
    bootstrap(s).to_csv(out/'zones.csv',index=False);bootstrap(s,'turnover_type').to_csv(out/'types.csv',index=False)
    team=bootstrap(s,'team_name')
    den=poss.groupby('team_id').size();names=d[['team_id','team_name_ko']].drop_duplicates().set_index('team_name_ko').team_id
    team['all_possessions']=[den.get(names[x],0) for x in team.group]
    team['high_turnover_pct']=100*team.n/team.all_possessions
    team.to_csv(out/'teams.csv',index=False)
    sensitivity=[]
    configs=[('main',{}),*[(f'window_{w}',dict(window=w)) for w in [5,10,20]],
        *[(f'x_{x}',dict(threshold=x)) for x in [65,75]],
        ('block_3',dict(block_seconds=3)),('block_10',dict(block_seconds=10)),
        ('no_block_credit',dict(credit_blocks=False)),('legacy_touch_set',dict(extended=False)),
        ('no_restart_reset',dict(reset_restarts=False))]
    for label,kw in configs:
        v,_=run(d,**kw);z=v.groupby('zone').is_shot.mean()
        sensitivity.append(dict(setting=label,**summarize(v),central_pct=100*z['Central'],flank_pct=100*z['Flank']))
    # Sensitivity to event ID ordering (timestamp regressions exist in source)
    alt=d.sort_values(['game_id','period_id','action_id'],kind='stable').reset_index(drop=True)
    v,_=run(alt);sensitivity.append(dict(setting='action_id_order',**summarize(v),central_pct=100*v[v.zone.eq('Central')].is_shot.mean(),flank_pct=100*v[v.zone.eq('Flank')].is_shot.mean()))
    pd.DataFrame(sensitivity).to_csv(out/'sensitivity.csv',index=False)
    formula='is_shot ~ C(zone, Treatment(reference="Flank")) + x10 + C(turnover_type) + C(team_id) + C(opponent_id) + C(period_id) + minute10 + home + score_diff'
    model=smf.glm(formula,s,family=sm.families.Binomial())
    fit=model.fit(cov_type='cluster',cov_kwds={'groups':s.game_id})
    ci=fit.conf_int()
    reg=pd.DataFrame(dict(term=fit.params.index,coefficient=fit.params.values,odds_ratio=np.exp(fit.params.values),
                         ci_low=np.exp(ci[0].values),ci_high=np.exp(ci[1].values),p=fit.pvalues.values))
    reg.to_csv(out/'regression.csv',index=False)
    checks=dict(converged=bool(fit.converged),rank=int(np.linalg.matrix_rank(model.exog)),columns=model.exog.shape[1],
        condition_number=float(np.linalg.cond(model.exog)),max_abs_coefficient=float(abs(fit.params).max()),
        clusters=s.game_id.nunique(),n=len(s),formula=formula)
    assert checks['converged'] and checks['rank']==checks['columns'] and np.isfinite(fit.params).all()
    # Same model with no block attribution to evaluate dependence on look-ahead rule.
    nob=s[~s.turnover_type.eq('Block')].copy()
    f2=smf.glm(formula,nob,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':nob.game_id})
    pd.DataFrame({'term':f2.params.index,'OR':np.exp(f2.params.values),'lo':np.exp(f2.conf_int()[0].values),'hi':np.exp(f2.conf_int()[1].values)}).to_csv(out/'regression_without_block.csv',index=False)
    audit=dict(**summarize(s),events=len(raw),games=raw.game_id.nunique(),teams=raw.team_id.nunique(),
        rounds=[int(matches.game_day.min()),int(matches.game_day.max())],date_range=[matches.game_date.min(),matches.game_date.max()],
        duplicate_event_ids=int(raw.duplicated(['game_id','action_id']).sum()),missing_core=0,
        direction_groups=len(direction),shot_direction_groups=int(direction.shot_x.notna().sum()),
        goal_kick_crosschecks=int(direction.gk_x.notna().sum()),direction_conflicts=int(direction.gk_agrees.eq(0).sum()),
        final_score_matches=int(final['match'].sum()),final_score_mismatches=int((~final['match']).sum()),
        duplicate_shots=int(s[s.is_shot.eq(1)].duplicated(['game_id','shot_action_id']).sum()),
        duplicate_possessions=int(s.possession_id.duplicated().sum()),
        action_time_inversions=int((raw.sort_values(['game_id','action_id']).groupby(['game_id','period_id']).time_seconds.diff()<0).sum()),
        rate_valid=int(s.ball_progress_rate.notna().sum()),rate_median=float(s.ball_progress_rate.median()),
        rate_max=float(s.ball_progress_rate.max()),rate_p99=float(s.ball_progress_rate.quantile(.99)),model=checks,
        sha256=hashlib.sha256(Path(args.data).read_bytes()).hexdigest(),
        versions=dict(python=platform.python_version(),pandas=pd.__version__,numpy=np.__version__,scipy=scipy.__version__,statsmodels=sm.__version__))
    (out/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
    print(json.dumps(audit,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
