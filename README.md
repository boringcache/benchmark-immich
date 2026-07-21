# benchmark-immich

Isolated Immich benchmark runner for BoringCache vs GitHub Actions cache.

This repo exists separately from the central benchmarks publisher so Immich can have:

- a pinned upstream source commit
- isolated GitHub Actions cache usage
- one per-repo BoringCache workspace name: `boringcache/benchmark-immich`
- independent benchmark runs triggered by upstream sync commits and manual dispatches

## Source Model

- upstream app source lives in the pinned `upstream/` submodule
- workflows build the upstream Dockerfile with `upstream/` as the Docker context

Pinned upstream source:

- see committed `upstream/` submodule on `main`

## Scenarios

- `cold`
- `warm1`

Fresh lane runs a no-prior-cache cold build plus one warm rerun on the same pinned source tree. Rolling lane records the upstream commit build as-is after each upstream sync against the prior rolling cache and skips `warm1`.

BoringCache compares the explicit registry/OCI cache path and the managed BuildKit backend path. It does not call BoringCache inside Dockerfile `RUN` steps, and upstream Dockerfile cache mounts stay native to BuildKit.

Scheduled, PR, and rolling-dispatch runs use [`.github/workflows/immich-benchmark.yml`](.github/workflows/immich-benchmark.yml), which runs GitHub Actions Cache, BoringCache OCI, and the managed BoringCache BuildKit backend side by side. ECR is retired; historical ECR runs remain available as evidence. Docker tool-cache lanes are intentionally absent until Immich has a static supported Turbo/Nx/sccache contract inside the measured Dockerfile.

## Token Model

This repo uses split BoringCache tokens as the standard CI shape:

- `BORINGCACHE_RESTORE_TOKEN` for read-only restore and proxy access
- `BORINGCACHE_SAVE_TOKEN` for trusted write paths
- `BORINGCACHE_API_TOKEN` only where a single bearer variable is still required for compatibility

## Output

Each workflow uploads machine-readable JSON and Markdown summaries. Those artifacts are intended to be ingested by the central `boringcache/benchmarks` publisher later.
