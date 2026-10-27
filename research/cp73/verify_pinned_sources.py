#!/usr/bin/env python3
"""CP73 fail-closed source authenticity and circle-theorem scope audit.

Checks original OpenAI Git blob identities from immutable commit, comparator
interface, mathlib-selected theorem, edge cases and original manuscript.
A source scan never counts as formal theorem acceptance.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,os,sys,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path

PIN="fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb"
DECL="OAI.EuclideanRamsey.CircleConsequence.at_most_five_circle_points_ramsey"

def need(ok,msg):
    if not ok: raise ValueError(msg)

def fetch(path):
    url="https://api.github.com/repos/openai/math/contents/"+urllib.parse.quote(path,safe="/")+"?ref="+PIN
    headers={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"CMIS-CP73-source-auth"}
    if os.getenv("GITHUB_TOKEN"): headers["Authorization"]="Bearer "+os.getenv("GITHUB_TOKEN")
    last=None
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=25) as r:
                need(r.status==200,"HTTP status "+str(r.status))
                return json.load(r)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
            last=exc
            if isinstance(exc,urllib.error.HTTPError) and exc.code not in (429,500,502,503,504):break
            time.sleep(i+1)
    raise RuntimeError("Pinned source unavailable: "+path+": "+str(last))

def check_scope(s):
    def read(path):return s[path].decode("utf-8")
    chall=read("lean/ComparatorChallenges/EuclideanRamseyCircle.lean")
    config=json.loads(read("lean/ComparatorChallenges/EuclideanRamseyCircle.json"))
    circle=read("lean/OAI/Combinatorics/EuclideanRamsey/Circle.lean")
    rows=read("lean/OAI/Combinatorics/EuclideanRamsey/CircleRows.lean")
    span=read("lean/OAI/Combinatorics/EuclideanRamsey/CircleSpan.lean")
    extension=read("lean/OAI/Combinatorics/EuclideanRamsey/CircleExtension.lean")
    interpolation=read("lean/OAI/Combinatorics/EuclideanRamsey/CircleInterpolation.lean")
    geometry=read("lean/OAI/Combinatorics/EuclideanRamsey/CircleGeometry.lean")
    quad=read("lean/OAI/Combinatorics/EuclideanRamsey/Quadratic.lean")
    main=read("lean/OAI/Combinatorics/EuclideanRamsey/Main.lean")
    paper_path="preprints/A-classification-of-finite-Euclidean-Ramsey-configurations-September-23-2026/build/sections/"
    consequences=read(paper_path+"07-consequences.tex")
    intro=read(paper_path+"01-introduction.tex")
    tensors=read(paper_path+"02-tensors.tex")
    docs=read("lean/docs/172.md")
    cases={
     "challenge":(chall,[
        "theorem at_most_five_circle_points_ramsey",
        "(hs : 0 < s)", "(hs5 : s ≤ 5)", "(ha : Function.Injective a)",
        "(hsphere : ∃ c : Space 2, ∃ r : ℝ, ∀ i, dist (a i) c = r) : Ramsey a",
        "∀ r : ℕ, 2 ≤ r → ∃ D : ℕ, 1 ≤ D ∧",
        "∀ c : Space D → Fin r, ∃ b : Fin s → Space D","Congruent a b","by\n  sorry"]),
     "publisher_solution":(circle,[
        "theorem five_circle_points_ramsey",
        "theorem at_most_five_circle_points_ramsey",
        "circle_five_affineSpan","circle_five_rows_independent",
        "spherical_quadraticIndependent_ramsey",
        "zero_radius_ramsey","extend_to_five","ramsey_restrict"]),
     "quadratic_rows":(rows,[
        "theorem normalized_isolators",
        "theorem quadratic_evaluation_surjective",
        "theorem circle_five_rows_independent",
        "five_point_isolator"]),
     "affine_span":(span,["theorem circle_five_affineSpan","secantValue_ne_zero"]),
     "extension":(extension,[
        "theorem stereographic_on_circle","theorem stereographic_injective",
        "theorem circle_infinite","theorem extend_to_five"]),
     "interpolation":(interpolation,[
        "theorem pairedSecantMatrix_vanishes","theorem five_point_isolator",
        "theorem secantValue_ne_zero"]),
     "geometry":(geometry,["theorem zero_radius_ramsey","theorem ramsey_restrict"]),
     "quadratic_sufficiency":(quad,[
        "theorem spherical_quadraticIndependent_ramsey_all",
        "theorem quadraticIndependent_fieldCriterion",
        "theorem spherical_quadraticIndependent_ramsey"]),
     "main_classification":(main,["theorem classification","theorem fieldCriterion_ramsey"]),
     "paper_five_circle":(consequences,[
        "\\begin{corollary}\\label{cons:quadrilateral}",
        "Every nonempty set of at most five distinct points on a circle is Ramsey.",
        "No three circle points are collinear",
        "quadratic evaluation onto","five resulting polynomials",
        "A monochromatic copy of that set contains a copy of the original set."]),
     "paper_intro":(intro,[
        "\\begin{theorem}[Classification]",
        "Congruence means preservation of every pairwise distance"]),
     "paper_tensors":(tensors,[
        "\\begin{proposition}\\label{alg:equivalence}",
        "\\begin{proposition}\\label{alg:necessity}"]),
     "family_scope":(docs,["at most five points on a circle","EuclideanRamseyCircle.lean"]),
    }
    for key,(content,needles) in cases.items():
        for needle in needles:
            need(needle in content,f"{key}: missing critical exact source text: {needle}")
    need(config.get("challenge_module")=="ComparatorChallenges.EuclideanRamseyCircle","Wrong challenge module")
    need(config.get("solution_module")=="OAI.Combinatorics.EuclideanRamsey.Circle","Wrong solution module")
    need(config.get("theorem_names")==[DECL],"Original theorem target mismatch")
    need(set(config.get("permitted_axioms",[]))=={"propext","Quot.sound","Classical.choice"},"Axiom whitelist drift")
    need(config.get("enable_nanoda") is False,"Unexpected nanoda verifier")
    need("sorry" not in circle and "admit" not in circle,"Publisher solution source has unreviewed placeholder")
    return {
     "selected_theorem":DECL,
     "s":">0 and <=5","injectivity":"required","dimension":"2","circle":"exists center and radius including zero",
     "zero_radius_injective_case":"necessarily singleton",
     "distance_scale":"original scale; no dilation","colorings":"every finite coloring, arbitrary function",
     "quantifier_order":"for every r>=2, exists ambient D>=1, for every coloring exists monochromatic congruent embedding",
     "scope_level":"single CircleConsequence comparator only",
     "deep_dependences":["CP71 original field classification","quadratic row independence","circle extension to five"],
     "source_contract_pass_does_not_prove_theorem":True
    }

def main():
    cli=argparse.ArgumentParser();cli.add_argument("--output-dir",type=Path,default=Path("research/cp73/receipt"))
    args=cli.parse_args()
    manifest=json.loads(Path("research/cp73/SOURCE_PINS.json").read_text())
    need(manifest["source_repository"]=="openai/math" and manifest["source_commit"]==PIN,"Source identifier drift")
    need(manifest["target_name"]==DECL,"Selected original theorem drift")
    paths=manifest["source_files"]
    need(len(paths)==15 and len({x["path"] for x in paths})==15,"Missing/duplicate pin")
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    src_dir=out/"source_snapshots";src_dir.mkdir(parents=True,exist_ok=True)
    data={};items=[]
    for spec in paths:
        path=spec["path"];obj=fetch(path)
        need(obj.get("encoding")=="base64","Unsupported GitHub source encoding: "+path)
        need(obj.get("sha")==spec["git_blob_sha1"],"GitHub source blob identity drift: "+path)
        b=base64.b64decode(obj["content"].replace("\n",""),validate=True)
        computed=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
        need(computed==spec["git_blob_sha1"],"Recomputed Git blob mismatch: "+path)
        target=src_dir/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        data[path]=b
        items.append({"path":path,"git_blob_sha1":computed,
          "sha256":hashlib.sha256(b).hexdigest(),"size_bytes":len(b),"role":spec["role"],
          "source_url":f"https://github.com/openai/math/blob/{PIN}/{path}"})
    result={"status":"PASS_CP73_15_ORIGINAL_SOURCE_OBJECTS_AND_SCOPE",
     "source_commit":PIN,"objects_checked":len(items),"original_objects":items,
     "scope":check_scope(data),"formal_proof_kernel":"SEPARATE_GITHUB_COMPARATOR",
     "other_family_comparators_awarded":0,"full_family_172_certified":False,
     "external_mathematical_certification":"DEFERRED"}
    doc=json.dumps(result,indent=2,sort_keys=True)+"\n"
    (out/"SOURCE_VALIDATION.json").write_text(doc)
    print(doc)
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("CP73 PINNED SOURCE AUDIT HOLD: "+str(e),file=sys.stderr)
        sys.exit(2)
