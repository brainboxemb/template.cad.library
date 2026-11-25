# CAD library template manual

## Branches and selection

Normal product branches are based on `dev`; squash them into `dev`. Promote `dev` to `main` with a merge commit only when an explicit product stabilization is intended. Release branches are different: create `release/vX.Y.Z` from stable `main`, merge that short-lived branch directly to `main`, publish from the resulting stable commit, then synchronize `main -> dev` with a merge commit. Do not rebase shared permanent branches. Root `build.yml` is an exact branch-local execution plan:

```yaml
schema: 1
branch: issue/25-multi-stage-verification
modules: [ci, verification]
library: false
models: [simple-box]
tasks: [test]
```

Use `modules: all` or `models: all` for full selection. Product-changing `main` commits and `dev -> main` promotions run full. A validated release-metadata-only `main` commit runs only the library + release capability and preserves the previous full stable CAD evidence. Permanent `dev` runs select changes since the last successful integration run; missing history falls back to full.

### Merge execution

The merge shape is policy-owned, not agent-selected. For every source-branch integration, post `/merge` on the pull request and let `.github/workflows/merge-policy.yml` execute the merge.

The policy chooses:

- normal short-lived branch -> `dev`: squash;
- `release/*` -> `main`: squash;
- explicit product promotion `dev` -> `main`: merge commit;
- stable synchronization `main` -> `dev`: merge commit.

A normal feature/issue/fix/docs/chore branch may not target `main` directly.

`release/*` is also a temporary branch class. Post-merge cleanup deletes it
after a successful same-repository merge to `main`; normal temporary branches
are deleted after their successful merge to `dev`. The manual sweep uses the
same target rule, so a release branch is never considered safely merged merely
because it reached development.

Do not use the direct GitHub merge API, auto-merge, a UI/manual fallback, or manual squash/merge/rebase selection. If `/merge` fails, repair the policy path rather than bypassing it.

Repeating `/merge` after a pull request has already been merged is an idempotent successful no-op. A pull request that is closed without being merged is still rejected.

## Library owner

`cadlib/` is independent of model owners and internal modules. Selecting the library runs its source tests and builds one qualification wheel. This is not a release.

A model can declare `needs: [cadlib]`; library changes then select that model and its downstream dependents.

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
- permanent `dev`/`main` events run one `build` job that executes `cad_library_ci` and publishes `build/qualification` through `cad_library_build.publish`;
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

Stable content is published at `/` and development content at `/dev/`.

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
