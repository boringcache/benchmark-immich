#!/usr/bin/env python3
"""Verify Immich's amd64 server image benchmark plan."""

import re
import sys
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
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
        plan = tomllib.loads((ROOT / ".boringcache.toml").read_text())
        command = plan["adapters"]["docker"]["command"]
        require(command[:7] == ["docker", "buildx", "build", "--file", "upstream/server/Dockerfile", "--platform", "linux/amd64"], "Docker plan changed")
        for fragment in ("BUILD_ID=__BUILD_ID__", "BUILD_IMAGE=ghcr.io/immich-app/immich-server:__SOURCE_REF__", "BUILD_SOURCE_REF=__SOURCE_REF__", "BUILD_SOURCE_COMMIT=__SOURCE_SHA__", "DEVICE=cpu", "immich-server-benchmark:local"):
            require(fragment in command, f"Docker plan changed: {fragment}")
        require(plan["adapters"]["ccache"]["tag"] == "immich-ccache-local", "ccache plan changed")
        activation = (ROOT / "scripts/activate-docker-plan.py").read_text()
        for fragment in ("base-images-upstream/server/Dockerfile", 'tool-cache = ["ccache"]', "upstream/server/Dockerfile", '"--push"'):
            require(fragment in activation, f"Docker plan activation changed: {fragment}")
        upstream = (ROOT / "upstream/.github/workflows/docker.yml").read_text()
        server = job_definition(upstream, "server")
        require(PINNED_BUILD_WORKFLOW.search(server) is not None, "upstream server build workflow changed or is not SHA-pinned")
        for fragment in ("context: .", "dockerfile: server/Dockerfile", "DEVICE=cpu"):
            require(fragment in server, f"upstream server job changed: {fragment}")
        action = (ROOT / ".github/actions/immich-docker-benchmark/action.yml").read_text()
        for fragment in ("BUILD_ID=${{ github.run_id }}", "BUILD_IMAGE=ghcr.io/immich-app/immich-server:${{ github.ref_name }}", "BUILD_SOURCE_REF=${{ github.ref_name }}", "BUILD_SOURCE_COMMIT=${{ steps.scope.outputs.source_sha }}", "DEVICE=cpu"):
            require(action.count(fragment) == 1, f"Actions/cache projection changed: {fragment}")
        require(action.count("Activate the BoringCache Docker plan") == 1, "BoringCache server plan activation drifted")
        base_action = (ROOT / ".github/actions/immich-base-images-benchmark/action.yml").read_text()
        require(base_action.count("Activate the BoringCache Docker plan") == 1, "BoringCache base-images plan activation drifted")
        staged_tools = (ROOT / "scripts/stage-ccache-binary.sh").read_text()
        rendered_profile = (ROOT / "scripts/prepare-immich-base-images-source.py").read_text()
        for fragment in ("ccache_version=\"4.14\"", "storage_version=\"0.9\"", "875dbf6d575d06e4c4492f1ba639beb68530bc23382031a6bacc767cded9f463"):
            require(fragment in staged_tools, f"ccache tool staging changed: {fragment}")
        require("COPY ccache-storage-http /usr/bin/ccache-storage-http" in rendered_profile, "base-images profile omits the ccache HTTP helper")
    except (KeyError, OSError, RuntimeError, tomllib.TOMLDecodeError) as error:
        print(f"Immich recipe mismatch: {error}", file=sys.stderr)
        return 1
    print("Verified Immich server amd64 plan and SHA-pinned reusable workflow.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
