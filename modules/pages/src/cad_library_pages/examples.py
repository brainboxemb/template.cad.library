"""Adapt library-owned metadata and durable build output to Hugo page bundles."""
import json
from pathlib import Path
import re
import shutil
import yaml


def prepare_examples(source_root: Path, site: Path, build_scope: Path | None):
    owners = source_root / "examples"
    if not owners.is_dir():
        return
    seen = set()
    for owner in sorted(owners.iterdir()):
        if not (owner / "model.yml").is_file():
            continue
        meta = yaml.safe_load((owner / "model.yml").read_text())
        purpose = meta.get("purpose", [])
        if "example" not in ([purpose] if isinstance(purpose, str) else purpose):
            continue
        ci = yaml.safe_load((owner / "ci.yml").read_text())
        item = ci["id"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", item) or item in seen:
            raise ValueError(f"invalid or duplicate example id: {item}")
        seen.add(item)
        bundle = site / "content" / "examples" / item
        bundle.mkdir(parents=True, exist_ok=True)
        source = owner / ci["source"]
        if not source.resolve().is_relative_to(owner.resolve()) or not source.is_file():
            raise ValueError(f"missing or unsafe example source: {source}")
        if source.suffix == ".py":
            shutil.copy2(source, bundle / "source.py")
        else:
            shutil.copy2(source, bundle / "source.txt")
        shutil.copy2(owner / "model.yml", bundle / "model.yml")
        shutil.copy2(owner / "ci.yml", bundle / "ci.yml")
        if (owner / "page.md").is_file():
            shutil.copy2(owner / "page.md", bundle / "background.md")
        data = {"title": str(meta.get("title", item)), "weight": meta.get("priority", 100),
                "params": {"model": meta, "builder": ci["builder"], "sourcepath": ci["source"],
                           "result": {"status": "unavailable"}, "provenance": {}, "checks": []}}
        evidence = build_scope / "examples" / item if build_scope else None
        if evidence and (evidence / "result.json").is_file():
            result = json.loads((evidence / "result.json").read_text())
            if result.get("status") != "pass" or result.get("id") != item:
                raise ValueError(f"invalid published evidence: {item}")
            provenance = json.loads((evidence / "source.json").read_text())
            report = json.loads((evidence / "verification/verification.json").read_text())
            data["params"].update(result=result, provenance=provenance, checks=report.get("checks", []))
            for name in ("result.json", "source.json", "model.stl", "model.step", "model.sc", "model.png", "preview.json", "solidcraft.json"):
                if (evidence / name).is_file():
                    shutil.copy2(evidence / name, bundle / name)
            shutil.copy2(evidence / "verification/verification.json", bundle / "verification.json")
        # JSON front matter avoids ad-hoc Markdown assembly; layouts own all presentation.
        (bundle / "index.md").write_text(json.dumps(data, indent=2) + "\n\n", encoding="utf-8")
