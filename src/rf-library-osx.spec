# -*- mode: python ; coding: utf-8 -*-

# Import data file
import importlib.util
spec = importlib.util.spec_from_file_location("data.py", "./data.py")
data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data)

# work-around for https://github.com/pyinstaller/pyinstaller/issues/4064
import distutils
if distutils.distutils_path.endswith('__init__.py'):
    distutils.distutils_path = os.path.dirname(distutils.distutils_path)

block_cipher = None

a = Analysis(['rf-library.py'],
             pathex=['/Users/stebunting/Dev/rf-library/src'],
             binaries=[],
             datas=[('icons/*', 'icons')],
             hiddenimports=['numpy.random.common',
                            'numpy.random.bounded_integers',
                            'numpy.random.entropy'],
             hookspath=['pyinstaller-hooks/analysis-hooks'],
             runtime_hooks=['pyinstaller-hooks/runtime-hooks/pyi_rth__tkinter.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='rf-library',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='rf-library')
app = BUNDLE(coll,
             name='RF Library.app',
             icon='icons/logo.icns',
             bundle_identifier='com.stevebunting.rflibrary',
             info_plist={'CFBundleShortVersionString': data.version,
                         'NSPrincipalClass': 'NSApplication',
                         'NSAppleScriptEnabled': False})
