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
  builder-<engine>/        # independent Python capability; planned
  verification/
    ci.yml
    pyproject.toml
    src/<package>/
    tests/
examples/
  <id>/
    ci.yml
    model.yml
    <engine>/              # authoring source
    verification/          # example-specific expectations
site/
```

`cadlib/` is a repository role, not a required import name. For a Forge consumer, its package may remain SCPF. Internal modules must not depend on that package merely to run generic CI.

## Standard builders

Provide separate, tested engine adapters for:

| Builder | Input |
| --- | --- |
| pythonscad | PythonSCAD 1.1.2 source |
| pybosl2 | PythonSCAD with pyBOSL2 at the qualified runtime revision |
| cadquery | Python CadQuery model |
| build123d | Python build123d model |
| solidcraft | Native SolidCraft source/commands |

A CAD builder builds an explicit source with an explicit qualified runtime and produces declared artifacts with a structured result. It does not select CI items, interpret expected geometry, publish Pages or decide releases. Shared runtime batching is allowed when it preserves individual result ownership. Do not invent model-authoring conventions before inspecting the existing implementations. The generic SolidCraft builder does not itself import Forge; a Forge consumer may compile a library example to the builder input.

Use the existing CAD model template and `lib.py.cad.ci` implementations as references. Standard engine builders will be implemented and qualified one at a time; no builder is claimed available solely because it appears in this design.

## Runtime separation

Root ci.yml pins two immutable images from docker.cad.solidcraft v0.3.5:

- reference: PythonSCAD 1.1.2, pyBOSL2 commit d4279910c12435ed7224b3406616e495db1c96ec, CadQuery 2.8.0, build123d 0.12.0 (separate interpreter /opt/build123d/bin/python).
- solidcraft: SolidCraft 0.48.1 and Pillow, deliberately without the heavy reference geometry stack.

Builders share compatible runtime batches. Local verification source is mounted into the appropriate runtime when needed. Do not combine the images or add a third verification image. CADCraft is already in the reference runtime but no CADCraft builder is in scope yet.

## Verification

- modules/verification/ owns generic comparisons, evidence, reports and CAD-specific adapters as a normal independent Python module.
- The existing cad_verification package and functional tests are local source. No external verification package or Git checkout is required.
- Organize reusable checks and adapters inside the module; split only when concrete independent ownership requires it. Engine-neutral APIs must remain independent of Forge.
- examples/<id>/verification/ owns model-specific expectations, tolerances, views and mutations.
- A verifier receives built artifacts or explicit measurements and explicit expectations. It does not schedule builds or publish Pages.
- CI installs ordinary third-party dependencies declared by selected modules only, then tests the module directly from source. Real CAD verification tasks use the relevant runtime image.

The source baseline is lib.py.cad.verification v0.16.0 at c7c145b7be0c602724e8cca874ef29990baaad1e, matching the existing Forge pin. The separate repository release-policy test is excluded because internal modules follow their containing repository's release policy. The import-boundary test explicitly points its isolated interpreter at local module source.

## Dependency boundary

The old verification repository is not modified or deleted. Migrate other consumers before retiring redundant ownership. After Forge adopts this template, its verification code is local and no longer depends on the external repository.

## Pages

Hugo consumes authored documentation and eventually generated example/reference evidence. It never runs a CAD builder or verifier. Use explicit model metadata purpose declarations to distinguish published examples and verification fixtures.
