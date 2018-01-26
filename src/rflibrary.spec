# -*- mode: python -*-

block_cipher = None


a = Analysis(['rflibrary'],
             pathex=['/Users/Ste/Documents/Programming/rf-library/src'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=['pyinstaller-hooks/hook-_tkinter.py', 'pyinstaller-hooks/pyi_rth__tkinter.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='rflibrary',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='rflibrary')
