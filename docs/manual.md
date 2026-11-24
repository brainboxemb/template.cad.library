# CAD library template manual

## Branches and execution

Temporary branches use prefixes configured in `ci.yml`. Squash into `dev`; merge-commit promotion into `main`; reverse integration only for actual stable-only changes. The owner uses `/merge` once CI is green. Branch cleanup removes merged temporary branches.

Root `ci.yml` holds stable settings. Root `build.yml` is an exact work-branch selection:

```yaml
schema: 1
branch: issue/12-ci-change
modules: [ci]
library: false
examples: []
tasks: [test]
```

Use `modules: all` and `examples: all` for full qualification. Set `library: true` to include the consumer library. If the branch does not match, the selection is ignored. `main` and `dev -> main` promotion PRs run full. `dev` push/dispatch selects paths since the last successful `dev` push/dispatch CI SHA; a missing or non-ancestor baseline falls back to full. Cancelled runs never advance that baseline.

## Library owner

`cadlib/` is independent of the internal modules and examples. When selected, CI runs its tests directly from source and builds one wheel from an isolated source copy. The wheel is qualification evidence, not a package release.

Examples may declare `needs: [cadlib]`; those examples are rebuilt when the library changes.

## Internal modules

Each module has `ci.yml`, `pyproject.toml`, `src/` and `tests/`. Discovery uses module-local `ci.yml`; there is no central module list. Tests execute from source with `unittest`. CI installs ordinary third-party dependencies declared by selected modules only.

The integrated `cad_verification` package lives in `modules/verification/`. Example-specific geometry contracts and other expectations remain inside the example.

## Standard CAD builders

The template qualifies five builders:

- `builder-pythonscad`;
- `builder-pybosl2`;
- `builder-cadquery`;
- `builder-build123d`;
- `builder-solidcraft`.

A builder declares its runtime and Python entrypoint in its own `ci.yml`. build123d additionally declares its isolated interpreter. pyBOSL2 declares its dependency on the shared PythonSCAD export adapter.

Builders do not decide verification, Pages publication or selection. They receive one explicit source and write artifacts into that example's output directory.

## Runtime roles

Root `ci.yml` pins exactly two immutable role images from `docker.cad.solidcraft v0.3.5`:

- `reference`: PythonSCAD, pyBOSL2, CadQuery, build123d and the geometry stack;
- `solidcraft`: SolidCraft 0.48.1 and its native CLI, deliberately without trimesh/scipy.

Builder runtime and verifier runtime are independent capabilities. CI derives a runtime dependency graph from selected examples and starts each required role once.

For ordinary reference-engine examples this is one reference container that builds and verifies the whole selected batch. When SolidCraft is selected, SolidCraft runs first and produces native `.sc`, STL and a native snapshot; the reference runtime then verifies the resulting STL. This remains two runtime images, not a third verification image.

## Verification and previews

`modules/verification/` owns reusable checks and evidence. `modules/preview/` owns deterministic mesh presentation rendering in the reference runtime. A failed verification fails the example. Presentation rendering happens only after verification passes.

SolidCraft already produces a native snapshot during its build, so it does not need the mesh preview adapter for that example.

## Durable output

Successful permanent-branch CI publishes example output to the generated `build` branch with separate `main/` and `dev/` scopes. Incremental `dev` builds preserve untouched example results and their original source SHA while replacing selected examples and pruning removed owners.

Pull requests upload candidate qualification evidence but do not publish generated branches.

## Pages

Hugo 0.169.0 and Hextra 0.13.0 live in `site/`. Pages is dispatched after successful permanent-branch CI and is separate from CAD execution.

The generated site combines:

- `main` at `/`;
- `dev` at `/dev/`.

Hugo consumes authored documentation and durable build evidence. It never executes a CAD engine or verifier. Verification-only fixtures are excluded from the public example catalogue.

The custom example presentation follows the established Hextra/CAD baseline from `exp.2026-015.hugo-cad-site` and `template.cad.model-project`; normal library documentation keeps the native Hextra documentation layout.
