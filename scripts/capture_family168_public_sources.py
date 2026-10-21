#!/usr/bin/env python3
"""Archive only public pinned Family 168 inputs; this does not verify a theorem.

AI-assisted engineering. The separate Comparator/kernel receipt controls credit.
The mathematical source is read from its exact git object, never the worktree.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path

PIN = "fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb"
ROOT_MODULE = "OAI.RepresentationTheory.KazhdanLusztig.Invariance"
PAPER = "preprints/Combinatorial-Invariance-of-Kazhdan-Lusztig-Polynomials-September-24-2026"
EXTRAS = ["lean/ComparatorChallenges/KLInvariance.json", "lean/ComparatorChallenges/KLInvariance.lean", "lean/docs/168.md", "lean/lean-toolchain", "lean/lake-manifest.json"]

def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE)

def imports(text: str) -> list[str]:
    # Strip nested Lean comments before collecting ordinary and public imports.
    out, i, depth = [], 0, 0
    while i < len(text):
        if text[i:i+2] == "/-": depth += 1; i += 2
        elif depth and text[i:i+2] == "-/": depth -= 1; i += 2
        elif depth:
            if text[i] == "\n": out.append("\n")
            i += 1
        elif text[i:i+2] == "--":
            j = text.find("\n", i); i = len(text) if j < 0 else j
        else: out.append(text[i]); i += 1
    if depth: raise ValueError("Unterminated Lean comment")
    result = []
    for match in re.finditer(r"(?m)^\s*(?:public\s+)?import\s+([^\n]+)", "".join(out)):
        result.extend(match.group(1).split())
    return result

def capture(repo: Path, dest: Path) -> dict:
    if dest.exists(): raise FileExistsError(f"Refusing to overwrite {dest}")
    commit = git(repo, "rev-parse", f"{PIN}^{{commit}}").decode().strip()
    if commit != PIN: raise ValueError("Source commit mismatch")
    paths = set(git(repo, "ls-tree", "-r", "--name-only", PIN).decode().splitlines())
    if any(p not in paths for p in EXTRAS): raise ValueError("Required exact public input missing")
    pending, seen, external = [ROOT_MODULE], {}, set()
    data_by_path = {}
    while pending:
        mod = pending.pop()
        if mod in seen: continue
        if not re.fullmatch(r"[\w.]+", mod): raise ValueError(f"Unexpected module syntax: {mod}")
        path = "lean/" + mod.replace(".", "/") + ".lean"
        if path not in paths:
            if mod.startswith("OAI."): raise ValueError(f"Missing project module: {mod}")
            external.add(mod); continue
        data = git(repo, "show", f"{PIN}:{path}")
        deps = imports(data.decode("utf-8"))
        seen[mod] = deps; data_by_path[path] = data
        pending.extend(deps)
    selected = set(EXTRAS) | {p for p in paths if p.startswith(PAPER + "/")} | set(data_by_path)
    if not any(p.startswith(PAPER + "/") for p in selected): raise ValueError("Original manuscript absent")
    dest.mkdir(parents=True)
    records = []
    for path in sorted(selected):
        data = data_by_path.get(path)
        if data is None: data = git(repo, "show", f"{PIN}:{path}")
        expected = git(repo, "rev-parse", f"{PIN}:{path}").decode().strip()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if actual != expected: raise ValueError(f"Git blob mismatch: {path}")
        target = dest / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        records.append({"path": path, "bytes": len(data), "git_blob": actual, "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {"source_commit": PIN, "root_module": ROOT_MODULE,
                "local_module_count": len(seen), "imports": dict(sorted(seen.items())),
                "external_import_names": sorted(external), "files": records,
                "scope": "Pinned public source capture only, not a proof verdict or complete external dependency archive."}
    (dest / "PUBLIC_SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

if __name__ == "__main__":
    root = Path.cwd()
    result = capture(root / ".cmis-work/openai-math", root / "cmis_family168_public_sources")
    print(json.dumps({"source_commit": PIN, "local_modules": result["local_module_count"], "files": len(result["files"])}))
