# CAD library template manual

## Branches and execution

Temporary branches use prefixes configured in ci.yml. Squash into dev; merge-commit promotion into main; reverse integration only for actual stable-only changes. The owner uses /merge once CI is green. Branch cleanup removes merged temporary branches.

Root ci.yml holds stable settings. Root build.yml is an exact work-branch selection:

```yaml
schema: 1
branch: issue/12-ci-change
modules: [ci]
tasks: [test]
```

Use modules: all for all modules. If the branch does not match, run full. Main and promotion PRs run full. Dev push/dispatch selects paths since the last successful dev push/dispatch CI SHA; missing or non-ancestor baseline falls back to full. Cancelled runs never advance that baseline.

## Library owner

Set library: true in a matching build.yml to test and package cadlib independently of modules and examples. Dev selects it on cadlib changes; main and promotion select it always. Tests run from source, then a wheel is built in an isolated source copy and included in the CI qualification artifact. This is package qualification, not a release. Examples declaring needs: [cadlib] are rebuilt on cadlib changes.

## Internal modules

Each module has ci.yml, pyproject.toml, src/ and tests/. Discovery uses module-local ci.yml; kind: python; impact: self or full; optional watch paths. Tests execute from source using unittest. CI installs ordinary third-party dependencies declared in pyproject.toml for selected modules only. The verification package is local source, not an external Git dependency. No root test suite. Verification is a normal Python module at modules/verification, selectable by its id; example-specific expectations belong with the example.

## CAD runtimes

Root ci.yml pins two immutable images: reference and solidcraft. PythonSCAD, pyBOSL2, CadQuery and build123d use reference; SolidCraft uses solidcraft. Local verification code is used in both roles as appropriate. Engine-neutral verification unit tests run on the host without CAD engines.

## Pages

Hugo 0.169.0 and Hextra 0.13.0 live in site/. CI dispatches a separate Pages workflow after successful main or dev CI, without waiting. During bootstrap dispatch is skipped until main contains the workflow. Pages independently builds both source scopes and publishes a combined tree to gh-pages, main at / and dev at /dev/. Pull requests verify the site without publishing.

Configure repository Pages to serve gh-pages at its root. A token or deployment mechanism that actually triggers GitHub Pages deployment may be required; a GITHUB_TOKEN branch push alone does not guarantee a Pages deployment. Verify the live site before accepting the baseline.

## Future extensions

The CAD library (cadlib) and examples are separate owners. Define their selection, verification, artifacts and documentation contracts before migration.
