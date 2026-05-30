$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BasePython = "D:\anaconda3\envs\tf\python.exe"
$PackagingTools = Join-Path $ProjectRoot "packaging_tools"
$BuildRoot = Join-Path $ProjectRoot "tk_qin_build_en"
$BuildSrc = Join-Path $BuildRoot "src"
$VenvDir = Join-Path $ProjectRoot "qin_venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$OutputDir = Join-Path $ProjectRoot "qinliang\qin"
$ZipPath = Join-Path $OutputDir "KeyBearCompanion-tk-qin-win64.zip"
$TfSite = "D:\anaconda3\envs\tf\Lib\site-packages"
$LegacyYierDirName = -join ([char[]](0x4e00, 0x4e8c, 0x5f62, 0x8c61))

Set-Location $ProjectRoot

if (!(Test-Path -LiteralPath (Join-Path $ProjectRoot "assets\processed\app_icon.ico"))) {
    & $BasePython icon_processor.py
}
if (!(Test-Path -LiteralPath (Join-Path $ProjectRoot "assets\processed\keyboard.png"))) {
    & $BasePython transparent_processor.py
}
& $BasePython prepare_qin_assets.py

if (!(Test-Path -LiteralPath $VenvPython)) {
    & $BasePython -m venv $VenvDir
}

$VenvSite = Join-Path $VenvDir "Lib\site-packages"
Copy-Item -LiteralPath (Join-Path $TfSite "pynput") -Destination (Join-Path $VenvSite "pynput") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $TfSite "six.py") -Destination (Join-Path $VenvSite "six.py") -Force
Get-ChildItem -LiteralPath $TfSite -Filter "pynput-*.dist-info" | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $VenvSite $_.Name) -Recurse -Force
}
Get-ChildItem -LiteralPath $TfSite -Filter "six-*.dist-info" | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $VenvSite $_.Name) -Recurse -Force
}

if (Test-Path -LiteralPath $BuildRoot) {
    Remove-Item -LiteralPath $BuildRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $BuildSrc | Out-Null

$includeFiles = @(
    "main_tk_light.py",
    "tk_light_app.py",
    "keyboard_layout.py",
    "keyboard_listener.py",
    "path_utils.py",
    "KeyBearCompanionTkQin.spec"
)
foreach ($file in $includeFiles) {
    Copy-Item -LiteralPath (Join-Path $ProjectRoot $file) -Destination (Join-Path $BuildSrc $file) -Force
}
Copy-Item -LiteralPath (Join-Path $ProjectRoot "qin_pack_assets") -Destination (Join-Path $BuildSrc "qin_pack_assets") -Recurse -Force

Set-Location $BuildSrc

$HadPythonPath = Test-Path Env:\PYTHONPATH
$OldPythonPath = if ($HadPythonPath) { $env:PYTHONPATH } else { "" }
if (Test-Path -LiteralPath $PackagingTools) {
    $env:PYTHONPATH = $PackagingTools
}
try {
    & $VenvPython -m PyInstaller --noconfirm --clean KeyBearCompanionTkQin.spec
}
finally {
    if ($HadPythonPath) {
        $env:PYTHONPATH = $OldPythonPath
    } else {
        Remove-Item Env:\PYTHONPATH -ErrorAction SilentlyContinue
    }
}

Set-Location $ProjectRoot

if (Test-Path -LiteralPath $OutputDir) {
    Remove-Item -LiteralPath $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDir | Out-Null

Copy-Item -LiteralPath (Join-Path $BuildSrc "dist\KeyBearCompanion") -Destination (Join-Path $OutputDir "KeyBearCompanion") -Recurse -Force

if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}
Compress-Archive -LiteralPath (Join-Path $OutputDir "KeyBearCompanion") -DestinationPath $ZipPath -Force

$folderSize = [Math]::Round(((Get-ChildItem -LiteralPath (Join-Path $OutputDir "KeyBearCompanion") -Recurse -File | Measure-Object Length -Sum).Sum) / 1MB, 2)
$zipSize = [Math]::Round((Get-Item -LiteralPath $ZipPath).Length / 1MB, 2)

Write-Host "Built Tk onedir: $(Join-Path $OutputDir 'KeyBearCompanion') ($folderSize MB)"
Write-Host "Built Tk zip:    $ZipPath ($zipSize MB)"
