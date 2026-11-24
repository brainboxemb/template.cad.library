# Repository plan

## Now

- #38: make the local `/merge` policy mandatory for agents, matching the stricter model-project/CAD NEW integration rule.
- #37: align CI/build/Pages workflow roles with `template.cad.model-project` so consumers do not inherit a second orchestration pattern.
- #25: qualify generic named verification stages across runtime roles. The first real consumer is Forge NEW historical simple-box: native saved-design/timeline verification in `solidcraft` plus mesh verification in `reference`.
- #12: restore the shared Hextra/CAD foundation using current template.cad.model-project and CAD NEW styling; qualify the current physical-owner/purpose projection and multi-engine evidence with rendered desktop/mobile screenshots before consumer adoption.
- #4: keep consumer migration open until Forge NEW is proven on the corrected template.

## Qualified baseline

- physical owner root is `models/`, matching `template.cad.model-project`;
- one owner can contain multiple engine implementations;
- `model.yml.purpose` may contain `example`, `verification`, or both;
- five standard builders are qualified through one `simple-box` owner;
- durable publication is owner-grouped below `build/<scope>/models/`;
- Pages links durable CAD artifacts instead of duplicating them.

## Next

- merge #25 after the multi-stage simple-box runtime run is green;
- consume #25 in `lib.py.solidcraft.forge.NEW#6` and qualify the historical saved-design case;
- migrate Forge physical models 1 -> 5 -> 10 -> remaining graph;
- retain the old Forge repository as A/B reference until parity is proven.
