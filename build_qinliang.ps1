$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\anaconda3\envs\tf\python.exe"
$PackagingTools = Join-Path $ProjectRoot "packaging_tools"
$BuildRoot = Join-Path $ProjectRoot "qinliang_build_en"
$BuildSrc = Join-Path $BuildRoot "src"
$OutputDir = Join-Path $ProjectRoot "dist"
$ExePath = Join-Path $OutputDir "KeyBearCompanion.exe"
$ZipPath = Join-Path $OutputDir "KeyBearCompanion-qinliang-win64.zip"

Set-Location $ProjectRoot

& $Python icon_processor.py
& $Python transparent_processor.py

if (Test-Path -LiteralPath $BuildRoot) {
    Remove-Item -LiteralPath $BuildRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $BuildSrc | Out-Null

$sourceFiles = @(
    "main.py",
    "app.py",
    "animation_controller.py",
    "cat_widget.py",
    "idle_detector.py",
    "keyboard_layout.py",
    "keyboard_listener.py",
    "path_utils.py",
    "pet_keyboard_window.py",
    "settings_manager.py",
    "settings_window.py",
    "startup_manager.py",
    "virtual_keyboard.py",
    "settings.json",
    "KeyBearCompanionQinliang.spec"
)

foreach ($name in $sourceFiles) {
    $source = Join-Path $ProjectRoot $name
    if (!(Test-Path -LiteralPath $source)) {
        throw "Required build input is missing: $source"
    }
    Copy-Item -LiteralPath $source -Destination (Join-Path $BuildSrc $name) -Force
}

$processedSource = Join-Path $ProjectRoot "assets\processed"
$processedDestination = Join-Path $BuildSrc "assets\processed"
if (!(Test-Path -LiteralPath $processedSource)) {
    throw "Required processed assets are missing: $processedSource"
}
New-Item -ItemType Directory -Path $processedDestination -Force | Out-Null
Get-ChildItem -LiteralPath $processedSource -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $processedDestination -Force
}

Set-Location $BuildSrc

$env:PYTHONPATH = $PackagingTools
try {
    & $Python -m PyInstaller --noconfirm --clean KeyBearCompanionQinliang.spec
}
finally {
    Remove-Item Env:\PYTHONPATH -ErrorAction SilentlyContinue
}

Set-Location $ProjectRoot

if (!(Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Copy-Item -LiteralPath (Join-Path $BuildSrc "dist\KeyBearCompanion.exe") -Destination $ExePath -Force

if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}
Compress-Archive -LiteralPath $ExePath -DestinationPath $ZipPath -Force

$exeSize = [Math]::Round((Get-Item -LiteralPath $ExePath).Length / 1MB, 2)
$zipSize = [Math]::Round((Get-Item -LiteralPath $ZipPath).Length / 1MB, 2)

Write-Host "Built exe: $ExePath ($exeSize MB)"
Write-Host "Built zip: $ZipPath ($zipSize MB)"
