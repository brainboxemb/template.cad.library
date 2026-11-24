# Repository plan

## Now

- #23: align the library template with `template.cad.model-project`: `models/` physical ownership, owner-level selection/publication and multiple engine implementations inside one owner.
- #12: rebase the Hextra CAD presentation onto the new model-owner contract after #23 is qualified.
- #4: keep consumer migration open until Forge is proven on the corrected template.

## Next

- Qualify one `simple-box` owner through all five standard engines and both runtime roles.
- Publish the corrected `build/dev/models/simple-box` scope and then promote #23 to `main`.
- Resume `lib.py.solidcraft.forge.NEW` bootstrap from the corrected template.
- Migrate Forge models 1 -> 5 -> 10 -> remaining graph; retain the old Forge repository as A/B reference until parity is proven.
