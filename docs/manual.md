# CAD library template manual

## Branches and selection

Normal product branches are based on `dev`; squash them into `dev`. Promote `dev` to `main` with a merge commit only when an explicit product stabilization is intended. Release branches are different: create `release/vX.Y.Z` from stable `main`, merge that short-lived branch directly to `main`, publish from the resulting stable commit, then synchronize `main -> dev` with a merge commit. Do not rebase shared permanent branches. Permanent `workflow_dispatch` runs explicitly qualify the current checked-out permanent branch head; they do not trust an event SHA that may lag immediately after a merge. Durable publication still fails closed if that branch moves again during the run.

Root `build.yml` is an exact branch-local execution plan:

```yaml
schema: 1
branch: issue/25-multi-stage-verification
modules: [ci, verification]
library: false
models: [simple-box]
api_probes: []
tasks: [test]
```

Use `modules: all` or `models: all` for full selection. API probes are
different: they are off by default, including full permanent builds. Select
them only while developing the API with `api_probes: [<id>]` (or explicitly
`api_probes: all`). Product-changing `main` commits and `dev -> main` promotions run full. A validated release-metadata-only `main` commit runs only the library + release capability and preserves the previous full stable CAD evidence. This classification is identical whether the permanent stable run arrived as a normal `push` or as the merge-policy `workflow_dispatch`; the source commit itself must still be a single-parent metadata-only delta. Permanent `dev` and `exp` runs select changes since the last successful integration run; missing history falls back to full.

### Qualification policy

Repository-wide cost policy belongs in root `ci.yml`, not in individual
feature branches. The template baseline uses:

```yaml
qualification:
  pull_requests:
    docs_only:
      prefixes:
        - docs/
      modules:
        - ci
  permanent:
    reuse_pr_qualification:
      branches:
        - dev
        - exp
```

A PR is docs-only only when **every** changed path in the complete base→head
delta is below one of the configured prefixes. It then ignores branch-local
`build.yml`, runs only the configured lightweight modules, and selects no
library, model owners or API probes. A mixed docs/source PR follows normal
selection. Permanent-lane promotion and release PR rules are evaluated first
and remain stronger.

After a normal temporary PR is merged into a configured permanent lane, the
permanent build first looks for the exact PR qualification artifact. It reuses
that artifact only when GitHub identifies one merged same-repository PR for the
source commit, the newest PR-specific central CI run is green, and the permanent
commit and PR head have exactly the same Git tree. The durable build-plan then
records the permanent `source_sha` plus `qualified_source_sha`, PR number and
CI run id. If any check fails or the artifact is missing/expired, the workflow
simply executes ordinary CAD-CI.

Do not enable reuse for `main` merely to make releases faster. Stable
qualification keeps its existing full/release-only rules unless a separately
reviewed policy changes them.

Pages is dispatched after durable publication and is intentionally
asynchronous. Do not block compiler/IR issue completion on Pages deployment
unless the work itself changes the public site contract.

### Merge execution

The merge shape is policy-owned, not agent-selected. For every source-branch integration, post `/merge` on the pull request and let `.github/workflows/merge-policy.yml` execute the merge.

The policy chooses:

- normal short-lived branch -> `dev` or `exp`: squash;
- `dev` -> `exp` synchronization and `exp` -> `dev` integration: merge commit, full PR qualification;
- `release/*` -> `main`: squash;
- explicit product promotion `dev` -> `main`: merge commit;
- stable synchronization `main` -> `dev`: merge commit.

A normal feature/issue/fix/docs/chore branch may not target `main` directly.

`release/*` is also a temporary branch class. Post-merge cleanup deletes it
after a successful same-repository merge to `main`; normal temporary branches
are deleted after their successful merge to `dev` or `exp`. The manual sweep uses the
same target rule, so a release branch is never considered safely merged merely
because it reached development.

Do not use the direct GitHub merge API, auto-merge, a UI/manual fallback, or manual squash/merge/rebase selection. If `/merge` fails, repair the policy path rather than bypassing it.

Repeating `/merge` after a pull request has already been merged is an idempotent successful no-op. A pull request that is closed without being merged is still rejected.


The green-CI gate uses the newest `pull_request` run of
`.github/workflows/ci.yml` for the exact head SHA and pull request. Historical
failed runs on the same commit do not permanently poison a replacement PR once
a newer qualification succeeds. Conversely, if the newest qualification is
still running or failed, `/merge` remains blocked. Permanent
`workflow_dispatch` runs are not substitutes for PR qualification.

#### Reviewed conflict recovery for permanent branches

Normal `/merge` remains the only ordinary integration command. If an exact
direct permanent-branch PR (`dev -> main`, `main -> dev`, `dev -> exp` or
`exp -> dev`) is genuinely conflicted, do not squash it and do not replace it
with a temporary integration branch.

Prepare a separate `resolve/*` branch that contains the intended combined
tree and open a **review-only** PR from that branch to the same permanent base.
That PR must be mergeable and central CI must be green; it is never merged.
After reviewing the exact base/head commits, resolution commit and Git tree,
comment on the original conflicted permanent PR:

