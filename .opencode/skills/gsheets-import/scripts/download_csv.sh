#!/usr/bin/env bash
set -euo pipefail

URL="$1"
OUT="$2"

curl -fsSL "$URL" -o "$OUT"
echo "$OUT"
