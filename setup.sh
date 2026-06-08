#!/usr/bin/env bash
# One-step setup for macOS, Linux, and GitHub Codespaces.
# In a terminal run:
#   bash setup.sh
# It installs the Python packages the workbench needs. Run it once after cloning.

echo "Setting up the GxP Validation Kit..."

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python was not found. Install Python 3.10 or newer, then run this again."
  echo "Download: https://www.python.org/downloads/"
  exit 1
fi

echo "Installing required packages..."
if "$PY" -m pip install -r scripts/requirements.txt; then
  echo "Done. Open this folder in Claude Code and type /start to begin."
else
  echo "Package install reported a problem. Check the messages above."
fi