```text
/merge-resolved
base <reviewed-base-sha>
head <reviewed-head-sha>
resolution-pr <review-pr-number>
resolution resolve/<name> <reviewed-resolution-commit-sha> <reviewed-tree-sha>
```

The original conflicted permanent head is not required to have an impossible
`pull_request` run. Instead its exact current branch SHA must match the
`source_sha` in durable `build/<head>/build-plan.json`, proving successful
permanent qualification of that source. The separate resolution PR still
requires normal green PR-specific central CI.

The policy revalidates both PRs and all mutable refs, creates exactly one merge
commit with the reviewed tree and parents `[base, head]`, verifies that object,
then advances the permanent base non-force. It dispatches the same permanent
CI/cleanup workflows as normal integration, closes both review PRs and removes
the unchanged resolution branch.

If the original PR becomes normally mergeable, use `/merge` instead.
`/merge-resolved` is refused for temporary, release and governance PRs.

## Library owner

`cadlib/` is independent of model owners and internal modules. Selecting the library runs its source tests and builds one qualification wheel. This is not a release.

A model can declare `needs: [cadlib]`; library changes then select that model and its downstream dependents.

## API probes

`api-probes/<id>/` is a separate owner type for temporary executable API/design
experiments. It is not a physical CAD model and is never a Pages catalogue
owner.

Each probe has one `probe.yml`:

```yaml
schema: 1
id: smoke
builder: builder-pythonscad
source: pythonscad/probe.py
```

Optional `needs` may name `cadlib` or internal module ids. The selected
builder remains responsible for turning the source into its normal CAD
artifacts.

Probes have no per-owner `process` flag. Root `ci.yml` permanently declares
the `api-probes/` root. Root `build.yml` is only the temporary branch-local
activation override used while developing an API:

```yaml
api_probes: [smoke]
```

Absent or empty means no branch-local probes. Full `main`, `dev` and
`exp` selection also keeps probes off.

To run an existing probe explicitly against an existing source, use the
`API Probe` workflow. Supply:

```text
source_ref: dev
probes: configuration-toggle
```

`probes` accepts a comma-separated list or `all`. The workflow checks out the
requested source, runs the same probe discovery/runtime path as branch-local CI,
and always uploads candidate evidence. When `source_ref` is `main`, `dev` or
`exp`, successful evidence is also published below
`build/<scope>/api-probes/<id>/`.

Probe publication is owner-incremental: selected probes are replaced, unselected
probe evidence is preserved, and `models/` is untouched. Ordinary model builds
also preserve API-probe evidence. Removal/reconciliation of stale probes is a
separate explicit concern rather than a side effect of unrelated builds.

Pages ignores API probe evidence.

## Model owners

`models/<id>/` is the physical ownership boundary. It owns:

- one `ci.yml` for execution;
- one `model.yml` for presentation and purpose;
- one or more implementation source directories;
- shared model-specific verification expectations.

Do not create separate model owners merely because the same geometry is implemented by different engines.

### Purpose

`model.yml.purpose` can contain one or more purposes:

```yaml
purpose: [example, verification]
```

`example` selects the Examples view. `verification` selects the Verification view. Both are allowed together; they project one physical model owner.

### Multiple implementations

A single owner can qualify multiple engines:

```yaml
primary: cadquery
implementations:
  - id: cadquery
    builder: builder-cadquery
    source: cadquery/model.py
  - id: build123d
    builder: builder-build123d
    source: build123d/model.py
  - id: solidcraft
    builder: builder-solidcraft
    source: solidcraft/commands.json
    preview: false
```

CI selects the owner once and expands all implementations. Builder module changes also select every owner that uses that builder. A model may additionally own `tests/`; those Python tests run only when that physical owner is selected, with `cadlib/src` on `PYTHONPATH`. They are intended for source/compiler contracts and do not replace built-artifact verification stages.

## Verification stages

A model can declare one or more named verification stages. The verifier module owns adapter-to-runtime mapping; the model only selects the adapter, definition, generated artifact and optional implementation filter.

```yaml
verifications:
  - id: native
    module: verification
    adapter: solidcraft-model
    definition: verification/solidcraft.py
    artifact: model.sc
    implementations: [solidcraft]

  - id: geometry
    module: verification
    adapter: mesh-geometry
    definition: verification/geometry.json
    artifact: model.stl
```

The current local verification module declares:

- `solidcraft-model` -> `solidcraft`;
- `mesh-geometry` -> `reference`.

A stage without `implementations` applies to every implementation. Each implementation must have at least one applicable stage.

For compatibility, the previous single `verification:` mapping is still accepted and becomes one `model.stl` verification stage.

Stage evidence is retained independently below:

```text
models/<owner>/<implementation>/verification/<stage>/
  verification.json
  stage-result.json
```

A later stage never overwrites earlier evidence. Implementation status passes only if its build, all applicable stages and configured preview pass.

