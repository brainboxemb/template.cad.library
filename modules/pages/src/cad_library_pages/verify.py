"""Verify generated example routes against source metadata and durable evidence."""
import argparse
import json
from pathlib import Path
import yaml


class SiteVerificationError(RuntimeError):
    pass


def _require(path: Path):
    if not path.is_file() or path.stat().st_size == 0:
        raise SiteVerificationError(f"missing generated site file: {path}")


def _public(meta):
    purpose = meta.get("purpose", [])
    return "example" in ([purpose] if isinstance(purpose, str) else purpose)


def verify(source_root: Path, site: Path, build_scope: Path | None):
    source_root, site = source_root.resolve(), site.resolve()
    build_scope = build_scope.resolve() if build_scope else None
    _require(site/"index.html")
    _require(site/"examples/index.html")
    for owner in sorted((source_root/"examples").iterdir()):
        if not owner.is_dir() or not (owner/"model.yml").is_file():
            continue
        meta = yaml.safe_load((owner/"model.yml").read_text()) or {}
        ci = yaml.safe_load((owner/"ci.yml").read_text()) or {}
        item = ci.get("id")
        route = site/"examples"/str(item)
        if not _public(meta):
            if route.exists():
                raise SiteVerificationError(f"verification-only fixture was published: {item}")
            continue
        page = route/"index.html"
        _require(page)
        html = page.read_text(encoding="utf-8")
        for expected in (str(meta.get("title", item)), str(ci.get("builder", ""))):
            if expected not in html:
                raise SiteVerificationError(f"{page}: expected rendered text {expected!r}")
        if build_scope is None:
            continue
        evidence = build_scope/"examples"/str(item)
        if not (evidence/"result.json").is_file():
            continue
        result = json.loads((evidence/"result.json").read_text())
        provenance = json.loads((evidence/"source.json").read_text())
        if result.get("status") != "pass":
            raise SiteVerificationError(f"published evidence is not passing: {item}")
        for expected in (str(result["verification_status"]), str(provenance["source_sha"])):
            if expected not in html:
                raise SiteVerificationError(f"{page}: missing evidence text {expected!r}")
        for name in ("model.stl", "result.json", "verification.json"):
            _require(route/name)
        if (evidence/"model.png").is_file():
            _require(route/"model.png")
        if (evidence/"model.sc").is_file():
            _require(route/"model.sc")
        if (evidence/"solidcraft.json").is_file():
            _require(route/"solidcraft.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--build-scope", type=Path)
    args = parser.parse_args()
    verify(args.source_root, args.site, args.build_scope)


if __name__ == "__main__":
    main()
