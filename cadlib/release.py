"""Default library-owned release validator used by the shared publisher."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import tomllib


_SHA = re.compile(r"^[0-9a-f]{40}$")


def validate(version: str, target_sha: str, notes_out: Path, *, root: Path = Path(".")) -> str:
    if _SHA.fullmatch(target_sha) is None:
        raise SystemExit("target SHA must be exactly 40 lowercase hex characters")

    pyproject = tomllib.loads(
        (root / "cadlib" / "pyproject.toml").read_text(encoding="utf-8")
    )
    project = pyproject["project"]
    package_version = str(project["version"])
    if package_version != version:
        raise SystemExit(
            f"package version mismatch: expected {version}, found {package_version}"
        )

    name = str(project["name"])
    notes_out.write_text(
        f"{name} {version}\n\nRelease of exact source `{target_sha}`.\n",
        encoding="utf-8",
    )
    return name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--target-sha", required=True)
    parser.add_argument("--notes-out", type=Path, required=True)
    args = parser.parse_args()
    name = validate(args.version, args.target_sha, args.notes_out)
    print(f"validated {name} {args.version} at {args.target_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
