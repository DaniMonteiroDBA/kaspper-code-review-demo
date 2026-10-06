import unittest
from process import decide
class DecisionTests(unittest.TestCase):
    def clean(self): return dict(findings=[],complete=True,limitations=[])
    def test_clean(self): self.assertEqual(decide(self.clean(),'success'),'CONCLUIDO_SEM_ESCALONAMENTO')
    def test_failed_ci(self): self.assertEqual(decide(self.clean(),'failure'),'INCONCLUSIVO')
    def test_partial(self):
        r=self.clean(); r['complete']=False; self.assertEqual(decide(r,'success'),'INCONCLUSIVO')
    def test_bugs(self):
        for p in ['P0','P1','P2']:
            r=self.clean(); r['findings']=[dict(priority=p,file='orders.py',line=1,scenario='x',expected='x',actual='y',impact='z',evidence='diff')]
            self.assertEqual(decide(r,'failure'),'REQUER_DESENVOLVEDOR')
    def test_invalid(self): self.assertEqual(decide({},'success'),'INCONCLUSIVO')
if __name__=='__main__': unittest.main()
