"""Separate symbolic/exact finite comparisons, same assistant-led exercise."""
from pathlib import Path
from fractions import Fraction as F
from time import perf_counter
import json,sys
import sympy as sp
sys.path.insert(0,str(Path(__file__).resolve().parent))
import two_adic as A
R=Path(__file__).resolve().parents[1]
start=perf_counter();checks=[]
def ck(id,v,detail=None):checks.append({'id':id,'pass':bool(v),'detail':detail})
x=sp.Symbol('x')
for kind in ('T','U'):
 for d in range(65):
  expected=sp.Poly((sp.chebyshevt if kind=='T' else sp.chebyshevu)(d,x),x,domain=sp.ZZ)
  vals=[int(expected.nth(i)) for i in range(d+1)]
  ck(f'symbolic_{kind}_{d}',vals==list(A.cheb(kind,d)))
# Independent factorial-floor count for central binomial valuations.
def factorial_v2(n):
 out=0
 while n:n//=2;out+=n
 return out
for u in range(0,513,2):
 v=factorial_v2(u)-2*factorial_v2(u//2)
 ck(f'factorial_floor_{u}',v==A.v2(__import__('math').comb(u,u//2)) and A.v2(A.moment(u))==1+u-v)
N,m,l,K,J,L=sp.symbols('N m l K J L',real=True)
n=48*N;b=7*N;C=63*N;H=65*N
q=-(H-b)*m+sp.Rational(3,2)*m*m+sp.Rational(1,2)*l*l+C*(n-m-l)
qedge=q.subs(l,n-m)
ck('symbolic_square_completion',sp.expand(qedge-(2*(m-sp.Rational(53,2)*N)**2-sp.Rational(505,2)*N*N))==0)
ck('symbolic_delta_coefficient',sp.Rational(5,24)/2+sp.Rational(5,24)**2/8==sp.Rational(505,4608))
ck('symbolic_l_derivative',sp.diff(q,l)==l-C)
term=-(H-b)*m+sp.Rational(3,2)*m*(m-1)-K*m+sp.Rational(1,2)*l*(l-1)-(2*L+2+K)*l+(C-2*J-3)*(n-m-l)
residue=(2*J+sp.Rational(3,2))*m+(2*(J-L)+sp.Rational(1,2))*l+K*(n-m-l)
ck('symbolic_finite_error_allowance',sp.expand(term-(q-n*(K+2*J+3))-residue)==0)
# Known 2-adic residue arithmetic is not real convergence.
partial=sum(F(2**k) for k in range(40))
ck('geometric_2adic_not_real_sum',A.congruent(partial,-1,40) and partial>0,{'terms':40,'two_adic_error_v2':A.v2(partial+1),'real_partial_sum':str(partial)})
protocol=json.loads((R/'records/COMPARISON_PROTOCOL.json').read_text());passed=A.gate(checks,protocol['expected_ids'])
out={'status':'PASS' if passed else 'HOLD','check_count':len(checks),'checks':checks,'seconds':perf_counter()-start,'versions':{'python':sys.version.split()[0],'sympy':sp.__version__},'scope':'Same input transcription and assistant authorship. Separate formula implementation, not outside audit or kernel proof.'}
(R/'results/COMPARISON.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'check_count':len(checks),'seconds':out['seconds']}));sys.exit(not passed)
