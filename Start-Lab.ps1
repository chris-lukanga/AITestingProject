$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$runtimePython = Join-Path $projectRoot '.runtime\python\python.exe'
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (Test-Path -LiteralPath $venvPython) { $labPython = $venvPython }
elseif (Test-Path -LiteralPath $runtimePython) { $labPython = $runtimePython }
else {
    $installedPython = Get-ChildItem -Path "$env:LOCALAPPDATA\Python\pythoncore-*\python.exe" -ErrorAction SilentlyContinue | Select-Object -Last 1
    $labPython = if ($installedPython) { $installedPython.FullName } else { (Get-Command python -ErrorAction Stop).Source }
}
Push-Location -LiteralPath $projectRoot
try { & $labPython (Join-Path $projectRoot 'setup_lab.py') }
finally { Pop-Location }
