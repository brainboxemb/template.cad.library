"""Check generated purpose views and durable evidence links."""
import argparse
from html import unescape
import json
from pathlib import Path
import yaml


def verify(source_root: Path, site: Path, build_scope: Path | None):
    def read(route):
        path = site / route / "index.html"
        if not path.is_file():
            raise RuntimeError(f"missing generated route: {path}")
        return unescape(path.read_text(encoding="utf-8"))

    for route, marker in (("", "cad-home"), ("docs", "Documentation"), ("docs/model-pages", "Understand verification"),
                          ("examples", "cad-model-grid"), ("verification", "cad-model-grid")):
        if marker not in read(route):
            raise RuntimeError(f"missing layout marker for {route}: {marker}")

    for model in sorted((source_root / "models").rglob("model.yml")):
        if not (model.parent / "ci.yml").is_file():
            continue
        meta = yaml.safe_load(model.read_text()) or {}
        ci = yaml.safe_load((model.parent / "ci.yml").read_text()) or {}
        purposes = meta.get("purpose", [])
        if isinstance(purposes, str):
            purposes = [purposes]
        item = ci["id"]
        for purpose, section in (("example", "examples"), ("verification", "verification")):
            route = f"{section}/{item}"
            if purpose not in purposes:
                if (site / route / "index.html").exists():
                    raise RuntimeError(f"unexpected purpose view: {route}")
                continue
            html = read(route)
            expected = ["cad-model-detail", str(meta.get("title", item)), "Build and verification"]
            order = ["expected-setup", "primary-source", "reference-code", "build-verification"]
            if not ci.get("implementations"):
                order.remove("primary-source")
            positions = [html.find(marker) for marker in order]
            if -1 in positions or positions != sorted(positions):
                raise RuntimeError(f"{route}: model reading order is incorrect: {order}")
            for implementation in ci.get("implementations", []):
                expected.append(f'{implementation["id"]} source')
            evidence = build_scope / "models" / item if build_scope else None
            if evidence and (evidence / "result.json").is_file():
                result = json.loads((evidence / "result.json").read_text())
                expected.append(json.loads((evidence / "source.json").read_text())["source_sha"])
                if (evidence / "model.png").is_file():
                    expected.append(f"/build/{build_scope.name}/models/{item}/model.png")
                if (evidence / "model.stl").is_file():
                    expected.append(f"/blob/build/{build_scope.name}/models/{item}/model.stl")
                for impl, state in result.get("implementations", {}).items():
                    impl_root = evidence / impl
                    if (impl_root / "solidcraft.json").is_file() and any(i["id"] == impl for i in ci.get("implementations", [])):
                        expected.append(f"Generated command sequence — {impl}")
                        if not html.find("cad-command-section") < html.find("reference-code"):
                            raise RuntimeError(f"{route}: generated commands must precede references")
                    if impl != ci.get("primary") and (impl_root / "model.png").is_file() and any(i["id"] == impl for i in ci.get("implementations", [])):
                        expected.append(f"/build/{build_scope.name}/models/{item}/{impl}/model.png")
                    for stage in state.get("verification_stages", {}):
                        report = f"{impl}/verification/{stage}/verification.json"
                        if (evidence / report).is_file():
                            expected.append(f"/blob/build/{build_scope.name}/models/{item}/{report}")
            for marker in expected:
                if marker not in html:
                    raise RuntimeError(f"{route}: missing rendered content: {marker}")
            for artifact in ("model.png", "model.stl", "model.sc", "solidcraft.json", "result.json"):
                if (site / route / artifact).exists():
                    raise RuntimeError(f"generated CAD artifact copied into Pages: {route}/{artifact}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--build-scope", type=Path)
    args = parser.parse_args()
    verify(args.source_root, args.site, args.build_scope)


if __name__ == "__main__":
    main()
