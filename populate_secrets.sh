#!/usr/bin/env bash
# populate_secrets.sh
# Reads the .env file and pushes each KEY=VALUE pair as a new
# Secret Manager version.  Assumes secrets already exist (created by Terraform).
#
# Usage: bash populate_secrets.sh [path/to/.env]

set -euo pipefail

ENV_FILE="${1:-.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: file '$ENV_FILE' not found" >&2
  exit 1
fi

while IFS='=' read -r key value; do
  # Skip comments and empty lines
  [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue

  # Strip surrounding double-quotes from value
  value="${value%\"}"
  value="${value#\"}"

  echo "→ Updating secret: $key"
  echo -n "$value" | gcloud secrets versions add "$key" --data-file=-
done < "$ENV_FILE"
