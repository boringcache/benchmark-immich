# BoringCache Immich benchmark

This repository contains the BoringCache benchmark for Immich.

Benchmark workflows are in [`.github/workflows/`](.github/workflows/), with configuration in [`.boringcache.toml`](.boringcache.toml).

The scheduled upstream sync automatically accepts new immutable revisions of Immich's reusable build workflow when the server context, Dockerfile, and CPU build argument remain compatible. A meaningful recipe change fails verification before the updated submodule is committed to `main`.
