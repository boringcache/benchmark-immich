# benchmark-immich

Isolated Immich benchmark runner for BoringCache vs GitHub Actions cache.

This repo exists separately from the central benchmarks publisher so Immich can have:

- a pinned upstream source commit
- isolated GitHub Actions cache usage
- one shared BoringCache workspace name: `boringcache/benchmarks`
- independent nightly benchmark runs

## Source Model

- upstream app source lives in the pinned `upstream/` submodule
- `Dockerfile.benchmark` is benchmark-owned and committed here
- stale scenarios are committed patches in `scenarios/`

Pinned upstream source:

- `immich-app/immich@dd97395f3ac72975af2daec584ebd29dac1f7f66`

## Scenarios

- `cold`
- `warm1`
- `warm2`
- `stale-low`: one server source file change
- `stale-mid`: one `package.json` metadata change
- `layer-miss`: `--no-cache` Docker rebuild on the same pinned tree

## Token Model

This repo uses split BoringCache tokens as the standard CI shape:

- `BORINGCACHE_RESTORE_TOKEN` for read-only restore and proxy access
- `BORINGCACHE_SAVE_TOKEN` for trusted write paths
- `BORINGCACHE_API_TOKEN` only where a single bearer variable is still required for compatibility

## Output

Each workflow uploads machine-readable JSON and Markdown summaries. Those artifacts are intended to be ingested by the central `boringcache/benchmarks` publisher later.
