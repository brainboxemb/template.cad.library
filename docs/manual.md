# CAD library template manual

## Branches and selection

Temporary branches are based on `dev`; squash them into `dev`. Promote `dev` to `main` with a merge commit. Root `build.yml` is an exact branch-local execution plan:

```yaml
schema: 1
branch: issue/25-multi-stage-verification
modules: [ci, verification]
library: false
models: [simple-box]
tasks: [test]
```

Use `modules: all` or `models: all` for full selection. `main` and `dev -> main` promotions run full. Permanent `dev` runs select changes since the last successful integration run; missing history falls back to full.

### Merge execution

The merge shape is policy-owned, not agent-selected. For every source-branch integration, post `/merge` on the pull request and let `.github/workflows/merge-policy.yml` execute the merge.

The policy chooses:

- short-lived branch -> `dev`: squash;
- `dev` -> `main`: merge commit;
- exceptional `main` -> `dev`: merge commit.

Do not use the direct GitHub merge API, auto-merge, a UI/manual fallback, or manual squash/merge/rebase selection. If `/merge` fails, repair the policy path rather than bypassing it.

## Library owner

`cadlib/` is independent of model owners and internal modules. Selecting the library runs its source tests and builds one qualification wheel. This is not a release.

A model can declare `needs: [cadlib]`; library changes then select that model and its downstream dependents.

## Model owners

`models/<id>/` is the physical ownership boundary. It owns:

- one `ci.yml` for execution;
- one `model.yml` for presentation and purpose;
- one or more implementation source directories;
- shared model-specific verification expectations.

Do not create separate model owners merely because the same geometry is implemented by different engines.

### Purpose

`model.yml.purpose` can contain one or more purposes:

```yaml
purpose: [example, verification]
```

`example` selects the Examples view. `verification` selects the Verification view. Both are allowed together; they project one physical model owner.

### Multiple implementations

A single owner can qualify multiple engines:

```yaml
primary: cadquery
implementations:
  - id: cadquery
    builder: builder-cadquery
    source: cadquery/model.py
  - id: build123d
    builder: builder-build123d
    source: build123d/model.py
  - id: solidcraft
    builder: builder-solidcraft
    source: solidcraft/commands.json
    preview: false
```

CI selects the owner once and expands all implementations. Builder module changes also select every owner that uses that builder. A model may additionally own `tests/`; those Python tests run only when that physical owner is selected, with `cadlib/src` on `PYTHONPATH`. They are intended for source/compiler contracts and do not replace built-artifact verification stages.

## Verification stages

A model can declare one or more named verification stages. The verifier module owns adapter-to-runtime mapping; the model only selects the adapter, definition, generated artifact and optional implementation filter.

```yaml
verifications:
  - id: native
    module: verification
    adapter: solidcraft-model
    definition: verification/solidcraft.py
    artifact: model.sc
    implementations: [solidcraft]

  - id: geometry
    module: verification
    adapter: mesh-geometry
    definition: verification/geometry.json
    artifact: model.stl
```

The current local verification module declares:

- `solidcraft-model` -> `solidcraft`;
- `mesh-geometry` -> `reference`.

A stage without `implementations` applies to every implementation. Each implementation must have at least one applicable stage.

For compatibility, the previous single `verification:` mapping is still accepted and becomes one `model.stl` verification stage.

Stage evidence is retained independently below:

```text
models/<owner>/<implementation>/verification/<stage>/
  verification.json
  stage-result.json
```

A later stage never overwrites earlier evidence. Implementation status passes only if its build, all applicable stages and configured preview pass.

## Dependencies

`dependencies` contains physical model owner ids. A selected dependency selects all downstream consumers transitively. This intentionally matches `template.cad.model-project`.

## Standard builders and runtime roles

The five standard builder modules are PythonSCAD, pyBOSL2, CadQuery, build123d and SolidCraft.

Reference engines share `cad-reference:v0.3.5`. build123d uses its isolated interpreter inside that container. SolidCraft builds in `cad-solidcraft:v0.3.5`.

Builder, verifier and preview runtimes are declared independently. CI derives one dependency graph and starts every required role at most once for the selected batch.

For the qualification box:
1. SolidCraft builds and runs its native SolidCraft verification in `solidcraft`;
2. all five implementations run geometry verification in `reference`;
3. reference previews run only after all applicable verification stages have passed.

No third verification image is used.

## Durable output

Successful permanent-branch CI publishes owner-grouped output below `build/<scope>/models/`. The owner root contains aggregate status and canonical primary artifacts; each implementation retains its own build, staged verification and preview evidence.

Pull requests upload candidate evidence but do not publish generated branches.

## Pages

Pages is separate from CAD CI. Hugo consumes `models/` metadata and the corresponding durable build scope. Examples and Verification are purpose-driven public views. Owners with both purposes appear in both views without duplicating physical ownership or generated artifacts. When implementation results contain named `verification_stages`, Pages renders each stage status and links the stage-local durable report. Legacy/single-stage results remain supported through the aggregate verification status and compatibility report link.

Stable content is published at `/` and development content at `/dev/`.
