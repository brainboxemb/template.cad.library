"""Project CI entrypoint."""
import os
from pathlib import Path
from urllib.error import URLError
from .config import current_branch, full_selection, load_build, load_project
from .history import changed_paths, last_successful_dev_sha
from .items import discover_modules, select
from .runner import execute
from .selection import changed_selection

def selection(repo, project, branch, modules):
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    base = os.environ.get("GITHUB_BASE_REF", "")
    if branch == project.stable_branch or (event == "pull_request" and branch == project.development_branch and base == project.stable_branch):
        return full_selection(branch)
    if branch == project.development_branch:
        if event not in {"push", "workflow_dispatch"}:
            return full_selection(branch)
        token, repository, target, run_id = (os.environ.get(key, "") for key in ("GH_TOKEN", "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_RUN_ID"))
        if not (token and repository and target and run_id.isdigit()):
            return full_selection(branch)
        try:
            baseline = last_successful_dev_sha(repository=repository, branch=branch, token=token, current_run_id=int(run_id), target_sha=target)
        except (URLError, ValueError):
            return full_selection(branch)
        paths = changed_paths(repo, baseline, target) if baseline else None
        return changed_selection(branch=branch, paths=paths, modules=modules) if paths is not None else full_selection(branch)
    return load_build(repo, branch) or full_selection(branch)

def main():
    repo = Path.cwd()
    project = load_project(repo)
    branch = current_branch(repo)
    modules = discover_modules(repo, project)
    plan = selection(repo, project, branch, modules)
    chosen = select(modules, plan.modules)
    print("Selected modules:", ", ".join(item.id for item in chosen), flush=True)
    execute(chosen)

if __name__ == "__main__":
    main()
