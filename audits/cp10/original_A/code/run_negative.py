from pathlib import Path
from fractions import Fraction as F
import copy,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import two_adic as A
R=Path(__file__).resolve().parents[1]
checks=[]
def ck(id,v,detail=None):checks.append({'id':id,'pass':bool(v),'detail':detail})

def main():
 c=A.bound_certificate(1,3);mutations=[]
 def mut(name,fn):
  z=copy.deepcopy(c);fn(z);mutations.append((name,z))
 mut('family',lambda z:z.update(family_id='006'))
 mut('pin',lambda z:z.update(pin='main'))
 mut('schema',lambda z:z.update(schema='OTHER'))
 mut('claim_inflation',lambda z:z.update(claim='CATALAN_IRRATIONALITY_PROVED'))
 mut('source_coefficient',lambda z:z.update(source_coefficient='505/4607'))
 mut('drop_error_term',lambda z:z.update(conditional_lower_bound=z['leading_bound']))
 mut('error_allowance',lambda z:z.update(explicit_error_allowance=0))
 mut('rounded_bound',lambda z:z.update(integer_rounded_lower_bound=-1211))
 mut('minimizer',lambda z:z.update(real_minimizer_E='27'))
 mut('missing_K_condition',lambda z:z.update(requires_v2_discrepancies_ge_minus_K=False))
 mut('cross_group_distinctness',lambda z:z.update(distinctness='ALL_INDICES_DISTINCT'))
 mut('nonintegral_filter',lambda z:z.update(filter='ARBITRARY_RATIONAL_FILTER'))
 mut('formal_claim',lambda z:z.update(formal_proof=True))
 mut('whole_theorem_claim',lambda z:z.update(full_irrationality_proved=True))
 mut('K_value',lambda z:z['parameters'].update(K=0))
 mut('N_bool',lambda z:z['parameters'].update(N=True))
 mut('missing_field',lambda z:z.pop('leading_bound'))
 mut('extra_field',lambda z:z.update(approved=True))
 for name,z in mutations:ck('bound_reject_'+name,not A.verify_bound(z,(1,3)))
 t=A.tail_cert(0,0,13,40)
 tmut=[]
 for name,key,val in [('short_cutoff','cutoff',1),('precision','precision',256),('tail_claim','tail_valuation_lower','1000'),('sum','partial_sum','0'),('index','i',1),('pin','pin','main'),('family','family_id','006')]:
  z=copy.deepcopy(t);z[key]=val;tmut.append((name,z))
 z=copy.deepcopy(t);z.pop('cutoff');tmut.append(('missing',z))
 z=copy.deepcopy(t);z['cutoff']=True;tmut.append(('bool_cutoff',z))
 for name,z in tmut:
  try:ok=not A.verify_tail(z,(0,0,13,40))
  except (ValueError,TypeError,KeyError):ok=True
  ck('tail_reject_'+name,ok)
 invalid=[lambda:A.bound_certificate(0,3),lambda:A.bound_certificate(1,-1),lambda:A.bound_certificate(True,3),lambda:A.bound_certificate(10001,3),lambda:A.bound_certificate(1,'3'),lambda:A.bound_certificate(1,2049),lambda:A.smoothing(0,0,0,24),lambda:A.smoothing(13,0,13,24),lambda:A.smoothing(0,0,13,0),lambda:A.smoothing(0,0,13,257),lambda:A.v2(float('nan')),lambda:A.v2(0.25)]
 for i,fn in enumerate(invalid):
  try:fn();ok=False
  except (ValueError,TypeError,ZeroDivisionError):ok=True
  ck(f'invalid_input_{i:02}',ok)
 expected=['a','b'];valid=[{'id':'a','pass':True},{'id':'b','pass':True}]
 ck('report_valid',A.gate(valid,expected))
 tests={'empty':[],'missing':valid[:1],'duplicate':[valid[0],valid[0]],'false':[valid[0],{'id':'b','pass':False}],'string':[valid[0],{'id':'b','pass':'True'}],'wrong_id':[valid[0],{'id':'c','pass':True}]}
 for k,v in tests.items():ck('report_reject_'+k,not A.gate(v,expected))
 proto=json.loads((R/'records/PROTOCOL.json').read_text());good=A.gate(checks,proto['negative_expected_ids'])
 out={'status':'PASS' if good else 'HOLD','check_count':len(checks),'checks':checks,'rejected_bound_mutations':len(mutations),'rejected_tail_mutations':len(tmut),'invalid_inputs':len(invalid)}
 (R/'results/NEGATIVE_CASES.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'check_count':len(checks),'failures':[c['id'] for c in checks if not c['pass']]}));return 0 if good else 1
if __name__=='__main__':sys.exit(main())
