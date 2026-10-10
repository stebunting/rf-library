# -*- mode: python ; coding: utf-8 -*-

import site
site.addsitedir('rflibrary')
import data

a = Analysis(
    ['rflibrary/__main__.py'],
    pathex=['./rflibrary'],
    binaries=[],
    datas=[('rflibrary/icons/*', 'icons')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
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

collection = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='rflibrary')

app = BUNDLE(
    collection,
    name='RF Library.app',
    icon='rflibrary/icons/logo.icns',
    bundle_identifier='com.stevebunting.rflibrary',
    info_plist={
        'CFBundleShortVersionString': data.VERSION,
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False})
