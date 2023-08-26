import platform
import os
import sys

# Get absolute path to resource, works for dev and for PyInstaller
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, relative_path)

# Software Details
TITLE = "RF Library"
VERSION = "v0.6.3"
ICON_LOCATION = resource_path('icons')
WEBSITE_URI = "https://rflibrary.stevebunting.com/"
UPDATE_FILE_LOCATION = "https://rf-library-backend.onrender.com/version"

# Check system and set necessary variables
if platform.system() == 'Darwin':
    SYSTEM = 'Mac'
    COMMAND = 'Command-'
    COMMAND_ABBR = 'Command-'
    COMMAND_SYMBOL = '⌘'
    MODIFIER = 'Shift-'
    MODIFIER_ABBR = 'Shift-'
    MODIFIER_SYMBOL = '⇧'
    ALT = 'Alt-'
    ALT_ABBR = 'Alt-'
    ALT_SYMBOL = '⎇'
    PLIST_PATH = os.path.expanduser('~/Library/Preferences')
    PLIST_FILE = 'com.stevebunting.rflibrary.plist'
    default_library_location = os.path.expanduser('~/Documents/Scans')
else:
    SYSTEM = 'Windows'
    COMMAND = 'Control-'
    COMMAND_ABBR = 'Ctrl+'
    COMMAND_SYMBOL = '^'
    MODIFIER = 'Shift-'
    MODIFIER_ABBR = 'Shift+'
    MODIFIER_SYMBOL = '⇧'
    ALT = 'Alt-'
    ALT_ABBR = 'Alt+'
    ALT_SYMBOL = '⎇'
    PLIST_FILE = 'rflibrary.plist'
    if platform.system() == 'Windows':
        PLIST_PATH = os.path.join(os.environ['APPDATA'], 'RF Library')
        if platform.release() >= '10':
            default_library_location = os.path.expanduser('~\\Documents\\Scans')
        else:
            default_library_location = os.path.expanduser('~\\My Documents\\Scans')
    else:
        PLIST_PATH = os.path.expanduser('~\\.rflibrary')
        default_library_location = os.path.expanduser('~\\Scans')
DEFAULT_LOG_FOLDER = default_library_location
PLIST_NAME = os.path.join(PLIST_PATH, PLIST_FILE)

# GUI Constants
PAD_X_DEFAULT = 2
PAD_Y_DEFAULT = 2

# Maintenence
MAKE_WSM = False
