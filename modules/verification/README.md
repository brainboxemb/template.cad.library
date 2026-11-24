# Verification module

A normal independent Python capability. Reusable project-specific checks and adapters belong in this module; model-specific expectations belong with the example. Generic comparison and evidence mechanics are delegated to the existing CAD verification library.

The starter unit tests run through normal module CI. To exercise the actual pinned external dependency locally:

```sh
python -m pip install -e modules/verification
python -m unittest discover -s modules/verification/tests -v
```

The external-package integration tests explicitly skip when the dependency is not installed. Qualification of that dependency in CI is tracked in #4.
