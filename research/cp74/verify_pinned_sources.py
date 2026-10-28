#!/usr/bin/env python3
"""CP74 read-only verification of 25 original publisher Git blobs and theorem scope.

Not a proof checker. Full selected theorem acceptance is a separate GitHub
Lean/Comparator action; source-file pinning alone grants zero theorem credit.
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

PIN="fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb"
DECL="OAI.GrahamSpherical.full_main"


def require(v,msg):
    if not v:raise ValueError(msg)


def github_content(path):
    url="https://api.github.com/repos/openai/math/contents/"+urllib.parse.quote(path,safe="/")+"?ref="+PIN
    headers={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28",
             "User-Agent":"CMIS-CP74-original-source-hash-verification"}
    if os.getenv("GITHUB_TOKEN"):headers["Authorization"]="Bearer "+os.getenv("GITHUB_TOKEN")
    err=None
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers=headers)
            with urllib.request.urlopen(req,timeout=28) as f:
                require(f.status==200,"Non-200 GitHub source response")
                return json.load(f)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as ex:
            err=ex
            if isinstance(ex,urllib.error.HTTPError) and ex.code not in (429,500,502,503,504):break
            time.sleep(1+attempt)
    raise RuntimeError(f"Pinned source fetch failed: {path}: {err}")


def exact_scope(data):
    def get(path):return data[path].decode("utf-8")
    prefix="lean/OAI/Combinatorics/SphericalRamsey/"
    c=get("lean/ComparatorChallenges/GrahamSpherical.lean")
    conf=json.loads(get("lean/ComparatorChallenges/GrahamSpherical.json"))
    model=get(prefix+"Model.lean")
    srcmain=get(prefix+"Main.lean")
    param=get(prefix+"Parameter.lean")
    wc=get(prefix+"WitnessCoordinates.lean")
    color=get(prefix+"Coloring.lean")
    mono=get(prefix+"MonochromaticObstruction.lean")
    energy=get(prefix+"EnergyIdentity.lean")
    copy=get(prefix+"CopyInvariant.lean")
    reald=get(prefix+"RealDerivation.lean")
    geom=get("preprints/A-classification-of-finite-Euclidean-Ramsey-configurations-September-23-2026/build/sections/07-consequences.tex")
    docs=get("lean/docs/172.md")
    criteria=[
      ("original_challenge",c,[
          "theorem full_main : Specification.FullAuthoredResult := by",
          "witness.ncard = 12",
          "witness ⊆ Metric.sphere",
          "∀ n : ℕ, 0 < n → ∃ color : Point n → Fin 50, AvoidsCopy witness color",
          "¬ EuclideanRamsey witness","by\n  sorry"]),
      ("original_model",model,[
          "def parameter : ℝ", "(m + 1).factorial",
          "def weight (i : Label) : ℤ := if i.1 = 2 then -2 else 1",
          "def EuclideanRamsey","def AvoidsCopy","Fin 3 × Fin 4"]),
      ("original_solution",srcmain,[
          "theorem exists_common_derivation_colorings",
          "theorem full_main : Specification.FullAuthoredResult := by",
          "exists_real_derivation parameter",
          "parameter_transcendental",
          "witness_ncard witness_subset_sphere",
          "energyColor (derivationEnergy",
          "exact ⟨energyColor"]),
      ("liouville",param,[
          "theorem parameter_transcendental",
          "theorem parameter_bounds",
          "liouvilleNumber 10",
          "theorem parameter_eq_liouville_sub"]),
      ("twelve_point_geometry",wc,[
          "theorem vertex_injective","theorem vertex_norm",
          "theorem witness_subset_sphere","theorem witness_ncard"]),
      ("color_obstruction",color,[
          "theorem rounding_obstruction",
          "Int.floor (3 * e i)",
          "50","(16 : ℝ) <",
          "(S : ℝ) < (32 : ℝ)"]),
      ("color_definition",mono,[
          "def energyColor","Int.floor (3 * e y)",
          "theorem energyColor_avoids_of_invariant"]),
      ("energy_identity",energy,[
          "theorem weighted_coordinate_square",
          "theorem weighted_affine_derivation_energy",
          "= 8 := by"]),
      ("isometric_copies",copy,[
          "theorem weighted_copy_derivation_energy",
          "(hf : Isometry f)",
          "theorem derivationColor_avoids"]),
      ("real_derivation",reald,[
          "theorem exists_real_derivation",
          "Transcendental ℚ a",
          "∃ D : Derivation ℤ ℝ ℝ"]),
      ("manuscript",geom,[
          "\\begin{proposition}\\label{cons:twelve}",
          "Liouville's constant",
          "weighted cancellation",
          "the three augmented moment identities",
          "right side $8"]),
      ("family_docs",docs,[
          "twelve-point set on the unit circle",
          "fifty-color obstruction",
          "GrahamSpherical.lean"]),
    ]
    for name,body,parts in criteria:
        for part in parts:
            require(part in body,f"Missing exact original scope {name}: {part}")
    require(conf.get("challenge_module")=="ComparatorChallenges.GrahamSpherical","Comparator challenge module mismatch")
    require(conf.get("solution_module")=="OAI.Combinatorics.SphericalRamsey.Main","Comparator solution module mismatch")
    require(conf.get("theorem_names")==[DECL],"Comparator selected theorem mismatch")
    require(set(conf.get("permitted_axioms",[]))=={"propext","Quot.sound","Classical.choice"},
            "Unexpected extra axiom permission")
    require(conf.get("enable_nanoda") is False,"Changed verifier mode")
    require("sorry" not in srcmain and "admit" not in srcmain,"Main solution has placeholder")
    require("def EuclideanRamsey" in c,"Missing Ramsey definition")
    require("∀ r : ℕ, 0 < r → ∃ n : ℕ, 0 < n ∧" in c,"Ramsey quantifier order changed")
    require("∀ color : Point n → Fin r," in c,"Universal coloring hypothesis changed")
    return {
      "selected_original_theorem":DECL,
      "exact_fifty_color_scope":True,
      "point_count":12,
      "unit_circle":"at origin and radius 1",
      "all_positive_dimensions":"forall n>0 exists coloring into Fin50",
      "unrestricted_colorings":True,
      "source_proof_energy":"nonconstructive real derivation and floor(3*energy) modulo50",
      "previous_CP71_CP73_credit_unmodified":True,
      "optional_16_color_consequence_in_original_source":False,
      "complete_Lean_verification":"SEPARATE_GITHUB_COMPARATOR"
    }


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--output-dir",type=Path,default=Path("research/cp74/receipt"))
    args=cli.parse_args()
    man=json.loads(Path("research/cp74/SOURCE_PINS.json").read_text())
    require(man["source_repository"]=="openai/math" and man["source_commit"]==PIN,
            "Unexpected corpus origin")
    require(man["target_declaration"]==DECL,"Unexpected original theorem")
    pins=man["source_files"]
    require(len(pins)==25 and len({x["path"] for x in pins})==25,"25 object source identity incomplete")
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    snapshots=out/"source_snapshots";snapshots.mkdir(parents=True,exist_ok=True)
    data={};verified=[]
    for obj in pins:
        path=obj["path"]
        remote=github_content(path)
        require(remote.get("sha")==obj["git_blob_sha1"],"Publisher Git blob changed "+path)
        require(remote.get("encoding")=="base64","Unexpected GitHub content encoding "+path)
        raw=base64.b64decode(remote["content"].replace("\n",""),validate=True)
        computed=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        require(computed==obj["git_blob_sha1"],"Recomputed source blob differs "+path)
        target=snapshots/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        data[path]=raw
        verified.append({"path":path,"git_blob_sha1":computed,"sha256":hashlib.sha256(raw).hexdigest(),
                         "bytes":len(raw),"role":obj["role"],
                         "source_url":"https://github.com/openai/math/blob/"+PIN+"/"+path})
    result={
        "status":"PASS_CP74_25_PINNED_PUBLISHER_SOURCES_AND_CLAIM_CONTRACT",
        "checked_source_files":len(verified),"pinned_source_commit":PIN,
        "original_objects":verified,"source_contract":exact_scope(data),
        "source_authentication_is_not_full_theorem_proof":True,
        "new_family_wide_validation":0,"external_certification":"DEFERRED"
    }
    txt=json.dumps(result,indent=2,sort_keys=True)+"\n"
    (out/"SOURCE_VALIDATION.json").write_text(txt)
    print(txt)


if __name__=="__main__":
    try:main()
    except Exception as e:
        print("CP74 SOURCE HOLD: "+str(e),file=sys.stderr)
        raise SystemExit(2)
