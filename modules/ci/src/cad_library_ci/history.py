"""Find a safe incremental baseline and changed Git paths."""

from __future__ import annotations

import json
from dataclasses import dataclass
import subprocess
from urllib import parse, request


class HistoryError(RuntimeError):
    """GitHub or Git history cannot provide a safe incremental baseline."""


@dataclass(frozen=True)
class ReusableQualification:
    pr_number: int
    qualified_source_sha: str
    run_id: int
    artifact_id: int


def _json(url: str, token: str):
    req = request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with request.urlopen(req) as response:
        return json.load(response)


def last_successful_dev_sha(
    *,
    repository: str,
    branch: str,
    token: str,
    current_run_id: int,
    target_sha: str,
    workflow_file: str = "ci.yml",
) -> str | None:
    branch_value = parse.quote(branch, safe="")
    workflow_value = parse.quote(workflow_file, safe="")
    url = (
        f"https://api.github.com/repos/{repository}/actions/workflows/"
        f"{workflow_value}/runs?branch={branch_value}&status=success&per_page=100"
    )
    runs = _json(url, token).get("workflow_runs", [])
    for run in runs:
        if run.get("id") == current_run_id:
            continue
        if run.get("event") not in {"push", "workflow_dispatch"}:
            continue
        if run.get("status") != "completed" or run.get("conclusion") != "success":
            continue
        sha = run.get("head_sha")
        if isinstance(sha, str) and sha and sha != target_sha:
            return sha
    return None


def changed_paths(repo, baseline: str, target: str) -> tuple[str, ...] | None:
    ancestor = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", baseline, target],
        check=False,
    )
    if ancestor.returncode != 0:
        return None

    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-only", baseline, target, "--"],
        check=True,
        capture_output=True,
        text=True,
    )
    return tuple(
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    )


def changed_paths_from_parent(repo, target: str) -> tuple[str, ...] | None:
    """Return one single-parent commit delta, or None for merge/root commits."""

    result = subprocess.run(
        ["git", "-C", str(repo), "rev-list", "--parents", "-n", "1", target],
        check=True,
        capture_output=True,
        text=True,
    )
    parts = result.stdout.strip().split()
    if len(parts) != 2:
        return None
    return changed_paths(repo, parts[1], target)


def changed_paths_from_base(repo, base_ref: str, target: str = "HEAD") -> tuple[str, ...] | None:
    """Return the PR delta from the remote base branch to target."""

    result = subprocess.run(
        ["git", "-C", str(repo), "merge-base", target, f"origin/{base_ref}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    baseline = result.stdout.strip()
    if not baseline:
        return None
    return changed_paths(repo, baseline, target)


def reusable_pr_qualification(
    *,
    repository: str,
    branch: str,
    token: str,
    source_sha: str,
    workflow_file: str = "ci.yml",
    artifact_name: str = "cad-qualification",
) -> ReusableQualification | None:
    """Find exact tree-identical successful PR evidence for one permanent commit."""

    repo_value = parse.quote(repository, safe="/")
    source_value = parse.quote(source_sha, safe="")
    pulls = _json(
        f"https://api.github.com/repos/{repo_value}/commits/{source_value}/pulls",
        token,
    )
    if not isinstance(pulls, list):
        return None

    candidates = []
    for pr in pulls:
        head = pr.get("head") or {}
        base = pr.get("base") or {}
        head_repo = head.get("repo") or {}
        if (
            pr.get("state") == "closed"
            and pr.get("merged_at")
            and pr.get("merge_commit_sha") == source_sha
            and base.get("ref") == branch
            and head_repo.get("full_name") == repository
            and isinstance(head.get("sha"), str)
            and head.get("sha")
        ):
            candidates.append(pr)
    if len(candidates) != 1:
        return None

    pr = candidates[0]
    pr_number = pr.get("number")
    head_sha = pr["head"]["sha"]
    if type(pr_number) is not int:
        return None

    source_commit = _json(
        f"https://api.github.com/repos/{repo_value}/git/commits/{source_value}",
        token,
    )
    head_value = parse.quote(head_sha, safe="")
    head_commit = _json(
        f"https://api.github.com/repos/{repo_value}/git/commits/{head_value}",
        token,
    )
    source_tree = (source_commit.get("tree") or {}).get("sha")
    head_tree = (head_commit.get("tree") or {}).get("sha")
    if not source_tree or source_tree != head_tree:
        return None

    workflow_value = parse.quote(workflow_file, safe="")
    runs = _json(
        f"https://api.github.com/repos/{repo_value}/actions/workflows/"
        f"{workflow_value}/runs?event=pull_request&head_sha={head_value}&per_page=100",
        token,
    ).get("workflow_runs", [])
    pr_runs = []
    for run in runs:
        pull_requests = run.get("pull_requests") or []
        if any(item.get("number") == pr_number for item in pull_requests):
            pr_runs.append(run)
    if not pr_runs:
        return None

    latest = max(pr_runs, key=lambda run: int(run.get("id") or 0))
    if (
        latest.get("status") != "completed"
        or latest.get("conclusion") != "success"
        or latest.get("head_sha") != head_sha
    ):
        return None
    run_id = latest.get("id")
    if type(run_id) is not int:
        return None

    artifacts = _json(
        f"https://api.github.com/repos/{repo_value}/actions/runs/{run_id}/artifacts"
        "?per_page=100",
        token,
    ).get("artifacts", [])
    matches = [
        artifact
        for artifact in artifacts
        if artifact.get("name") == artifact_name
        and artifact.get("expired") is False
        and type(artifact.get("id")) is int
    ]
    if len(matches) != 1:
        return None

    return ReusableQualification(
        pr_number=pr_number,
        qualified_source_sha=head_sha,
        run_id=run_id,
        artifact_id=matches[0]["id"],
    )
