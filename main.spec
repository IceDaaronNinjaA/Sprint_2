# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

import arcade
from PyInstaller.utils.hooks import copy_metadata

# Arcade resolves its built-in textures, fonts, and shaders at runtime through
# the ``:resources:`` path.  Metadata alone is not enough for a frozen build;
# include the assets directory as well.  Arcade's own PyInstaller hook already
# supplies the system resources and VERSION file.
arcade_dir = Path(arcade.__file__).parent
datas = [
    (str(arcade_dir / 'resources' / 'assets'), 'arcade/resources/assets'),
]
datas += copy_metadata('arcade')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
