# CAD builder and verification qualification

The contract is evaluated through physical model owners.

`models/simple-box` owns one 40 × 30 × 10 mm physical definition and five engine implementations: CadQuery, build123d, PythonSCAD, pyBOSL2 and SolidCraft.

Each implementation chooses a standard builder module. Builder capabilities declare their runtime and entrypoint locally; the model owner does not encode engine behavior into central CI.

The model currently qualifies two verification stages:

- `native`: only the SolidCraft implementation, using `solidcraft-model` in the `solidcraft` role against `model.sc`;
- `geometry`: all five implementations, using `mesh-geometry` in the `reference` role against `model.stl`.

Verifier adapter/runtime ownership is declared by `modules/verification/ci.yml`. Central CI only resolves capabilities and schedules runtime dependencies.

Reference-engine implementations are built together in one `reference` Docker role. build123d uses its isolated interpreter inside that role. SolidCraft builds in the separate lightweight `solidcraft` role, runs native verification there, and then its STL joins the reference geometry batch.

Generated candidate output is grouped by model owner:

```text
build/qualification/models/<owner>/
  result.json
  model.stl
  model.png
  <implementation>/
    build.json
    result.json
    model.stl
    verification/
      <stage>/
        verification.json
        stage-result.json
      verification.json
```

A later verification role does not overwrite earlier stage evidence. An implementation passes only when its build, all applicable stages and configured preview pass.

Permanent successful builds publish separate `main/` and `dev/` scopes to the generated build branch. Incremental publication replaces complete selected owners and preserves untouched active owners.
