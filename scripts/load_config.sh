#!/usr/bin/env bash
# Sourced (not executed) at the top of every command's bash blocks that need config:
#   source "$CLAUDE_PLUGIN_ROOT/scripts/load_config.sh" || exit 1
#
# Loads ~/.learning-os/config.env into the environment and does a minimal sanity check.
# Per-command required variables aren't enforced here (each command only needs a subset) —
# this just confirms the config file exists at all and is readable, so commands fail with a
# clear "run /learning-os-setup first" message instead of a confusing missing-variable error
# three steps into a session.

LEARNING_OS_CONFIG="${LEARNING_OS_CONFIG:-$HOME/.learning-os/config.env}"

if [ ! -f "$LEARNING_OS_CONFIG" ]; then
  echo "No Learning OS config found at $LEARNING_OS_CONFIG." >&2
  echo "Run /learning-os-setup first, then re-run this command." >&2
  return 1 2>/dev/null || exit 1
fi

set -a
# shellcheck disable=SC1090
source "$LEARNING_OS_CONFIG"
set +a
