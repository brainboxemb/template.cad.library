# Library website presentation

The visual foundation follows template.cad.model-project and
2026-011-02.cad.solidcraft.NEW, derived from exp.2026-015.hugo-cad-site.
Reuse the existing CSS, footer and code block component. Native Hextra owns
documentation layout, search, sidebar and table of contents.

Physical owners remain under models/. Pages projects model.yml purposes to
Examples and Verification, with legacy Models routes as aliases. Both views
use the same catalogue and detail layouts. The adapter reads metadata,
declared implementation sources and durable owner/implementation evidence.
Displayed source is not represented as the built revision. Images and files
link directly to build; no generated artifacts are copied to Pages.

Public documentation is reader-oriented. Library-specific API, Guide and
Cheatsheet content belongs to the consumer. The generic landing and shared
style belong here.

PR Pages qualification captures desktop/mobile views of the home,
documentation, catalogues and model details from the generated site.
Visual acceptance and stable/development public route checks remain distinct
from a green Hugo build.
