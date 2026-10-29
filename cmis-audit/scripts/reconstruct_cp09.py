"""Fresh reconstruction from pinned nonvanishing.tex. Standard library only.
No full growing-prime determinant or universal digit-layer claim is tested here.
"""
from fractions import Fraction as Q
from math import factorial,comb
from pathlib import Path
import json,hashlib,re
BASE=Path(__file__).resolve().parents[1];OUT=BASE/'results';OUT.mkdir(exist_ok=True)
m=[Q(0)]*65
for i in range(0,65,2):m[i]=Q(2*4**(i//2)*factorial(i//2)**2,factorial(i+1))
for i in range(2,65,2):assert m[i]==Q(i,i+1)*m[i-2]
minus=[Q(0)]*65;plus=[Q(0)]*59;minus[1]=2
for i in range(2,65):minus[i]=((i-1)*minus[i-2]+m[i-2]+m[i-1])/i
for j in range(2,59):plus[j]=((j-2)*plus[j-2]+Q(2,j-1))/(j-1)
Y=[];J=[]
harm=lambda n,d:sum((Q(1,k**d) for k in range(1,n+1)),Q(0))
for i in range(65):
 yr=[];jr=[]
 for j in range(59):
  q=min(i,j);boundary=minus[i-j] if i>=j else plus[j-i]
  yr.append(boundary-sum((m[i-k-1]/(j-k) for k in range(q)),Q(0)))
  jr.append(-Q(3,2)*harm(i,2) if i==j else Q(3,2)*(harm(i,1)-harm(j,1))/(i-j))
 Y.append(yr);J.append(jr)
for i in range(1,65):
 for j in range(1,59):assert Y[i][j]==Y[i-1][j-1]-m[i-1]/j
for v in [v for a in (Y,J) for row in a for v in row]:
 d=v.denominator
 for prime in (2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61):
  while d%prime==0:d//=prime
 assert d==1
E=[[0]*65 for _ in range(45)];I=[[0]*65 for _ in range(45)]
E[0][62]=1;E[1][61]=1;I[1][62]=1
for a in (E,I):
 for n in range(2,45):
  assert a[n-1][0]==0
  a[n]=[2*x-y for x,y in zip(a[n-1][1:]+[0],a[n-2])]
def factor(a):
 return [a[k]-(2*a[k-1] if k>=1 else 0)+(a[k-2] if k>=2 else 0) for k in range(65)]
B=[]
for r in range(49):
 u=abs(r-4);sgn=(r>4)-(r<4);P=factor(E[u]);D=[sgn*x for x in factor(I[u])]
 raw=[sum((P[i]*Y[i][j]-D[i]*J[i][j] for i in range(65)),Q(0)) for j in range(7,59)]
 B.append([sum(((-1)**h*comb(4,h)*raw[k+h] for h in range(5)),Q(0)) for k in range(48)])
assert min(i for i,x in enumerate(factor(E[44])) if x)==18
def eliminate(A,p):
 a=[[int(x.numerator)*pow(x.denominator,-1,p)%p for x in row] for row in A]
 pivots=[];swaps=[];det=1
 for i in range(len(a)):
  r=next((r for r in range(i,len(a)) if a[r][i]),None)
  if r is None:return {'det':0,'pivots':pivots,'swaps':swaps}
  if r!=i:a[i],a[r]=a[r],a[i];swaps.append([i,r]);det=-det
  pivot=a[i][i];pivots.append(pivot);det=det*pivot%p
  for r in range(i+1,len(a)):
   c=a[r][i]*pow(pivot,-1,p)%p
   if c:
    for j in range(i,len(a)):a[r][j]=(a[r][j]-c*a[i][j])%p
 return {'det':det,'pivots':pivots,'swaps':swaps}
src=(BASE/'evidence/pinned_sources/authenticated/nonvanishing.tex').read_text()
table=src.split('\\begin{tabular}{cl}')[1].split('\\bottomrule')[0]
expected={};current=None
for line in table.splitlines():
 match=re.search(r'\$(-?\d+)\$ &',line)
 if match:current=int(match[1]);expected[current]=[]
 if current is not None and '& $' in line:
  nums=re.search(r'& \$([0-9,]+)\$',line)
  if nums:expected[current]+=[int(s) for s in nums[1].split(',')]
digit_tests=[]
def modq(x,p):return x.numerator*pow(x.denominator,-1,p)%p
for p in (17,19,23,29,31,37,41,43,47,53,59,61,67):
 assert p*p>4*65
 checks=0;negative=[];boundary_count=0
 for i in range(65):
  for j in range(59):
   ell=j%p;d=(j-i-1)%p;ip=(i+1+d-ell)//p-1;jp=j//p
   ed=0 if d%2 else (-1)**(d//2)*comb((p-1)//2,d//2)%p
   reduced=plus[jp+1] if ip==-1 else Y[ip][jp]
   left=modq(p*p*Y[i][j],p);right=ed*modq(reduced,p)%p
   assert left==right,(p,i,j,'Y',left,right)
   zl=modq(p*p*Q(2,3)*J[i][j],p)
   zr=modq(Q(2,3)*J[i//p][jp],p) if i%p==ell else 0
   assert zl==zr,(p,i,j,'Z',zl,zr)
   checks+=2;boundary_count+=(ip==-1)
   wrong=ed*modq(Y[i//p][jp],p)%p
   if wrong!=left and not negative:negative.append({'i':i,'j':j,'correct_i_prime':ip,'wrong_i_prime':i//p,'correct_residue':left,'wrong_residue':wrong})
 digit_tests.append({'prime':p,'moment_and_harmonic_congruences_checked':checks,'negative_index_boundary_cases':boundary_count,'incorrect_carry_control':negative})
results=[]
for p in (101,263,269,271):
 for sigma in (0,1,-1):
  A=[[B[i][j]+sigma*B[i+1][j] for j in range(48)] for i in range(48)];r=eliminate(A,p)
  if p==101:assert r['pivots']==expected[sigma]
  results.append({'prime':p,'sigma':sigma,**r})
matrix=json.dumps([[str(x) for x in row] for row in B],separators=(',',':'))
(OUT/'CP09_EXACT_49x48_MATRIX.json').write_text(matrix)
result={'scope':'fresh exact rational fixed-matrix reconstruction, bounded digit congruences and modular certificates','dimensions':[49,48],'source_pivots_matched':144,'moment_entries':3835,'harmonic_entries':3835,'denominator_support_verified_up_to':65,'matrix_sha256':hashlib.sha256(matrix.encode()).hexdigest(),'modular_eliminations':results,'bounded_digit_congruences':digit_tests,'full_growing_matrix_built':False,'digit_layer_universal_theorem_verified':False,'checkpoint_certified':False}
(OUT/'CP09_FRESH_RECONSTRUCTION.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='modular_eliminations'},indent=2));print('DETERMINANTS',[(x['prime'],x['sigma'],x['det']) for x in results])
