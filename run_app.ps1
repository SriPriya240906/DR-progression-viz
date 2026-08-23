param(
  [string]$App = "app.py"
)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$activate = Join-Path $scriptDir "venv\Scripts\Activate.ps1"
if (Test-Path $activate) {
  Write-Host "Activating venv..."
  & $activate
} else {
  Write-Host "Activate.ps1 not found at $activate"
}
$python = Join-Path $scriptDir "venv\Scripts\python.exe"
if (Test-Path $python) {
  Write-Host "Running Streamlit with venv python: $python"
  & $python -m streamlit run $App
} else {
  Write-Host "venv python not found; please activate venv and run 'streamlit run $App'"
}
