# Agent guidance

Read `docs/plan.md`, `docs/design.md` and `docs/manual.md` before changing the repository.

Work from a temporary branch based on `dev`. Set `build.yml.branch` to the actual branch and select the necessary library, modules and **physical model owners**. Squash temporary branches into `dev`; promote `dev` to `main` with a merge commit.

The repository root for CAD ownership is `models/`, matching `template.cad.model-project`. Do not reintroduce `examples/` as an execution owner root.

One `models/<id>/` directory is one physical owner. Multiple engine implementations belong under that owner and are declared in its `ci.yml`. Do not create sibling owners such as `model-build123d` or `model-solidcraft` solely to represent engines.

`model.yml.purpose` may contain multiple purposes. Supported values are `example` and `verification`; `[example, verification]` is valid.

Builders, verifier adapters and previews declare runtime capabilities locally. Central CI schedules owners, implementation tasks, verification stages and runtime roles but must not contain engine-specific branches.

A model may declare multiple named verification stages. Stage evidence must remain isolated below the stage id; a later runtime may not overwrite an earlier stage report. Keep the legacy single `verification:` mapping backward compatible.

Preview is presentation, not verification. When enabled it runs only after every applicable verification stage for that implementation has passed.

Preserve the two released runtime roles; do not add a third verification image.

Physical model dependencies name owner ids. Selection closes over downstream dependents.

Reusable verification belongs in `modules/verification/`; owner-specific built-artifact expectations stay in `models/<id>/verification/`. Optional `models/<id>/tests/` are owner-local source/compiler contract tests and run only with that selected owner; do not move them into `cadlib/tests` unless the contract is genuinely package-wide.

Pages is separate from CAD CI. Hugo reads source metadata and durable build evidence only. Project model purposes into Examples and Verification without duplicating physical owners or generated artifacts. Keep the established Hextra/CAD presentation baseline.
