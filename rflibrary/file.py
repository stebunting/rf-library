import os
import re
import datetime
import xml.etree.ElementTree
import data

class InvalidFileError(Exception):
    "Invalid file"

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
            self.update_tv_channels()
            self._get_new_filename()
            self._io_read()

    def start_frequency_format(self):
        return None if self._start_frequency is None else f'{self._start_frequency:.3f}MHz'

    def stop_frequency_format(self):
        return None if self._stop_frequency is None else f'{self._stop_frequency:.3f}MHz'

    def resolution_format(self):
        return f'{self.resolution:.3f}MHz'

    def date_format(self, date_format):
        return self.creation_date.strftime(date_format)

    # Method to check validity and get file details
    def _read_file(self):
        # Ensure file has valid extension
        if self._ext.lower() != '.csv' and self._ext.lower() != '.sdb2':
            return False

        # Read first line of file
        with open(self._full_filename, 'r', encoding='utf-8') as file:
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
    def update_tv_channels(self):
        if self._tv_country == 'United States of America':
            self._tv_country = 'United States of America'
        else:
            self._tv_country = 'UK'
        for chan in TV_CHANNELS[self._tv_country]:
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

    def get_output_file(self):
        output_string = ''
        for [freq, value] in self.frequencies:
            output_string += f'{freq:09.4f},{value:09.4f}\n'
        return output_string


TV_CHANNELS = {
    'UK': [
        [1, 43.25, 50],
        [2, 50, 55],
        [3, 55, 60],
        [4, 60, 65],
        [5, 65, 70],
        [6, 178, 183],
        [7, 183, 188],
        [8, 188, 193],
        [9, 193, 198],
        [10, 198, 203],
        [11, 203, 208],
        [12, 208, 213],
        [13, 213, 218],
        [21, 470, 478],
        [22, 478, 486],
        [23, 486, 494],
        [24, 494, 502],
        [25, 502, 510],
        [26, 510, 518],
        [27, 518, 526],
        [28, 526, 534],
        [29, 534, 542],
        [30, 542, 550],
        [31, 550, 558],
        [32, 558, 566],
        [33, 566, 574],
        [34, 574, 582],
        [35, 582, 590],
        [36, 590, 598],
        [37, 598, 606],
        [38, 606, 614],
        [39, 614, 622],
        [40, 622, 630],
        [41, 630, 638],
        [42, 638, 646],
        [43, 646, 654],
        [44, 654, 662],
        [45, 662, 670],
        [46, 670, 678],
        [47, 678, 686],
        [48, 686, 694],
        [49, 694, 702],
        [50, 702, 710],
        [51, 710, 718],
        [52, 718, 726],
        [53, 726, 734],
        [54, 734, 742],
        [55, 742, 750],
        [56, 750, 758],
        [57, 758, 766],
        [58, 766, 774],
        [59, 774, 782],
        [60, 782, 790],
        [61, 790, 798],
        [62, 798, 806],
        [63, 806, 814],
        [64, 814, 822],
        [65, 822, 830],
        [66, 830, 838],
        [67, 838, 846],
        [68, 846, 854],
        [69, 854, 862],
        [70, 862, 870],
        [71, 870, 878]
    ],
    'United States of America': [
        [2, 54, 60],
        [3, 60, 66],
        [4, 66, 72],
        [5, 76, 82],
        [6, 82, 88],
        [7, 174, 180],
        [8, 180, 186],
        [9, 186, 192],
        [10, 192, 198],
        [11, 198, 204],
        [12, 204, 210],
        [13, 210, 216],
        [14, 470, 476],
        [15, 476, 482],
        [16, 482, 488],
        [17, 488, 494],
        [18, 494, 500],
        [19, 500, 506],
        [20, 506, 512],
        [21, 512, 518],
        [22, 518, 524],
        [23, 524, 530],
        [24, 530, 536],
        [25, 536, 542],
        [26, 542, 548],
        [27, 548, 554],
        [28, 554, 560],
        [29, 560, 566],
        [30, 566, 572],
        [31, 572, 578],
        [32, 578, 584],
        [33, 584, 590],
        [34, 590, 596],
        [35, 596, 602],
        [36, 602, 608],
        [37, 608, 614],
        [38, 614, 620],
        [39, 620, 626],
        [40, 626, 632],
        [41, 632, 638],
        [42, 638, 644],
        [43, 644, 650],
        [44, 650, 656],
        [45, 656, 662],
        [46, 662, 668],
        [47, 668, 674],
        [48, 674, 680],
        [49, 680, 686],
        [50, 686, 692],
        [51, 692, 698],
        [52, 698, 704],
        [53, 704, 710],
        [54, 710, 716],
        [55, 716, 722],
        [56, 722, 728],
        [57, 728, 734],
        [58, 734, 740],
        [59, 740, 746],
        [60, 746, 752],
        [61, 752, 758],
        [62, 758, 764],
        [63, 764, 770],
        [64, 770, 776],
        [65, 776, 782],
        [66, 782, 788],
        [67, 788, 794],
        [68, 794, 800],
        [69, 800, 806],
        [70, 806, 812],
        [71, 812, 818],
        [72, 818, 824],
        [73, 824, 830],
        [74, 830, 836],
        [75, 836, 842],
        [76, 842, 848],
        [77, 848, 854],
        [78, 854, 860],
        [79, 860, 866],
        [80, 866, 872],
        [81, 872, 878],
        [82, 878, 884],
        [83, 884, 890]
    ]
}
