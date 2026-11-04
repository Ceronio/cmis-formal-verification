"""Exact finite support for the reviewed, conditional two-adic subclaim.

No floating arithmetic, no assertion that a p-adic sum equals a real sum,
no full-irrationality or proof-assistant claim. Inputs are bounded for replay.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import comb
from hashlib import sha256
import json

FAMILY='005'
PIN='fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
CLAIM='CONDITIONAL_TWO_ADIC_LOWER_BOUND_WITH_SUPPLIED_DISCREPANCY_BUDGET'

def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(obj):return sha256(canonical(obj)).hexdigest()
def integer(x,lo=0,hi=10000):
    if type(x) is not int or not lo<=x<=hi:raise ValueError('integer input outside declared domain')
    return x

def rational(x):
    if type(x) not in (int,str,F):raise ValueError('exact integer, fraction string or Fraction required')
    if type(x) is str and (len(x)>4096 or any(t in x.lower() for t in ('.','e','nan','inf'))):raise ValueError('fraction string required')
    return F(x)

def v2(q):
    q=rational(q)
    if not q:return None  # +infinity, not a finite number
    def count(z):
        z=abs(z);return (z&-z).bit_length()-1
    return count(q.numerator)-count(q.denominator)

def at_least(q,bound):
    a=v2(q);return a is None or a>=bound

def congruent(a,b,precision):return at_least(F(a)-F(b),precision)
def ceil_log2(n):integer(n,1,1000000);return (n-1).bit_length()
def floor_log2(n):integer(n,1,1000000);return n.bit_length()-1

def rational_residue(q,absolute_precision):
    q=rational(q);integer(absolute_precision,1,2048)
    val=v2(q)
    if val is None or val>=absolute_precision:
        return {'known_valuation':None,'zero_modulo_precision':True,'absolute_precision':absolute_precision,'exact_zero_not_asserted':True}
    scale=F(2**val) if val>=0 else F(1,2**(-val))
    unit=q/scale;mod=2**(absolute_precision-val)
    r=unit.numerator*pow(unit.denominator,-1,mod)%mod
    return {'known_valuation':val,'unit_residue':str(r),'absolute_precision':absolute_precision,'zero_modulo_precision':False}

@lru_cache(None)
def central(twice):
    if twice<0 or twice%2:return F(0)
    return F(comb(twice,twice//2),2**twice)

@lru_cache(None)
def moment(i):
    integer(i,0,4096)
    if i%2:return F(0)
    if not i:return F(2)
    return F(i,i+1)*moment(i-2)

@lru_cache(None)
def km(i):
    integer(i,0,1024)
    if i==0:return F(0)
    if i==1:return F(2)
    return ((i-1)*km(i-2)+moment(i-2)+moment(i-1))/i

@lru_cache(None)
def kp(j):
    integer(j,0,1024)
    if j<2:return F(0)
    return ((j-2)*kp(j-2)+F(2,j-1))/(j-1)

@lru_cache(None)
def m0(i,j):
    integer(i,0,192);integer(j,0,192)
    if i>=j:return km(i-j)-sum((moment(i-j+k-1)/k for k in range(1,j+1)),F(0))
    d=j-i
    return kp(d)-sum((moment(k-d-1)/k for k in range(d+1,j+1)),F(0))

@lru_cache(None)
def harmonic(i,d):return sum((F(1,k**d) for k in range(1,i+1)),F(0))
@lru_cache(None)
def z0(i,j):
    integer(i,0,192);integer(j,0,192)
    return -harmonic(i,2) if i==j else (harmonic(i,1)-harmonic(j,1))/(i-j)

@lru_cache(None)
def cheb(kind,d):
    if kind not in ('T','U'):raise ValueError('kind')
    integer(d,0,192)
    a=(1,);b=(0,1 if kind=='T' else 2)
    if d==0:return a
    for _ in range(2,d+1):
        c=[0]+[2*x for x in b]
        for j,x in enumerate(a):c[j]-=x
        a,b=b,tuple(c)
    return b

def convolution(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b):
                if y:out[i+j]+=x*y
    return out

def rows(N,r):
    integer(N,1,3);integer(r,0,48*N-1)
    C=63*N;d=abs(r-4*N);P=[0]*C;D=[0]*C
    for u,c in enumerate(cheb('T',d)):P[C-1-u]=c
    if d:
        for u,c in enumerate(cheb('U',d-1)):D[C-1-u]=((r>4*N)-(r<4*N))*c
    f=[(-1)**j*comb(2*N,j) for j in range(2*N+1)]
    return convolution(P,f),convolution(D,f)


def cutoff(i,j,H,precision):
    integer(H,1,512);integer(i,0,H-1);integer(j,0,H-1);integer(precision,1,256)
    # For every k>=32, 2ceil(log2(k+1)) <= k/2. The contract proves it.
    return max(32,2*(precision-i-1+2*ceil_log2(H)))

@lru_cache(None)
def smoothing(i,j,H,precision):
    T=cutoff(i,j,H,precision)
    partial=sum((moment(i+k)/F(j+k+1) for k in range(T)),F(0))
    return partial,T

def tail_cert(i,j,H,precision):
    S,T=smoothing(i,j,H,precision)
    return {'family_id':FAMILY,'pin':PIN,'claim':'TWO_ADIC_PARTIAL_SUM_WITH_PROVED_TAIL_VALUATION',
      'i':i,'j':j,'H':H,'precision':precision,'cutoff':T,'partial_sum':str(S),
      'tail_valuation_lower':str(F(i+1-2*ceil_log2(H))+F(T,2))}

def verify_tail(c,request):
    expected=tail_cert(*request)
    return type(c) is dict and c==expected and all(type(c[k]) is int for k in ('i','j','H','precision','cutoff')) and F(c['tail_valuation_lower'])>=c['precision']


def parameters(N,K):
    integer(N,1,10000);integer(K,0,2048)
    return {'N':N,'K':K,'n':48*N,'b':7*N,'C':63*N,'H':65*N,'delta':'5/24','J':ceil_log2(65*N),'L':floor_log2(65*N)}

def bound_certificate(N,K):
    p=parameters(N,K);n=p['n'];J=p['J']
    leading=-F(505,4608)*n*n;allowance=n*(K+2*J+3);bound=leading-allowance
    return {'schema':'CMIS_F005_TWO_ADIC_BOUND_V1','family_id':FAMILY,'pin':PIN,'claim':CLAIM,
       'parameters':p,'source_coefficient':'505/4608','real_minimizer_E':str(F(53*N,2)),
       'real_minimizer_B':str(F(43*N,2)),'leading_bound':str(leading),'explicit_error_allowance':allowance,
       'conditional_lower_bound':str(bound),'integer_rounded_lower_bound':-((-bound.numerator)//bound.denominator),
       'requires_v2_discrepancies_ge_minus_K':True,'distinctness':'WITHIN_E_AND_WITHIN_B_NOT_ACROSS_GROUPS',
       'filter':'SOURCE_INTEGER_FILTER','formal_proof':False,'full_irrationality_proved':False}

def verify_bound(c,request):
    try:
        if type(c) is not dict:return False
        expected=bound_certificate(*request)
        if set(c)!=set(expected) or type(c.get('parameters')) is not dict or set(c['parameters'])!=set(expected['parameters']):return False
        for k in ('N','K','n','b','C','H','J','L'):
            if type(c['parameters'][k]) is not int:return False
        for k in ('requires_v2_discrepancies_ge_minus_K','formal_proof','full_irrationality_proved'):
            if type(c[k]) is not bool:return False
        if type(c['explicit_error_allowance']) is not int or type(c['integer_rounded_lower_bound']) is not int:return False
        return c==expected
    except (ValueError,TypeError,KeyError,ZeroDivisionError):return False


def twice_Q(N,m,l):
    n,b,C,H=48*N,7*N,63*N,65*N
    return -2*(H-b)*m+3*m*m+l*l+2*C*(n-m-l)

def twice_term_bound(N,K,m,l):
    p=parameters(N,K);n,b,C,H,J,L=[p[k] for k in ('n','b','C','H','J','L')]
    return (-2*(H-b)*m+3*m*(m-1)-2*K*m +l*(l-1)-2*(2*L+2+K)*l
            +2*(C-2*J-3)*(n-m-l))

def gate(records,expected):
    return type(records) is list and len(expected)>0 and len(records)==len(expected) and [r.get('id') for r in records]==expected and len(set(expected))==len(expected) and all(type(r.get('pass')) is bool and r['pass'] for r in records)
