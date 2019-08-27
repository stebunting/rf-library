# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['rf-library'],
             pathex=['C:\\Users\\USER\\Documents\\rf-library\\src'],
             binaries=[],
             datas=[('icons/*', 'icons')],
             hiddenimports=['numpy.random.common',
                            'numpy.random.bounded_integers',
                            'numpy.random.entropy'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='RF Library',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='icons/logo.ico')
