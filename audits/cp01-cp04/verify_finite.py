#!/usr/bin/env python3
"""CMIS CP01-CP04 exact synthetic finite verification; not formal Lean proof or full historical replay."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse,hashlib,json,platform,re,sys
t={}

def test(key,actual,expected):
    t[key]=t.get(key,0)+1
    if actual!=expected: raise AssertionError(f"{key} {t[key]}: {actual!r} != {expected!r}")

def bounds(a,b):
    if not (0<=a<=1 and 0<=b<=1): raise ValueError("probability domain")
    return max(F(0),a+b-1), min(a,b)

def joint(a,b,z): return z,a-z,b-z,1-a-b+z

def cp01():
    for i,j in product(range(21),repeat=2):
        a,b=F(i,20),F(j,20)
        lo,hi=bounds(a,b)
        test("cp01_formula",(lo,hi),(max(F(0),a+b-1),min(a,b)))
        for z in (lo,hi):
            w=joint(a,b,z)
            test("cp01_attaining_joint_table",(min(w)>=0,sum(w)==1,w[0]+w[1]==a,w[0]+w[2]==b),(True,True,True,True))
    test("cp01_interval_demo",(max(F(0),F(1,100)+F(2,100)-1),min(F(3,100),F(4,100))),(F(0),F(3,100)))

def rational(x):
    if type(x) is int: return F(x)
    if type(x) is not str or not 0<len(x)<=60 or not re.fullmatch(r"[+-]?\d+(?:/\d+|\.\d+)?",x,re.ASCII): raise ValueError("not an exact rational")
    try:return F(x)
    except (ValueError,ZeroDivisionError) as e:raise ValueError("invalid rational") from e

def binary_cert(m,c):
    # Only 2x2 validation, not CP02's full historical generic transport model.
    try:
        if set(m)!={"a","b"} or set(c)!={"p11","p10","p01","p00","claim"}:return False
        a,b=(rational(m[k]) for k in ("a","b"))
        lo,hi=bounds(a,b)
        q=tuple(rational(c[k]) for k in ("p11","p10","p01","p00"))
        z=rational(c["claim"])
        return min(q)>=0 and sum(q)==1 and q[0]+q[1]==a and q[0]+q[2]==b and q[0]==z and lo<=z<=hi
    except (ValueError,TypeError,KeyError,ZeroDivisionError):return False

def cp02():
    for i,j in product(range(11),repeat=2):
        a,b=F(i,10),F(j,10)
        for z in bounds(a,b):
            m={"a":str(a),"b":str(b)}
            c=dict(zip(("p11","p10","p01","p00"),map(str,joint(a,b,z))))
            c["claim"]=str(z)
            test("cp02_good_certificate",binary_cert(m,c),True)
            for key,value in (("claim","2"),("p11","NaN"),("p10","1/0"),("p01",True),("p00","-1")):
                bad=c.copy();bad[key]=value
                test("cp02_corrupt_certificate_rejected",binary_cert(m,bad),False)
            for mode in ("missing","invented_pass"):
                bad=c.copy()
                if mode=="missing":bad.pop("p00")
                else:bad["PASS"]=True
                test("cp02_corrupt_certificate_rejected",binary_cert(m,bad),False)
    for bad in (True,1.0,float("nan"),None,"1e3","1/0","",float("inf")):
        try:rational(bad);ok=False
        except ValueError:ok=True
        test("cp02_strict_rational_rejection",ok,True)

def slot(a0,a1,b0,b1):
    if not (0<=a0<=a1<=1 and 0<=b0<=b1<=1):raise ValueError("interval")
    return max(F(0),a0+b0-1),min(a1,b1)

def window(slots):
    p=[slot(*s) for s in slots]
    return max([F(0)]+[x for x,y in p]), min(F(1),sum((y for x,y in p),F(0)))

def traj(dist):
    a=[F(0)]*3;b=[F(0)]*3;z=[F(0)]*3;event=F(0)
    assert sum(dist.values(),F(0))==1
    for state,m in dist.items():
        if "X" in state:event+=m
        for i,ch in enumerate(state):
            if ch in ("A","X"):a[i]+=m
            if ch in ("B","X"):b[i]+=m
            if ch=="X":z[i]+=m
    return a,b,z,event

def cp03():
    one=(F(1,100),F(3,100),F(2,100),F(4,100))
    test("cp03_three_hour_bounds",window([one]*3),(F(0),F(9,100)))
    u={"X00":F(3,100),"0X0":F(3,100),"00X":F(3,100),"000":F(91,100)}
    test("cp03_attain_upper",traj(u),([F(3,100)]*3,[F(3,100)]*3,[F(3,100)]*3,F(9,100)))
    l={"A00":F(1,100),"0A0":F(1,100),"00A":F(1,100),"B00":F(2,100),"0B0":F(2,100),"00B":F(2,100),"000":F(91,100)}
    test("cp03_attain_lower",traj(l),([F(1,100)]*3,[F(2,100)]*3,[F(0)]*3,F(0)))
    for i,j in product(range(1,7),range(1,6)):
        a,b=F(i,10),F(j,10)
        test("cp03_single_slot",window([(a,a,b,b)]),bounds(a,b))
    test("cp03_six_slot_semantics",window([one]*6),(F(0),F(18,100)))

def evt(bits,n,contiguous):return ("1"*n in bits) if contiguous else (bits.count("1")>=n)

def mass(dist,n,contiguous):return sum((v for k,v in dist.items() if evt(k,n,contiguous)),F(0))

def cp04():
    pairs={"110":F(3,200),"101":F(3,200),"011":F(3,200),"000":F(191,200)}
    test("cp04_total2_witness",mass(pairs,2,False),F(9,200))
    test("cp04_slot_marginals",[sum((v for k,v in pairs.items() if k[i]=="1"),F(0)) for i in range(3)],[F(3,100)]*3)
    full={"111":F(3,100),"000":F(97,100)}
    test("cp04_contiguous2_witness",mass(full,2,True),F(3,100))
    test("cp04_total3_witness",mass(full,3,False),F(3,100))
    any_={"100":F(3,100),"010":F(3,100),"001":F(3,100),"000":F(91,100)}
    test("cp04_any_witness",mass(any_,1,False),F(9,100))
    for w in map("".join,product("01",repeat=3)):
        test("cp04_contiguous_implies_total",evt(w,2,True) and not evt(w,2,False),False)
        test("cp04_three_implies_contiguous",evt(w,3,False) and not evt(w,2,True),False)
    test("cp04_upper_counting_bound",(3*F(3,100)/2,F(3,100)),(F(9,200),F(3,100)))
    test("cp04_nonconsecutive_counterexample",(evt("101",2,False),evt("101",2,True)),(True,False))

tests={"CP01":cp01,"CP02":cp02,"CP03":cp03,"CP04":cp04}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cp",choices=[*tests,"ALL"],required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    error=None
    try:
        for fn in (list(tests.values()) if args.cp=="ALL" else [tests[args.cp]]):fn()
        result="PASS"
    except Exception as ex:
        result="FAIL";error=f"{type(ex).__name__}: {ex}"
    report={"checkpoint":args.cp,"status":result,"checks":t,"assertion_count":sum(t.values()),"python":platform.python_version(),
            "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope":"Public synthetic exact-arithmetic bounded tests, not full historical source replay, Lean proof or real-world reliability certification.",
            "remaining":["Original CP archive/full-suite crosswalk not performed in this workflow","CP02 generic transport not covered","No expert endorsement"],"error":error}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    return int(result!="PASS")
if __name__=="__main__":sys.exit(main())
