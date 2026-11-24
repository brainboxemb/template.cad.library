# Verification modules

Copy _template to a new verification/<id>/ directory, rename the package and module id, and replace the illustrative check with consumer-specific checks. Each module owns ci.yml, pyproject.toml, src/ and tests/. Generic checks and evidence use lib.py.cad.verification; example-specific expectations remain under examples/<id>/verification/.

The starter is intentionally not registered with CI. Its tests require the qualified external verification package. See docs/design.md and issue #4 for the pending CI integration.
