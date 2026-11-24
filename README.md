# template.cad.library

Self-contained CAD library repository template derived from `template.cad.model-project`.

- `cadlib/`: consumer-owned Python library source, packaging and tests.
- `models/`: physical model owners, each with one metadata/config owner and one or more CAD-engine implementations.
- `modules/`: local CI capabilities, verification, preview rendering and standard CAD builders.
- `site/`: Hugo/Hextra documentation and model presentation.

A model is selected once regardless of how many engine implementations it owns:

```text
models/
  simple-box/
    ci.yml
    model.yml
    cadquery/model.py
    build123d/model.py
    pythonscad/model.py
    pybosl2/model.py
    solidcraft/commands.json
    verification/geometry.json
```

`model.yml.purpose` may contain multiple purposes. Supported values are `example` and `verification`; `[example, verification]` is the normal public qualification case.

Qualified standard builders remain PythonSCAD, pyBOSL2, CadQuery, build123d and SolidCraft. The template keeps the two released runtime roles separate: `reference` and `solidcraft`.

Stable source is `main`, development source is `dev`. See the [manual](docs/manual.md), [design](docs/design.md), [builder contract](docs/builder-contract.md) and [plan](docs/plan.md).
