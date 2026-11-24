# Repository plan

## Now

- #45: add generic library release qualification on durable build evidence and delegate publication to released `tool.py.lib.ci`.
- #25: qualify generic named verification stages across runtime roles. The first real consumer is Forge NEW historical simple-box: native saved-design/timeline verification in `solidcraft` plus mesh verification in `reference`.
- #12: restore the shared Hextra/CAD foundation using current template.cad.model-project and CAD NEW styling; qualify the current physical-owner/purpose projection and multi-engine evidence with rendered desktop/mobile screenshots before consumer adoption.
- #4: keep consumer migration open until Forge NEW is proven on the corrected template.

## Qualified baseline

- physical owner root is `models/`, matching `template.cad.model-project`;
- one owner can contain multiple engine implementations;
- `model.yml.purpose` may contain `example`, `verification`, or both;
- five standard builders are qualified through one `simple-box` owner;
- durable publication is owner-grouped below `build/<scope>/models/`;
- Pages links durable CAD artifacts instead of duplicating them;
- pull requests run only central `ci`; permanent `dev`/`main` runs use one `build` job and dispatch the independent Pages workflow after durable publication;
- every source-branch integration is executed through the local `/merge` policy; agents do not select or bypass merge methods;
- stable release qualification is independent of Pages and is based on exact durable `build/main` evidence plus explicit library qualification.

## Next

- adopt the accepted CI/build/Pages split and mandatory `/merge` governance in `lib.py.solidcraft.forge.NEW` without repository-local orchestration changes;
- merge #25 after the multi-stage simple-box runtime run is green;
- consume #25 in `lib.py.solidcraft.forge.NEW#6` and qualify the historical saved-design case;
- migrate Forge physical models 1 -> 5 -> 10 -> remaining graph;
- retain the old Forge repository as A/B reference until parity is proven.
