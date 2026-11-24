# Library source

This root owns the consumer's CAD library source, package metadata and unit tests. Rename the starter distribution and package to the actual library identity when adopting the template. For Forge this does not require renaming the existing SCPF API.

Select the library with library: true in the matching build.yml. CI runs its tests directly from source and builds a qualification wheel. No release is created by this step.
