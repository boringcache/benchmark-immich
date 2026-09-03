#!/usr/bin/env bash
set -euo pipefail

destination="${1:?usage: stage-ccache-binary.sh DESTINATION_DIRECTORY}"
ccache_version="4.14"
ccache_archive="ccache-${ccache_version}-linux-x86_64-glibc.tar.gz"
ccache_checksum="c64760b0b85ba86068f4cd162dc42e2dc39c6f46b0cb8c1990dfccbec7a1fed0"
storage_version="0.9"
storage_archive="ccache-storage-http-go-${storage_version}-linux-amd64.tar.gz"
storage_checksum="875dbf6d575d06e4c4492f1ba639beb68530bc23382031a6bacc767cded9f463"
temporary_dir="$(mktemp -d)"
trap 'rm -rf "$temporary_dir"' EXIT

curl --fail --location --show-error --silent \
  --retry 8 --retry-all-errors --connect-timeout 30 --max-time 180 \
  "https://github.com/ccache/ccache/releases/download/v${ccache_version}/${ccache_archive}" \
  --output "${temporary_dir}/${ccache_archive}"
echo "${ccache_checksum}  ${temporary_dir}/${ccache_archive}" | sha256sum --check --status
tar xzf "${temporary_dir}/${ccache_archive}" -C "$temporary_dir"

curl --fail --location --show-error --silent \
  --retry 8 --retry-all-errors --connect-timeout 30 --max-time 180 \
  "https://github.com/ccache/ccache-storage-http-go/releases/download/v${storage_version}/${storage_archive}" \
  --output "${temporary_dir}/${storage_archive}"
echo "${storage_checksum}  ${temporary_dir}/${storage_archive}" | sha256sum --check --status
tar xzf "${temporary_dir}/${storage_archive}" -C "$temporary_dir"

mkdir -p "$destination"
install -m 0755 \
  "${temporary_dir}/ccache-${ccache_version}-linux-x86_64-glibc/ccache" \
  "$destination/ccache"
install -m 0755 \
  "${temporary_dir}/ccache-storage-http-go-${storage_version}-linux-amd64/ccache-storage-http" \
  "$destination/ccache-storage-http"
