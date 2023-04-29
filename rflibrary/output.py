import os
import datetime
from file import File, InvalidFileError
import settings

class Output:
    def __init__(self, **kwargs):
        # File List
        self.files = []

        # Venue Details
        self.venue = kwargs['venue']
        self.town = kwargs['town']
        self.country = kwargs['country']
        self.in_out = io_list[0]

        # Filesystem Details
        self._subdirectory = True
        self._default_master_filename = True
        self._custom_master_filename = False
        self.custom_subdirectory = False
        self.scan_output_location = None
        self._target_location = None
        self._library_location = None
        self.target_subdirectory = self.in_out
        self.file_structure = kwargs['file_structure']
        self.scan_master_filename = ''
        self.default_output_location = True
        self.default_library_location = kwargs['default_library_location']
        self.dir_structure = kwargs['dir_structure']

        # Timestamp Details
        self.scan_datetimestamp = datetime.date.today()
        self.date_format = self.set_date_format(kwargs['date_format'])

        # Personal Details
        self.forename = kwargs['forename']
        self.surname = kwargs['surname']

        # Preferences
        self.copy_source_files = kwargs['copy_source_files']
        self.delete_source_files = kwargs['delete_source_files']

        self.io_guess = 0
        self.io_fixed = False

        self.low_freq_limit = kwargs['low_freq_limit']
        self.high_freq_limit = kwargs['high_freq_limit']

        self._set_master_filename()

    def num_files(self):
        return len(self.files)

    def formatted_date(self):
        return self.scan_datetimestamp.strftime(self.date_format)

    def add_file(self, file, country):
        new_file = File(file, country)
        if not new_file.valid:
            raise InvalidFileError

        self.io_guess += new_file.in_out
        self.files.append(new_file)
        self._update_output()

    def remove_file(self, file):
        self.io_guess -= file.in_out
        self.files.remove(file)
        self._update_output()

    def clear_files(self):
        del self.files[:]
        self.io_fixed = False
        self.io_guess = 0
        self._update_output()

    def use_date(self, file_index):
        self.scan_datetimestamp = self.files[file_index].creation_date
        self._set_master_filename()
        return self.formatted_date()

    def reset_output_location(self):
        self.default_output_location = True
        self._set_master_filename()
        return self.target_subdirectory

    def set_custom_subdirectory(self):
        self.custom_subdirectory = True
        self._set_master_filename()

    def set_custom_master_filename(self):
        self._custom_master_filename = True
        self._default_master_filename = False

    def reset_master_filename(self):
        self._custom_master_filename = False
        self._default_master_filename = True
        self._set_master_filename()
        return self._default_master_filename

    def set_custom_destination(self, destination):
        self.default_output_location = False
        self._library_location = destination
        self.scan_output_location = self._library_location

    def _update_output(self):
        self.get_scan_date()
        if self.default_output_location is True:
            self.target_subdirectory = self.in_out
            self._subdirectory = True
        else:
            self.target_subdirectory = ''
            self._subdirectory = False
        self._set_master_filename()

    def get_scan_date(self):
        if len(self.files) == 0:
            self.scan_datetimestamp = datetime.date.today()
        else:
            self.scan_datetimestamp = min(
                self.files,
                key=lambda file: file.creation_date).creation_date

    # Method to convert user input directory structure into path
    def parse_structure(self, string):
        for old, new in [
            ('%c', self.country),
            ('%t', self.town),
            ('%v', self.venue),
            ('%y', str(self.scan_datetimestamp.year)),
            ('%i', self.in_out),
            ('%s', self.target_subdirectory),
            ('%f', self.forename),
            ('%n', self.surname),
            ('%m', f'{self.scan_datetimestamp.month:02d}'),
            ('%M', self.scan_datetimestamp.strftime('%B')),
            ('%d', f'{self.scan_datetimestamp.day:02d}')]:
            string = string.replace(old, new)
        return string

    def _set_master_filename(self):
        # Return if user has entered a custom master filename
        if self._custom_master_filename:
            return

        self.scan_master_filename = self.parse_structure(self.file_structure + '.csv')

        if self.default_output_location is True:
            self._library_location = self.default_library_location
            self._target_location = self.parse_structure(os.path.join(self.dir_structure, '%s'))
        else:
            self._target_location = self.target_subdirectory
            if self.target_subdirectory != '':
                self._target_location = self._target_location
        self.scan_output_location = os.path.join(self._library_location, self._target_location)

    def write_output_file(self):
        output_file = []
        for file in self.files:
            for freq, value in file.frequencies:
                if freq >= self.low_freq_limit and (self.high_freq_limit == 0 or freq <= self.high_freq_limit):
                    output_file.append([float(freq), float(value)])

        # Remove duplicates
        output_file = sorted(output_file)
        i = 1
        while i < len(output_file):
            if output_file[i][0] == output_file[i - 1][0]:
                output_file.remove(output_file[i - 1])
            else:
                i += 1

        output_string = ''
        for freq, value in output_file:
            output_string += f'{freq:09.4f},{value:09.4f}\n'

        return output_string

    def write_wsm_file(self, title):
        output_file = []
        for file in self.files:
            for freq, value in file.frequencies:
                if freq >= self.low_freq_limit and (self.high_freq_limit == 0 or freq <= self.high_freq_limit):
                    output_file.append([float(freq), float(value)])

        # Remove duplicates
        output_file = sorted(output_file)
        i = 1
        while i < len(output_file):
            if output_file[i][0] == output_file[i - 1][0]:
                output_file.remove(output_file[i - 1])
            else:
                i += 1

        wsm_date = self.scan_datetimestamp.strftime('%Y-%m-%d 00:00:00')
        output_string = (f'Receiver;{title}\n'
                         f'Date/Time;{wsm_date}\n'
                         'RFUnit;dBm\n\n\nFrequency Range [kHz];'
                         f'{(self.low_freq_limit * 1000):06d};'
                         f'{self.high_freq_limit * 1000:06d};\n')
        output_string += 'Frequency;RF level (%);RF level\n'
        for freq, value in reversed(output_file):
            output_string += f'{int(freq * 1000):06d};;{value:04.1f}\n'

        return output_string

    # Helper function to set dateFormat
    def set_date_format(self, date_format):
        if date_formats.get(date_format):
            return date_formats.get(date_format)
        return date_formats.get(settings.DEFAULT_DATE_FORMAT)

date_formats = {
    'yyyy-mm-dd': '%Y-%m-%d',
    'yyyy-dd-mm': '%Y-%d-%m',
    'dd-mm-yyyy': '%d-%m-%Y',
    'mm-dd-yyyy': '%m-%d-%Y'
}

io_list = [
    'Inside',
    'Outside']

country_list = (
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
    f'C{chr(244)}te d\'Ivoire',
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
    'Zimbabwe')
