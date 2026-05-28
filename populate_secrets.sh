#!/usr/bin/env bash
# NOTE: This project has been decommissioned. This script is kept for documentation purposes only.
# populate_secrets.sh
set -euo pipefail

ENV_FILE="${1:-.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: file '$ENV_FILE' not found" >&2
  exit 1
fi

while IFS= read -r line || [[ -n "$line" ]]; do
  # Skip comments and empty lines
  [[ "$line" =~ ^[[:space:]]*# || -z "${line// }" ]] && continue

  # Split on FIRST '=' only
  key="${line%%=*}"
  value="${line#*=}"

  # Skip if key is empty
  [[ -z "$key" ]] && continue

  # Strip surrounding quotes (single or double)
  value="${value%\"}" ; value="${value#\"}"
  value="${value%\'}" ; value="${value#\'}"

  # Strip carriage return (Windows line endings)
  value="${value%$'\r'}"

  echo "→ Updating secret: $key"
  printf '%s' "$value" | gcloud secrets versions add "$key" --data-file=-
done < "$ENV_FILE"
