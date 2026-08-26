#!/usr/bin/env bash
set -euo pipefail

destination="${1:?usage: stage-ccache-binary.sh DESTINATION}"
version="4.14"
archive="ccache-${version}-linux-x86_64-glibc.tar.gz"
checksum="c64760b0b85ba86068f4cd162dc42e2dc39c6f46b0cb8c1990dfccbec7a1fed0"
temporary_dir="$(mktemp -d)"
trap 'rm -rf "$temporary_dir"' EXIT

curl --fail --location --show-error --silent \
  --retry 8 --retry-all-errors --connect-timeout 30 --max-time 180 \
  "https://github.com/ccache/ccache/releases/download/v${version}/${archive}" \
  --output "${temporary_dir}/${archive}"
actual_checksum="$(sha256sum "${temporary_dir}/${archive}" | awk '{print $1}')"
if [[ "$actual_checksum" != "$checksum" ]]; then
  echo "Checksum mismatch for $archive" >&2
  exit 1
fi
tar xzf "${temporary_dir}/${archive}" -C "$temporary_dir"
install -m 0755 \
  "${temporary_dir}/ccache-${version}-linux-x86_64-glibc/ccache" \
  "$destination"
