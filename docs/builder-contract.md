# CAD builder qualification

The builder contract is evaluated through physical model owners.

`models/simple-box` owns one 40 × 30 × 10 mm geometry definition, one geometry verification contract and five engine implementations: CadQuery, build123d, PythonSCAD, pyBOSL2 and SolidCraft.

Each implementation chooses a standard builder module. Builder capabilities declare their runtime and entrypoint locally; the model owner does not encode engine behavior into CI.

The owner-level verification contract is applied independently to every implementation. A build is successful only when all declared implementations pass.

Reference-engine implementations are built together in one `reference` Docker role. build123d uses its isolated interpreter inside that role. SolidCraft builds in the separate lightweight `solidcraft` role and is then verified in `reference`.

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
```

The owner root mirrors the model-project concept: selection and publication happen once per physical model. Engine implementation ids are local details.

Permanent successful builds publish separate `main/` and `dev/` scopes to the generated build branch. Incremental publication replaces complete selected owners and preserves untouched active owners.
