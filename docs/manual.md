# CAD library template manual

## Branches and selection

Temporary branches are based on `dev`; squash them into `dev`. Promote `dev` to `main` with a merge commit. Root `build.yml` is an exact branch-local execution plan:

```yaml
schema: 1
branch: issue/23-model-owners
modules: [ci]
library: false
models: [simple-box]
tasks: [test]
```

Use `modules: all` or `models: all` for full selection. `main` and `dev -> main` promotions run full. Permanent `dev` runs select changes since the last successful integration run; missing history falls back to full.

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

`example` makes the owner public in Pages. `verification` marks it as qualification material. Both are allowed together.

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
  - id: pythonscad
    builder: builder-pythonscad
    source: pythonscad/model.py
  - id: pybosl2
    builder: builder-pybosl2
    source: pybosl2/model.py
  - id: solidcraft
    builder: builder-solidcraft
    source: solidcraft/commands.json
    preview: false
```

CI selects the owner once and expands all implementations. Builder module changes also select every owner that uses that builder.

## Dependencies

`dependencies` contains physical model owner ids. A selected dependency selects all downstream consumers transitively. This is intentionally the same model as `template.cad.model-project`.

## Standard builders and runtimes

The five standard builder modules are:

- PythonSCAD;
- pyBOSL2;
- CadQuery;
- build123d;
- SolidCraft.

Reference engines share `cad-reference:v0.3.5`. build123d uses its isolated interpreter inside that container. SolidCraft builds in `cad-solidcraft:v0.3.5`; mesh verification follows in the reference runtime.

## Verification and preview

Owner-local `verification/` contains expectations. Reusable verification logic lives in `modules/verification/`. A single geometry contract can therefore qualify equivalent implementations of the same physical model.

The configured preview module runs after successful verification. An implementation can set `preview: false` when its builder already produces a native preview, as SolidCraft does.

## Durable output

Successful permanent-branch CI publishes owner-grouped output below `build/<scope>/models/`. The owner root contains aggregate status and canonical primary artifacts; each implementation retains its own output below an implementation subdirectory.

Pull requests upload candidate evidence but do not publish generated branches.

## Pages

Pages is separate from CAD CI. Hugo consumes `models/` metadata and the corresponding durable build scope. Verification-only owners are excluded; an owner containing both `example` and `verification` is public.

Stable content is published at `/` and development content at `/dev/`.
