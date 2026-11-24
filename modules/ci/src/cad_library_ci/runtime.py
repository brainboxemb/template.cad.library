"""Container batch dispatcher. Builder and verifier behavior lives in modules."""
import argparse
import importlib
import json
from pathlib import Path
import shutil
import traceback


def resolve(entry):
    module, function = entry.split(":", 1)
    return getattr(importlib.import_module(module), function)


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def execute(manifest, output):
    if manifest.get("schema") != 1:
        raise ValueError("unsupported manifest")
    results = []
    for row in manifest["examples"]:
        item_id = row["id"]
        target = output / "examples" / item_id
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        artifact = target / "model.stl"
        result = {"id": item_id, "builder": row["builder"], "runtime": manifest["image"], "build_status": "error", "verification_status": None, "status": "error"}
        try:
            resolve(row["build_entry"])(Path(row["source"]), artifact)
            result["build_status"] = "pass"
            report = resolve(row["verify_entry"])(row["adapter"], artifact, Path(row["definition"]), target / "verification", verification_id=item_id)
            result["verification_status"] = report["status"]
            result["status"] = report["status"]
        except Exception as exc:
            result["error"] = "".join(traceback.format_exception_only(type(exc), exc)).strip()
            if result["build_status"] == "pass":
                result["verification_status"] = "error"
        write_json(target / "result.json", result)
        results.append(result)
        print(f"{item_id}: {result['status']}", flush=True)
    status = "pass" if results and all(r["status"] == "pass" for r in results) else "fail"
    write_json(output / f"batch-{manifest['runtime']}.json", {"schema": 1, "status": status, "results": results})
    return 0 if status == "pass" else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    return execute(json.loads(args.manifest.read_text()), args.output)


if __name__ == "__main__":
    raise SystemExit(main())
