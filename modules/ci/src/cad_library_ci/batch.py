"""Run selected examples once per CAD runtime, without engine-specific branches."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

from .config import ConfigError, mapping


def run_batches(repo, project, modules, examples, output):
    if not examples:
        return
    runtimes = mapping(repo / "ci.yml").get("runtimes", {})
    by_id = {m.id: m for m in modules}
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    groups = {}
    for example in examples:
        groups.setdefault(example.runtime, []).append(example)
    failed = False
    for role, rows in sorted(groups.items()):
        image = runtimes.get(role, {}).get("image")
        if not isinstance(image, str) or ":" not in image or image.endswith(":latest"):
            raise ConfigError(f"missing pinned runtime: {role}")
        source_paths = {"/repo/modules/ci/src"}
        records = []
        for e in rows:
            for dependency in e.dependencies:
                if dependency == "cadlib":
                    source_paths.add("/repo/cadlib/src")
                else:
                    path = by_id[dependency].root.relative_to(repo)
                    source_paths.add(f"/repo/{path.as_posix()}/src")
            records.append({
                "id": e.id, "builder": e.builder, "build_entry": e.build_entry,
                "verify_entry": e.verify_entry, "adapter": e.adapter,
                "source": "/repo/" + e.source.relative_to(repo).as_posix(),
                "definition": "/repo/" + e.definition.relative_to(repo).as_posix(),
                "preview_entry": e.preview_entry, "preview_adapter": e.preview_adapter,
            })
        manifest = {"schema": 1, "runtime": role, "image": image, "examples": records}
        with tempfile.TemporaryDirectory(prefix="cad-batch-") as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            command = ["docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}",
                "-e", "HOME=/tmp", "-e", "PYTHONDONTWRITEBYTECODE=1",
                "-e", "PYTHONPATH=" + ":".join(sorted(source_paths)),
                "-v", f"{repo.resolve()}:/repo:ro",
                "-v", f"{output}:/output", "-v", f"{path}:/manifest.json:ro",
                "-w", "/repo", image, "python", "-m", "cad_library_ci.runtime",
                "--manifest", "/manifest.json", "--output", "/output"]
            result = subprocess.run(command, check=False, timeout=1800)
            failed |= result.returncode != 0
    if failed:
        raise RuntimeError("one or more CAD example batches failed")
