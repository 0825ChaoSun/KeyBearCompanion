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
        "PySide6/translations/".lower(),
        "PySide6/plugins/generic/".lower(),
        "PySide6/plugins/iconengines/".lower(),
        "PySide6/plugins/networkinformation/".lower(),
        "PySide6/plugins/platforminputcontexts/".lower(),
        "PySide6/plugins/styles/".lower(),
        "PySide6/plugins/tls/".lower(),
    )
    drop_names = {
        "libopenblas.fb5ae2tyxyh2ijrdkgdgq3xbklktf43h.gfortran-win_amd64.dll",
        "libcrypto-3-x64.dll",
        "libssl-3-x64.dll",
        "PySide6/Qt6Network.dll".lower(),
        "PySide6/Qt6OpenGL.dll".lower(),
        "PySide6/Qt6Pdf.dll".lower(),
        "PySide6/Qt6Qml.dll".lower(),
        "PySide6/Qt6QmlMeta.dll".lower(),
        "PySide6/Qt6QmlModels.dll".lower(),
        "PySide6/Qt6QmlWorkerScript.dll".lower(),
        "PySide6/Qt6Quick.dll".lower(),
        "PySide6/Qt6Svg.dll".lower(),
        "PySide6/Qt6VirtualKeyboard.dll".lower(),
        "PySide6/opengl32sw.dll".lower(),
        "PySide6/QtNetwork.pyd".lower(),
    }
    drop_image_plugins = (
        "PySide6/plugins/imageformats/qgif.dll".lower(),
        "PySide6/plugins/imageformats/qicns.dll".lower(),
        "PySide6/plugins/imageformats/qpdf.dll".lower(),
        "PySide6/plugins/imageformats/qsvg.dll".lower(),
        "PySide6/plugins/imageformats/qtga.dll".lower(),
        "PySide6/plugins/imageformats/qtiff.dll".lower(),
        "PySide6/plugins/imageformats/qwbmp.dll".lower(),
        "PySide6/plugins/imageformats/qwebp.dll".lower(),
    )
    if name in drop_names or name in drop_image_plugins:
        return False
    return not any(name.startswith(prefix) for prefix in drop_prefixes)


def _processed_datas():
    datas = []
    processed = Path("assets") / "processed"
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
        "app_icon.ico",
        "app_icon.png",
    ]
    for name in keep:
        path = processed / name
        if path.exists():
            datas.append((str(path), "assets/processed"))
    if Path("settings.json").exists():
        datas.append(("settings.json", "."))
    return datas


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=_processed_datas(),
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "asset_generator",
        "transparent_processor",
        "icon_processor",
        "PIL",
        "Pillow",
        "numpy",
        "PySide6.QtNetwork",
        "PySide6.QtOpenGL",
        "PySide6.QtPdf",
        "PySide6.QtQml",
        "PySide6.QtQuick",
        "PySide6.QtSvg",
        "PySide6.QtVirtualKeyboard",
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="KeyBearCompanion",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["assets\\processed\\app_icon.ico"],
)
