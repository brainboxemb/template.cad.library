# template.cad.library

Self-contained CAD library repository template derived from template.cad.model-project.

- `cadlib/`: consumer-owned library source, packaging and tests.
- `examples/`: CAD examples and model-specific verification expectations.
- `verification/`: reusable project-specific verification modules.
- `modules/`: internal CI capabilities, including the standard CAD builders as they are implemented.
- `site/`: Hugo/Hextra documentation.

Stable source is `main`, development source is `dev`. See [manual](docs/manual.md), [design](docs/design.md) and [plan](docs/plan.md).
