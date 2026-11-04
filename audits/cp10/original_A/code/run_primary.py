"""Deterministic CP10 finite replay; claims are conditional and bounded."""
from pathlib import Path
from fractions import Fraction as F
from math import comb
from time import perf_counter
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import two_adic as A
R=Path(__file__).resolve().parents[1]
checks=[]
def ck(name,val,detail=None):
    if type(val) is not bool:raise TypeError('A check must provide an explicit Boolean')
    checks.append({'id':name,'pass':val,'detail':detail})
def write(name,obj):
    p=R/'results'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

def main():
    start=perf_counter();proto=json.loads((R/'records/PROTOCOL.json').read_text())
    # Moments: exact recurrence against a closed binomial formula and its valuation.
    for u in range(0,257,2):
        m=A.moment(u);closed=F(2**(u+1),(u+1)*comb(u,u//2))
        ck(f'moment_{u}',m==closed and A.v2(m)==1+u-A.v2(comb(u,u//2)) and A.v2(m)>=u+1-A.floor_log2(u+1),{'v2':A.v2(m)})
    for kind in ('T','U'):
        for d in range(97):
            poly=A.cheb(kind,d);checks_per_poly=sum(x!=0 for x in poly)
            ok=all(A.at_least(x,u-(1 if kind=='T' else 0)) for u,x in enumerate(poly))
            ck(f'coefficient_{kind}_{d}',ok,{'nonzero_coefficients':checks_per_poly})
    # Exact elementary inequalities supporting the infinite tail proof.
    ck('tail_growth_base',all(2**(k+2)>=(k+1)**2 for k in range(3)))
    ck('tail_growth_induction',all(2*(k+1)**2>=(k+2)**2 for k in range(2,1001)))
    ck('tail_dyadic_blocks',all(2*r<=2**(r-2) for r in range(6,80)))
    # Grid Z harmonic denominator bounds.
    H=65;L=A.floor_log2(H)
    for i in range(H):
        ck(f'harmonic_grid_row_{i}',all(A.at_least(A.z0(i,j),-2*L) for j in range(H)),{'pairs':H})
    # Infinite sums represented by finite rational partial sums with proved tail exponents.
    H=13;P=40;high=80;grid={};tails=[]
    for i in range(H):
        good=True
        for j in range(H):
            s,t=A.smoothing(i,j,H,P);s2,t2=A.smoothing(i,j,H,high)
            c=A.tail_cert(i,j,H,P);tails.append(c);grid[(i,j)]=s2
            good &= A.verify_tail(c,(i,j,H,P)) and A.congruent(s,s2,P) and A.at_least(s2,i-2*A.ceil_log2(H)-1)
        ck(f'smoothing_row_{i}',bool(good),{'pairs':H,'precision':P,'comparison_precision':high})
    for i in range(12):
        ck(f'diagonal_recurrence_row_{i}',all(A.congruent(grid[(i,j)]-grid[(i+1,j+1)],A.moment(i)/F(j+1),P) for j in range(12)),{'pairs':12})
    for d in range(2,13):
        ck(f'minus_boundary_{d}',A.congruent(d*grid[(d,0)],(d-1)*grid[(d-2,0)]+A.moment(d-2)+A.moment(d-1),P))
        ck(f'plus_boundary_{d}',A.congruent((d-1)*grid[(0,d)],(d-2)*grid[(0,d-2)]+F(2,d-1),P))
    ck('minus_start_one',A.congruent(grid[(1,0)],2,P))
    for gi,gtext in enumerate(proto['rational_placeholders']):
        g=F(gtext);e1=4*g-grid[(0,0)];e2=-grid[(0,1)]
        for i in range(H):
            ok=True
            for j in range(H):
                left=A.m0(i,j)+4*g*A.central(i-j)
                right=grid[(i,j)]+e1*A.central(i-j)+e2*A.central(j-i-1)
                ok &= A.congruent(left,right,P)
            ck(f'discrepancy_g{gi}_row{i}',bool(ok),{'pairs':H,'placeholder':gtext,'not_actual_G':True})
    # The scalar bounds are independently exercised using manufactured rational discrepancies.
    H,C,h=65,63,2;L=A.floor_log2(H)
    for u in range(44):
        ok=True
        for j in range(7,59):
            ac=sum(((-1)**v*comb(h,v)*A.central(C-1-u+v-j) for v in range(h+1)),F(0))
            ok &= A.at_least(ac,u+j-H+1)
            for e2txt in ('0','1/3','-5/8'):
                e2=F(e2txt);K=3
                bc=sum(((-1)**v*comb(h,v)*(e2*(C-1-u+v==j)-F(3,2)*A.z0(C-1-u+v,j)) for v in range(h+1)),F(0))
                ok &= A.at_least(bc,-2*L-1-K)
        ck(f'exceptional_scalars_u{u}',bool(ok),{'raw_columns':52,'a_kernels':52,'b_test_values':156})
    # All 4x4 selected source raw positions, with two manufactured G values.
    H=65;P=32;high=128;s00,_=A.smoothing(0,0,H,high);s01,_=A.smoothing(0,1,H,high)
    raw_records=[]
    for r in (0,4,17,47):
        pr,dr=A.rows(1,r)
        for j in (7,13,31,58):
            S=sum((coef*A.smoothing(i,j,H,high)[0] for i,coef in enumerate(pr) if coef),F(0))
            Cker=sum((coef*A.central(i-j) for i,coef in enumerate(pr)),F(0))
            for gi,gt in enumerate(('1/3','-5/8')):
                g=F(gt);e1=4*g-s00;e2=-s01
                E=e1*Cker
                B=sum((dr[i]*(e2*(i==j)-F(3,2)*A.z0(i,j)) for i in range(len(dr))),F(0))
                direct=sum((pr[i]*(A.m0(i,j)+4*g*A.central(i-j))-F(3,2)*dr[i]*A.z0(i,j) for i in range(len(pr))),F(0))
                lowerS=C-2*A.ceil_log2(H)-3
                good=A.congruent(direct,S+E+B,P) and A.at_least(S,lowerS)
                raw_records.append({'row':r,'column':j,'placeholder':gt,'precision':P,'difference_v2':A.v2(direct-S-E-B),'S_valuation':A.v2(S),'required_S_bound':lowerS})
                ck(f'raw_SEB_r{r}_j{j}_g{gi}',good,raw_records[-1])
    # Exact exhaustive finite minimization, distinct from the written all-N argument.
    minima=[]
    for N in range(1,13):
        n,b,C,H=48*N,7*N,63*N,65*N;J,L=A.ceil_log2(H),A.floor_log2(H)
        best=None;arg=[];best_terms={K:None for K in (0,3,9)};choices=0
        for m in range(n+1):
            for l in range(n-m+1):
                q2=A.twice_Q(N,m,l);choices+=1
                if best is None or q2<best:best=q2;arg=[(m,l)]
                elif q2==best:arg.append((m,l))
                for K in (0,3,9):
                    term2=(-2*(H-b)*m+3*m*(m-1)-2*K*m+l*(l-1)-2*(2*L+2+K)*l+2*(C-2*J-3)*(n-m-l))
                    if best_terms[K] is None or term2<best_terms[K]:best_terms[K]=term2
        expected=-505*N*N+(N%2)
        good=best==expected and all(q>=-505*N*N-2*n*(K+2*J+3) for K,q in best_terms.items())
        detail={'N':N,'integer_column_count_choices':choices,'minimum_twice_Q':best,'argmin':arg,'real_minimum_Q':str(-F(505,2)*N*N),'minimum_twice_term_bounds':best_terms}
        minima.append(detail);ck(f'finite_minimization_N{N}',good,detail)
    certs=[]
    for N in proto['bound_N']:
        for K in proto['bound_K']:
            c=A.bound_certificate(N,K);certs.append(c)
            ck(f'conditional_certificate_N{N}_K{K}',A.verify_bound(c,(N,K)))
    # Explicit examples that distinguish permitted from unproved inferences.
    S0=A.smoothing(0,0,13,80)[0]
    ck('e1_must_not_be_discarded',not A.congruent(S0,0,40),{'v2_smoothed_start':A.v2(S0),'placeholder_G':0})
    ck('cross_group_indices_may_repeat',F(1)*F(1)-F(0)*F(0)==1,{'P0':[1,0],'D0':[0,1],'u_E':0,'u_B':0,'determinant':1})
    ck('within_group_repeat_zero',2*6-3*4==0,{'columns':[[2,3],[4,6]],'same_fixed_vector':[2,3]})
    ck('nonintegral_filter_loses_valuation',A.v2(F(1,4))==-2,{'raw_matrix':'I2','altered_filter':'diag(1/2,1/2)','raw_det_v2':0,'filtered_det_v2':-2})
    ck('zero_is_infinite_valuation',A.v2(0) is None and A.at_least(0,100000))
    ck('zero_residue_not_exact_zero',A.rational_residue(F(2**80),40)==A.rational_residue(F(0),40))
    ck('nearby_rationals_different_at_higher_precision',A.rational_residue(F(2**80),100)!=A.rational_residue(F(0),100))
    ck('leading_term_not_complete_finite_bound',A.bound_certificate(2,3)['conditional_lower_bound']=='-3122' and A.bound_certificate(2,3)['leading_bound']=='-1010')
    write('SMOOTHING_CERTIFICATES.json',tails);write('CONDITIONAL_BOUND_CERTIFICATES.json',certs)
    write('RAW_COLUMN_DIAGNOSTICS.json',{'scope':'Manufactured rational placeholders; not values of the real Catalan constant','records':raw_records})
    write('FINITE_MINIMA.json',minima)
    got=[c['id'] for c in checks];expected=proto['primary_expected_ids']
    good=A.gate(checks,expected)
    report={'status':'PASS' if good else 'HOLD','check_count':len(checks),'checks':checks,'expected_ids_match':got==expected,'seconds':perf_counter()-start,'scope':'Bounded finite evidence plus separately written conditional argument. No full theorem or formal kernel credit.'}
    write('TWO_ADIC_PRIMARY.json',report)
    print(json.dumps({'status':report['status'],'check_count':len(checks),'seconds':report['seconds'],'failed':[x['id'] for x in checks if not x['pass']],'ids_match':got==expected}))
    return 0 if good else 1
if __name__=='__main__':sys.exit(main())
