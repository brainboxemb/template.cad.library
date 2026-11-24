# Agent guidance

Read `docs/plan.md`, `docs/design.md` and `docs/manual.md` before changing the repository.

Work from a temporary branch based on `dev`. Set `build.yml.branch` to the actual branch and select the necessary library, modules and **physical model owners**. Squash temporary branches into `dev`; promote `dev` to `main` with a merge commit.

The repository root for CAD ownership is `models/`, matching `template.cad.model-project`. Do not reintroduce `examples/` as an execution owner root.

One `models/<id>/` directory is one physical owner. Multiple engine implementations belong under that owner and are declared in its `ci.yml`. Do not create sibling owners such as `model-build123d` or `model-solidcraft` solely to represent engines.

`model.yml.purpose` may contain multiple purposes. Supported values are `example` and `verification`; `[example, verification]` is valid and expected.

Builders, verifiers and previews declare runtime capabilities locally. Central CI schedules owners and runtime roles but must not contain engine-specific branches. Preserve the two released runtime roles; do not add a third verification image.

Physical model dependencies name owner ids. Selection closes over downstream dependents.

Reusable verification belongs in `modules/verification/`; owner-specific expectations stay in `models/<id>/verification/`.

Pages is separate from CAD CI. Hugo reads source metadata and durable build evidence only. Verification-only owners are not public. Keep the established Hextra/CAD presentation baseline.

Do not resume Forge.NEW bulk migration until the current model-owner template change is green on `dev` and `main`.
