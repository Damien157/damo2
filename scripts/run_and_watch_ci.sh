#!/usr/bin/env bash
set -euo pipefail

repo="Damien157/damo2"
workflow="ci.yml"
ref="${1:-main}"

echo "Triggering workflow '$workflow' on ref '$ref' in repo '$repo'..."
gh workflow run "$workflow" --repo "$repo" --ref "$ref"

echo "Waiting for the run to appear..."
run_id=""
for i in {1..30}; do
  run_id=$(gh run list --repo "$repo" --workflow="$workflow" --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || true)
  if [[ -n "$run_id" && "$run_id" != "null" ]]; then
    break
  fi
  sleep 2
done

if [[ -z "$run_id" || "$run_id" == "null" ]]; then
  echo "ERROR: could not determine run id for workflow '$workflow'" >&2
  exit 2
fi

echo "Found run id: $run_id"
echo "Streaming logs (this will follow until completion)..."
gh run watch "$run_id" --repo "$repo"

echo "Fetching final status..."
status=$(gh run view "$run_id" --repo "$repo" --json status,conclusion --jq '.status + " / " + (.conclusion // "null")')
echo "Final status: $status"
echo "Run details: https://github.com/${repo}/actions/runs/${run_id}"

exit 0
