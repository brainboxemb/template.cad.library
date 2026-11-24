# template.cad.library

Self-contained CAD library repository template derived from `template.cad.model-project`.

- `cadlib/`: consumer-owned library source, packaging and tests.
- `examples/`: public examples and verification-only qualification fixtures.
- `modules/`: local CI capabilities, verification, preview rendering and standard CAD builders.
- `site/`: Hugo/Hextra documentation and example presentation.

Qualified standard builders:

| Builder | Runtime |
| --- | --- |
| PythonSCAD | `reference` |
| pyBOSL2 | `reference` |
| CadQuery | `reference` |
| build123d | `reference`, using `/opt/build123d/bin/python` |
| SolidCraft | `solidcraft`; mesh verification follows in `reference` |

The template intentionally keeps the two released CAD runtime roles separate. It does not add a third verification image.

Stable source is `main`, development source is `dev`. See the [manual](docs/manual.md), [design](docs/design.md), [builder contract](docs/builder-contract.md) and [plan](docs/plan.md).
