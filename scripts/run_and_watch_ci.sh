#!/usr/bin/env bash
# Watchdog script for GitHub Actions CI with alerts + logging
# Usage: ./scripts/run_and_watch_ci.sh <branch>

set -euo pipefail

BRANCH=${1:-main}
REPO="Damien157/damo2"
INTERVAL=60

# Optional: Slack webhook URL (set as environment variable)
SLACK_WEBHOOK=${SLACK_WEBHOOK:-""}

# Log file path (dated archive under Haven1)
LOG_DIR="archive/ci_logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/ci_watch_$(date +%Y-%m-%d).log"

echo "🔍 Watching CI for branch: $BRANCH on $REPO"
echo "📜 Logging to $LOG_FILE"

while true; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  STATUS=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 1 --json status -q '.[0].status' 2>/dev/null || echo "")
  CONCLUSION=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 1 --json conclusion -q '.[0].conclusion' 2>/dev/null || echo "")

  if [[ "$STATUS" == "completed" ]]; then
    if [[ "$CONCLUSION" == "success" ]]; then
      MESSAGE="✅ [$TIMESTAMP] CI passed for branch $BRANCH"
      # desktop notification if available
      command -v notify-send >/dev/null 2>&1 && notify-send "CI Success" "$MESSAGE" || true
    else
      MESSAGE="❌ [$TIMESTAMP] CI failed for branch $BRANCH (conclusion: $CONCLUSION)"
      command -v notify-send >/dev/null 2>&1 && notify-send "CI Failure" "$MESSAGE" || true

      # Send Slack alert if webhook is configured
      if [[ -n "$SLACK_WEBHOOK" ]]; then
        curl -s -X POST -H 'Content-type: application/json' \
          --data "{\"text\":\"${MESSAGE//"/\\\"}\"}" \
          "$SLACK_WEBHOOK" >/dev/null || true
      fi
    fi
  else
    MESSAGE="🚧 [$TIMESTAMP] CI still running (status: $STATUS)"
  fi

  # Append to log file
  echo "$MESSAGE" >> "$LOG_FILE"
  echo "$MESSAGE"

  sleep $INTERVAL
done
