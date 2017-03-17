"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

import sys
from setuptools import setup
import data

if sys.platform == 'win32':
    import ez_setup
    ez_setup.use_setuptools()

mainscript = 'rflibrary.py'

APP = ['rflibrary']
APP_NAME = 'RFLibrary'
DATA_FILES = ['data.py', 'settings.py', 'gui.ico']
if sys.platform == 'darwin':
    OPTIONS = {
        'includes':'tkinter',
        'iconfile':'rflibrary.icns',
        'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleVersion': data.version,
        'CFBundleShortVersionString': data.version, }
        }
elif sys.platform == 'win32':
     extra_options = dict(
         setup_requires=['py2exe'],
         app=[mainscript],
     )
else:
     extra_options = dict(
         # Normally unix-like platforms will use "setup.py install"
         # and install the main script as such
         scripts=[mainscript],
     )

setup(
    app = APP,
    data_files = DATA_FILES,
    options = {'py2app': OPTIONS},
    setup_requires = ['py2app'],
)

