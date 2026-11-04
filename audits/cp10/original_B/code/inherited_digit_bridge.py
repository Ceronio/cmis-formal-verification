"""CP09 exact finite tests for the stated digit-layer identities; not a proof assistant.

All finite checks retain p^2>4H, 0<=i,j<H and the exceptional i'=-1 convention.
The primary small-case construction uses original rational recurrences, not
predicted digit residues. Integer types are strict: booleans/floats are rejected.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import comb, isqrt
from hashlib import sha256
import json

FAMILY='005'
COMMIT='fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'

def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(o):return sha256(canonical(o)).hexdigest()
def isprime(p):return type(p) is int and p>=2 and all(p%d for d in range(2,isqrt(p)+1))
def mod(q,p):
    q=F(q)
    if q.denominator%p==0:raise ValueError('nonintegral rational cannot be reduced')
    return q.numerator%p*pow(q.denominator,-1,p)%p

def validate_domain(p,H,i=None,j=None):
    if not isprime(p) or p==2:raise ValueError('odd prime required')
    if type(H) is not int or not 1<=H<=20000 or p>H or not p*p>4*H:raise ValueError('requires bounded H with p^2>4H')
    if i is not None and (type(i) is not int or not 0<=i<H):raise ValueError('i outside stated range')
    if j is not None and (type(j) is not int or not 0<=j<H):raise ValueError('j outside stated range')

def E_at(d,p):
    if d<0 or d>=p or d%2:return 0
    return (-1)**(d//2)*comb((p-1)//2,d//2)%p

def reduced_indices(i,j,p):
    ell=j%p;d=(j-i-1)%p
    return ell,d,(i+1+d-ell)//p-1,j//p

@lru_cache(maxsize=32)
def arrays(H):
    if type(H) is not int or not 2<=H<=512:raise ValueError('bounded rational array limit')
    m=[F(0)]*(H+1);km=[F(0)]*(H+1);kp=[F(0)]*(H+1)
    m[0]=F(2);km[1]=F(2)
    for i in range(2,H+1,2):m[i]=i*m[i-2]/(i+1)
    for d in range(2,H+1):
        km[d]=((d-1)*km[d-2]+m[d-2]+m[d-1])/d
        kp[d]=((d-2)*kp[d-2]+F(2,d-1))/(d-1)
    M=[[F(0)]*H for _ in range(H)]
    for i in range(H):M[i][0]=km[i]
    for j in range(H):M[0][j]=kp[j]
    for i in range(1,H):
        for j in range(1,H):M[i][j]=M[i-1][j-1]-m[i-1]/j
    h1=[F(0)];h2=[F(0)]
    for i in range(1,H+1):h1.append(h1[-1]+F(1,i));h2.append(h2[-1]+F(1,i*i))
    Z=[[(-h2[i] if i==j else (h1[i]-h1[j])/(i-j)) for j in range(H)] for i in range(H)]
    return m,km,kp,M,Z

def moment(M,kp,i,j):
    if i==-1:return kp[j+1]
    if i<0 or j<0:raise ValueError('unsupported reduced index')
    return M[i][j]

def digit_case(p,H,i,j):
    validate_domain(p,H,i,j)
    if H>512:raise ValueError('use guarded p-adic comparator for large domain')
    _,_,kp,M,Z=arrays(max(2,H))
    ell,d,I,J=reduced_indices(i,j,p)
    return {'p':p,'H':H,'i':i,'j':j,'ell':ell,'d':d,'reduced_i':I,'reduced_j':J,
       'M_left':mod(p*p*M[i][j],p),'M_right':E_at(d,p)*mod(moment(M,kp,I,J),p)%p,
       'Z_left':mod(p*p*Z[i][j],p),'Z_right':(mod(Z[i//p][J],p) if i%p==j%p else 0)}

def certificate(cases):
    return {'schema':'CMIS_F005_DIGIT_V1','family_id':FAMILY,'commit':COMMIT,
        'claim':'LISTED_DIGIT_INSTANCES_ONLY','cases':[digit_case(*x) for x in cases]}

def verify_certificate(cert,expected_cases):
    try:
        if type(cert) is not dict or set(cert)!={'schema','family_id','commit','claim','cases'}:return False
        if (cert['schema'],cert['family_id'],cert['commit'],cert['claim'])!=('CMIS_F005_DIGIT_V1',FAMILY,COMMIT,'LISTED_DIGIT_INSTANCES_ONLY'):return False
        if type(cert['cases']) is not list or len(cert['cases'])!=len(expected_cases):return False
        for got,case in zip(cert['cases'],expected_cases):
            if type(got) is not dict or any(type(x) is not int for x in got.values()):return False
            want=digit_case(*case)
            if got!=want or want['M_left']!=want['M_right'] or want['Z_left']!=want['Z_right']:return False
        return True
    except (TypeError,ValueError,KeyError,ZeroDivisionError):return False

# Integer polynomial arithmetic. Ascending coefficient order; exact or mod p.
def mul(a,b,p=None):
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b):
                if y:c[i+j]+=x*y
    return [x%p for x in c] if p else c

def cheb(kind,n):
    if n<0:return [0]
    a=[1];b=[0,1 if kind=='T' else 2]
    if n==0:return a
    for _ in range(2,n+1):
        c=[0]+[2*x for x in b]
        for i,x in enumerate(a):c[i]-=x
        a,b=b,c
    return b

def base_row(N,r):
    if type(N) is not int or not 1<=N<=3 or type(r) is not int or not 0<=r<=48*N:raise ValueError('bounded row domain')
    C=63*N;g=4*N;d=abs(r-g);P=[0]*C;D=[0]*C
    for k,v in enumerate(cheb('T',d)):P[C-1-k]=v
    if d:
        for k,v in enumerate(cheb('U',d-1)):D[C-1-k]=((r>g)-(r<g))*v
    a=[(-1)**k*comb(2*N,k) for k in range(2*N+1)]
    return mul(P,a),mul(D,a)

def raw_layer_case(p,N,r,j,shift=1,include_boundary=True):
    H=65*N;validate_domain(p,H,0,j)
    P,D=base_row(N,r);_,_,kp,M,Z=arrays(H)
    G=F(7,13) # Explicit hypothetical rational value, not an estimate of G.
    if G.denominator%p==0:raise ValueError('excluded denominator prime')
    C=lambda k:F(comb(k,k//2),2**k) if k>=0 and k%2==0 else F(0)
    raw=sum((F(P[i])*(M[i][j]+4*G*C(i-j))-F(3,2)*D[i]*Z[i][j] for i in range(H)),F(0))
    actual=mod(p*p*raw,p)
    E=[E_at(d,p) for d in range(p)]
    tPE=mul([0]+[a%p for a in P],E,p)
    ell=j%p;k=j//p;rhs=F(0);terms=[]
    for u in range(-1,H//p+2):
        idx=(u+shift)*p+ell
        cp=tPE[idx] if 0<=idx<len(tPE) else 0
        cd=D[u*p+ell]%p if u>=0 and u*p+ell<len(D) else 0
        mp=moment(M,kp,u,k) if u>=0 or include_boundary else F(0)
        term=cp*mp-(F(3,2)*cd*Z[u][k] if u>=0 else 0)
        rhs+=term
        if cp or cd:terms.append([u,cp,cd])
    return {'p':p,'N':N,'r':r,'j':j,'left':actual,'right':mod(rhs,p),'terms':terms}
