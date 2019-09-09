#!/usr/bin/env python

import platform
import os
import sys
import plistlib
import keyring

# Get absolute path to resource, works for dev and for PyInstaller
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, relative_path)

# Software Details
APPLICATION_NAME = "RF Library"
APPLICATION_VERSION = "0.5.4"
WEBSITE_URI = "https://rflibrary.stevebunting.com/"
APPLICATION_UPDATE_XML_LOCATION = "{}latestVersion.xml".format(WEBSITE_URI)
ICON_LOCATION = resource_path('icons')

# Check system and set necessary variables
if platform.system() == 'Windows':
    system = 'Windows'
    command = 'Control-'
    command_abbr = 'Ctrl+'
    command_symbol = '^'
    modifier = 'Shift-'
    modifier_abbr = 'Shift+'
    modifier_symbol = '⇧'
    alt = 'Alt-'
    alt_abbr = 'Alt+'
    alt_symbol = '⎇'
elif platform.system() == 'Darwin':
    system = 'Mac'
    command = 'Command-'
    command_abbr = 'Command-'
    command_symbol = '⌘'
    modifier = 'Shift-'
    modifier_abbr = 'Shift-'
    modifier_symbol = '⇧'
    alt = 'Alt-'
    alt_abbr = 'Alt-'
    alt_symbol = '⎇'

# GUI Constants
PAD_X = 2
PAD_Y = 2

# Defaults
logFileName = 'rflibrary-log.csv'

# Maintenence
show_ofcom = False
makeWSM = False

class Settings():

    def __init__(self):

        self.plist = dict()

        # Define location of settings file
        if platform.system() == 'Windows':
            self.plistPath = os.path.join(os.environ['APPDATA'], 'RF Library')
            self.plistFile = 'rflibrary.plist'
            if platform.release() == '10':
                self.defaultLibraryLocation = os.path.expanduser('~\\Documents\\Scans')
            else:
                self.defaultLibraryLocation = os.path.expanduser('~\\My Documents\\Scans')

        elif platform.system() == 'Darwin':
            self.plistPath = os.path.expanduser('~/Library/Preferences')
            self.plistFile = 'com.stevebunting.rflibrary.plist'
            self.defaultLibraryLocation = os.path.expanduser('~/Documents/Scans')

        self.plistName = os.path.join(self.plistPath, self.plistFile)
        self.defaultLogFolder = self.defaultLibraryLocation

        # Defaults
        self.defaultDateFormat = 'yyyy-mm-dd'
        self.defaultDirectoryStructure = os.path.join('%c', '%t %v', '%y')
        self.defaultFilenameStructure = '%t %c-%v-%y%m%d-%i %f %n'

        # Load settings plist if it exists yet
        self._errors = []
        self.exists = True
        new_settings_file = False

        # Create settings file if it doesn't exist
        if not os.path.isfile(self.plistName):
            self.exists = False

            # Create path
            try:
                os.makedirs(self.plistPath, exist_ok=True)
            except PermissionError:
                self._errors.append(2)

            # Create file
            try:
                fp = open(self.plistName, 'wb')
                fp.close()
                os.chmod(self.plistName, 0o600)
                new_settings_file = True
            except (PermissionError, FileNotFoundError):
                self._errors.append(3)

        # Load settings file if it exists
        else:
            try:
                with open(self.plistName, 'rb') as fp:
                    self.plist = plistlib.load(fp)
            except PermissionError:
                self._errors.append(1)

        # Check through all preferences and add default if not there
        vars = ('ofcomAccountName', 'ofcomUserName', 'createLog', 'logFolder',
                'forename', 'surname', 'dirStructure',
                'fileStructure', 'defaultOfcomInclude', 'defaultDateFormat',
                'lowFreqLimit', 'highFreqLimit', 'defaultVenue', 'defaultTown',
                'defaultCountry', 'defaultCopy', 'defaultDelete',
                'defaultSourceLocation', 'defaultLibraryLocation',
                'autoUpdateCheck')
        defaults = ('', '', True, self.defaultLogFolder,
                    '', '', self.defaultDirectoryStructure,
                    self.defaultFilenameStructure, False, self.defaultDateFormat,
                    0, 0, 'Venue', 'Town',
                    'United Kingdom', True, False,
                    os.path.expanduser('~'), self.defaultLibraryLocation,
                    True)
        for var, default in zip(vars, defaults):
            if var not in self.plist:
                self.plist[var] = default

        if new_settings_file:
            self.dump()

    # Dump plist to settings file
    def dump(self):
        try:
            with open(self.plistName, 'wb') as fp:
                plistlib.dump(self.plist, fp)
        except PermissionError:
            self._errors.append(1)

    # Update OFCOM password in Keychain
    def set_ofcom_password(self, account_name, account_password):
        keyring.set_password(APPLICATION_NAME, account_name, account_password)

    # Retrieve OFCOM password from Keychain
    def get_ofcom_password(self):
        return keyring.get_password(APPLICATION_NAME, self.plist['ofcomAccountName'])

    # Return true if errors are present
    def has_error(self):
        if len(self._errors) > 0:
            return True
        else:
            return False

    # Return error code for display
    def display_error(self):
        return self._errors.pop(0)

