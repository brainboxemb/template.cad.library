# Repository plan

## Now

- #1: qualify base CI, merge/cleanup, Hugo/Hextra and live Pages deployment. Main and dev CI and generated gh-pages are green; live deployment still needs confirmation.
- #4: establish cadlib, examples and reusable verification module structure; agree on independent item selection and builder/verification interfaces.

## Next

- Wire cadlib packaging/unit tests into CI and qualify the integrated local verification code and functional tests.
- Implement standard PythonSCAD, pyBOSL2, CadQuery, build123d and SolidCraft builders using the two pinned runtime roles and qualify incrementally.
- Integrate examples, explicit verification actions, example-owned expectations and generated build scopes.
- Migrate Forge and other consumers away from the external verification dependency; do not retire the source repository prematurely.
- Integrate API/reference and example documentation into Hugo; replace the existing custom Forge site during migration.
