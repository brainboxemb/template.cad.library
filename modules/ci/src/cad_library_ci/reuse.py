"""Materialize reusable PR qualification for one permanent source commit."""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import shutil
from urllib import error, parse, request
import zipfile

from .config import ConfigError, load_project
from .history import _json, reusable_pr_qualification


def _write_output(path: Path, **values):
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def _download_artifact(repository: str, artifact_id: int, token: str) -> bytes:
    repo_value = parse.quote(repository, safe="/")
    req = request.Request(
        f"https://api.github.com/repos/{repo_value}/actions/artifacts/"
        f"{artifact_id}/zip",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with request.urlopen(req) as response:
        return response.read()


def _extract_zip(data: bytes, candidate: Path):
    candidate.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            path = Path(info.filename)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("qualification artifact contains unsafe path")
        archive.extractall(candidate)


def _tree_sha(repository: str, sha: str, token: str) -> str:
    repo_value = parse.quote(repository, safe="/")
    sha_value = parse.quote(sha, safe="")
    commit = _json(
        f"https://api.github.com/repos/{repo_value}/git/commits/{sha_value}",
        token,
    )
    tree = (commit.get("tree") or {}).get("sha")
    if not isinstance(tree, str) or not tree:
        raise ValueError("cannot resolve qualification tree")
    return tree


def _rebind_plan(
    candidate: Path,
    *,
    source_sha: str,
    qualified_source_sha: str,
    pr_number: int,
    run_id: int,
):
    path = candidate / "build-plan.json"
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            "qualification artifact has no valid build-plan.json"
        ) from exc
    if (
        plan.get("schema") != 2
        or plan.get("source_sha") != qualified_source_sha
    ):
        raise ValueError("qualification artifact provenance mismatch")

    plan["source_sha"] = source_sha
    plan["qualified_source_sha"] = qualified_source_sha
    plan["qualification_reused"] = True
    plan["qualification_pr"] = pr_number
    plan["qualification_run_id"] = run_id
    path.write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def materialize(
    *,
    repo: Path,
    repository: str,
    branch: str,
    source_sha: str,
    token: str,
    candidate: Path,
) -> dict:
    project = load_project(repo)
    if branch not in project.reuse_pr_branches:
        return {"reuse": False, "reason": "branch-not-configured"}

    evidence = reusable_pr_qualification(
        repository=repository,
        branch=branch,
        token=token,
        source_sha=source_sha,
    )
    if evidence is None:
        return {"reuse": False, "reason": "no-exact-pr-evidence"}

    shutil.rmtree(candidate, ignore_errors=True)
    data = _download_artifact(repository, evidence.artifact_id, token)
    _extract_zip(data, candidate)

    # Re-check exact tree identity after the artifact has been materialized.
    if _tree_sha(repository, source_sha, token) != _tree_sha(
        repository,
        evidence.qualified_source_sha,
        token,
    ):
        raise ValueError("source tree changed during qualification reuse")

    _rebind_plan(
        candidate,
        source_sha=source_sha,
        qualified_source_sha=evidence.qualified_source_sha,
        pr_number=evidence.pr_number,
        run_id=evidence.run_id,
    )
    return {
        "reuse": True,
        "reason": "tree-identical-green-pr",
        "qualified_source_sha": evidence.qualified_source_sha,
        "pr_number": evidence.pr_number,
        "run_id": evidence.run_id,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--repository", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--github-output", type=Path, required=True)
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        _write_output(
            args.github_output,
            reuse="false",
            reason="missing-token",
        )
        return

    try:
        result = materialize(
            repo=args.repo,
            repository=args.repository,
            branch=args.branch,
            source_sha=args.source_sha,
            token=token,
            candidate=args.candidate,
        )
    except ConfigError:
        raise
    except (
        error.URLError,
        OSError,
        ValueError,
        KeyError,
        zipfile.BadZipFile,
    ) as exc:
        shutil.rmtree(args.candidate, ignore_errors=True)
        _write_output(
            args.github_output,
            reuse="false",
            reason="reuse-fallback",
        )
        print(f"Reusable PR qualification unavailable: {exc}")
        return

    values = {
        "reuse": "true" if result["reuse"] else "false",
        "reason": result["reason"],
    }
    if result["reuse"]:
        values.update(
            qualified_source_sha=result["qualified_source_sha"],
            pr_number=result["pr_number"],
            run_id=result["run_id"],
        )
    _write_output(args.github_output, **values)


if __name__ == "__main__":
    main()
