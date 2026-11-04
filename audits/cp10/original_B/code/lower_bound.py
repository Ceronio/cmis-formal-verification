"""CP10 bounded exact arithmetic for source family 005 lower-bound components.
No all-N proof, real approximation to G, or proof-assistant claim is made by this code.
Rationals and local residues are exact. Infinite-series enclosures carry an explicit
2-adic absolute tail precision. Inputs are purposefully bounded.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import comb, isqrt
import json
from hashlib import sha256
from inherited_digit_bridge import arrays, base_row, cheb, E_at

COMMIT='fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
FAMILY='005'

def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def digest(x):return sha256(canonical(x)).hexdigest()
def integer(x,lo,hi):
    if type(x) is not int or not lo<=x<=hi:raise ValueError('bounded integer required')
    return x

def vp(q,p=2):
    q=F(q)
    if q==0:return None # infinity, never confused with 0
    def v(n):
        n=abs(n);s=0
        while n%p==0:n//=p;s+=1
        return s
    return v(q.numerator)-v(q.denominator)
def at_least(q,b,p=2):
    v=vp(q,p);return v is None or v>=b

def residue(q,p,precision=1):
    q=F(q);integer(precision,1,256)
    if q.denominator%p==0:raise ValueError('nonintegral reduction: HOLD')
    modulus=p**precision
    return q.numerator%modulus*pow(q.denominator,-1,modulus)%modulus

def ceil_log2(n):integer(n,1,10**12);return (n-1).bit_length()

def c(d):return F(comb(d,d//2),2**d) if d>=0 and d%2==0 else F(0)
@lru_cache(maxsize=2048)
def moment(i):
    integer(i,0,2048)
    return F(2*2**i,(i+1)*comb(i,i//2)) if i%2==0 else F(0)

@lru_cache(maxsize=2048)
def smooth(i,j,H,K):
    integer(H,2,260);integer(i,0,H-1);integer(j,0,H-1);integer(K,16,1024)
    # All omitted k>=K: v2(term)>=i+floor(K/2)-2ceil(log2 H)-1.
    # The inequality (k+1)^4 <= 2^(k+4) for integers k>=16 gives this
    # conservative monotone bound for the entire infinite tail.
    q=sum((moment(i+k)/F(j+k+1) for k in range(K)),F(0))
    return q,i+K//2-2*ceil_log2(H)-1

def series_case(i,j,H,K,g):
    s,P=smooth(i,j,H,K);s0,P0=smooth(0,0,H,K);s1,P1=smooth(0,1,H,K)
    _,_,_,M,_=arrays(H)
    minus,plus=c(i-j),c(j-i-1)
    e1=4*g-s0;e2=-s1
    target=M[i][j]+4*g*minus
    residual=target-s-e1*minus-e2*plus
    precisions=[P]
    if minus:precisions.append(P0+vp(minus))
    if plus:precisions.append(P1+vp(plus))
    actual_precision=min(precisions)
    # These are exact finite enclosures, not a real-valued approximation.
    return {'i':i,'j':j,'g':str(g),'tail_precision':actual_precision,
       'residual_valuation':vp(residual),'agrees_mod_tail':at_least(residual,actual_precision),
       'smooth_uniform_bound':at_least(s,i-2*ceil_log2(H)-1),
       'wrong_zero_discrepancies_residual_valuation':vp(target-s)}

def quadratic(N,m,l):
    n,C,H,b=48*N,63*N,65*N,7*N
    return -(H-b)*m+F(3,2)*m*m+F(1,2)*l*l+C*(n-m-l)
def finite_term_bound(N,m,l,K):
    n,C,H,b=48*N,63*N,65*N,7*N
    L=H.bit_length()-1;h=ceil_log2(H)
    return F(3*m*(m-1),2)+(b-H-K)*m+F(l*(l-1),2)-(2*L+2+K)*l+(C-2*h-3)*(n-m-l)

def finite_uniform_bound(N,K):
    integer(N,1,10**6);integer(K,0,10**6)
    n=48*N;return -F(505,4608)*n*n-n*(2*ceil_log2(65*N)+K+3)

def group_counts(N,p):
    integer(N,1,10**6)
    n,H,L,A,b,q=48*N,65*N,59*N,19*N,7*N,4*N
    if not type(p) is int or p*p<=4*H or p>H or p<3 or any(p%d==0 for d in range(2,isqrt(p)+1)):
        raise ValueError('source large odd prime conditions not met')
    if 2*p<=H:
        d0=max(0,min(p,L-p,A)-max(b,H-2*p));return {'range':'paired','d0':d0,'loss':2*n-max(0,d0-q)}
    K,J=L-p,H-p
    B=max(0,min(A,K)-b)
    e=max(0,min(b,J)-max(0,K))
    R=max(K,0)+max(K-A,0)+max(J-max(b,K),0)
    R0=max(K,0)+max(J-b,0)-B
    S=B+e
    return {'range':'central','R':R,'R0':R0,'S':S,'B':B,'e':e,'K':K,'J':J,'loss':min(2*n,n+R,2*R+S)}

PIECES=[('0','25','96','0','2400'),('25','29','146','-2','368'),
('29','65/2','88','0','308'),('65/2','69/2','153','-2','172'),
('69/2','40','222','-4','803/2'),('40','58','182','-3','630'),
('58','59','124','-2','7'),('59','65','65','-1','18')]
def loss_table(x):
    x=F(x)
    if x<0:raise ValueError('negative scale')
    for a,b,c0,c1,area in PIECES:
        if F(a)<=x<=F(b):return F(c0)+F(c1)*x
    return F(0)
def loss_count_formula(x):
    x=F(x);pos=lambda a:max(F(0),a)
    if x<=F(65,2):
        d0=pos(min(x,59-x,19)-max(F(7),65-2*x))
        return 96-pos(d0-4)
    K,J=59-x,65-x
    R=pos(K)+pos(K-19)+pos(J-max(F(7),K))
    S=pos(min(F(19),K)-7)+pos(min(F(7),J)-max(F(0),K))
    return min(F(96),48+R,2*R+S)

def scaled_raw(N,p,precision=2):
    """Original rational recurrences, reduced only after p^2 multiplication.
    Explicit g=0 algebraic surrogate, not a numerical estimate of Catalan G.
    Its G-dependent term vanishes modulo p^2 for every p-integral rational g.
    """
    integer(N,1,2);group_counts(N,p)
    H,n,b,L=65*N,48*N,7*N,59*N;mod=p**precision
    _,_,_,M,Z=arrays(H)
    MM=[[residue(p*p*M[i][j],p,precision) for j in range(b,L)] for i in range(H)]
    ZZ=[[residue(F(3,2)*p*p*Z[i][j],p,precision) for j in range(b,L)] for i in range(H)]
    rows=[];prs=[]
    for r in range(n):
        P,D=base_row(N,r);prs.append((P,D))
        sp=[(i,v) for i,v in enumerate(P) if v];sd=[(i,v) for i,v in enumerate(D) if v]
        rows.append([(sum(v*MM[i][j] for i,v in sp)-sum(v*ZZ[i][j] for i,v in sd))%mod for j in range(L-b)])
    return rows,prs

def elimination_case(N,p):
    info=group_counts(N,p);S,prs=scaled_raw(N,p)
    n,H,b,L,A=48*N,65*N,7*N,59*N,19*N
    mod=p*p;columns=[[row[j-b] for row in S] for j in range(b,L)]
    if info['range']=='paired':
        ell_list=list(range(max(b,H-2*p),min(p,L-p,A)))
        ok=True
        for ell in ell_list:
            columns[p+ell-b]=[(x+y)%mod for x,y in zip(columns[p+ell-b],columns[ell-b])]
            ok=ok and all(x%p==0 for x in columns[p+ell-b])
        return {'N':N,'p':p,**info,'paired_columns':len(ell_list),'improved_columns_integral_after_p':ok,
          'count_matches':len(ell_list)==info['d0'],'finite_model':'source_rows_g0_surrogate_mod_p2'}
    K,J=info['K'],info['J'];cent=list(range(max(b,J),min(p,L)))
    E=[E_at(d,p) for d in range(p)]
    Vs={}
    for ell in range(max(0,J)):
        V=[]
        for P,D in prs:
            cp=sum(P[i]*E[2*p+ell-1-i] for i in range(H) if 0<=2*p+ell-1-i<p)%p
            cd=D[p+ell]%p if p+ell<H else 0
            V.append((2*cp-F(3,2).numerator*pow(2,-1,p)*cd)%p)
        Vs[ell]=V
    central_ok=True
    for j in cent:
        col=columns[j-b]
        central_ok &= all(x%p==0 for x in col)
        actual=[(x//p)%p for x in col]
        want=[-sum(Vs[ell][r]*pow(j-ell,-1,p) for ell in range(J))%p for r in range(n)]
        central_ok &= actual==want
    paired=list(range(b,min(A,K))) if min(A,K)>b else []
    for ell in paired:columns[p+ell-b]=[(x+y)%mod for x,y in zip(columns[p+ell-b],columns[ell-b])]
    retained=[j for j in range(b,L) if (j>=p or j<J) and j not in [p+e for e in paired]]
    exceptional=list(range(max(0,K),min(b,J))) if min(b,J)>max(0,K) else []
    representatives={}
    for ell in range(J):
        if ell in exceptional:continue
        if b<=ell<J:representatives[ell]=(ell,1)
        else:representatives[ell]=(p+ell,-1)
    represented_ok=all(j in retained and [x%p for x in columns[j-b]]==[(sign*v)%p for v in Vs[ell]] for ell,(j,sign) in representatives.items())
    for j in cent:
        out=columns[j-b][:]
        for ell,(k,sign) in representatives.items():
            coeff=p*sign*pow(j-ell,-1,p)
            out=[(x+coeff*y)%mod for x,y in zip(out,columns[k-b])]
        columns[j-b]=out
    residual_ok=True
    for j in cent:
        col=columns[j-b]
        residual_ok &= all(x%p==0 for x in col)
        residual_ok &= [(x//p)%p for x in col]==[-sum(Vs[e][r]*pow(j-e,-1,p) for e in exceptional)%p for r in range(n)]
    # Elementary column operations over Z/p^2: a lifted unit is invertible.
    cc=[columns[j-b][:] for j in cent];rank=0
    for row in range(n):
        hit=next((k for k in range(rank,len(cc)) if (cc[k][row]//p)%p),None)
        if hit is None:continue
        cc[rank],cc[hit]=cc[hit],cc[rank]
        inv=pow((cc[rank][row]//p)%p,-1,p)
        cc[rank]=[(x*inv)%mod for x in cc[rank]]
        for k in range(rank+1,len(cc)):
            a=(cc[k][row]//p)%p
            if a:cc[k]=[(x-a*y)%mod for x,y in zip(cc[k],cc[rank])]
        rank+=1
        if rank==len(cc):break
    zeros=all(all(x==0 for x in col) for col in cc[rank:])
    return {'N':N,'p':p,**info,'central_columns':len(cent),'central_identity':bool(central_ok),
      'retained_actual':len(retained),'pair_sums':len(paired),'exceptional_actual':len(exceptional),
      'representatives_correct':represented_ok,'residual_identity':bool(residual_ok),
      'central_rank':rank,'central_rank_le_exceptional':rank<=info['e'],
      'remaining_central_columns_integral':zeros,'pair_sums_at_most_p_denominator':all(all(x%p==0 for x in columns[p+e-b]) for e in paired),
      'counts_match':len(retained)==info['R']==info['R0'] and len(paired)==info['B'] and len(exceptional)==info['e'],
      'finite_model':'source_rows_g0_surrogate_mod_p2'}

def log2_enclosure(terms=6):
    integer(terms,1,100)
    lo=2*sum((F(1,(2*j+1)*3**(2*j+1)) for j in range(terms)),F(0))
    rem=F(2,3**(2*terms+1)*(2*terms+1))*F(9,8)
    return lo,lo+rem

def certificate(cases):
    return {'schema':'CMIS_F005_LOWER_FINITE_V1','family_id':FAMILY,'commit':COMMIT,
      'claim':'LISTED_COLUMN_ELIMINATIONS_AND_CONSTANT_ARITHMETIC_ONLY',
      'cases':[elimination_case(*case) for case in cases],
      'odd_area':str(sum(((F(b)-F(a))*(2*F(c0)+F(c1)*(F(a)+F(b)))/2 for a,b,c0,c1,area in PIECES),F(0))),
      'two_adic_coefficient':'505/4608','source_lower_rational':'-10556055541/4608000000',
      'whole_theorem_verified':False}

def validate_record(r):
    names=['central_identity','representatives_correct','residual_identity','central_rank_le_exceptional','remaining_central_columns_integral','pair_sums_at_most_p_denominator','counts_match'] if r['range']=='central' else ['improved_columns_integral_after_p','count_matches']
    return all(type(r[k]) is bool and r[k] for k in names)

def verify_certificate(obj,cases):
    try:
        want=certificate(cases)
        # Canonical equality also separates true/1, 0/0.0 and false/0.
        return type(obj) is dict and canonical(obj)==canonical(want) and all(validate_record(r) for r in want['cases'])
    except (ValueError,TypeError,KeyError,ZeroDivisionError):return False

def result_gate(records,ids):
    return type(records) is list and len(records)==len(ids) and all(type(r) is dict and set(r)=={'id','pass','detail'} and r['id']==i and type(r['pass']) is bool and r['pass'] for r,i in zip(records,ids))
