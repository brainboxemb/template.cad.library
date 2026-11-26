# Repository plan

## Now


### #77 — bind permanent dispatches to the current branch head

Make policy-dispatched permanent qualification robust against GitHub event-SHA
lag immediately after a merge. The build job must explicitly check out the
current permanent ref, resolve that checked-out SHA once, and use it for CI
history selection and durable publication while retaining the publisher's
fail-closed source freshness check.


### #73 — optional experimental integration line

Implement the `exp` branch contract tracked in [#73](https://github.com/brainboxemb/template.cad.library/issues/73). Preserve stable release semantics. Qualify merge policy, CI/history, build publication, Pages and cleanup before Forge adoption.

### #67 — preserve stable full baseline for workflow-dispatched release-only builds

Merge policy starts permanent stable qualification with
`workflow_dispatch`. Treat a single-parent metadata-only stable commit from
that dispatch exactly like the already-qualified push case:

- select only `release` + library;
- select zero models;
- record `full: false` and `release_only: true`;
- preserve the previous full `build/main` product evidence;
- keep product-changing stable commits and merge commits full/fail-closed.

After #67 is qualified on `dev`, promote the template correction to
`main` so canonical consumers such as Forge can consume it before their next
release.

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
