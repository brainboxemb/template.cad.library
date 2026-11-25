# Repository plan

## Now

### #47 — separate release metadata from product promotion

Complete and qualify the generic stable-main release lane:

- normal product work remains short-lived branch -> `dev`, with explicit
  `dev -> main` promotion only when product stabilization is intended;
- `release/vX.Y.Z` starts from stable `main`;
- release branches may change only `CHANGELOG.md` and
  `cadlib/pyproject.toml`;
- release PR/main-push qualification selects library + release only;
- release-only stable commits preserve the prior full `build/main` product
  evidence instead of rebuilding unchanged model owners;
- release validation proves every stable commit since that durable baseline is
  linear and metadata-only;
- publication still targets exact current `main` HEAD;
- after publication synchronize `main -> dev`; never rebase permanent
  branches.

After #47 is accepted on `dev`, promote the generic policy/capability to
template `main` so issue-comment merge policy can actually authorize future
`release/* -> main` integrations.

## Qualified baseline

- physical owner root is `models/`, matching `template.cad.model-project`;
- one owner can contain multiple engine implementations;
- `model.yml.purpose` may contain `example`, `verification`, or both;
- five standard builders are qualified through one `simple-box` owner;
- durable publication is owner-grouped below `build/<scope>/models/`;
- Pages links durable CAD artifacts instead of duplicating them;
- pull requests run only central `ci`; permanent `dev`/`main` runs use one
  `build` job and dispatch independent Pages after durable publication;
- every source-branch integration is executed through local `/merge` policy;
- generic durable library release qualification and shared
  `tool.py.lib.ci` publication are already accepted;
- merge policy now has the `release/* -> main` branch classification on
  `dev`; #47 completes the evidence/selection half before stable promotion.

## Next

1. consume accepted #47 in canonical `lib.py.solidcraft.forge` (#98);
2. then resume the Forge Pages quality phase;
3. keep unrelated historical template migration work out of this release-flow
   change.
