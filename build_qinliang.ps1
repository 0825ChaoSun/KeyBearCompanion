$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "D:\anaconda3\envs\tf\python.exe"
$PackagingTools = Join-Path $ProjectRoot "packaging_tools"
$BuildRoot = Join-Path $ProjectRoot "qinliang_build_en"
$BuildSrc = Join-Path $BuildRoot "src"
$OutputDir = Join-Path $ProjectRoot "qinliang"
$ExePath = Join-Path $OutputDir "KeyBearCompanion.exe"
$ZipPath = Join-Path $OutputDir "KeyBearCompanion-qinliang-win64.zip"
$LegacyYierDirName = -join ([char[]](0x4e00, 0x4e8c, 0x5f62, 0x8c61))

Set-Location $ProjectRoot

& $Python icon_processor.py
& $Python transparent_processor.py

if (Test-Path -LiteralPath $BuildRoot) {
    Remove-Item -LiteralPath $BuildRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $BuildSrc | Out-Null

$excludeDirs = @(
    ".git",
    ".idea",
    "__pycache__",
    "build",
    "dist",
    "user_data",
    "keybear_build_en",
    "qinliang",
    "qinliang_build_en",
    "tmp_appdata_smoke",
    $LegacyYierDirName
)
$excludeFiles = @(
    "KeyBearCompanion-win64.zip",
    "KeyBearCompanion-qinliang-win64.zip",
    "PackagingSmoke.spec",
    "packaging_smoke.py"
)

Get-ChildItem -LiteralPath $ProjectRoot -Force | ForEach-Object {
    if ($_.PSIsContainer) {
        if ($excludeDirs -notcontains $_.Name) {
            Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $BuildSrc $_.Name) -Recurse -Force
        }
    } else {
        if ($excludeFiles -notcontains $_.Name) {
            Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $BuildSrc $_.Name) -Force
        }
    }
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

Write-Host "Built qinliang exe: $ExePath ($exeSize MB)"
Write-Host "Built qinliang zip: $ZipPath ($zipSize MB)"
