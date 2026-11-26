# CAD library architecture

## Ownership

The library follows the same physical model-owner concept as `template.cad.model-project`.

```text
cadlib/
  ci.yml
  pyproject.toml
  src/<consumer package>/
  tests/

models/
  ci.yml
  <model-id>/
    ci.yml
    model.yml
    <engine>/...
    verification/...

modules/
  ci/
  build/
  release/
  pages/
  verification/
  preview/
  builder-pythonscad/
  builder-pybosl2/
  builder-cadquery/
  builder-build123d/
  builder-solidcraft/
```

`cadlib/` is a repository role, not an import name. A Forge consumer can therefore expose `scpf` unchanged.

A **model directory is the selection and publication owner**. Engine implementations are local implementations of that owner, never sibling owners.

## Model metadata and purpose

`model.yml` owns presentation intent. `purpose` accepts one or more supported purposes:

```yaml
purpose: [example, verification]
```

Supported values are `example` and `verification`. A model may have either or both. Pages projects each declared purpose into its own catalogue; both purposes may refer to the same physical owner.

## Model execution contract

`models/<id>/ci.yml` owns process identity, implementation execution and verification stages:

```yaml
schema: 1
id: simple-box
process: true
primary: cadquery

implementations:
  - id: cadquery
    builder: builder-cadquery
    source: cadquery/model.py
  - id: solidcraft
    builder: builder-solidcraft
    source: solidcraft/commands.json
    preview: false

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

preview:
  module: preview
  adapter: mesh
```

The owner is selected once; CI expands declared implementations and applicable verification stages. `primary` determines canonical owner-level artifacts. Each implementation retains its own build, stage and preview evidence.

The legacy single `verification:` mapping remains supported and maps to one STL verification stage.

## Model-local source contracts

A physical owner may contain `tests/` for source/compiler semantics that are specific to that model. CI runs those tests only when the owner is selected. `cadlib/src` and the model root are available on `PYTHONPATH`; library dependencies are installed only when a tested owner declares `needs: [cadlib]` and they were not already installed through library selection. Reference CAD engines are not installed for these host-side tests. Geometry/native checks remain verification stages.

## Capability boundaries

CI decides **what owners and runtime roles** run. Builders decide **how one implementation** becomes CAD artifacts. Verifier capabilities map adapters to runtime-local entrypoints. Verification stages apply generated artifacts to owner-local expectations. Preview renders already-built verified geometry. Pages consumes durable evidence only.

No central engine switch is allowed. Runtime and adapter behavior remains module-local.

## Runtime graph

Root `ci.yml` pins exactly two immutable images:

- `reference`: PythonSCAD, pyBOSL2, CadQuery, build123d and geometry tooling;
- `solidcraft`: SolidCraft 0.48.1 without the heavy reference geometry stack.

For every implementation CI derives edges from:
- build runtime -> each applicable verifier runtime;
- build runtime -> preview runtime;
- each verifier runtime -> preview runtime when they differ.

The graph is topologically ordered and each role starts at most once per selected batch. A cycle is a configuration error.

The current cross-role qualification is:

```text
solidcraft build
  ├─ native solidcraft-model verification
  └───────────────┐
                  v
          reference geometry verification
                  v
             reference preview
```

Reference implementations build and verify entirely inside the reference role.

## Stage evidence and aggregation

Runtime-local stage evidence is never overwritten by a later role:

```text
build/<scope>/models/<owner>/<implementation>/
  build.json
  model.stl
  model.sc                 # when produced
  verification/
    native/
      verification.json
      stage-result.json
    geometry/
      verification.json
      stage-result.json
    verification.json      # compatibility alias to canonical stage
  preview-result.json
  result.json
```

The implementation result aggregates build, all applicable stages and preview. The owner result aggregates implementations. Owner-level canonical artifacts come from the configured primary implementation.

## Physical dependencies

Physical model dependencies name other owner ids. Selection closes transitively over downstream dependents, matching the model-project behavior.

## Durable output

Incremental publication replaces selected model owners, preserves untouched active owners with their source provenance and removes deleted owners. Permanent successful runs publish separate `main/`, `dev/` and optional `exp/` scopes on the generated `build` branch. `build-plan.json` records whether the independent library owner was selected and qualified; stable release qualification requires `library: true` in addition to a full model-owner build.

Workflow roles mirror `template.cad.model-project`: pull requests run only the `ci` qualification job; permanent `dev`/`main`/`exp` events run one `build` job that executes the selected project work and publishes the durable scope. Pages is not a downstream job in that build graph: after successful publication the build only dispatches the independent `pages.yml` workflow and finishes without waiting for it.

## Experimental development line

`exp` is an optional permanent integration branch, not a release source. Temporary work branches squash into `dev` or `exp`; `dev -> exp` and `exp -> dev` use merge commits and full PR qualification. `exp -> main` is forbidden. Incremental permanent builds use the history of their own source branch. The generated build branch keeps `exp/` isolated and Pages assembles `/exp/` only when the source branch exists. The single Pages publication remains serialized because it replaces the whole site.

