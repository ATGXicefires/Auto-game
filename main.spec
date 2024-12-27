# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\modules\\main.py','src\\modules\\functions.py','src\\modules\\ui_logic.py','src\\modules\\main_view.py','src\\modules\\log_view.py'],
    pathex=[],
    binaries=[],
    datas=[('ADB', 'ADB')],
    hiddenimports=[],
    hookspath=[],
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
    name='AutoGameClicker v0.4.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version.txt',
    icon='app.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoGameClicker v0.4.1',
)
