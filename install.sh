#!/usr/bin/env bash
# Install Hermes Loop Mastering into the current user's Hermes skills directory.
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_BASE="${HERMES_HOME:-$HOME/.hermes}/skills/software-development"
DEST="$DEST_BASE/hermes-loop-mastering"
FORCE="${FORCE:-0}"

if [ -e "$DEST" ] && [ "$FORCE" != "1" ]; then
  echo "Destination already exists: $DEST"
  echo "Set FORCE=1 to overwrite."
  exit 1
fi

mkdir -p "$DEST_BASE"
if [ -e "$DEST" ]; then
  rm -rf "$DEST"
fi

mkdir -p "$DEST"
cp -R "$SRC_DIR"/SKILL.md "$SRC_DIR"/templates "$SRC_DIR"/scripts "$SRC_DIR"/examples "$DEST"/

echo "Installed Hermes Loop Mastering to: $DEST"
echo "Start a fresh Hermes session before loading the skill."
