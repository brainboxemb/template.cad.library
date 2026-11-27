# Repository plan

## Now

### #108 — configurable qualification policy and PR evidence reuse

Implemented on `dev` by PR #109. Root `ci.yml` owns the optional docs-only
pull-request policy and the permanent lanes allowed to reuse an already-green
PR qualification.

Docs-only classification is fail-safe and lower priority than permanent-lane
promotion/release rules. A PR is lightweight only when its complete base→head
delta is below configured prefixes; it runs only configured lightweight
modules, with no library/model/API-probe qualification.

Permanent reuse prefers a merge-policy binding: before integration, `/merge`
binds the reviewed PR head and exact green PR CI run into the permanent workflow
dispatch. Until stable `main` carries that merge-policy revision, configured
permanent lanes may conservatively discover the single merged PR associated
with the permanent commit and use only the newest central PR run for its exact
head/ref. In both paths, the artifact's original `source_sha` is GitHub's
synthetic PR merge commit; that commit must have the reviewed base/head as its
two parents and its Git tree must exactly equal the permanent merge tree.
Durable evidence records the permanent `source_sha`, synthetic
`qualified_source_sha`, reviewed `qualified_head_sha`, PR number and CI run
id. Missing, ambiguous, failed, stale or mismatched evidence falls back to
normal CAD-CI.

PR #109 itself proved the lightweight infrastructure selection with only the
`ci` and `merge-policy` modules: 59 CI tests and 34 merge-policy tests passed
with zero selected models and zero selected API probes. A separate docs-only PR
now verifies the configured path classification against the merged `dev`
implementation.

Pages remains asynchronously dispatched after durable build publication; CAD
compiler qualification does not wait for Pages deployment.

### #106 — explicit API-probe runs and isolated publication

Keep `ci.yml` as the permanent API-probe capability/root contract and
`build.yml` as the temporary branch-local override. Add a dedicated API Probe
workflow that can run existing probes against `main`, `dev`, `exp` or
another requested source without changing source configuration.

Probe publication must be independent from model publication: selected probes
replace only their own `build/<scope>/api-probes/<id>/` evidence; unselected
probes and all `models/` output remain untouched. Ordinary model/library builds
must preserve existing probe evidence.

### #95 — latest PR-specific central CI in merge policy

When the same permanent head SHA is reused by a replacement pull request,
GitHub can associate historical failed checks from the superseded PR with the
new PR. Merge policy must validate the newest central `pull_request` CI run
for the exact head/PR instead of requiring every historical check on that SHA
to be green.

Keep the gate fail-closed: no current PR CI, a latest pending run, or a latest
failed run still blocks integration. This is merge-policy infrastructure only;
CAD/model/release semantics remain unchanged.


### #90 — reviewed conflict recovery for permanent branch merges

Restore the reviewed `/merge-resolved` contract lost during the local
merge-policy migration. Keep normal `/merge` unchanged; a separate green
`resolve/*` review PR must bind the exact resolved tree for a genuinely
conflicted direct permanent merge. This is required before canonical Forge can
complete its current `dev -> exp` synchronization without squash, rebase or
manual ref mutation.




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
