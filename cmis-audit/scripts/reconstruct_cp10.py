"""Bounded exact algebra checks, not the analytic/PNT proof of CP10."""
from fractions import Fraction as F
from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[1]
pieces=[(F(0),F(25),96,0),(F(25),F(29),146,-2),(F(29),F(65,2),88,0),(F(65,2),F(69,2),153,-2),(F(69,2),F(40),222,-4),(F(40),F(58),182,-3),(F(58),F(59),124,-2),(F(59),F(65),65,-1)]
integrals=[]
for k,(a,b,c,d) in enumerate(pieces):
 area=c*(b-a)+F(d,2)*(b*b-a*a);integrals.append(str(area))
 if k:assert pieces[k-1][2]+pieces[k-1][3]*a==c+d*a
assert sum((F(s) for s in integrals),F(0))==F(8609,2)
def pos(x):return max(x,0)
count=0
for a,b,c,d in pieces:
 for q in range(101):
  x=a+(b-a)*F(q,100)
  if x<=F(65,2):
   d0=pos(min(x,59-x,19)-max(7,65-2*x));loss=96-pos(d0-4)
  else:
   K=59-x;J=65-x
   R=pos(K)+pos(K-19)+pos(J-max(7,K))
   S=pos(min(19,K)-7)+pos(min(7,J)-max(0,K))
   loss=min(96,48+R,2*R+S)
  assert loss==c+d*x;count+=1
x=F(1,3);n=20
lo=2*sum((x**(2*k+1)/(2*k+1) for k in range(n)),F(0))
hi=lo+2*x**(2*n+1)/((2*n+1)*(1-x*x))
lower=-F(8609,4608)-F(2809,4608)*hi
upper=-F(8609,4608)-F(2809,4608)*lo
assert lower>F(-229084,100000)
delta=F(5,24);assert delta/2+delta*delta/8==F(505,4608)
matrix=[[F(1,25),F(1,25)],[F(0),F(1,5)]];det=matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0];assert det==F(1,125)
result={'scope':'source loss-profile arithmetic and finite counterexample to invalid denominator shortcut','loss_piece_integrals':integrals,'total_area':'8609/2','loss_profile_comparisons':count,'two_adic_coefficient':'505/4608','conditional_lower_constant_enclosure':[str(lower),str(upper)],'conditional_lower_constant_approx':[float(lower),float(upper)],'greater_than_minus_2_29084':True,'invalid_leading_residue_shortcut_counterexample':{'prime':5,'matrix':[[str(x) for x in r] for r in matrix],'determinant':str(det),'determinant_valuation':-3},'pnt_or_analytic_limit_reproved':False,'full_finite_place_proof_certified':False}
(BASE/'results/CP10_FRESH_ALGEBRA.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
