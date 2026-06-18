# One-step setup for Windows PowerShell.
# Right-click this file and "Run with PowerShell", or in a terminal run:
#   ./setup.ps1
# It configures pip to use Lilly Artifactory and installs the Python packages the workbench needs.
# Run it once after cloning.

Write-Host "Setting up the GxP Validation Kit..." -ForegroundColor Cyan

$python = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $python) {
    Write-Host "Python was not found. Install Python 3.10 or newer, then run this again." -ForegroundColor Yellow
    Write-Host "Download: https://www.python.org/downloads/"
    exit 1
}

# Configure pip to use Lilly Artifactory
Write-Host ""
Write-Host "Configuring pip to use Lilly Artifactory..." -ForegroundColor Cyan
Write-Host "You will need your Artifactory API token. Find it at: https://elilillyco.jfrog.io/ui/user_profile"
Write-Host ""

$token = Read-Host "Artifactory token"
$email = Read-Host "Your Lilly email"
$enc   = [Uri]::EscapeDataString($email)
$dir   = "C:\Users\$env:USERNAME\AppData\Roaming\pip"
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
[System.IO.File]::WriteAllText(
    "$dir\pip.ini",
    "[global]`nindex-url = https://${enc}:${token}@elilillyco.jfrog.io/artifactory/api/pypi/Lilly-Python/simple",
    [System.Text.Encoding]::ASCII
)
Write-Host "pip.ini written to $dir" -ForegroundColor Green

Write-Host ""
Write-Host "Installing required packages..."
python -m pip install -r scripts/requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "Done. Open this folder in Claude Code and type /start to begin." -ForegroundColor Green
} else {
    Write-Host "Package install reported a problem. Check the messages above." -ForegroundColor Yellow
}
