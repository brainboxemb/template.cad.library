---
title: Reading model pages
weight: 10
---

Each model page brings the geometry, source and published build evidence together.

## Choose a model

Use [Examples](../../examples/) to explore practical models or [Verification](../../verification/) to inspect models used to qualify CAD behaviour. A model can appear in both catalogues.

## Inspect the geometry

The model preview shows the published result of the primary implementation. Where available, the Files panel links to the corresponding STL, native model and other build artifacts.

A missing preview or file means that the corresponding artifact is not available in the published build.

## Read the source

The primary implementation is open by default. Expand the other source sections to compare how different CAD engines construct the same model.

For example, a centred box in CadQuery can be described as:

```python
import cadquery as cq

model = cq.Workplane("XY").box(40, 30, 10)
```

The displayed source comes from the site branch. The build revision recorded in the evidence section identifies the source used to produce the published artifacts.

## Understand verification

Each implementation has its own build and verification status. Named verification stages may check different properties, such as mesh geometry or the native CAD document. Open an available stage report to inspect its checks.

A model is marked Verified when its published result reports a passing status. No published build evidence is displayed explicitly when it is unavailable.
