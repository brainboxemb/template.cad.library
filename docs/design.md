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

Supported values are `example` and `verification`. A model may have either or both. Verification-only models stay out of Pages.

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

A physical owner may contain `tests/` for source/compiler semantics that are specific to that model. CI runs those tests only when the owner is selected. They receive `cadlib/src` on `PYTHONPATH` but do not trigger installation of reference CAD engines. This keeps compiler command contracts with the model that owns them while geometry/native checks remain verification stages.

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

Incremental publication replaces selected model owners, preserves untouched active owners with their source provenance and removes deleted owners. Permanent successful runs publish separate `main/` and `dev/` scopes on the generated `build` branch.

## Presentation

Hugo reads model metadata plus durable build output. It never executes CAD or verification. Public visibility is controlled only by `model.yml.purpose`.

The custom model presentation continues to use the established Hextra CAD baseline from `exp.2026-015.hugo-cad-site` and `template.cad.model-project`.
