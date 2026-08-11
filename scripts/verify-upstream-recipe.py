#!/usr/bin/env python3
"""Verify Immich's amd64 server image benchmark plan."""

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCRIPT = "source_sha=$(git -C upstream rev-parse HEAD); build_id=${GITHUB_RUN_ID:-local}; source_ref=${GITHUB_REF_NAME:-local}; exec docker buildx build --file upstream/server/Dockerfile --platform linux/amd64 --build-arg BUILD_ID=${build_id} --build-arg BUILD_IMAGE=ghcr.io/immich-app/immich-server:${source_ref} --build-arg BUILD_SOURCE_REF=${source_ref} --build-arg BUILD_SOURCE_COMMIT=${source_sha} --build-arg DEVICE=cpu --tag immich-server-benchmark:local upstream"
# The revision may advance automatically, but it must remain an immutable SHA.
PINNED_BUILD_WORKFLOW = re.compile(
    r"^    uses: immich-app/devtools/\.github/workflows/multi-runner-build\.yml@[0-9a-f]{40}(?:\s+#.*)?$",
    re.MULTILINE,
)


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def job_definition(workflow: str, job: str) -> str:
    match = re.search(
        rf"^  {re.escape(job)}:\n.*?(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        workflow,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise RuntimeError(f"upstream {job} job missing")
    return match.group(0)


def main() -> int:
    try:
        command = tomllib.loads((ROOT / ".boringcache.toml").read_text())["adapters"]["docker"]["command"]
        require(command == ["bash", "-euo", "pipefail", "-c", EXPECTED_SCRIPT], "Docker plan changed")
        upstream = (ROOT / "upstream/.github/workflows/docker.yml").read_text()
        server = job_definition(upstream, "server")
        require(PINNED_BUILD_WORKFLOW.search(server) is not None, "upstream server build workflow changed or is not SHA-pinned")
        for fragment in ("context: .", "dockerfile: server/Dockerfile", "DEVICE=cpu"):
            require(fragment in server, f"upstream server job changed: {fragment}")
        action = (ROOT / ".github/actions/immich-docker-benchmark/action.yml").read_text()
        for fragment in ("BUILD_ID=${{ github.run_id }}", "BUILD_IMAGE=ghcr.io/immich-app/immich-server:${{ github.ref_name }}", "BUILD_SOURCE_REF=${{ github.ref_name }}", "BUILD_SOURCE_COMMIT=${{ steps.scope.outputs.source_sha }}", "DEVICE=cpu"):
            require(action.count(fragment) == 3, f"provider projection changed: {fragment}")
    except (KeyError, OSError, RuntimeError, tomllib.TOMLDecodeError) as error:
        print(f"Immich recipe mismatch: {error}", file=sys.stderr)
        return 1
    print("Verified Immich server amd64 plan and SHA-pinned reusable workflow.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
