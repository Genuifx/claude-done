#!/bin/sh
set -e

REPO="https://github.com/Genuifx/claude-done.git"
INSTALL_DIR="$HOME/.codex/claude-done"
SKILLS_DIR="$HOME/.agents/skills"

echo "Installing Claude Done..."

if [ -d "$INSTALL_DIR" ]; then
  echo "Updating existing installation..."
  git -C "$INSTALL_DIR" pull
else
  git clone "$REPO" "$INSTALL_DIR"
fi

mkdir -p "$SKILLS_DIR"

if [ ! -L "$SKILLS_DIR/claude-done" ]; then
  ln -s "$INSTALL_DIR/skills" "$SKILLS_DIR/claude-done"
fi

echo "Done! Restart Codex to activate /done and /recall."
