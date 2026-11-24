# Repository plan

## Now

- #1: qualify base CI, merge/cleanup, Hugo/Hextra and live Pages deployment. Main and dev CI and generated gh-pages are green; live deployment still needs confirmation.
- #4: establish cadlib, examples and reusable verification module structure; agree on independent item selection and builder/verification interfaces.

## Next

- Wire cadlib packaging/unit tests and verification module tests into CI.
- Implement standard Python/OpenSCAD, BOSL, CadQuery, build123d and SolidCraft builders; confirm runtime/toolchain pins and qualify incrementally.
- Integrate examples, explicit verification actions, example-owned expectations and generated build scopes.
- Decide whether the generic verification library remains independent or is reorganized; preserve engine-neutral verification.
- Integrate API/reference and example documentation into Hugo; replace the existing custom Forge site during migration.
