# Repository plan

## Now

- #4: complete cadlib and standard builder integration; local verification module is qualified and merged to dev.
- #6: first CadQuery vertical slice; qualify runtime, negative verification, durable build scope and Hugo evidence. The first PR covers builder, selection, one runtime batch and CI evidence.

## Next

- Wire cadlib packaging/unit tests into CI.
- Add persistent generated build scope and Hugo evidence for #6 before expanding.
- Implement PythonSCAD, pyBOSL2, build123d and SolidCraft incrementally using the two pinned runtime roles.
- Migrate Forge and other consumers away from the external verification dependency; do not retire the source repository prematurely.
- Integrate API/reference and example documentation into Hugo; replace the existing custom Forge site during migration.
