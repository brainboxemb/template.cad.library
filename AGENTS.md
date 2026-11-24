# Agent guidance

Read `docs/plan.md` and `docs/manual.md` before changing the repository.

Work from a temporary branch based on `dev`; set `build.yml.branch` to the actual branch and select the necessary library/modules/examples. Squash temporary branches into `dev`. Promote `dev` to `main` using a merge commit. Merge `main` back only for actual stable-only content. Never clean up `main`, `dev`, `build` or `gh-pages`.

Internal Python capabilities own `ci.yml`, `pyproject.toml`, `src/` and `tests/`. Keep workflows thin and run capabilities directly from source. Do not add a central module or engine registry.

Builders, verifiers and previews declare their own runtime capability. Keep engine behavior in the owning module. Central CI may schedule capabilities and runtime roles but must not contain CadQuery/build123d/PythonSCAD/pyBOSL2/SolidCraft branches.

Preserve the two released runtime roles. A SolidCraft build runs in `solidcraft`; generic mesh verification runs in `reference`. Do not merge the images and do not add a third verification image.

Matching work-branch `build.yml` controls selection; stale selections are ignored. `dev` selects changes since the last successful integration CI run. `main` and `dev -> main` promotion run full. Cancel superseded runs. Keep generated output below `build/`.

The `cadlib` and examples roots are separate owners. Reusable verification belongs in `modules/verification`; example-owned expectations stay in the example. Verification-only fixtures must not enter the public catalogue.

Pages is separate from CI. Hugo reads documentation and durable build evidence; it never executes CAD or verification. Publish `main` at `/` and `dev` at `/dev/` on `gh-pages`. Keep the established Hextra/CAD presentation baseline rather than inventing a second site style.