# Variables
tv_channels = {
    'UK': (
        (1, 43.25, 50),
        (2, 50, 55),
        (3, 55, 60),
        (4, 60, 65),
        (5, 65, 70),
        (6, 178, 183),
        (7, 183, 188),
        (8, 188, 193),
        (9, 193, 198),
        (10, 198, 203),
        (11, 203, 208),
        (12, 208, 213),
        (13, 213, 218),
        (21, 470, 478),
        (22, 478, 486),
        (23, 486, 494),
        (24, 494, 502),
        (25, 502, 510),
        (26, 510, 518),
        (27, 518, 526),
        (28, 526, 534),
        (29, 534, 542),
        (30, 542, 550),
        (31, 550, 558),
        (32, 558, 566),
        (33, 566, 574),
        (34, 574, 582),
        (35, 582, 590),
        (36, 590, 598),
        (37, 598, 606),
        (38, 606, 614),
        (39, 614, 622),
        (40, 622, 630),
        (41, 630, 638),
        (42, 638, 646),
        (43, 646, 654),
        (44, 654, 662),
        (45, 662, 670),
        (46, 670, 678),
        (47, 678, 686),
        (48, 686, 694),
        (49, 694, 702),
        (50, 702, 710),
        (51, 710, 718),
        (52, 718, 726),
        (53, 726, 734),
        (54, 734, 742),
        (55, 742, 750),
        (56, 750, 758),
        (57, 758, 766),
        (58, 766, 774),
        (59, 774, 782),
        (60, 782, 790),
        (61, 790, 798),
        (62, 798, 806),
        (63, 806, 814),
        (64, 814, 822),
        (65, 822, 830),
        (66, 830, 838),
        (67, 838, 846),
        (68, 846, 854),
        (69, 854, 862),
        (70, 862, 870),
        (71, 870, 878)
    ),
    'United States of America': (
        (2, 54, 60),
        (3, 60, 66),
        (4, 66, 72),
        (5, 76, 82),
        (6, 82, 88),
        (7, 174, 180),
        (8, 180, 186),
        (9, 186, 192),
        (10, 192, 198),
        (11, 198, 204),
        (12, 204, 210),
        (13, 210, 216),
        (14, 470, 476),
        (15, 476, 482),
        (16, 482, 488),
        (17, 488, 494),
        (18, 494, 500),
        (19, 500, 506),
        (20, 506, 512),
        (21, 512, 518),
        (22, 518, 524),
        (23, 524, 530),
        (24, 530, 536),
        (25, 536, 542),
        (26, 542, 548),
        (27, 548, 554),
        (28, 554, 560),
        (29, 560, 566),
        (30, 566, 572),
        (31, 572, 578),
        (32, 578, 584),
        (33, 584, 590),
        (34, 590, 596),
        (35, 596, 602),
        (36, 602, 608),
        (37, 608, 614),
        (38, 614, 620),
        (39, 620, 626),
        (40, 626, 632),
        (41, 632, 638),
        (42, 638, 644),
        (43, 644, 650),
        (44, 650, 656),
        (45, 656, 662),
        (46, 662, 668),
        (47, 668, 674),
        (48, 674, 680),
        (49, 680, 686),
        (50, 686, 692),
        (51, 692, 698),
        (52, 698, 704),
        (53, 704, 710),
        (54, 710, 716),
        (55, 716, 722),
        (56, 722, 728),
        (57, 728, 734),
        (58, 734, 740),
        (59, 740, 746),
        (60, 746, 752),
        (61, 752, 758),
        (62, 758, 764),
        (63, 764, 770),
        (64, 770, 776),
        (65, 776, 782),
        (66, 782, 788),
        (67, 788, 794),
        (68, 794, 800),
        (69, 800, 806),
        (70, 806, 812),
        (71, 812, 818),
        (72, 818, 824),
        (73, 824, 830),
        (74, 830, 836),
        (75, 836, 842),
        (76, 842, 848),
        (77, 848, 854),
        (78, 854, 860),
        (79, 860, 866),
        (80, 866, 872),
        (81, 872, 878),
        (82, 878, 884),
        (83, 884, 890)
    )
}

