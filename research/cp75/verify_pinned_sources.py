#!/usr/bin/env python3
"""CP75 fail-closed original-source and theorem-contract verifier, read-only.

Checks all twenty pinned original Git objects, bytes, SHA1 Git blobs, exact
algebraic-independence hypotheses and manuscript/Lean proof scope.
This is NOT a proof checker; full theorem admission runs separately.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,os,sys,time
import urllib.error,urllib.parse,urllib.request
from pathlib import Path

PIN="fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb"
DECL="OAI.EuclideanRamsey.NineStatement.nine_circle_configuration"
BASE="lean/OAI/Combinatorics/EuclideanRamsey/"
PAPER="preprints/A-classification-of-finite-Euclidean-Ramsey-configurations-September-23-2026/build/sections/"

def need(ok,message):
    if not ok:raise ValueError(message)

def fetch(path):
    url="https://api.github.com/repos/openai/math/contents/"+urllib.parse.quote(path,safe="/")+"?ref="+PIN
    headers={"Accept":"application/vnd.github+json",
             "X-GitHub-Api-Version":"2022-11-28",
             "User-Agent":"CMIS-CP75-source-contract"}
    if os.getenv("GITHUB_TOKEN"):headers["Authorization"]="Bearer "+os.getenv("GITHUB_TOKEN")
    error=None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as reply:
                need(reply.status==200,"GitHub source non-200")
                return json.load(reply)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
            error=exc
            if isinstance(exc,urllib.error.HTTPError) and exc.code not in (429,500,502,503,504):break
            time.sleep(attempt+1)
    raise ValueError(f"Pinned source fetch failed {path}: {error}")

def check_scope(data):
    def txt(path):return data[path].decode("utf-8")
    challenge=txt("lean/ComparatorChallenges/EuclideanRamseyNine.lean")
    config=json.loads(txt("lean/ComparatorChallenges/EuclideanRamseyNine.json"))
    solution=txt(BASE+"NineStatement.lean")
    proof=txt(BASE+"Nine.lean")
    grid=txt(BASE+"NineGridDeterminant.lean")
    rational=txt(BASE+"NineRationalDeterminant.lean")
    geometry=txt(BASE+"NineGeometry.lean")
    field=txt(BASE+"NineField.lean")
    linear=txt(BASE+"NineLinearObstruction.lean")
    main=txt(BASE+"Main.lean")
    paper=txt(PAPER+"07-consequences.tex")
    docs=txt("lean/docs/172.md")
    contracts={
      "challenge":(challenge,[
        "theorem nine_circle_configuration", "(ht : AlgebraicIndependent ℚ t)",
        "Function.Injective (literalCircleConfig t)",
        "∀ i, dist (literalCircleConfig t i) 0 = 1",
        "¬ Ramsey (literalCircleConfig t)", "by\n  sorry",
        "∀ r : ℕ, 2 ≤ r → ∃ D : ℕ, 1 ≤ D ∧",
        "∀ c : Space D → Fin r, ∃ b : Fin s → Space D",
        "(1 - (t i)^2) / (1 + (t i)^2)", "(2 * t i) / (1 + (t i)^2)"]),
      "solution":(solution,[
        "theorem nine_circle_configuration","literalCircleConfig_eq",
        "NineMain.nine_circle_configuration t ht"]),
      "source_main":(proof,[
        "theorem nine_circle_not_ramsey", "theorem evaluationMatrix_det_ne_zero",
        "polynomialEmbedding_injective", "NineLinearObstruction.not_ramsey_of_det_ne_zero",
        "theorem nine_circle_configuration"]),
      "grid":(grid,[
        "lemma det_C : Matrix.det C = 8",
        "lemma det_evaluated_E",
        "lemma gridEval_det_E",
        "theorem det_E_ne_zero", "Matrix.det_kronecker"]),
      "rational":(rational,[
        "theorem det_genericMatrix_ne_zero", "lemma cleared_matrix",
        "theorem det_fin9Matrix_ne_zero"]),
      "linear_obstruction":(linear,[
        "theorem not_fieldCriterion_of_det_ne_zero",
        "theorem not_ramsey_of_det_ne_zero",
        "vector_eq_zero_of_det_ne_zero"]),
      "coefficient_field":(field,[
        "def coordinateTensorEmbedding",
        "theorem coordinateTensorEmbedding_injective",
        "def coefficientEquiv",
        "AlgebraicIndependent ℚ t"]),
      "geometry":(geometry,[
        "theorem circlePoint_recover", "theorem circleConfig_injective",
        "theorem circleConfig_affineSpan",
        "theorem circleConfig_coordinateField"]),
      "main":(main,["theorem classification","theorem fieldCriterion_ramsey"]),
      "paper":(paper,[
        "\\begin{proposition}\\label{cons:nine}",
        "algebraically independent real numbers",
        "Kronecker product", "2^6=64",
        "There are no","nine points"]) if False else (paper,[
        "\\begin{proposition}\\label{cons:nine}",
        "algebraically independent real numbers",
        "Kronecker product", "2^6=64",
        "nine points"]),
      "family_docs":(docs,[
        "EuclideanRamseyNine.lean",
        "nine-point circle configuration",
        "algebraically independent parameters"]),
    }
    for name,(content,fragments) in contracts.items():
        for fragment in fragments:
            need(fragment in content,f"{name}: expected pinned theorem fragment absent: {fragment}")
    need(config.get("challenge_module")=="ComparatorChallenges.EuclideanRamseyNine",
         "Comparator challenge drift")
    need(config.get("solution_module")=="OAI.Combinatorics.EuclideanRamsey.NineStatement",
         "Comparator solution module drift")
    need(config.get("theorem_names")==[DECL],"Comparator selected theorem drift")
    need(set(config.get("permitted_axioms",[]))==
         {"propext","Quot.sound","Classical.choice"},"Unexpected permitted axioms")
    need(config.get("enable_nanoda") is False,"Unexpected comparison mode")
    need("sorry" not in solution and "admit" not in solution,"Original solution has placeholder")
    return {
       "exact_selected_declaration":DECL,
       "hypothesis":"AlgebraicIndependent ℚ t for t : Fin 9 → ℝ",
       "conclusion":["Function.Injective literalCircleConfig",
                     "all nine lie on unit circle",
                     "not Ramsey in arbitrary sufficiently large Euclidean space"],
       "field_method":"Exact F⊗_Q F embeds into rational functions on 18 independent variables",
       "proof_dependency":"Original CP71 tensor necessity + nonsingular 9x9 evaluation matrix",
       "publisher_rational_specialization_det":"64",
       "publisher_denominator_cleared_det":"8^6 = 262144",
       "deduction_from_source_not_novel_authorship":True,
       "source_audit_is_not_theorem_admission":True
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,default=Path("research/cp75/receipt"))
    args=ap.parse_args()
    pins=json.loads(Path("research/cp75/SOURCE_PINS.json").read_text(encoding="utf-8"))
    need(pins["source_repository"]=="openai/math" and pins["source_commit"]==PIN,"Publisher identity drift")
    need(pins["target"]==DECL,"Original selected theorem drift")
    records=pins["source_files"]
    need(len(records)==20 and len({rec["path"] for rec in records})==20,"Source pin count or duplicate")
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    snaps=out/"source_snapshots";snaps.mkdir(parents=True,exist_ok=True)
    sources={};results=[]
    for rec in records:
        path=rec["path"];remote=fetch(path)
        need(remote.get("sha")==rec["git_blob_sha1"],"GitHub blob changed: "+path)
        need(remote.get("encoding")=="base64","Unsupported GitHub blob encoding: "+path)
        raw=base64.b64decode(remote["content"].replace("\n",""),validate=True)
        sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
        need(sha==rec["git_blob_sha1"],"Recomputed Git blob mismatch: "+path)
        target=snaps/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        sources[path]=raw
        results.append({"path":path,"git_blob_sha1":sha,
                        "sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),
                        "role":rec["role"],
                        "source_url":f"https://github.com/openai/math/blob/{PIN}/{path}"})
    scoped=check_scope(sources)
    receipt={"status":"PASS_CP75_20_PINNED_SOURCE_OBJECTS_AND_CLAIM_SCOPE",
             "original_source_commit":PIN,"sources_checked":len(results),
             "objects":results,"scope_contract":scoped,
             "full_selected_theorem":"SEPARATE_PINNED_LEAN_COMPARATOR",
             "other_family_targets_awarded":0,"whole_family_validated":False,
             "external_certification":"DEFERRED"}
    text=json.dumps(receipt,indent=2,sort_keys=True)+"\n"
    (out/"SOURCE_VALIDATION.json").write_text(text,encoding="utf-8")
    print(text)

if __name__=="__main__":
    try:main()
    except Exception as error:
        print("CP75 SOURCE CONTRACT HOLD: "+str(error),file=sys.stderr)
        raise SystemExit(2)
