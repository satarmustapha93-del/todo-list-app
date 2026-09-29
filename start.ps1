$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root 'backend'
$python = Get-Command python -ErrorAction SilentlyContinue
$pythonPath = if ($python) { $python.Source } else { $null }
if ($pythonPath) { & $pythonPath -c "import sys; assert sys.version_info >= (3,11)" 2>$null; if ($LASTEXITCODE -ne 0) { $pythonPath = $null } }
if (-not $pythonPath) {
  $runtimePython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
  if (Test-Path $runtimePython) { & $runtimePython -c "import sys; assert sys.version_info >= (3,11)" 2>$null; if ($LASTEXITCODE -eq 0) { $pythonPath = $runtimePython } }
}
if (-not $pythonPath) {
  Write-Host 'Python is required for the FastAPI server. Install Python 3.11+ from python.org, then reopen this file.' -ForegroundColor Yellow
  exit 1
}
$npm = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npm -and (Test-Path 'C:\Program Files\nodejs\npm.cmd')) { $npm = @{ Source = 'C:\Program Files\nodejs\npm.cmd' } }
if (-not $npm) {
  Write-Host 'Node.js is required for the React website. Install the LTS version from nodejs.org, then reopen this file.' -ForegroundColor Yellow
  exit 1
}
if (-not (Test-Path (Join-Path $root 'node_modules'))) {
  Write-Host 'Installing the web app dependencies (first run only)...' -ForegroundColor Cyan
  Push-Location $root
  $env:npm_config_cache = Join-Path $root 'work\npm-cache'
  & $npm.Source install
  Pop-Location
}
$env:TEMP = Join-Path $root 'work\tmp'
$env:TMP = $env:TEMP
$env:TMPDIR = $env:TEMP
New-Item -ItemType Directory -Force -Path $env:TEMP,(Join-Path $root 'work\pip-cache'),(Join-Path $root 'work\python-packages') | Out-Null
$env:PIP_CACHE_DIR = Join-Path $root 'work\pip-cache'
$env:PYTHONPATH = Join-Path $root 'work\python-packages'
& $pythonPath -c "import fastapi, uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host 'Installing the Python server dependencies (first run only)...' -ForegroundColor Cyan
  & $pythonPath -m pip install --target $env:PYTHONPATH -r (Join-Path $root 'requirements.txt')
  if ($LASTEXITCODE -ne 0) { Write-Host 'Dependency installation failed. Check your internet connection and try again.' -ForegroundColor Red; exit 1 }
}
Write-Host 'Starting Little List at http://localhost:5173' -ForegroundColor Green
Start-Process -FilePath 'powershell' -ArgumentList @('-NoExit','-Command',"Set-Location '$backend'; & '$pythonPath' -m uvicorn main:app --reload --port 8000") -WindowStyle Hidden
Start-Process -FilePath 'powershell' -ArgumentList @('-NoExit','-Command',"Set-Location '$root'; & '$($npm.Source)' run dev") -WindowStyle Hidden
Start-Sleep -Seconds 3
Start-Process 'http://localhost:5173'
