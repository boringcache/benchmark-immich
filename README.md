# benchmark-immich

Isolated Immich benchmark runner for BoringCache vs GitHub Actions cache.

This repo exists separately from the central benchmarks publisher so Immich can have:

- a pinned upstream source commit
- isolated GitHub Actions cache usage
- one shared BoringCache workspace name: `boringcache/benchmarks`
- independent benchmark runs triggered by upstream sync commits and the nightly schedule

## Source Model

- upstream app source lives in the pinned `upstream/` submodule
- `Dockerfile.benchmark` is benchmark-owned and committed here

Pinned upstream source:

- see committed `upstream/` submodule on `main`

## Scenarios

- `cold`
- `warm1`

On the BoringCache side, these runs restore/save internal caches for pnpm, mise, native libraries, and server/cli incremental build outputs so source-level rebuild behavior can be measured separately from Docker layer reuse.

## Token Model

This repo uses split BoringCache tokens as the standard CI shape:

- `BORINGCACHE_RESTORE_TOKEN` for read-only restore and proxy access
- `BORINGCACHE_SAVE_TOKEN` for trusted write paths
- `BORINGCACHE_API_TOKEN` only where a single bearer variable is still required for compatibility

## Output

Each workflow uploads machine-readable JSON and Markdown summaries. Those artifacts are intended to be ingested by the central `boringcache/benchmarks` publisher later.
