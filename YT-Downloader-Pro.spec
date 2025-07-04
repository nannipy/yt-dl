# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['downloader_nannipy.py'],
    pathex=[],
    binaries=[('ffmpeg', '.'), ('ffprobe', '.')],
    datas=[('icon.png', '.'), ('logo.png', '.')],
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
    name='YT-Downloader-Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YT-Downloader-Pro',
)
app = BUNDLE(
    coll,
    name='YT-Downloader-Pro.app',
    icon='icon.icns',
    bundle_identifier=None,
)
