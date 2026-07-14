#!/usr/bin/env bash
# Shared "save this session's transcript to NotebookLM" helper — replaces the near-identical
# notebooklm-use / write-to-tempfile / source-add block repeated across every command's
# END OF SESSION AUTOMATION.
#
# Usage: pipe the transcript (or any text) in on stdin.
#   cat <<'EOF' | scripts/notebooklm_save.sh "$NOTEBOOK_TUTOR" tutor
#   <FULL_CONVERSATION_TRANSCRIPT>
#   EOF
#
# Args:
#   $1 - notebook ID to save into (required)
#   $2 - short label used in the temp filename, e.g. "tutor", "mathtutor" (required)

set -euo pipefail

NOTEBOOK_ID="${1:?Usage: notebooklm_save.sh <notebook_id> <label> < transcript.txt}"
LABEL="${2:?Usage: notebooklm_save.sh <notebook_id> <label> < transcript.txt}"

if ! command -v notebooklm >/dev/null 2>&1; then
  echo "notebooklm CLI not found on PATH. Install notebooklm-py and run 'notebooklm login' first." >&2
  exit 1
fi

SESSION_FILE="/tmp/${LABEL}-session-$(date '+%Y-%m-%d-%H%M%S').txt"
cat > "$SESSION_FILE"

if ! notebooklm use "$NOTEBOOK_ID"; then
  echo "Could not select notebook $NOTEBOOK_ID. Run 'notebooklm login' and try again." >&2
  exit 1
fi

notebooklm source add "$SESSION_FILE"
echo "Saved session transcript to notebook $NOTEBOOK_ID ($SESSION_FILE)"
