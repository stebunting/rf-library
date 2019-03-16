# -*- mode: python -*-

# Tkinter location fix using hooks
# https://github.com/pyinstaller/pyinstaller/issues/3753

# work-around for https://github.com/pyinstaller/pyinstaller/issues/4064
import distutils
if distutils.distutils_path.endswith('__init__.py'):
    distutils.distutils_path = os.path.dirname(distutils.distutils_path)

block_cipher = None

a = Analysis(['rf-library'],
             pathex=['/Users/stebunting/Dev/rf-library/src'],
             binaries=[],
             datas=[('icons/*', 'icons')],
             hiddenimports=[],
             hookspath=[],	
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='rf-library',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
app = BUNDLE(exe,
          name='RF Library.app',
          icon='icons/logo.icns',
          version='0.42',
          bundle_identifier='com.stevebunting.rf-library')