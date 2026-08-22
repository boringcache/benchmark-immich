#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scope="${1:-}"
if [[ ! "$scope" =~ ^[a-z0-9][a-z0-9._-]+$ ]]; then
  echo "Expected a lowercase benchmark cache scope, got: ${scope:-<empty>}" >&2
  exit 1
fi
config_path="${repo_root}/.boringcache.toml"
python3 - "$config_path" "$scope" <<'PY'
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
scope = sys.argv[2]
source = config_path.read_text()
docker_tag = 'tag = "immich-docker-local"'
ccache_tag = 'tag = "immich-ccache-local"'

if source.count(docker_tag) != 1:
    raise SystemExit(f"Missing expected local Docker tag in {config_path}")

source = source.replace(docker_tag, f'tag = "{scope}-docker"', 1)
if source.count(ccache_tag) > 1:
    raise SystemExit(f"Expected at most one local ccache tag in {config_path}")
source = source.replace(ccache_tag, f'tag = "{scope}-ccache"', 1)
config_path.write_text(source)
PY
echo "Scoped the BoringCache adapter tags to ${scope}."
