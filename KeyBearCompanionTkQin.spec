# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path, PureWindowsPath


block_cipher = None


def _norm(name):
    return str(PureWindowsPath(name)).replace("\\", "/").lower()


def _keep_toc_entry(entry):
    name = _norm(entry[0])
    drop_prefixes = (
        "numpy/",
        "PIL/".lower(),
        "PySide6/".lower(),
        "shiboken6/".lower(),
        "PyQt6/".lower(),
        "qt6".lower(),
        "tcl/tzdata/".lower(),
        "tcl/http1.0/".lower(),
        "tcl/opt0.4/".lower(),
    )
    drop_names = {
        "libopenblas.fb5ae2tyxyh2ijrdkgdgq3xbklktf43h.gfortran-win_amd64.dll",
        "libcrypto-3-x64.dll",
        "libssl-3-x64.dll",
    }
    if name in drop_names:
        return False
    return not any(name.startswith(prefix) for prefix in drop_prefixes)


def _datas():
    datas = []
    processed = Path("qin_pack_assets") / "assets" / "processed"
    keep = [
        "bear_peek_idle.png",
        "bear_peek_press_left.png",
        "bear_peek_press_right.png",
        "bear_peek_sleep.png",
        "bear_peek_wow.png",
        "bear_peek_smile.png",
        "bear_peek_happy.png",
        "bear_peek_sad.png",
        "keyboard.png",
    ]
    for name in keep:
        path = processed / name
        if path.exists():
            datas.append((str(path), "assets/processed"))
    return datas


a = Analysis(
    ["main_tk_light.py"],
    pathex=[],
    binaries=[],
    datas=_datas(),
    hiddenimports=[
        "pynput._util.win32",
        "pynput._util.win32_vks",
        "pynput.keyboard._base",
        "pynput.keyboard._win32",
        "pynput.mouse._base",
        "pynput.mouse._win32",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6",
        "shiboken6",
        "PIL",
        "Pillow",
        "numpy",
        "asset_generator",
        "transparent_processor",
        "icon_processor",
        "prepare_qin_assets",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

a.binaries = [entry for entry in a.binaries if _keep_toc_entry(entry)]
a.datas = [entry for entry in a.datas if _keep_toc_entry(entry)]
a.pure = [entry for entry in a.pure if _keep_toc_entry(entry)]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="KeyBearCompanion",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    icon=["qin_pack_assets\\assets\\processed\\app_icon.ico"],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="KeyBearCompanion",
)
