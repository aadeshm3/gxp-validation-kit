# One-step setup for Windows PowerShell.
# Right-click this file and "Run with PowerShell", or in a terminal run:
#   ./setup.ps1
# It installs the Python packages the workbench needs. Run it once after cloning.

Write-Host "Setting up the Validation AI Workbench..." -ForegroundColor Cyan

$python = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $python) {
    Write-Host "Python was not found. Install Python 3.10 or newer, then run this again." -ForegroundColor Yellow
    Write-Host "Download: https://www.python.org/downloads/"
    exit 1
}

Write-Host "Installing required packages..."
python -m pip install -r scripts/requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "Done. Open this folder in Claude Code and type /start to begin." -ForegroundColor Green
} else {
    Write-Host "Package install reported a problem. Check the messages above." -ForegroundColor Yellow
}
