# Agent guidance

Read docs/plan.md and docs/manual.md before changing the repository.

Work from a temporary branch based on dev; set build.yml.branch to the actual branch and select the necessary items/tasks. Squash temporary branches into dev. Promote dev to main using a merge commit. Merge main back only for actual stable-only content. Never clean up main, dev, build or gh-pages.

Internal Python capabilities own ci.yml, pyproject.toml, src/ and tests/ under modules/<id>/. Keep workflows thin and run capabilities directly from source. No central list of modules.

Matching work-branch build.yml controls selection; stale selections are ignored. Dev selects changes since the last successful integration CI run, including declared impact. Main and dev-to-main PRs run full. Cancel superseded runs. Keep generated output below build/.

Pages is separate from CI; publish main at / and dev at /dev/ on gh-pages. Hugo consumes documentation, not CAD execution. Never put release evidence in Pages. Forge and examples verification are planned separate owners; do not create model-project-specific workarounds.
