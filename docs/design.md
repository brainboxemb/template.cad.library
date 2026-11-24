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

Supported values are:

- `example`: publish the model in the public catalogue;
- `verification`: use the model as qualification/verification evidence.

A model may have either purpose or both. Verification-only models stay out of Pages.

## Model execution contract

`models/<id>/ci.yml` owns process identity and implementation execution:

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

verification:
  module: verification
  adapter: mesh-geometry
  definition: verification/geometry.json

preview:
  module: preview
  adapter: mesh

dependencies: []
needs: []
```

The owner is selected once; CI expands all declared implementations. `primary` determines the canonical owner-level STL/preview used for presentation. Each implementation still retains its own build and verification evidence.

Physical model dependencies name other owner ids. Selection closes transitively over downstream dependents, matching the model-project behavior.

## Capability boundaries

CI decides **what owners** run. Builders decide **how one implementation** becomes CAD artifacts. Verification checks generated artifacts against owner-local expectations. Preview renders verified geometry. Pages consumes durable evidence only.

No central engine switch is allowed. Runtime and adapter behavior remains module-local.

## Runtime graph

Root `ci.yml` pins two immutable images from `docker.cad.solidcraft v0.3.5`:

- `reference`: PythonSCAD, pyBOSL2, CadQuery, build123d and geometry tooling;
- `solidcraft`: SolidCraft 0.48.1 without the heavy reference geometry stack.

Builder and verifier runtimes are independent capabilities. For a multi-engine owner, all reference implementations build in one reference batch. SolidCraft builds in the SolidCraft role first and its STL is then verified in the reference role.

## Durable output

Generated evidence is owner-grouped:

```text
build/<scope>/models/simple-box/
  result.json
  source.json
  model.stl
  model.png
  verification/
  cadquery/
  build123d/
  pythonscad/
  pybosl2/
  solidcraft/
```

The owner-level artifacts come from the configured primary implementation. Implementation directories preserve their engine-specific artifacts and reports.

Incremental publication replaces selected model owners, preserves untouched active owners with their source provenance and removes deleted owners.

## Presentation

Hugo reads model metadata plus durable build output. It never executes CAD or verification. Public visibility is controlled only by `model.yml.purpose`.

The custom model presentation continues to use the established Hextra CAD baseline from `exp.2026-015.hugo-cad-site` and `template.cad.model-project`.
