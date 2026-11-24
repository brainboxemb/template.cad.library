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
| python-openscad | Python-authored OpenSCAD; exact authoring tool/runtime to be confirmed |
| bosl | OpenSCAD source using BOSL/BOSL2; exact supported version to be confirmed |
| cadquery | Python CadQuery model |
| build123d | Python build123d model |
| solidcraft | Native SolidCraft source/commands |

A CAD builder builds an explicit source with an explicit qualified runtime and produces declared artifacts with a structured result. It does not select CI items, interpret expected geometry, publish Pages or decide releases. Shared runtime batching is allowed when it preserves individual result ownership. Do not invent model-authoring conventions before inspecting the existing implementations. The generic SolidCraft builder does not itself import Forge; a Forge consumer may compile a library example to the builder input.

Use the existing CAD model template and `lib.py.cad.ci` implementations as references. Standard engine builders will be implemented and qualified one at a time; no builder is claimed available solely because it appears in this design.

## Verification

- `lib.py.cad.verification` is the initial dependency for generic comparisons, evidence, reports and engine-specific verification adapters.
- `modules/verification/` owns reusable consumer-specific verification behavior as a normal independently selectable Python module. Organize checks and adapters inside its package; split into additional sibling modules only if a concrete independent ownership or execution need arises.
- `examples/<id>/verification/` owns the specific expectations, tolerances, views and mutation definitions. It is data, not a second verification library.
- A verifier receives built artifacts or explicit measured values and explicit expectations. It does not rebuild a model, publish pages or implement CI selection. Generic pass/fail/error and evidence mechanics remain in the verification library.
- Module selection and unit tests use the existing Python-module mechanism. Library and example selection, dependency propagation, external verification dependency installation and CAD verification task execution will be implemented explicitly.

The concrete `modules/verification/` starter demonstrates a consumer check that delegates to the existing verification package. The module is registered with normal CI discovery. Unit tests verify the delegation boundary without external dependencies; integration tests exercise the pinned external package when installed, otherwise explicitly skip. Wiring that dependency into CI remains open. This is not a qualified CAD verification adapter.

## Dependency boundary

Whether the generic verification library remains its own repository or is consolidated into another distribution is an independent design decision. Do not copy it into Forge or duplicate it inside the template as a shortcut. In either case, engine-neutral verification must remain usable without importing Forge.

## Pages

Hugo consumes authored documentation and eventually generated example/reference evidence. It never runs a CAD builder or a verifier. Published examples are distinct from verification-only fixtures; when both purposes apply, use an explicit model metadata purpose declaration.
