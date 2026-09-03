#!/usr/bin/env python3
"""Select an Immich Docker request while preserving scoped cache identity."""

import argparse
import json
import re
import tomllib
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1] / ".boringcache.toml"


def quoted(value: str) -> str:
    return json.dumps(value)


def render_command(values: list[str]) -> str:
    return "command = [\n" + "".join(f"  {quoted(value)},\n" for value in values) + "]\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=("server", "base-images"), required=True)
    parser.add_argument("--tool-cache", choices=("true", "false"), default="false")
    parser.add_argument("--source-sha", default="")
    parser.add_argument("--build-id", default="")
    parser.add_argument("--source-ref", default="")
    parser.add_argument("--push", choices=("true", "false"), default="false")
    parser.add_argument("--image", default="")
    parser.add_argument("--plan", type=Path, default=PLAN)
    args = parser.parse_args()

    current = tomllib.loads(args.plan.read_text())
    workspace = current["workspace"]
    docker_tag = current["adapters"]["docker"]["tag"]
    ccache_tag = current["adapters"]["ccache"]["tag"]

    if args.scenario == "server":
        if not re.fullmatch(r"[0-9a-f]{40}", args.source_sha):
            raise SystemExit("source SHA must be a full lowercase commit SHA")
        if not args.build_id or not args.source_ref:
            raise SystemExit("server plans require build ID and source ref")
        output_image = args.image if args.push == "true" else "immich-server-benchmark:local"
        command = [
            "docker", "buildx", "build",
            "--file", "upstream/server/Dockerfile",
            "--platform", "linux/amd64",
            "--build-arg", f"BUILD_ID={args.build_id}",
            "--build-arg", f"BUILD_IMAGE=ghcr.io/immich-app/immich-server:{args.source_ref}",
            "--build-arg", f"BUILD_SOURCE_REF={args.source_ref}",
            "--build-arg", f"BUILD_SOURCE_COMMIT={args.source_sha}",
            "--build-arg", "DEVICE=cpu",
            "--tag", output_image,
        ]
        if args.push == "true":
            command.append("--push")
        command.append("upstream")
        metadata = ["benchmark=immich-server", "upstream-job=server-amd64"]
        tool_cache = False
    else:
        if args.push == "true":
            raise SystemExit("base-images plans do not publish an image")
        command = [
            "docker", "buildx", "build",
            "--file", "base-images-upstream/server/Dockerfile",
            "--platform", "linux/amd64",
            "--target", "libvips",
            "--tag", "immich-base-images-benchmark:local",
            "base-images-upstream/server",
        ]
        metadata = ["benchmark=immich-base-images", "upstream-job=server-native-amd64"]
        tool_cache = args.tool_cache == "true"

    rendered = (
        f"workspace = {quoted(workspace)}\n\n"
        "[adapters.docker]\n"
        f"tag = {quoted(docker_tag)}\n"
        f"metadata-hints = [{', '.join(quoted(value) for value in metadata)}]\n"
    )
    if tool_cache:
        rendered += 'tool-cache = ["ccache"]\n'
    rendered += (
        render_command(command)
        + "\n[adapters.ccache]\n"
        + f"tag = {quoted(ccache_tag)}\n"
        + 'metadata-hints = ["benchmark=immich-base-images", "upstream-job=server-native-amd64"]\n'
    )
    tomllib.loads(rendered)
    args.plan.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
