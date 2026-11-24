# CAD builder qualification

The first example is a 40 x 30 x 10 mm CadQuery box based at Z=0. Its independently authored geometry contract checks bounds, volume and watertightness.

Each module declares a builder capability (runtime and Python entrypoint) or verifier capability (Python entrypoint) in its local ci.yml. An example declares its builder, source, verification module, adapter and definition. Optional needs declares additional module or cadlib dependencies. CI groups selected examples by runtime and starts one Docker container per role; local source directories are mounted read-only. Build and verification adapters are resolved from module metadata, not from a central engine switch.

This first contract currently exports STL. The generic runtime dispatcher records build status, verification status and a batch report. A failed verification fails the batch. Outputs are written below build/qualification/examples/<id>/. Persistent build-branch publication and Hugo evidence integration are separate outstanding acceptance steps of #6.

Temporary branch example selection is explicit in build.yml. Dev derives example selection from changed example paths and selected dependency modules; main runs all. Additional isolated interpreter handling, native SolidCraft artifacts and non-STL formats will be added when their builders are qualified.
