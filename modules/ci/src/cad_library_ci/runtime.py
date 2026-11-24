"""Container dispatcher: build in compatible interpreter batches, verify in parent."""
import argparse
import importlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import traceback


def resolve(entry):
    module, function = entry.split(":", 1)
    return getattr(importlib.import_module(module), function)


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def describe_error(exc):
    return "".join(traceback.format_exception_only(type(exc), exc)).strip()


def build_row(row, output):
    artifact = output / "examples" / row["id"] / "model.stl"
    try:
        resolve(row["build_entry"])(Path(row["source"]), artifact)
        if not artifact.is_file() or not artifact.stat().st_size:
            raise RuntimeError("builder did not produce a nonempty STL")
        return {"status": "pass"}
    except Exception as exc:
        return {"status": "error", "error": describe_error(exc)}


def engine_batch(rows, output, interpreter):
    """Run all rows for one isolated interpreter in a single child process."""
    with tempfile.TemporaryDirectory(prefix="cad-engine-") as tmp:
        root = Path(tmp)
        manifest, report = root / "manifest.json", root / "report.json"
        write_json(manifest, {"schema": 1, "examples": rows})
        try:
            completed = subprocess.run(
                [interpreter, "-m", "cad_library_ci.runtime", "--manifest", str(manifest),
                 "--output", str(output), "--build-report", str(report)],
                check=False, timeout=1500,
            )
            payload = json.loads(report.read_text())
            if payload.get("schema") != 1 or set(payload["results"]) != {row["id"] for row in rows}:
                raise RuntimeError("invalid engine batch report")
            results = payload["results"]
            if any(not isinstance(r, dict) or r.get("status") not in {"pass", "error"} for r in results.values()):
                raise RuntimeError("invalid engine result")
            expected = 0 if all(r["status"] == "pass" for r in results.values()) else 1
            if completed.returncode != expected:
                raise RuntimeError(f"engine report disagrees with process exit {completed.returncode}")
            return results
        except Exception as exc:
            return {row["id"]: {"status": "error", "error": describe_error(exc)} for row in rows}


def execute(manifest, output):
    if manifest.get("schema") != 1:
        raise ValueError("unsupported manifest")
    groups, built = {}, {}
    rows = manifest["examples"]
    for row in rows:
        target = output / "examples" / row["id"]
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        interpreter = row.get("engine_python")
        if interpreter:
            groups.setdefault(interpreter, []).append(row)
        else:
            built[row["id"]] = build_row(row, output)
    for interpreter, group in groups.items():
        built.update(engine_batch(group, output, interpreter))

    results = []
    for row in rows:
        item_id = row["id"]
        target = output / "examples" / item_id
        artifact = target / "model.stl"
        build = built[item_id]
        result = {"id": item_id, "builder": row["builder"], "runtime": manifest["image"],
                  "build_status": build["status"], "verification_status": None, "status": "error"}
        if build["status"] == "pass":
            try:
                report = resolve(row["verify_entry"])(row["adapter"], artifact, Path(row["definition"]), target / "verification", verification_id=item_id)
                status = report["status"]
                if status not in {"pass", "fail", "error"}:
                    raise ValueError(f"invalid verification status: {status}")
                result["verification_status"] = status
                result["status"] = status
                if status == "pass" and row.get("preview_entry"):
                    result["preview_status"] = "error"
                    resolve(row["preview_entry"])(row["preview_adapter"], artifact, target)
                    result["preview_status"] = "pass"
            except Exception as exc:
                result["error"] = describe_error(exc)
                result["status"] = "error"
                if result.get("preview_status") != "error":
                    result["verification_status"] = "error"
        else:
            result["error"] = build.get("error")
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
    parser.add_argument("--build-report", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    if args.build_report:
        if manifest.get("schema") != 1:
            raise ValueError("unsupported engine manifest")
        results = {row["id"]: build_row(row, args.output) for row in manifest["examples"]}
        write_json(args.build_report, {"schema": 1, "results": results})
        return 0 if all(r["status"] == "pass" for r in results.values()) else 1
    return execute(manifest, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