## Presentation

Hugo reads model metadata plus durable build output. It never executes CAD or verification. Each declared `model.yml.purpose` projects the owner into Examples and/or Verification. Legacy Models routes redirect to the matching purpose view. Pages must not copy generated CAD artifacts.

Homepage composition follows the same generated Pages boundary. Repository-owned
`site/home.yml` declares typed presentation blocks and destinations.
`modules/pages` validates that source and writes the prepared Hugo
`data/home.json`. The Hugo homepage layout owns only rendering and styling of
the generated blocks; it must not own consumer-specific copy, routes or URLs.
The generated contract currently supports `hero`, `flow`, `links` and
`catalogue` blocks, with base-relative routes distinguished from absolute
HTTPS destinations.

The custom model presentation continues to use the established Hextra CAD baseline from `exp.2026-015.hugo-cad-site` and `template.cad.model-project`.

Verification detail pages identify their purpose with **What this verifies**.
Owner-local `page.md` is engineering context rather than verification evidence.
Render it as **Engineering explanation** immediately after the primary source,
before generated command sequences, drawings, reference implementations and
verification evidence. This ordering is shared by Example and Verification
detail pages.

Detailed measured checks remain durable evidence, but are collapsed by default
with the same `cad-collapsible` interaction used for generated command
sequences. Example pages retain **What this model makes**. Owner-local
engineering-explanation placement is a separate presentation concern.

Optional `model.yml.presentation_primary` selects a declared implementation for
the featured source and image without changing the execution primary. It defaults
to `ci.yml.primary`. Native builder snapshots use their own implementation
artifact; Pages never substitutes another implementation's preview.

## Main-owned governance merge boundary

Normal product work still integrates through `dev` or `exp`. A repository
may keep its small volatile governance entrypoints directly on stable `main`
without using the development lane as a staging copy.

The merge-policy route is deliberately narrow:

- the source branch uses the existing `docs/` temporary prefix;
- the target is `main`;
- the merge method is squash;
- changed paths are exhaustively read from the pull request and may contain
  only `AGENTS.md`, `docs/plan.md` and `docs/handoff.md`;
- any other path fails closed before merge;
- ordinary `docs/* -> dev|exp` work keeps its existing behavior.

Branch cleanup accepts a successfully merged `docs/* -> main` PR as a valid
temporary-branch completion, but this does not make stable a valid target for
issue/fix/feature/chore branches.

## Release boundary

Release qualification is separate from normal product qualification, durable
publication and Pages.

A product-changing stable source is qualified normally: full model-owner
selection, library qualification and durable `build/main` evidence. A later
release metadata commit does not invalidate that product evidence merely
because package version or changelog text changed.

The release lane is therefore intentionally narrow:

```text
qualified main product source
  -> release/vX.Y.Z from main
  -> CHANGELOG.md + cadlib/pyproject.toml only
  -> lightweight library + release PR qualification
  -> squash to main
  -> lightweight stable qualification, no build/main replacement
  -> /release exact-main-sha
  -> main -> dev synchronization
```

CI records release-only candidates with `release_only: true`. Stable
classification is based on the single-parent source delta, not on whether the
permanent run was triggered by `push` or merge-policy `workflow_dispatch`.
A metadata-only delta selects release + library and zero models; a merge commit
or any product path remains full/fail-closed. Build publication treats
`release_only: true` as a stable-baseline preservation instruction: it checks
source freshness but leaves the previous full `build/main` scope untouched.

The template-owned `modules/release` capability validates that retained scope
as the product baseline, then validates the exact requested release source
history. The baseline must remain a full library + all-owner PASS. Every
first-parent stable commit between baseline and release target must be
single-parent and may change only `CHANGELOG.md` and the `project.version`
value in `cadlib/pyproject.toml`. Any other path requires a new normal full stable
qualification instead of baseline reuse.

`.github/workflows/release.yml` checks out the exact requested source with
history, performs that repository/template-owned evidence check, and then
delegates tag/GitHub Release publication to released `tool.py.lib.ci`.
Consumer-specific package/release-note rules remain in `cadlib/release.py`.

The shared publisher still requires the requested SHA to equal `main` HEAD.
The release tag therefore always names a stable commit even when its CAD
product evidence comes from an unchanged earlier full stable baseline.

Pages and `gh-pages` are not release evidence.


## Permanent dispatch source identity

Policy-owned permanent qualification treats the current permanent branch head
as the source of truth, not the workflow event SHA. A `workflow_dispatch`
created immediately after a merge can temporarily carry the previous ref SHA.
The build job therefore explicitly checks out `github.ref_name`, resolves that
checked-out HEAD once, passes it to CI as `CAD_SOURCE_SHA`, and publishes
durable evidence against the same resolved SHA. Publisher freshness validation
still compares that SHA with the live source ref and fails closed if the branch
moves again during the run.
