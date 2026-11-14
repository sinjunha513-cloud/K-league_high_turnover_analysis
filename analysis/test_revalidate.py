import unittest
import pandas as pd
from revalidate import run

def events(spec):
    out=[]
    for i,item in enumerate(spec):
        typ,team,time,*opts=item
        d=dict(type_name=typ,team_id=team,time_seconds=time,result_name='Successful',
               game_id=1,period_id=1,team_name_ko=str(team),action_id=i,x=80.,y=34.)
        if opts:d.update(opts[0])
        out.append(d)
    return pd.DataFrame(out)
class Rules(unittest.TestCase):
    def test_recovery_shot(self):
        s,_=run(events([('Pass',2,0),('Recovery',1,1),('Shot',1,4,{'result_name':'Goal'})]))
        self.assertEqual((len(s),s.is_shot.sum(),s.is_goal.sum()),(1,1,1))
    def test_failed_tackle(self):
        s,_=run(events([('Pass',2,0),('Tackle',1,1,{'result_name':'Unsuccessful'}),('Pass',1,2)]))
        self.assertTrue(s.empty)
    def test_block_intervening_no_doublecount(self):
        s,_=run(events([('Pass',2,0),('Block',1,1),('Intervention',2,1.5),('Block',1,1.6),('Recovery',1,2),('Shot',1,4)]))
        self.assertEqual(len(s),1);self.assertEqual(s.iloc[0].turnover_type,'Block');self.assertEqual(s.iloc[0].time_seconds,2)
    def test_restart_terminates(self):
        s,_=run(events([('Pass',2,0),('Recovery',1,1),('Pass_Freekick',1,3),('Shot',1,4)]))
        self.assertEqual(s.is_shot.sum(),0)
    def test_catch_terminates(self):
        s,_=run(events([('Pass',2,0),('Recovery',1,1),('Catch',2,3),('Shot',1,4)]))
        self.assertEqual(s.is_shot.sum(),0)
    def test_period_boundary(self):
        s,_=run(events([('Pass',2,0),('Recovery',1,1),('Shot',1,4,{'period_id':2})]))
        self.assertEqual(s.is_shot.sum(),0)
    def test_window_inclusive(self):
        for t,expected in [(16,1),(16.001,0)]:
            s,_=run(events([('Pass',2,0),('Recovery',1,1),('Shot',1,t)]))
            self.assertEqual(s.is_shot.sum(),expected)
    def test_equal_time_no_speed(self):
        s,_=run(events([('Pass',2,0),('Recovery',1,1),('Shot',1,1)]))
        self.assertTrue(pd.isna(s.iloc[0].ball_progress_rate))
    def test_first_shot_not_rebound_goal(self):
        s,_=run(events([('Pass',2,0),('Recovery',1,1),('Shot',1,3),('Shot',1,4,{'result_name':'Goal'})]))
        self.assertEqual(s.is_goal.sum(),0);self.assertEqual(s.is_shot.sum(),1)
    def test_threshold(self):
        s,_=run(events([('Pass',2,0),('Recovery',1,1,{'x':69.999}),('Shot',1,3)]))
        self.assertTrue(s.empty)
if __name__=='__main__':unittest.main()
