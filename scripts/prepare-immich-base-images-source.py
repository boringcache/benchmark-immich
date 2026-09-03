#!/usr/bin/env python3
"""Apply the benchmark-only ccache profile to Immich base-images."""

from __future__ import annotations

import argparse
from pathlib import Path


class ProfileMismatch(RuntimeError):
    pass


def replace_once(source: str, before: str, after: str, boundary: str) -> str:
    if source.count(before) != 1:
        raise ProfileMismatch(f"expected one {boundary}, found {source.count(before)}")
    return source.replace(before, after, 1)


def render(source: str, profile: str) -> str:
    if profile == "baseline":
        return source
    if profile != "ccache":
        raise ProfileMismatch(f"unknown cache profile: {profile}")

    source = replace_once(
        source,
        "  build-essential \\\n  cmake \\\n",
        "  build-essential \\\n  ccache \\\n  cmake \\\n",
        "base build package list",
    )
    return replace_once(
        source,
        "  libaom-dev\n\nFROM base AS geodata\n",
        "  libaom-dev\n\n"
        "# BoringCache's current ccache adapter targets ccache 4.14's @-attribute syntax.\n"
        "# Keep Debian's compiler wrappers, but replace its older ccache binary and HTTP helper.\n"
        "ARG CCACHE_VERSION=4.14\n"
        "ARG CCACHE_STORAGE_HTTP_VERSION=0.9\n"
        "COPY ccache /usr/bin/ccache\n"
        "COPY ccache-storage-http /usr/bin/ccache-storage-http\n"
        "RUN chmod 0755 /usr/bin/ccache /usr/bin/ccache-storage-http && \\\n"
        "  ccache --version | grep -F \"ccache version ${CCACHE_VERSION}\" && \\\n"
        "  ccache-storage-http --version 2>&1 | grep -F \"Version: ${CCACHE_STORAGE_HTTP_VERSION}\"\n\n"
        'ENV PATH="/usr/lib/ccache:${PATH}"\n\n'
        "FROM base AS geodata\n",
        "base stage boundary",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", choices=("baseline", "ccache"))
    parser.add_argument("source", type=Path)
    args = parser.parse_args()

    dockerfile = args.source / "server/Dockerfile"
    original = dockerfile.read_text()
    rendered = render(original, args.profile)
    dockerfile.write_text(rendered)

    if "CCACHE_REMOTE_STORAGE" in rendered:
        raise ProfileMismatch("the Dockerfile must not own BoringCache credentials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
