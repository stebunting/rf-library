import os
import re
import datetime
import xml.etree.ElementTree
import data

################################################################################
##########                        FILE OBJECT                         ##########
################################################################################

# Define Data class
class File:
    # Initialise class
    def __init__(self, name, tv_country):
        self.frequencies = []
        self.model = ''
        self.creation_date = datetime.datetime.now()
        self._start_frequency = None
        self._stop_frequency = None
        self.start_tv_channel = None
        self.stop_tv_channel = None
        self.data_points = 0
        self.resolution = 0
        self.new_filename = ''
        self.in_out = 0
        self.valid = None

        self._full_filename = name
        self._tv_country = tv_country
        self.filename = os.path.basename(self._full_filename)
        self.file, self._ext = os.path.splitext(self.filename)

        self.valid = self._read_file()
        if self.valid:
            self._update_tv_channels()
            self._get_new_filename()
            self._io_read()

    def start_frequency_format(self):
        return None if self._start_frequency is None else f'{self._start_frequency:.3f}MHz'

    def stop_frequency_format(self):
        return None if self._stop_frequency is None else f'{self._stop_frequency:.3f}MHz'

    def resolution_format(self):
        return f'{self.resolution:.3f}MHz'

    # Method to check validity and get file details
    def _read_file(self):
        # Ensure file has valid extension
        if self._ext.lower() != '.csv' and self._ext.lower() != '.sdb2':
            return False

        # Read first line of file
        file = open(self._full_filename, 'r', encoding='utf-8')
        first_line = file.readline().rstrip()
        file.seek(0)

        # Identify type of scan file from first line and parse
        if first_line[0:11] == 'Model Type:':
            self._parse_csv_scan(file, f'TTi {first_line[12:-1]}')
        elif first_line[0:9] == 'Receiver;':
            self._parse_wsm_scan(file)
        elif first_line[0:38] == '<?xml version="1.0" encoding="UTF-8"?>':
            self._parse_shure_scan(file)
        else:
            self._parse_csv_scan(file, 'Generic')
        file.close()
        if len(self.frequencies) == 0:
            return False

        # Get file details
        self._start_frequency = min(freq[0] for freq in self.frequencies)
        self._stop_frequency = max(freq[0] for freq in self.frequencies)
        self.data_points = len(self.frequencies)
        self.resolution = ((self._stop_frequency - self._start_frequency)
                          / (self.data_points - 1))

        return True

    # Parse an XML scan created by Shure WWB6 and hardware
    def _parse_shure_scan(self, file):
        tree = xml.etree.ElementTree.parse(file)
        xmldoc = tree.getroot()
        model = xmldoc.attrib['model']
        if model in ('TODO', ''):
            self.model = 'Shure AXT600'
        else:
            self.model = f'Shure {model} ({xmldoc.attrib["band"]})'
        self.frequencies = []
        for freq, level in zip(xmldoc[0][0], xmldoc[0][1]):
            self.frequencies.append([float(freq.text) / 1000, float(level.text)])
        self.creation_date = datetime.datetime.fromtimestamp(
                            float(xmldoc[0][1].attrib['date_time']) / 1000)

    # Parse a CSV file
    def _parse_csv_scan(self, file, model):
        self.model = model
        for line in file:
            split_line = re.split('[\t,;]', line)
            try:
                freq = float(split_line[0].strip())
                value = float(split_line[1].strip())
                self.frequencies.append([freq, value])
            except ValueError:
                pass
        self.get_creation_date()

    # Parse a WSM file
    def _parse_wsm_scan(self, file):
        self.model = 'Sennheiser WSM'
        wsm_low_limit = -99
        wsm_high_limit = -30
        wsm_multiplier = wsm_low_limit - wsm_high_limit # -69
        for line in file:
            split_line = re.split('[    ,; ]', line)
            try:
                freq = float(split_line[0]) / 1000
                value = wsm_low_limit - (float(split_line[2]) * 0.0065 * wsm_multiplier)
                # -34.2 = -99 - (9988 * ? * -69)
                # -64.8 / (9988 * -69) = 0,0065

                if freq > 1:
                    self.frequencies.append([freq, value])
            except (ValueError, IndexError):
                pass
        self.get_creation_date()

    # Method to return creation date from file
    def get_creation_date(self):
        if data.SYSTEM == 'Mac':
            self.creation_date = datetime.datetime.fromtimestamp(
                os.stat(self._full_filename).st_birthtime)
        elif data.SYSTEM == 'Windows':
            self.creation_date = datetime.datetime.fromtimestamp(
                os.stat(self._full_filename).st_ctime)

    # Method to get TV channels
    def _update_tv_channels(self):
        if self._tv_country == 'United States of America':
            self._tv_country = 'United States of America'
        else:
            self._tv_country = 'UK'
        for chan in data.TV_CHANNELS[self._tv_country]:
            if self.start_tv_channel is None:
                if (self._start_frequency >= float(chan[1]) and
                    self._start_frequency < float(chan[2])):
                    self.start_tv_channel = chan[0]
            else:
                if (self._stop_frequency > float(chan[1]) and
                    self._stop_frequency <= float(chan[2])):
                    self.stop_tv_channel = chan[0]
                    break

    # Method to get new filename based on BestAudio naming structure
    def _get_new_filename(self):
        if 80 <= self._start_frequency <= 120:
            self.new_filename = 'FM'
        elif 54 <= self._start_frequency <= 88:
            self.new_filename = f'{(int(self._start_frequency - 42) // 6):02d}'
        elif 174 <= self._start_frequency <= 216:
            self.new_filename = f'{int(self._start_frequency - 132) // 6:02d}'
        elif 470 <= self._start_frequency <= 890:
            self.new_filename = f'{int(self._start_frequency - 386) // 6:02d}'
        elif 902 <= self._start_frequency <= 928:
            self.new_filename = '900'
        elif 944 <= self._start_frequency <= 952:
            self.new_filename = 'X1'
        elif 1920 <= self._start_frequency <= 1930:
            self.new_filename = 'DUSA'
        elif 1910 <= self._start_frequency <= 1930:
            self.new_filename = 'DSA'
        elif 1910 <= self._start_frequency <= 1920:
            self.new_filename = 'DBRA'
        elif 1893 <= self._start_frequency <= 1906:
            self.new_filename = 'DJAP'
        elif 1880 <= self._start_frequency <= 1900:
            self.new_filename = 'DEUR'
        else:
            self.new_filename = f'{self._start_frequency:.0f}MHz'
        self.new_filename = f'{self.new_filename}.csv'

    # Method to guess whether scan is inside or outside
    def _io_read(self):
        lowercase_filename = self.file.lower()
        if 'in' in lowercase_filename:
            self.in_out = 1
        elif 'out' in lowercase_filename:
            self.in_out = -1
