# BoringCache Immich benchmark

This repository contains the BoringCache benchmark for Immich.

Benchmark workflows are in [`.github/workflows/`](.github/workflows/), with configuration in [`.boringcache.toml`](.boringcache.toml).

The `base_images_ccache_experiment` mode of the manual Immich benchmark compares
the GitHub Actions cache, BoringCache's Docker layer cache, and BoringCache's
Docker layer cache plus ccache. It rebuilds `base-server-dev` across a pinned
Node base-image bump on fresh runners so compiler-object reuse is not confused
with local BuildKit state.

The scheduled upstream sync automatically accepts new immutable revisions of Immich's reusable build workflow when the server context, Dockerfile, and CPU build argument remain compatible. A meaningful recipe change fails verification before the updated submodule is committed to `main`.
