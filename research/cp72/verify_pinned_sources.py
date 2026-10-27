#!/usr/bin/env python3
"""Authenticate CP72's nine pinned publisher source objects and exact theorem scope.

This is source authenticity / claim-definition checking; a separate pinned
Lean+Comparator runner must establish actual theorem verification.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SOURCE_SHA="fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb"
SOURCE_REPO="openai/math"
TARGET="OAI.EuclideanRamsey.TransitiveConsequence.subset_of_finite_transitive_ramsey"


def require(ok, why):
    if not ok:
        raise ValueError(why)


def fetch(path):
    url=("https://api.github.com/repos/openai/math/contents/"
         +urllib.parse.quote(path,safe="/")+"?ref="+SOURCE_SHA)
    headers={
      "Accept":"application/vnd.github+json",
      "X-GitHub-Api-Version":"2022-11-28",
      "User-Agent":"CMIS-CP72-source-integrity",
    }
    token=os.getenv("GITHUB_TOKEN","")
    if token:
        headers["Authorization"]="Bearer "+token
    last=None
    for i in range(3):
        try:
            req=urllib.request.Request(url,headers=headers)
            with urllib.request.urlopen(req,timeout=30) as response:
                require(response.status==200,"Non-200 source lookup "+path)
                return json.load(response)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
            last=exc
            if isinstance(exc,urllib.error.HTTPError) and exc.code not in (429,500,502,503,504):
                break
            time.sleep(i+1)
    raise ValueError("Pinned source fetch failed for "+path+": "+str(last))


def exact_scope_checks(sources):
    def text(path):
        return sources[path].decode("utf-8")
    chall=text("lean/ComparatorChallenges/EuclideanRamseyTransitive.lean")
    conf=json.loads(text("lean/ComparatorChallenges/EuclideanRamseyTransitive.json"))
    solution=text("lean/OAI/Combinatorics/EuclideanRamsey/Transitive.lean")
    main=text("lean/OAI/Combinatorics/EuclideanRamsey/Main.lean")
    paper_prefix=("preprints/A-classification-of-finite-Euclidean-Ramsey-configurations-"
                  "September-23-2026/build/sections/")
    paper=text(paper_prefix+"07-consequences.tex")
    intro=text(paper_prefix+"01-introduction.tex")
    docs=text("lean/docs/172.md")
    license_text=text("LICENSE")
    for name,part,needles in [
      ("comparator",chall,[
        "theorem subset_of_finite_transitive_ramsey",
        "(hs : 0 < s)", "(ha : Function.Injective a)",
        "(_hy : Function.Injective y)",
        "σ : Equiv.Perm (Fin t)",
        "∀ k l : Fin t, dist (y (σ k)) (y (σ l)) = dist (y k) (y l)",
        "σ i = j", "(hsub : Set.range a ⊆ Set.range y) : Ramsey a",
        "∀ r : ℕ, 2 ≤ r → ∃ D : ℕ, 1 ≤ D ∧",
        "∀ c : Space D → Fin r, ∃ b : Fin s → Space D",
        "Congruent a b", "by\n  sorry"]),
      ("publisher_solution",solution,[
        "import OAI.Combinatorics.EuclideanRamsey.Main",
        "def distancePermutationGroup",
        "theorem orbit_sum_eq", "theorem averaged_realCriterion",
        "theorem isometric_subconfiguration_ramsey",
        "theorem subset_of_finite_transitive_ramsey",
        "have htrans' : IsTransitive y",
        "have hex (i : Fin s)",
        "RealCriterion a",
        "realCriterion_fieldCriterion"]),
      ("publisher_main_dependency",main,[
        "theorem fieldCriterion_ramsey",
        "theorem classification",
        "theorem full_affine_representative",
        "theorem classification_nonempty"]),
      ("manuscript_corollary",paper,[
        "\\begin{corollary}\\label{cons:transitive}",
        "Every nonempty subset of a finite transitive Euclidean set is Ramsey.",
        "For each $h\\in H$",
        "\\frac1{|H|}",
        "gradient Gram matrix",
        "(e_i\\otimes e_i)(T)=0",
        "Proposition~\\ref{alg:equivalence}"]),
      ("manuscript_introduction",intro,[
        "\\begin{theorem}[Classification]",
        "every integer $r\\ge2$",
        "Congruence means preservation of every pairwise distance"]),
      ("family_catalogue",docs,[
        "Classification of finite Euclidean Ramsey configurations",
        "every nonempty subset of a finite transitive configuration",
        "EuclideanRamseyTransitive.lean"]),
      ("licence",license_text,["Apache License","Version 2.0"])
    ]:
        for needle in needles:
            require(needle in part,f"{name} is missing exact source-contract fragment: {needle}")
    require(conf.get("challenge_module")=="ComparatorChallenges.EuclideanRamseyTransitive",
            "Comparator challenge module mismatch")
    require(conf.get("solution_module")=="OAI.Combinatorics.EuclideanRamsey.Transitive",
            "Comparator solution module mismatch")
    require(conf.get("theorem_names")==[TARGET],"Unexpected selected theorem")
    require(set(conf.get("permitted_axioms",[]))==
            {"propext","Quot.sound","Classical.choice"},"Axiom allowance altered")
    require(conf.get("enable_nanoda") is False,"Unexpected nanoda mode")
    require("sorry" not in solution,"Imported theorem solution contains source-level sorry")
    return {
        "selected_theorem":TARGET,
        "hypotheses":["s>0","a injective","y injective",
           "distance-preserving permutation action transitive",
           "range(a) subset range(y)"],
        "conclusion":"Ramsey a with original-scale congruence and arbitrary finite colorings",
        "formal_scope":"specific transitive-subset theorem, not seven-result whole family",
        "source_to_manuscript":"pinned exact-text consistency and proof architecture checked",
        "full_lean_comparator":"SEPARATE_INDEPENDENT_WORKFLOW",
        "certification":"DEFERRED",
    }


def run(out):
    manifest=json.loads(Path("research/cp72/SOURCE_PINS.json").read_text(encoding="utf-8"))
    require(manifest["source_repo"]==SOURCE_REPO,"Source repository changed")
    require(manifest["source_commit"]==SOURCE_SHA,"Source commit changed")
    require(manifest["exact_selected_declaration"]==TARGET,"Target declaration changed")
    expected=manifest["source_files"]
    require(len(expected)==9,"Source evidence objects lost")
    require(len({z["path"] for z in expected})==9,"Duplicate source pin")
    snapshots=out/"source_snapshots"
    snapshots.mkdir(parents=True,exist_ok=True)
    data={}
    files=[]
    for item in expected:
        path=item["path"]
        obj=fetch(path)
        require(obj.get("sha")==item["git_blob_sha1"],"GitHub source object identity changed "+path)
        require(obj.get("encoding")=="base64","Source content encoding unrecognized "+path)
        raw=base64.b64decode(obj.get("content","").replace("\n",""),validate=True)
        computed=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
        require(computed==item["git_blob_sha1"],"Recomputed Git blob mismatch "+path)
        target=snapshots/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(raw)
        data[path]=raw
        files.append({
            "path":path,"git_blob_sha1":computed,
            "sha256":hashlib.sha256(raw).hexdigest(),
            "bytes":len(raw),"source_url":f"https://github.com/openai/math/blob/{SOURCE_SHA}/{path}",
            "role":item["role"]
        })
    scope=exact_scope_checks(data)
    result={
      "status":"PASS_CP72_NINE_PINNED_SOURCE_OBJECTS_AND_CONTRACT",
      "source_commit":SOURCE_SHA,"checked_object_count":len(files),
      "source_objects":files,"scope":scope,"full_family_172_credit":0,
      "separate_full_comparator_receipt_required":True,
      "does_not_certify_full_family":True
    }
    (out/"SOURCE_VALIDATION.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return result


if __name__=="__main__":
    try:
        ap=argparse.ArgumentParser()
        ap.add_argument("--output-dir",type=Path,default=Path("research/cp72/receipt"))
        args=ap.parse_args()
        run(args.output_dir)
    except Exception as exc:
        print("CP72 SOURCE HOLD: "+str(exc),file=sys.stderr)
        raise SystemExit(2)
