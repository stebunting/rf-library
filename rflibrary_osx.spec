# -*- mode: python ; coding: utf-8 -*-

import site
site.addsitedir('rflibrary')
import data

block_cipher = None

a = Analysis(
    ['rflibrary/__main__.py'],
    pathex=[
        '/Users/stebunting/Dev/.virtualEnvs/rf-library/lib/python3.11/site-packages',
        './rflibrary'],
    binaries=[],
    datas=[('rflibrary/icons/*', 'icons')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='rflibrary',
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
    entitlements_file=None)

app = BUNDLE(
    exe,
    name='RF Library.app',
    icon='rflibrary/icons/logo.icns',
    bundle_identifier='com.stevebunting.rflibrary',
    info_plist={
        'CFBundleShortVersionString': data.VERSION,
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False})
