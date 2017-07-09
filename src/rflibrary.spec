# -*- mode: python -*-

block_cipher = None


a = Analysis(['rflibrary'],
             pathex=['/Users/Ste/Documents/Programming/rf-library/src'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['pyinstaller-hooks'],
             runtime_hooks=['pyinstaller-hooks/pyi_rth__tkinter.py'],
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
          name='rflibrary',
          debug=False,
          strip=False,
          upx=True,
          console=False )
app = BUNDLE(exe,
             name='RF Library.app',
             icon='rflibrary.icns',
             bundle_identifier=None,
             info_plist={
              'CFBundleName': 'RF Library',
              'CFBundleDisplayName': 'RF Library',
              'CFBundleVersion': 0.4,
              'CFBundleShortVersionString': 0.4,
              'CFBundleGetInfoString': '0.4 © Steve Bunting 2017'
            })
