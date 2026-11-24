# Library website presentation

## Visual foundation

The visual foundation follows `template.cad.model-project` and
`2026-011-02.cad.solidcraft.NEW`, derived from
`exp.2026-015.hugo-cad-site`. Reuse the existing CSS, footer and code-block
component. Native Hextra owns documentation layout, search, sidebar and table
of contents.

## Information architecture: historical Forge comparison

Shared visual styling is not sufficient to qualify library model pages.
Forge Verification is an engineering explanation and comparison page, not a
product CAD file/download page.

The historical Forge site is the information-architecture reference:
`brainboxemb/lib.py.solidcraft.forge`, current `gh-pages` plus
`backup/gh-pages-before-f11-2026-11-20`. Inspected public route equivalents:

- `verification/simple-box/`;
- `verification/anchored-holes/`;
- `verification/components/`;
- `examples/simple-box/`;
- backup `qualification/simple-box/`.

Relevant historical source: `site/templates/qualification-case.html`,
`qualification-reference-row.html`, `qualification-current.html`,
`example.html`, `site/html_writer.py`, and
`docs/background/pages-content-parity.md`.

| Historical content | Required presentation in the new library foundation |
| --- | --- |
| What this example makes; expected setup diagram | Introduce the intended model, show the expected geometry first. The historical setup SVG is a conceptual projection of declared expected body envelopes, not a render of actual geometry. |
| Native/primary model preview | Show the actual published primary result near the expectation, with distinct labels. |
| Goal, API used, model and geometry rationale | Preserve model-owned engineering explanation and requirements; do not replace it with a Files panel or a generic code example. |
| Complete Forge code | Display the primary implementation source in full, without requiring disclosure. |
| Generated command sequence | Show the actual durable command sequence where an implementation produces one, before the independent reference comparison. This is explicit in the old Examples page; the old Verification page additionally exposes lowering and raw command evidence. Do not invent commands for engines that do not produce them. |
| Reference code | For each declared independent implementation, show the source beside its own result image, with status, artifact links and expected-versus-measured evidence. Stack these columns on narrow screens. Show the source even when no preview or evidence exists. |
| Native result, editable parameters, body sizes and saved-design results | Retain the available current evidence; do not reduce it to a single PASS badge. |
| Visual actual/goal/overlay/diff | Present when there is a current visual verification policy and current artifacts. Never relabel historical or ordinary presentation images as a current visual PASS. |
| Verification checks, geometry evidence, reference notes and raw test files | Retain access to actual checks and provenance, with technical details lower on the page. |

The historical audit distinguishes Examples and Verification. The requested
new reading flow intentionally combines the strongest parts of both:
featured SolidCraft/expected imagery first, then the complete featured
SolidCraft/SCPF source, then the generated command sequence in a collapsed
disclosure, then independent reference source beside each result. Only after
that come the consolidated image and check overviews. Engineering/background
material and raw technical evidence follow those primary comparisons. Exact historical Examples and Verification compositions
are not identical; preserve their distinct purpose rather than blindly
copying the historical HTML. Use shared components for both views.

## Ownership and data

Physical owners remain under `models/`. Pages projects
`model.yml.purpose` into Examples and Verification, with legacy Models
routes as aliases. Both views can reuse the same layout components without
duplicating model owners.

The adapter reads model metadata, model-owned engineering prose, declared
implementation sources, expectations and durable owner/implementation
evidence. Displayed source is not represented as the built revision.
Images and files link directly to `build`; generated CAD artifacts are
not copied to Pages. A conceptual expected-setup SVG may be produced as a
presentation-only diagram from declared expected values, without running
CAD or deriving the expectation from measured geometry.

Forge NEW already retains the model explanation in `models/<id>/page.md`,
generated SCPF command JSON, native baseline/saved-design reports and the
independent implementation previews under `build/<scope>/models/<id>/`.
For example, the native baseline report for simple-box exposes declared
expected body envelopes separately from actual values. The geometry report
also retains expected bounds. These can support a generic presentation
adapter without importing or executing model/verification Python.

Historical visual-baseline and setup-diagram coverage must be audited
separately during Forge migration. A native/geometry acceptance gate alone
does not prove visual-evidence or presentation parity.

Public documentation is reader-oriented. Library-specific API, Guide and
Cheatsheet content belongs to the consumer. The generic landing and shared
style belong here.

## Acceptance status

The earlier draft's shared CSS and basic Hugo layout passed technical
qualification, but the model-detail information architecture was incomplete:
it begins with a generic preview/files panel, lacks a separate expected-setup
diagram and command sequence, and puts independent source blocks apart from
their result images. A passing screenshot job is not acceptance of this layout.

The revised candidate implements the expected/actual overview, engineering
prose, primary source, durable command sequences, independent source/preview
rows and per-stage report details. Verify this composition before consumer
adoption. Current visual actual/goal/overlay/diff migration and a dedicated
presentation for native parameter and saved-design measurements remain open;
reports preserve the exact machine evidence in the meantime. Compare the rendered full page,
not only the first viewport. Require visible expectation/result distinction,
primary source, applicable generated commands, side-by-side reference
comparisons, and access to real verification evidence. Capture representative
Examples and Verification desktop/mobile screenshots; verify links, route
order, absence of fabricated evidence and durable artifact ownership.
Stable/development public route checks and user visual acceptance remain
separate from successful Hugo rendering.

## Presentation order clarification

The featured SolidCraft snapshot comes first, alongside the separately labelled
expected setup. Its source is immediately followed by a collapsed generated
command sequence, then independent source/image rows, then a consolidated image
and check overview and raw report details. The builder-produced native
`model.png` is used directly, with no fallback to owner-level STL preview.
For the template's simple-box, `model.yml.presentation_primary: solidcraft`
selects the presentation subject without changing `ci.yml.primary: cadquery`.
For Forge, the default SCPF build primary already identifies the native subject.
Verification report image artifacts are displayed only when present, preserving
stage/check provenance. An ordinary model preview is not a visual comparison.

The consolidated check overview additionally displays explicit expected/measured
values from the published report, including native parameter pairs, body
envelopes, geometry bounds and saved-design checks where available. No new
verification decisions are made in Pages; raw report links remain available.
Historical visual comparison policy migration is still a separate task.

## Exact historical route audit

The generated historical pages were inspected directly, not inferred from
current templates.

Historical `verification/simple-box/` order is: hero; What this example makes
with setup diagram and native SolidCraft preview; complete Forge source + API;
Reference code with one source/result row per PythonSCAD, pyBOSL2, CadQuery and
build123d; lowering explanation; native SolidCraft measurements/saved-design;
visual verification grouped by view; collapsed technical checks/raw evidence;
sources of truth.

Historical `examples/simple-box/` order is: hero; one large model image;
stages + goal; engineering explanation; Python source and generated command
sequence; provenance notice.

The template target is not a blind copy of either route. It follows the user
specified hybrid order: SolidCraft/expected images → featured source → collapsed
commands → reference source + own result → all images → all checks → background
and raw evidence. This order is now an explicit rendered-site assertion.
