param(
  [string]$PythonBin = "$PSScriptRoot/../.venv/Scripts/python.exe"
)

$RootDir = (Resolve-Path "$PSScriptRoot/..").Path
$ResolvedPython = (Resolve-Path $PythonBin -ErrorAction SilentlyContinue)

if (-not $ResolvedPython) {
  throw "Python executable not found at $PythonBin. Create a virtual environment first or pass -PythonBin."
}

& $ResolvedPython.Path -m pip install -r "$RootDir/requirements-build.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Remove-Item "$RootDir/build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$RootDir/dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$RootDir/FOSSolitaire.spec" -Force -ErrorAction SilentlyContinue

& $ResolvedPython.Path -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --name "FOSSolitaire" `
  --specpath "$RootDir" `
  --distpath "$RootDir/dist" `
  --workpath "$RootDir/build" `
  --paths "$RootDir" `
  --add-data "$RootDir/assets;assets" `
  "$RootDir/main.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Build complete."
Write-Host "Windows app folder: $RootDir/dist/FOSSolitaire"
