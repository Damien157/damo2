#!/usr/bin/env bash
# Watchdog script for GitHub Actions CI
# Usage: ./scripts/run_and_watch_ci.sh <branch>

set -euo pipefail

BRANCH=${1:-main}
REPO="Damien157/damo2"
INTERVAL=60

echo "🔍 Watching CI for branch: $BRANCH on $REPO"

while true; do
  echo "⏳ Checking latest workflow run..."
  STATUS=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 1 --json status --jq '.[0].status' 2>/dev/null || echo "")
  CONCLUSION=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null || echo "")

  if [[ "$STATUS" == "completed" ]]; then
    if [[ "$CONCLUSION" == "success" ]]; then
      echo "✅ CI passed for branch $BRANCH"
    else
      echo "❌ CI failed for branch $BRANCH (conclusion: $CONCLUSION)"
    fi
  elif [[ -z "$STATUS" ]]; then
    echo "⚠️  No workflow runs found yet for branch $BRANCH"
  else
    echo "🚧 CI still running (status: $STATUS)"
  fi

  sleep $INTERVAL
done
