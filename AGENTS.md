# Agent guidance

Read `docs/plan.md`, `docs/design.md` and `docs/manual.md` before changing the repository.

Normal product work starts from `dev` on a temporary branch. Optional experimental work starts from permanent `exp` on a temporary branch; sync `dev -> exp` and integrate completed experiments through `exp -> dev`. Never promote `exp` directly to `main`. Set `build.yml.branch` to the actual branch and select the necessary library,
modules and **physical model owners**. API probes are a separate explicit
selection axis: keep `api_probes: []` unless the branch is deliberately
developing/proving an API probe. Squash normal temporary branches into `dev`; promote `dev` to `main` with a merge commit only when an explicit product stabilization is intended.

Release preparation is separate: create `release/vX.Y.Z` from stable `main` and change only `CHANGELOG.md` and the `project.version` value in `cadlib/pyproject.toml`. Merge that short-lived release branch directly to `main` through `/merge`. Release-only stable commits reuse the previous full `build/main` product qualification; they must not rebuild or replace unchanged model evidence. After publication, synchronize the stable-only release commit back with `main -> dev`. Never rebase the shared permanent `dev` branch.

## Mandatory merge execution rule

This repository deliberately does **not** let an agent choose the merge method.

For every source-branch integration:

- short-lived branch -> `dev` or `exp`;
- `dev` -> `exp` and `exp` -> `dev`;
- `dev` -> `main`;
- exceptional `main` -> `dev`;

an agent MUST post `/merge` on the pull request and let
`.github/workflows/merge-policy.yml` perform the merge.

An agent MUST NOT:

- call GitHub's direct merge API;
- enable or use auto-merge;
- use a UI/manual merge fallback;
- manually choose squash, merge or rebase.

If `/merge` fails, stop the integration and repair the merge-policy path.
Never bypass the policy.

A genuinely conflicted **direct permanent-branch** PR may use the policy-owned
reviewed `/merge-resolved` recovery only after a separate same-repository
`resolve/*` PR has exposed the exact combined tree and passed central CI.
The resolution PR is review-only and must never be merged normally. Do not use
this path for temporary, release or governance PRs.

The repository root for physical CAD ownership is `models/`, matching
`template.cad.model-project`. Do not reintroduce `examples/` as an execution
owner root. Temporary executable API/design evidence belongs under
`api-probes/<id>/probe.yml`; probes are opt-in through root `build.yml`, are
off in normal full permanent builds, and are not Pages/model-catalogue owners.

One `models/<id>/` directory is one physical owner. Multiple engine implementations belong under that owner and are declared in its `ci.yml`. Do not create sibling owners such as `model-build123d` or `model-solidcraft` solely to represent engines.

`model.yml.purpose` may contain multiple purposes. Supported values are `example` and `verification`; `[example, verification]` is valid.

Builders, verifier adapters and previews declare runtime capabilities locally. Central CI schedules owners, implementation tasks, verification stages and runtime roles but must not contain engine-specific branches.

A model may declare multiple named verification stages. Stage evidence must remain isolated below the stage id; a later runtime may not overwrite an earlier stage report. Keep the legacy single `verification:` mapping backward compatible.

Preview is presentation, not verification. When enabled it runs only after every applicable verification stage for that implementation has passed.

Preserve the two released runtime roles; do not add a third verification image.

Physical model dependencies name owner ids. Selection closes over downstream dependents.

Reusable verification belongs in `modules/verification/`; owner-specific built-artifact expectations stay in `models/<id>/verification/`. Optional `models/<id>/tests/` are owner-local source/compiler contract tests and run only with that selected owner; do not move them into `cadlib/tests` unless the contract is genuinely package-wide.

Pages is separate from CAD CI. Hugo reads source metadata and durable build evidence only. Project model purposes into Examples and Verification without duplicating physical owners or generated artifacts. Keep the established Hextra/CAD presentation baseline.
