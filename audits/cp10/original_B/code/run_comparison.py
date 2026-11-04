"""Separate SymPy formulation and counting checks; same exercise/source inputs.
Not external peer review, unseen data or proof-assistant verification.
"""
from pathlib import Path
from fractions import Fraction as F
import json,time
import sympy as s
import lower_bound as L
R=Path(__file__).resolve().parent.parent
P=json.loads((R/'records/COMPARISON_PROTOCOL.json').read_text())
checks=[]
def ck(i,b,d=None):checks.append({'id':i,'pass':bool(b),'detail':d})
x=s.symbols('x');t0=time.perf_counter()
for degree in range(49):
    good=True
    for kind,fun in [('T',s.chebyshevt),('U',s.chebyshevu)]:
        poly=s.Poly(fun(degree,x),x,domain=s.ZZ)
        coeff=[int(poly.nth(j)) for j in range(degree+1)]
        good &= coeff==L.cheb(kind,degree)
    ck(f'sympy_chebyshev_{degree}',good)
n,m,delta=s.symbols('n m delta')
expr=-n*(1+delta)*m+s.Rational(3,2)*m*m+s.Rational(1,2)*(n-m)**2
square=2*(m-(2+delta)*n/4)**2-(delta/2+delta**2/8)*n*n
ck('symbolic_square_completion',s.expand(expr-square)==0)
ck('symbolic_twoadic_coefficient',s.Rational(5,24)/2+s.Rational(5,24)**2/8==s.Rational(505,4608))
areas=[]
for i,(a,b,c0,c1,area) in enumerate(L.PIECES):
    integral=s.integrate(s.Rational(c0)+s.Rational(c1)*x,(x,s.Rational(a),s.Rational(b)))
    areas.append(integral);ck(f'symbolic_loss_area_{i}',integral==s.Rational(area))
ck('symbolic_total_area',sum(areas)==s.Rational(8609,2))
lg=sum(s.Rational(2,(2*j+1)*3**(2*j+1)) for j in range(6))
tail=s.Rational(2,13*3**13)*s.Rational(9,8)
ck('symbolic_log2_enclosure',F(lg)==L.log2_enclosure()[0] and F(lg+tail)==L.log2_enclosure()[1])
ck('symbolic_source_constant',-s.Rational(8609,4608)-s.Rational(2809,4608)*s.Rational(693149,10**6)==-s.Rational(10556055541,4608000000))
for N in range(1,5):
    n,b,A,H,LE=48*N,7*N,19*N,65*N,59*N
    rows=[]
    for p in list(s.primerange(H//2+1,H+1)):
        p=int(p);info=L.group_counts(N,p);K,J=LE-p,H-p
        physical=set(range(b,LE));high={j for j in physical if j>=p};low={j for j in physical if j<J}
        pairs={ell for ell in range(p) if b<=ell<A and ell+p<LE}
        retained=(high|low)-{p+ell for ell in pairs}
        missing={ell for ell in range(J) if ell not in low and p+ell not in high}
        rows.append(len(retained)==info['R'] and len(pairs)==info['B'] and len(missing)==info['e'])
    ck(f'independent_population_counts_N{N}',all(rows),{'prime_cases':len(rows)})
report={'status':'PASS' if L.result_gate(checks,P['expected_ids']) else 'HOLD','check_count':len(checks),'checks':checks,'elapsed_seconds':time.perf_counter()-t0,'sympy_version':s.__version__,'scope':'alternate library construction; shares transcribed inputs and assistant authorship'}
(R/'results/SYMBOLIC_COMPARISON.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[c for c in checks if not c['pass']]}))
raise SystemExit(report['status']!='PASS')
