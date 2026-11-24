# Library website presentation

The technical Hugo pipeline is not a visual design baseline. Use the established Hextra CAD presentation from exp.2026-015.hugo-cad-site and its integration in template.cad.model-project (approved model-detail baseline documented in the source CSS). Reuse the CAD CSS, code-block partial, footer and framed page hierarchy. Do not redesign these components locally.

Library documentation uses native Hextra documentation pages. Example pages adapt the existing CAD homepage, catalogue and detail layouts to builder-independent metadata. The model project has a different build data contract, so its SolidCraft-specific content adapter is not copied verbatim.

Each public example is a Hugo leaf bundle projected in a temporary site. model.yml provides title, purpose, tagline, description, parameters, stages and priority. ci.yml provides builder and source path. Optional page.md provides background. Durable build scope provides result.json, source.json, verification report, and available model files. Source from the displayed branch is distinguished from the built source revision. No CAD code executes in Pages. Only purpose example (alone or combined with verification) enters the catalogue.

Missing previews and artifacts are not invented. Model previews must eventually be generated and published by the build layer. Optional SolidCraft native/command sections are shown only when present. Non-Python sources and richer reference views require further qualification as builders are introduced.

PR Pages qualification captures rendered desktop and mobile screenshots against actual durable evidence when available. Visual approval remains distinct from successful Hugo rendering; do not call this presentation complete until reviewed. No production CAD or experiment repository changes are made here.
