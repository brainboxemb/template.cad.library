"""Project public model owners and durable implementation evidence into Hugo."""
import json
from pathlib import Path
import re
import shutil
import yaml


_ID = re.compile(r"[a-z0-9][a-z0-9_-]*")


def _purposes(meta):
    raw = meta.get("purpose", [])
    return [raw] if isinstance(raw, str) else raw


def prepare_models(source_root: Path, site: Path, build_scope: Path | None):
    owners = source_root / "models"
    if not owners.is_dir():
        return

    for model_yml in sorted(owners.rglob("model.yml")):
        owner = model_yml.parent
        ci_path = owner / "ci.yml"
        if not ci_path.is_file():
            continue
        meta = yaml.safe_load(model_yml.read_text()) or {}
        if "example" not in _purposes(meta):
            continue
        ci = yaml.safe_load(ci_path.read_text()) or {}
        item = ci.get("id")
        if not isinstance(item, str) or not _ID.fullmatch(item):
            raise ValueError(f"invalid model id: {ci_path}")

        title = str(meta.get("title", item))
        page = site / "content" / "models" / item / "index.md"
        page.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "---",
            "title: " + json.dumps(title),
            "---",
            "",
            meta.get("description", "").strip(),
            "",
            "## Build evidence",
            "",
        ]

        evidence = build_scope / "models" / item if build_scope else None
        if evidence and (evidence / "result.json").is_file():
            result = json.loads((evidence / "result.json").read_text())
            if result.get("status") != "pass" or result.get("id") != item:
                raise ValueError(f"invalid published model evidence: {item}")
            revision = json.loads((evidence / "source.json").read_text())["source_sha"]
            primary = result.get("primary")
            lines += [
                f"- Primary implementation: `{primary}`",
                f"- Build source: `{revision}`",
                "",
                "### Implementations",
                "",
            ]
            static = site / "static" / "models" / item
            for impl_id, state in sorted(result.get("implementations", {}).items()):
                lines.append(
                    f"- **{impl_id}** — {state.get('builder')}: "
                    f"build={state.get('build_status')}, "
                    f"verification={state.get('verification_status')}"
                )
                source = evidence / impl_id
                target = static / impl_id
                for rel in (
                    "model.stl",
                    "model.png",
                    "model.sc",
                    "solidcraft.json",
                    "result.json",
                    "verification/verification.json",
                ):
                    origin = source / rel
                    if origin.is_file():
                        dest = target / rel
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(origin, dest)
            for rel in ("model.stl", "model.png", "result.json", "verification/verification.json"):
                origin = evidence / rel
                if origin.is_file():
                    dest = static / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(origin, dest)
            lines += [
                "",
                f"[Primary STL](./model.stl)",
                "",
            ]
        else:
            lines.append("No published build evidence is available for this source scope.")

        page.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
