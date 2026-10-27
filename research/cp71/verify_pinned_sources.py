#!/usr/bin/env python3
"""Fetch exactly pinned OpenAI Family172 source, validate Git blobs and scope.

This source binding is an independent read of published texts, not proof
admission. It fails closed on any identity/statement/config drift.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,os,re,sys,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path

REPO="openai/math"
PIN="fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb"
EXPECTED={
"lean/docs/172.md":"66a70def5fdc63c39958196e5bfd3902f7f19dd0",
"lean/ComparatorChallenges/EuclideanRamsey.lean":"6268acd3bf3f2537607064aae93b425aed117b4c",
"lean/ComparatorChallenges/EuclideanRamsey.json":"7b3d0e9dc89a1a5e254ead95031f29b8f0ccb9f2",
"lean/OAI/Combinatorics/EuclideanRamsey/Main.lean":"f61dbf1f08e982747098c903896971d7fd4d1524",
"preprints/A-classification-of-finite-Euclidean-Ramsey-configurations-September-23-2026/build/sections/01-introduction.tex":"7124c465bde3ba0a9975aa4dcb6380c527173589",
"preprints/A-classification-of-finite-Euclidean-Ramsey-configurations-September-23-2026/build/sections/02-tensors.tex":"357a5dc4fab8c0f083541e90a009106372ac05da"
}

def fail(msg):
    raise RuntimeError(msg)

def fetch_github(path):
    url=("https://api.github.com/repos/openai/math/contents/"
         +urllib.parse.quote(path,safe="/")+"?ref="+PIN)
    headers={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28",
             "User-Agent":"CMIS-CP71-readonly-replay"}
    # GH Actions GITHUB_TOKEN may have public-repo API read access.
    # Access is intentionally read-only; no source repository writes.
    token=os.getenv("GITHUB_TOKEN","")
    if token:headers["Authorization"]="Bearer "+token
    last=None
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=25) as response:
                if response.status!=200:fail("GitHub HTTP "+str(response.status))
                obj=json.load(response)
                return obj
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            last=e
            if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):
                break
            time.sleep(i+1)
    fail("Pinned source fetch failed for "+path+": "+str(last))

def assert_contract(data):
    challenge=data["lean/ComparatorChallenges/EuclideanRamsey.lean"].decode("utf-8")
    config=json.loads(data["lean/ComparatorChallenges/EuclideanRamsey.json"])
    solution=data["lean/OAI/Combinatorics/EuclideanRamsey/Main.lean"].decode("utf-8")
    manuscript=data["preprints/A-classification-of-finite-Euclidean-Ramsey-configurations-September-23-2026/build/sections/01-introduction.tex"].decode("utf-8")
    tensors=data["preprints/A-classification-of-finite-Euclidean-Ramsey-configurations-September-23-2026/build/sections/02-tensors.tex"].decode("utf-8")
    scope=data["lean/docs/172.md"].decode("utf-8")
    must_in={
        "challenge":{"def Congruent","def Ramsey","∀ r : ℕ, 2 ≤ r → ∃ D : ℕ, 1 ≤ D ∧",
                    "∀ c : Space D → Fin r","Congruent a b","def coordinateField",
                    "def FieldCriterion","Ramsey a ↔ FieldCriterion a","(hs : 2 ≤ s)",
                    "(hd : 1 ≤ d)","(ha : Function.Injective a)",
                    "affineSpan ℝ (Set.range a) = ⊤","by\n  sorry"},
        "solution":{"theorem classification","theorem fieldCriterion_ramsey",
                    "theorem full_affine_representative",
                    "theorem classification_nonempty"},
        "manuscript":{"\\begin{theorem}[Classification]","\\label{eq:field-evaluations}",
                      "\\label{eq:field-spatial}","An equality in $B$ is stronger",
                      "There are no separate conditions"},
        "tensors":{"\\section{Rational tensors and the coloring obstruction}",
                   "extending the coefficient ring from $B$",
                   "\\begin{proposition}\\label{alg:equivalence}",
                   "\\begin{proposition}\\label{alg:necessity}",
                   "even when their coordinate fields differ"},
        "scope":{"Classification of finite Euclidean Ramsey configurations",
                 "Comparator links", "cospherical"}
    }
    for name,s in {"challenge":challenge,"solution":solution,
                   "manuscript":manuscript,"tensors":tensors,"scope":scope}.items():
        for needle in must_in[name]:
            if needle not in s:fail(f"Missing authoritative contract fragment {name}: {needle}")
    if config.get("challenge_module")!="ComparatorChallenges.EuclideanRamsey":
        fail("Comparator challenge module mismatch")
    if config.get("solution_module")!="OAI.Combinatorics.EuclideanRamsey.Main":
        fail("Comparator solution module mismatch")
    if config.get("theorem_names")!=["OAI.EuclideanRamsey.classification"]:
        fail("Comparator theorem mismatch")
    if set(config.get("permitted_axioms",[]))!={"propext","Quot.sound","Classical.choice"}:
        fail("Permitted axiom drift")
    if config.get("enable_nanoda") is not False:fail("nanoda flag unexpectedly changed")
    if "∀ r : ℕ, 2 ≤ r → ∃ D : ℕ" not in challenge:
        fail("Ramsey quantifier order drift")
    if "∀ c : Space D → Fin r, ∃ b : Fin s → Space D" not in challenge:
        fail("Universal-colouring/existential-image order drift")
    if "((augmented a i α) ⊗ₜ[ℚ] (1 : Coeff a))" not in challenge:
        fail("Exact tensor evaluation substrate changed")
    if "multiply a (P (some α) (some β))" not in challenge:
        fail("Spatial block constraints changed")
    if "theorem classification" not in solution:
        fail("No publisher solution interface found")
    if "sorry" in solution:
        fail("Publisher solution file contains textual sorry; needs independent review")
    return {
      "Ramsey_quantifiers":"forall r>=2 / exists D>=1 / forall coloring / exists isometric configuration and color",
      "full_theorem":"OAI.EuclideanRamsey.classification",
      "theorem_hypotheses":["s>=2","d>=1","a injective","affine span full"],
      "tensor_over":"coordinate field tensor product over Q, equality BEFORE multiplication",
      "permitted_axioms":config["permitted_axioms"],
      "source_theorem_compared_to_manuscript":"INTERFACE_AND_TEXT_ONLY",
      "publisher_solution_seen":"YES_NOT_EXECUTED_IN_LEAN"
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,default=Path("research/cp71/receipt/source"))
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    man=json.loads(Path("research/cp71/SOURCE_PINS.json").read_text(encoding="utf-8"))
    if man.get("commit")!=PIN or man.get("source_repository")!=REPO:fail("Manifest source pin drift")
    observed={r["path"]:r["git_blob_sha"] for r in man.get("source_files",[])}
    if observed!=EXPECTED:fail("Pinned expected source files/SHAs have changed")
    data={}
    records=[]
    for path,sha in EXPECTED.items():
        response=fetch_github(path)
        if response.get("sha")!=sha or response.get("encoding")!="base64":
            fail("GitHub object identity or encoding mismatch: "+path)
        raw=base64.b64decode(response.get("content","").replace("\n",""),validate=True)
        git=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
        if git!=sha:fail("Recomputed Git blob is not the pinned object "+path)
        data[path]=raw
        target=args.output_dir/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(raw)
        records.append({"path":path,"git_blob_sha1":git,"sha256":hashlib.sha256(raw).hexdigest(),
                        "byte_count":len(raw),"source_url":
                        f"https://github.com/openai/math/blob/{PIN}/{path}"})
    claim_contract=assert_contract(data)
    report={"status":"PASS_PINNED_SOURCE_AND_SCOPE_ONLY","checkpoint":"CP71",
            "source_commit":PIN,"source_object_count":len(records),
            "objects":records,"scope_contract":claim_contract,
            "classification_lean_kernel":"NOT_RUN",
            "proof_admission":"NOT_RUN",
            "claim_validated":False}
    text=json.dumps(report,sort_keys=True,indent=2)+"\n"
    (args.output_dir.parent/"SOURCE_VALIDATION.json").write_text(text,encoding="utf-8")
    print(text)

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("SOURCE CONTRACT HOLD: "+str(exc),file=sys.stderr)
        sys.exit(2)
