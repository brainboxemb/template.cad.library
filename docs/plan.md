# Repository plan

## Now

- #4: standard library architecture is implemented: independent cadlib owner, five standard builders, local verification, previews, examples, two runtime roles and durable build publication. Remaining acceptance is consumer migration before the historical verification repository can be retired.
- #12: qualify the established Hextra CAD presentation visually and on public main/dev routes.

## Next

- Promote the completed five-builder baseline from `dev` to `main` after permanent-branch qualification.
- Migrate Forge onto this repository structure and remove its external verification dependency only after equivalent CI/build/site behavior is proven.
- Adapt the generic example presentation to richer consumer metadata as real Forge examples are migrated; do not add template-only page conventions without a consumer need.
