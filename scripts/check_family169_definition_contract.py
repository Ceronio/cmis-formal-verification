#!/usr/bin/env python3
"""Additional definition-aware gates over an unchanged original Comparator run.
The legacy runner's SELECTED_THEOREM/status labels are compatibility names only.
This checker neither builds nor modifies the mathematical source or configuration.
"""
from pathlib import Path
import argparse, hashlib, json, os, re

TARGET='OAI.elementaryPositivityWitness'
CONFIG={
 'challenge_module':'ComparatorChallenges.ElementaryPositivity',
 'solution_module':'OAI.Combinatorics.Chromatic.Main',
 'theorem_names':[], 'definition_names':[TARGET],
 'permitted_axioms':['propext','Quot.sound','Classical.choice'],
 'enable_nanoda':False,
}
BLOBS={
 'ComparatorChallenges/ElementaryPositivity.json':'ad132610a54c09f797dbfc87d30d4549c79fcbc9',
 'ComparatorChallenges/ElementaryPositivity.lean':'2e90d68d97df418c71af9bf5080711c8a2b349ef',
 'OAI/Combinatorics/Chromatic/Main.lean':'12abe371e589d0b2ca4548b3c90631afb030aa7f',
}

def inspect(root, outcome):
    receipt=root/'cmis_receipt';project=root/'.cmis-work/openai-math/lean'
    checks=[]
    def check(name, condition):
        checks.append({'name':name,'pass':bool(condition)})
    def text(name):return (receipt/name).read_text()
    check('formal_step_success',outcome=='success')
    for rel,expected in BLOBS.items():
        data=(project/rel).read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        check('original_blob:'+rel,actual==expected)
    config=json.loads((project/'ComparatorChallenges/ElementaryPositivity.json').read_text())
    check('exact_definition_configuration',config==CONFIG)
    check('legacy_runner_success',text('FINAL_STATUS.txt').strip()=='PASS_SELECTED_THEOREM')
    check('comparator_exit_zero',text('04_comparator.exit_code').strip()=='0')
    check('bounded_exit_zero','exit_code=0' in text('98_bounded_exit.txt').splitlines())
    check('inner_exit_zero','exit_code=0' in text('98_exit.txt').splitlines())
    out=text('04_comparator.stdout')
    check('comparator_acceptance','Your solution is okay!' in out)
    check('default_kernel_acceptance','Lean default kernel accepts the solution' in out)
    axioms=text('06_axioms.stdout')
    matches=re.findall(r"'"+re.escape(TARGET)+r"' depends on axioms:\s*\[([^\]]*)\]",axioms,re.S)
    parsed={x.strip() for x in matches[0].split(',') if x.strip()} if len(matches)==1 else None
    check('one_selected_definition_axiom_report',len(matches)==1)
    check('only_permitted_axioms',parsed is not None and parsed<=set(CONFIG['permitted_axioms']))
    check('postcheck_exact_import_and_root',text('PostCheckAxioms.lean').splitlines()==[
        'import OAI.Combinatorics.Chromatic.Main','#print axioms '+TARGET])
    return {'schema':'CMIS_ORIGINAL_DEFINITION_GATE_V1','target':TARGET,
            'selection_kind':'definition_names','theorem_names':[],
            'configuration':config,'checks':checks,'axioms':sorted(parsed or []),
            'accepted':all(c['pass'] for c in checks),
            'note':'Legacy PASS_SELECTED_THEOREM names are not a second theorem or separate proof. Human/CMIS semantic scope review and receipt audit remain required.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path.cwd());a=parser.parse_args()
    receipt=a.root/'cmis_receipt';receipt.mkdir(exist_ok=True)
    status=receipt/'DEFINITION_FINAL_STATUS.txt'
    status.write_text('DEFINITION_CONTRACT_HOLD\n')
    try: result=inspect(a.root,os.environ.get('FORMAL_STEP_OUTCOME','unknown'))
    except Exception as exc:
        result={'schema':'CMIS_ORIGINAL_DEFINITION_GATE_V1','accepted':False,'error':type(exc).__name__+': '+str(exc)}
    (receipt/'07_definition_contract.json').write_text(json.dumps(result,indent=2)+'\n')
    if result['accepted']:status.write_text('PASS_SELECTED_DEFINITION\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['accepted'] else 4)

if __name__=='__main__':main()