## Dependencies

`dependencies` contains physical model owner ids. A selected dependency selects all downstream consumers transitively. This intentionally matches `template.cad.model-project`.

## Standard builders and runtime roles

The five standard builder modules are PythonSCAD, pyBOSL2, CadQuery, build123d and SolidCraft.

Reference engines share `cad-reference:v0.3.5`. build123d uses its isolated interpreter inside that container. SolidCraft builds in `cad-solidcraft:v0.3.5`.

Builder, verifier and preview runtimes are declared independently. CI derives one dependency graph and starts every required role at most once for the selected batch.

For the qualification box:
1. SolidCraft builds and runs its native SolidCraft verification in `solidcraft`;
2. all five implementations run geometry verification in `reference`;
3. reference previews run only after all applicable verification stages have passed.

No third verification image is used.

## Durable output

The permanent-branch `build` job publishes owner-grouped output below `build/<scope>/models/`. The owner root contains aggregate status and canonical primary artifacts; each implementation retains its own build, staged verification and preview evidence.

Pull requests run the `ci` qualification job only, may upload candidate evidence for inspection, and never publish generated branches.

## Workflow roles

The thin workflow shape matches `template.cad.model-project`:

- pull requests run the `ci` job only and never publish generated branches;
- permanent `dev`/`main`/`exp` events run one `build` job that executes `cad_library_ci` and publishes `build/qualification` through `cad_library_build.publish`;
- after successful build publication, that job dispatches `pages.yml` and finishes without waiting for Pages.

Do not reintroduce a permanent-branch `verify -> publish-build -> dispatch-pages` job chain or pass qualification output between those permanent-branch jobs as an Actions artifact.

## Pages

Pages is separate from CAD CI. Hugo consumes `models/` metadata and the corresponding durable build scope. Examples and Verification are purpose-driven public views. Owners with both purposes appear in both views without duplicating physical ownership or generated artifacts. When implementation results contain named `verification_stages`, Pages renders each stage status and links the stage-local durable report. Legacy/single-stage results remain supported through the aggregate verification status and compatibility report link.

Homepage content is generated rather than authored in the Hugo layout. Edit
`site/home.yml` to declare the ordered homepage blocks. The Pages preparation
step validates that source and generates `data/home.json` inside the temporary
Hugo site. `site/layouts/home.html` renders that manifest with the normal Hugo
templates and CSS. Use `route` for repository-local destinations so Hugo can
apply the active base URL; use `url` only for absolute HTTPS destinations.
Changing homepage labels, text, links or block order must not require editing
the layout.

Stable content is published at `/` and development content at `/dev/`. If the optional permanent `exp` branch exists, its experimental content is published at `/exp/`, with separate build evidence under `build/exp/`. Experimental development cannot release or promote directly to `main`. Create `exp` from a qualified `dev` only after the template support has reached `main`. Use a new temporary branch for each experimental work item; synchronize using `/merge`.

## Releases

A release is an explicit repository-owner action and never follows
automatically from normal CI.

Release preparation must not implicitly promote the current `dev` branch.
Create `release/vX.Y.Z` from stable `main`. A release branch may change only:

- `cadlib/pyproject.toml`, with only `project.version` changing;
- `CHANGELOG.md`.

The release PR targets `main` directly. CI validates the branch diff before
running only the library owner plus `modules/release`; model owners are not
selected. Any third path fails closed, and CI also rejects a `pyproject.toml` change that alters anything besides `project.version`. Integration still goes through
`/merge`, and the merge policy permits only `release/*` as a short-lived
direct-to-main branch.

Product changes from `dev` must be stabilized separately through an explicit
`dev -> main` promotion before release preparation. A release metadata change
never implies product promotion.

The full product qualification remains the last durable `build/main` scope.
A release-only `main` push records `release_only: true` in its candidate,
runs library/release checks, and deliberately does not replace that durable
scope. The release validator accepts the requested stable main SHA only when:

1. the retained durable product source is a full library + all-owner PASS;
2. that product source is on the release SHA's first-parent history;
3. every stable commit since it is single-parent;
4. every changed path across those commits is one of the two release metadata
   files above;
5. the repository-specific release validator passes at the exact requested SHA.

This permits consecutive metadata-only patch releases to reuse one unchanged
product qualification while still rejecting any intervening source/model/CI
change.

Publication is requested on a normal issue with:

```text
/release vX.Y.Z <exact-40-character-main-sha>
```

The shared publisher still requires that SHA to equal current `main` HEAD and
creates/verifies the annotated tag plus GitHub Release. After publication,
synchronize `main -> dev` through `/merge` so version/changelog metadata
returns to development. Do not rebase the shared `dev` branch.

Update planning/status documentation on `dev` after the release; do not add
`docs/plan.md` to the stable release-metadata commit.

Pages is not consulted and is not release evidence. The release adapter must
not reimplement tag creation, GitHub Release creation, stable-head checks or
idempotent publication.
