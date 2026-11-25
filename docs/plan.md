# Repository plan

## Now

### #62 — avoid full model qualification for history-only main -> dev sync

Keep the accepted stable release flow, but remove the unnecessary full model
qualification when already-qualified stable-only history is synchronized back
to `dev`.

The lightweight path must prove that synchronized commits were already accepted
on stable `main`, contain no product/source/model delta that requires normal
qualification, and fail closed otherwise. Normal `dev -> main` promotion
remains full.

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
- the #47 stable-main release branch flow is accepted on template `main`
  and consumed by canonical Forge.
