# CAD library architecture

## Ownership

```text
cadlib/
  ci.yml
  pyproject.toml
  src/<package>/
  tests/
modules/
  ci/
  branch-cleanup/
  merge-policy/
  pages/
  build/
  verification/
  preview/
  builder-pythonscad/
  builder-pybosl2/
  builder-cadquery/
  builder-build123d/
  builder-solidcraft/
examples/
  <id>/
    ci.yml
    model.yml
    <engine>/
    verification/
site/
```

`cadlib/` is a repository role, not a required import name. A Forge consumer may therefore continue to expose SCPF while using this repository architecture.

## Capability boundaries

CI decides **what** to run. A builder decides **how** one explicit source becomes CAD artifacts. Verification decides whether those artifacts satisfy explicit expectations. Preview decides how already-built geometry is presented. Pages only reads authored metadata and durable evidence.

These boundaries are expressed through module-local `ci.yml` capabilities rather than a central engine switch.

## Standard builders

| Builder | Input contract | Build runtime |
| --- | --- | --- |
| `builder-pythonscad` | Python source exposing `model.export(...)` | reference |
| `builder-pybosl2` | pyBOSL2 source using the same export contract | reference |
| `builder-cadquery` | Python source exposing `model` | reference |
| `builder-build123d` | Python source exposing `model` | reference via `/opt/build123d/bin/python` |
| `builder-solidcraft` | SolidCraft command-document JSON | solidcraft |

The SolidCraft builder is intentionally independent of Forge. A consumer that compiles another DSL or library to SolidCraft commands does that before invoking the generic SolidCraft builder.

## Runtime graph

Root `ci.yml` pins two immutable images from `docker.cad.solidcraft v0.3.5`:

- reference: PythonSCAD 1.1.2, pyBOSL2 at the qualified revision, CadQuery 2.8.0, build123d 0.12.0, trimesh/scipy/Pillow;
- solidcraft: SolidCraft 0.48.1 and Pillow, without the heavy reference geometry stack.

Builders and verifiers declare runtimes independently. Selected examples produce a small dependency graph between runtime roles. CI topologically orders that graph and starts every required role once.

Current cross-role edge:

```text
solidcraft build
      ↓
reference mesh verification
```

Reference builders have no cross-role edge and are built and verified within the same reference container.

## Verification

`modules/verification/` contains the local `cad_verification` package and its functional tests. It is based on the previous external verification repository but no runtime Git dependency remains.

`examples/<id>/verification/` owns expectations such as geometry contracts. Verification receives built artifacts and expectations; it does not build models, schedule work or publish Pages.

The separate historical verification repository remains untouched until consumers have migrated.

## Presentation

`modules/preview/` renders deterministic STL previews in the reference runtime after successful verification. SolidCraft can produce its own native snapshot during its build.

Hugo reads only durable build output. Public visibility is controlled by `model.yml.purpose`: `example` is public, `verification` alone is not.

The custom example layouts reuse the established Hextra CAD presentation baseline; documentation, API and guide pages use Hextra's normal documentation layout.
