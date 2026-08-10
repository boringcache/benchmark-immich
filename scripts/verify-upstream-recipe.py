#!/usr/bin/env python3
"""Verify Immich's amd64 server image benchmark plan."""

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCRIPT = "source_sha=$(git -C upstream rev-parse HEAD); build_id=${GITHUB_RUN_ID:-local}; source_ref=${GITHUB_REF_NAME:-local}; exec docker buildx build --file upstream/server/Dockerfile --platform linux/amd64 --build-arg BUILD_ID=${build_id} --build-arg BUILD_IMAGE=ghcr.io/immich-app/immich-server:${source_ref} --build-arg BUILD_SOURCE_REF=${source_ref} --build-arg BUILD_SOURCE_COMMIT=${source_sha} --build-arg DEVICE=cpu --tag immich-server-benchmark:local upstream"

def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)

def main() -> int:
    try:
        command = tomllib.loads((ROOT / ".boringcache.toml").read_text())["adapters"]["docker"]["command"]
        require(command == ["bash", "-euo", "pipefail", "-c", EXPECTED_SCRIPT], "Docker plan changed")
        upstream = (ROOT / "upstream/.github/workflows/docker.yml").read_text()
        for fragment in ("uses: immich-app/devtools/.github/workflows/multi-runner-build.yml@50dc3a14f0606ecd8fc28d78d3a3c655115ab695", "context: .", "dockerfile: server/Dockerfile", "DEVICE=cpu"):
            require(fragment in upstream, f"upstream server job changed: {fragment}")
        action = (ROOT / ".github/actions/immich-docker-benchmark/action.yml").read_text()
        for fragment in ("BUILD_ID=${{ github.run_id }}", "BUILD_IMAGE=ghcr.io/immich-app/immich-server:${{ github.ref_name }}", "BUILD_SOURCE_REF=${{ github.ref_name }}", "BUILD_SOURCE_COMMIT=${{ steps.scope.outputs.source_sha }}", "DEVICE=cpu"):
            require(action.count(fragment) == 3, f"provider projection changed: {fragment}")
    except (KeyError, OSError, RuntimeError, tomllib.TOMLDecodeError) as error:
        print(f"Immich recipe mismatch: {error}", file=sys.stderr)
        return 1
    print("Verified Immich server amd64 plan and pinned reusable workflow.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
