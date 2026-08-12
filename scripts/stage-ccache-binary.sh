#!/usr/bin/env bash
set -euo pipefail

destination="${1:?usage: stage-ccache-binary.sh DESTINATION}"
version="4.13.6"
archive="ccache-${version}-linux-x86_64-glibc.tar.gz"
checksum="567b1b648411819590f918f045218c92da14418bdec3b30db94a3b4f5d77cf13"
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
