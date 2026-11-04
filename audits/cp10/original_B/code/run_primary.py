from pathlib import Path
import json,sys,time,copy
from fractions import Fraction as F
from math import comb
import lower_bound as L
R=Path(__file__).resolve().parent.parent
P=json.loads((R/'records/PROTOCOL.json').read_text())
checks=[]
def ck(i,b,d=None):checks.append({'id':i,'pass':bool(b),'detail':d})
t0=time.perf_counter()
# Two-adic exact components: valuations and coefficients.
for start,stop in P['moment_blocks']:
    bad=[]
    for i in range(start,stop):
        m=L.moment(i)
        if i%2:
            if m!=0:bad.append(i)
        elif L.vp(m)!=i+1-(i//2).bit_count():bad.append(i)
    ck(f'moment_valuation_{start}_{stop}',not bad,{'indices':stop-start,'bad':bad})
for d in range(P['coefficient_degree_max']+1):
    T,U=L.cheb('T',d),L.cheb('U',d)
    ck(f'Chebyshev_valuation_d{d}',all(L.at_least(a,u-1) for u,a in enumerate(T)) and all(L.at_least(a,u) for u,a in enumerate(U)),{'coefficients':len(T)+len(U)})
ck('tail_all_k_supporting_integer_inequality',all((k+1)**4<=2**(k+4) for k in range(16,1025)),{'tested_k':[16,1024],'all_larger_k':'proved by monotone ratio in contract, not inferred from test'})
H=P['series_H'];K=P['series_K'];ng=P['series_grid_side']
for gs in P['hypothetical_rationals']:
    g=F(gs);cases=[L.series_case(i,j,H,K,g) for i in range(ng) for j in range(ng)]
    ck('twoadic_discrepancy_g'+gs,all(x['agrees_mod_tail'] and x['smooth_uniform_bound'] for x in cases),{'pairs':len(cases),'minimum_absolute_precision':min(x['tail_precision'] for x in cases)})
# Higher precision checks are exact inclusions, never float agreement.
for i,j in P['series_precision_pairs']:
    a,p=L.smooth(i,j,H,K);b,q=L.smooth(i,j,H,K+32)
    ck(f'series_higher_precision_{i}_{j}',L.at_least(b-a,p) and q>p,{'precision_old':p,'precision_new':q})
_,_,_,M,Z=L.arrays(130)
ck('harmonic_twoadic_grid',all(L.at_least(z,-14) for row in Z for z in row),{'pairs':130**2,'floor_log2_H':7})
for N in P['quadratic_exhaustive_N']:
    n=48*N
    vals=[(L.quadratic(N,m,l),m,l) for m in range(n+1) for l in range(n-m+1)]
    exact,m,l=min(vals);real=-F(505,2)*N*N
    ck(f'quadratic_exhaustive_N{N}',exact==real+(F(1,2) if N%2 else 0) and l==n-m,{'m':m,'l':l,'integer_min':str(exact),'real_min':str(real),'pairs':len(vals)})
    for KG in P['error_K_values']:
        bound=L.finite_uniform_bound(N,KG)
        minimal=min(L.finite_term_bound(N,m,l,KG) for m in range(n+1) for l in range(n-m+1))
        ck(f'finite_error_bound_N{N}_K{KG}',minimal>=bound,{'exact_term_min':str(minimal),'explicit_lower':str(bound)})
# Column-pool replays preserve original rows, scalar denominators and filters.
eliminations=[]
for N,p in P['elimination_cases']:
    x=L.elimination_case(N,p);eliminations.append(x)
    ck(f'columns_N{N}_p{p}',L.validate_record(x),x)
# The full piecewise loss, all breakpoints, area and exact constant comparison.
for idx,(a,b,c0,c1,area) in enumerate(L.PIECES):
    a,b,c0,c1,area=map(F,(a,b,c0,c1,area))
    points=[a+(b-a)*F(k,16) for k in range(17)]
    integral=(b-a)*(2*c0+c1*(a+b))/2
    ck(f'loss_piece_{idx}',all(L.loss_count_formula(x)==c0+c1*x==L.loss_table(x) for x in points) and integral==area,{'from':str(a),'to':str(b),'integral':str(integral),'points':17})
area=sum((F(x[4]) for x in L.PIECES),F(0));ck('odd_area',area==F(8609,2),str(area))
for N in range(1,P['integer_scale_max']+1):
    good=True;count=0
    for p in range(3,65*N+1,2):
        if p*p>4*65*N and all(p%d for d in range(2,L.isqrt(p)+1)):
            info=L.group_counts(N,p);count+=1
            good &= info['loss']==N*L.loss_table(F(p,N))
    ck(f'loss_integer_scale_N{N}',good,{'primes_checked':count})
lo,hi=L.log2_enclosure(6)
source_lower=-F(10556055541,4608000000)
computed_lower=-F(8609,4608)-F(2809,4608)*hi
ck('six_term_log2_enclosure',hi<F(693149,10**6),{'lower':str(lo),'upper':str(hi)})
ck('source_lower_constant_arithmetic',source_lower==-F(8609,4608)-F(2809,4608)*F(693149,10**6) and computed_lower>source_lower>F('-2.29084'),{'source_rational':str(source_lower),'rational_verified_lower':str(computed_lower),'decimal_display':float(computed_lower)})
cp_upper=F('-2.290939875')
ck('conditional_gap_positive',source_lower>cp_upper,{'gap_using_source_rational':str(source_lower-cp_upper),'decimal_display':float(source_lower-cp_upper),'unresolved_analytic_upper_bridge':True})
# Boundary findings: incorrect inferences are not source errors.
ck('no_cross_group_distinctness',1*1-0*0==1,{'E_u0':[1,0],'B_u0':[0,1],'determinant':1,'same_index_in_distinct_groups_allowed':True})
p=5;toy_det=F(1,p**3)
ck('leading_dependence_not_integrality',L.vp(toy_det,p)==-3 and -3 < -2,{'matrix':[['1/25','1/25'],['0','1/5']],'actual_v5':-3,'invalid_integral_second_column_prediction':-2})
bad_zero=L.series_case(0,0,H,K,F(1))
ck('homogeneous_discrepancy_not_silently_zero',bad_zero['wrong_zero_discrepancies_residual_valuation']<bad_zero['tail_precision'],bad_zero)
ck('unknown_G_not_a_finite_numeric_bound',L.finite_uniform_bound(1,10)<L.finite_uniform_bound(1,3)<-F(505,2),{'interpretation':'the leading coefficient alone is not this finite-N bound'})
# Small-prime per-entry inequality using a conservative explicit denominator bound.
for p in P['small_odd_primes']:
    h=130;lp=0;v=1
    while v*p<=h:v*=p;lp+=1
    ck(f'small_prime_array_denominator_p{p}',all(L.at_least(x,-4*lp,p) for row in M for x in row) and all(L.at_least(z,-2*lp,p) for row in Z for z in row),{'pairs_each':h*h,'floor_logp_H':lp})
# A deterministic certificate is bound to exact source and list of instances.
cs=P['certificate_cases'];cert=L.certificate(cs)
(R/'results/LOWER_BOUND_CERTIFICATE.json').write_bytes(json.dumps(cert,indent=2,ensure_ascii=False).encode()+b'\n')
ck('correct_finite_certificate',L.verify_certificate(cert,cs))
mutations=[]
def mut(name,change):
    q=copy.deepcopy(cert);change(q);mutations.append((name,q))
mut('family',lambda q:q.update(family_id='006'))
mut('commit',lambda q:q.update(commit='main'))
mut('schema',lambda q:q.update(schema='WRONG'))
mut('whole_theorem',lambda q:q.update(whole_theorem_verified=True))
mut('false_as_integer',lambda q:q.update(whole_theorem_verified=0))
mut('claim_scope',lambda q:q.update(claim='ALL_PRIMES_THEOREM_VERIFIED'))
mut('area',lambda q:q.update(odd_area='8608/2'))
mut('two_adic_coefficient',lambda q:q.update(two_adic_coefficient='504/4608'))
mut('lower_bound',lambda q:q.update(source_lower_rational='0'))
mut('omit_case',lambda q:q['cases'].pop())
mut('duplicate_case',lambda q:q['cases'].append(q['cases'][0]))
mut('reverse_cases',lambda q:q['cases'].reverse())
mut('p',lambda q:q['cases'][0].update(p=41))
mut('retained_count',lambda q:q['cases'][0].update(R=0))
mut('central_rank',lambda q:q['cases'][0].update(central_rank=99))
mut('extra_field',lambda q:q.update(extra='unbound'))
for name,q in mutations:ck('reject_certificate_'+name,not L.verify_certificate(q,cs))
(R/'results/NEGATIVE_CERTIFICATE_CASES.json').write_text(json.dumps([{'name':n,'certificate':q} for n,q in mutations],indent=2)+'\n')
invalid=[lambda:L.smooth(0,0,2,0),lambda:L.smooth(-1,0,2,64),lambda:L.smooth(0,2,2,64),lambda:L.smooth(0,0,True,64),lambda:L.smooth(0,0,2,1025),lambda:L.finite_uniform_bound(0,3),lambda:L.finite_uniform_bound(1,-1),lambda:L.finite_uniform_bound(True,3),lambda:L.group_counts(1,2),lambda:L.group_counts(1,13),lambda:L.group_counts(1,49),lambda:L.group_counts(1,67),lambda:L.residue(F(1,2),2),lambda:L.residue(1,2,0)]
for k,f in enumerate(invalid):
    rejected=False
    try:f()
    except (ValueError,TypeError):rejected=True
    ck(f'invalid_{k:02}',rejected)
base=[{'id':'a','pass':True,'detail':None},{'id':'b','pass':True,'detail':None}]
ck('report_gate_accept',L.result_gate(base,['a','b']))
variants=[[],base[:1],base+[base[0]],list(reversed(base)),[{'id':'a','pass':False,'detail':None},base[1]],[{'id':'a','pass':1,'detail':None},base[1]],[{'id':'a','pass':True},base[1]]]
for k,v in enumerate(variants):ck(f'report_gate_reject_{k}',not L.result_gate(v,['a','b']))
report={'status':'PASS' if L.result_gate(checks,P['expected_primary_ids']) else 'HOLD','check_count':len(checks),'checks':checks,'elapsed_seconds':time.perf_counter()-t0,'scope':'finite exact arithmetic diagnostics; general arguments supplied separately; no full theorem verification'}
(R/'results/PRIMARY_REPLAY.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'seconds':report['elapsed_seconds'],'failed':[x for x in checks if not x['pass']]}))
sys.exit(report['status']!='PASS')