countries = (
    'Afghanistan',
    'Albania',
    'Algeria',
    'Andorra',
    'Angola',
    'Antigua and Barbuda',
    'Argentina',
    'Armenia',
    'Australia',
    'Austria',
    'Azerbaijan',
    'Bahamas',
    'Bahrain',
    'Bangladesh',
    'Barbados',
    'Belarus',
    'Belgium',
    'Belize',
    'Benin',
    'Bhutan',
    'Bolivia',
    'Bosnia and Herzegovina',
    'Botswana',
    'Brazil',
    'Brunei Darussalam',
    'Bulgaria',
    'Burkina Faso',
    'Burundi',
    'Cabo Verde',
    'Cambodia',
    'Cameroon',
    'Canada',
    'Central African Republic',
    'Chad',
    'Chile',
    'China',
    'Colombia',
    'Comoros',
    'Congo',
    'Costa Rica',
    'C{}te d\'Ivoire'.format(chr(244)),
    'Croatia',
    'Cuba',
    'Cyprus',
    'Czech Republic',
    'Democratic People\'s Republic of Korea',
    'Democratic Republic of the Congo',
    'Denmark',
    'Djibouti',
    'Dominica',
    'Dominican Republic',
    'Ecuador',
    'Egypt',
    'El Salvador',
    'Equatorial Guinea',
    'Eritrea',
    'Estonia',
    'Ethiopia',
    'Fiji',
    'Finland',
    'France',
    'Gabon',
    'Gambia',
    'Georgia',
    'Germany',
    'Ghana',
    'Greece',
    'Grenada',
    'Guatemala',
    'Guinea',
    'Guinea Bissau',
    'Guyana',
    'Haiti',
    'Honduras',
    'Hungary',
    'Iceland',
    'India',
    'Indonesia',
    'Iran',
    'Iraq',
    'Ireland',
    'Israel',
    'Italy',
    'Jamaica',
    'Japan',
    'Jordan',
    'Kazakhstan',
    'Kenya',
    'Kiribati',
    'Kuwait',
    'Kyrgyzstan',
    'Lao People\'s Democratic Republic',
    'Latvia',
    'Lebanon',
    'Lesotho',
    'Liberia',
    'Libya',
    'Liechtenstein',
    'Lithuania',
    'Luxembourg',
    'Macedonia',
    'Madagascar',
    'Malawi',
    'Malaysia',
    'Maldives',
    'Mali',
    'Malta',
    'Marshall Islands',
    'Mauritania',
    'Mauritius',
    'Mexico',
    'Micronesia (Federated States of)',
    'Monaco',
    'Mongolia',
    'Montenegro',
    'Morocco',
    'Mozambique',
    'Myanmar',
    'Namibia',
    'Nauru',
    'Nepal',
    'Netherlands',
    'New Zealand',
    'Nicaragua',
    'Niger',
    'Nigeria',
    'Norway',
    'Oman',
    'Pakistan',
    'Palau',
    'Panama',
    'Papua New Guinea',
    'Paraguay',
    'Peru',
    'Philippines',
    'Poland',
    'Portugal',
    'Qatar',
    'Republic of Korea',
    'Republic of Moldova',
    'Romania',
    'Russian Federation',
    'Rwanda',
    'Saint Kitts and Nevis',
    'Saint Lucia',
    'Saint Vincent and the Grenadines',
    'Samoa',
    'San Marino',
    'Sao Tome and Principe',
    'Saudi Arabia',
    'Senegal',
    'Serbia',
    'Seychelles',
    'Sierra Leone',
    'Singapore',
    'Slovakia',
    'Slovenia',
    'Solomon Islands',
    'Somalia',
    'South Africa',
    'South Sudan',
    'Spain',
    'Sri Lanka',
    'Sudan',
    'Suriname',
    'Swaziland',
    'Sweden',
    'Switzerland',
    'Syrian Arab Republic',
    'Tajikistan',
    'Thailand',
    'Timor-Leste',
    'Togo',
    'Tonga',
    'Trinidad and Tobago',
    'Tunisia',
    'Turkey',
    'Turkmenistan',
    'Tuvalu',
    'Uganda',
    'Ukraine',
    'United Arab Emirates',
    'United Kingdom',
    'United Republic of Tanzania',
    'United States of America',
    'Uruguay',
    'Uzbekistan',
    'Vanuatu',
    'Venezuela',
    'Vietnam',
    'Yemen',
    'Zambia',
    'Zimbabwe'
)

date_formats = {
    'yyyy-mm-dd': '%Y-%m-%d',
    'yyyy-dd-mm': '%Y-%d-%m',
    'dd-mm-yyyy': '%d-%m-%Y',
    'mm-dd-yyyy': '%m-%d-%Y'
}
