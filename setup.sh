#!/usr/bin/env bash
# One-step setup for macOS, Linux, and GitHub Codespaces.
# In a terminal run:
#   bash setup.sh
# It configures pip to use Lilly Artifactory and installs the Python packages the workbench needs.
# Run it once after cloning.

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

# Configure pip to use Lilly Artifactory
echo ""
echo "Configuring pip to use Lilly Artifactory..."
echo "You will need your Artifactory API token. Find it at: https://elilillyco.jfrog.io/ui/user_profile"
echo ""

read -rp "Artifactory token: " token
read -rp "Your Lilly email: " email
enc=$(python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$email")

pip_dir="$HOME/.config/pip"
mkdir -p "$pip_dir"
cat > "$pip_dir/pip.conf" <<EOF
[global]
index-url = https://${enc}:${token}@elilillyco.jfrog.io/artifactory/api/pypi/Lilly-Python/simple
EOF
echo "pip.conf written to $pip_dir"

echo ""
echo "Installing required packages..."
if "$PY" -m pip install -r scripts/requirements.txt; then
  echo "Done. Open this folder in Claude Code and type /start to begin."
else
  echo "Package install reported a problem. Check the messages above."
fi
