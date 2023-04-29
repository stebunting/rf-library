import os
import plistlib
import data

# Defaults
DEFAULT_DIRECTORY_STRUCTURE = os.path.join('%c', '%t %v', '%y')
DEFAULT_FILENAME_STRUCTURE = '%t %c-%v-%y%m%d-%i %f %n'
DEFAULT_DATE_FORMAT = 'yyyy-mm-dd'

# Load settings plist if it exists yet
errors_to_display = []

def get_plist_file():
    settings = {}
    exists = True
    new_file = False

    if not os.path.isfile(data.PLIST_NAME):
        exists = False
        try:
            os.makedirs(data.PLIST_PATH, exist_ok=True)
        except PermissionError:
            errors_to_display.append(2)
        try:
            with open(data.PLIST_NAME, 'wb'):
                os.chmod(data.PLIST_NAME, 0o600)
            new_file = True
        except (PermissionError, FileNotFoundError):
            errors_to_display.append(3)
    else:
        try:
            with open(data.PLIST_NAME, 'rb') as plist_file:
                settings = plistlib.load(plist_file)
        except PermissionError:
            errors_to_display.append(1)
    return settings, exists, new_file

def set_plist_defaults(settings):
    # Check for preferences and add default if not there
    plist_keys = [
        'create_log',
        'logFolder',
        'forename',
        'surname',
        'dir_structure',
        'file_structure',
        'defaultOfcomInclude',
        'default_date_format',
        'low_freq_limit',
        'high_freq_limit',
        'defaultVenue',
        'defaultTown',
        'defaultCountry',
        'defaultCopy',
        'defaultDelete',
        'defaultSourceLocation',
        'default_library_location',
        'auto_update_check']
    plist_defaults = [
        True,
        data.DEFAULT_LOG_FOLDER,
        '',
        '',
        DEFAULT_DIRECTORY_STRUCTURE,
        DEFAULT_FILENAME_STRUCTURE,
        False,
        DEFAULT_DATE_FORMAT,
        0,
        0,
        'Venue',
        'Town',
        'United Kingdom',
        True,
        False,
        os.path.expanduser('~'),
        data.default_library_location,
        True]
    for plist_var, plist_default in zip(plist_keys, plist_defaults):
        if plist_var not in plist:
            settings[plist_var] = plist_default
    return settings

def dump_plist(settings):
    with open(data.PLIST_NAME, 'wb') as plist_file:
        plistlib.dump(settings, plist_file)

plist, SETTINGS_EXISTS, NEW_SETTINGS_FILE = get_plist_file()
plist = set_plist_defaults(plist)
if NEW_SETTINGS_FILE:
    dump_plist(plist)

def set_new_defaults(venue, town, country, copy_source, delete_source):
    plist['defaultVenue'] = venue
    plist['defaultTown'] = town
    plist['defaultCountry'] = country
    plist['defaultCopy'] = copy_source
    plist['defaultDelete'] = delete_source

    with open(data.PLIST_NAME, 'wb') as file:
        plistlib.dump(plist, file)
