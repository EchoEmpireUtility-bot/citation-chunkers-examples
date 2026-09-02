#!/usr/bin/env sh
set -eu

: "${APIFY_TOKEN:?Set APIFY_TOKEN to an Apify API token}"

run_actor() {
  actor_id="$1"
  input_file="$2"
  curl --fail-with-body -X POST \
    "https://api.apify.com/v2/actors/${actor_id}/run-sync-get-dataset-items?clean=true&maxTotalChargeUsd=0.05" \
    -H "Authorization: Bearer ${APIFY_TOKEN}" \
    -H "Content-Type: application/json" \
    --data "@${input_file}"
}

# Embedded-text PDF → citation-ready JSON chunks
run_actor "H1c9OyB0AnRf8Sy4y" "inputs/pdf-citation-chunker.json"

# Scanned/image-only PDF → OCR citation-ready JSON chunks
# run_actor "50meJWqJ27Aw2QYZD" "inputs/ocr-citation-chunker.json"
