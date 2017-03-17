"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup
import data

APP = ['rflibrary']
APP_NAME = 'RFLibrary'
DATA_FILES = ['data.py', 'settings.py', 'gui.ico']
OPTIONS = {
    'includes':'tkinter',
	'iconfile':'rflibrary.icns',
	'plist': {
	'CFBundleName': APP_NAME,
    'CFBundleDisplayName': APP_NAME,
    'CFBundleVersion': data.version,
    'CFBundleShortVersionString': data.version, }
    }

setup(
    app = APP,
    data_files = DATA_FILES,
    options = {'py2app': OPTIONS},
    setup_requires = ['py2app'],
)
