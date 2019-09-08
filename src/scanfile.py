#!/usr/bin/env python3

################################################################################
##########                        FILE OBJECT                         ##########
################################################################################

import os
import re
import datetime
import xml.etree.ElementTree
import data

# Define Exception
class InvalidFile(Exception):
    pass

# Define Data class
class ScanFile():

    # Initialise class
    def __init__(self, name, country):

        # Filename with complete path
        self.full_filename = name

        # Filename
        self.filename = os.path.basename(self.full_filename)

        # Split into file and extension
        self.file, self.ext = os.path.splitext(self.filename)

        # Path to file
        self.path = os.path.dirname(self.full_filename)

        # List to store file contents [freq, level]
        self.frequencies = list()

        self._read_file()

        # Analyse file
        self._update__tv_channels(country)
        self.new_filename = self._get_new_filename()
        self.io = self._in_out_read()

    # Method to check validity and get file destails
    def _read_file(self):

        # Ensure file has valid extension
        if self.ext.lower() != '.csv' and self.ext.lower() != '.sdb2':
            raise InvalidFile('File must of type csv or sdb2 only')
        
        # Read first line of file
        fp = open(self.full_filename, 'r', encoding='utf-8')
        first_line = fp.readline().rstrip()
        fp.seek(0)
        
        # Identify type of scan file from first line and parse
        if first_line[0:11] == 'Model Type:':
            self._parse_csv_scan(fp, 'TTi {}'.format(first_line[12:-1]))
        elif first_line[0:9] == 'Receiver;':
            self._parse_wsm_scan(fp)
        elif first_line[0:38] == '<?xml version="1.0" encoding="UTF-8"?>':
            self._parse_shure_scan(fp)
        else:
            self._parse_csv_scan(fp, 'Generic')
        fp.close()

        # If there is no scan information in file, return False
        if len(self.frequencies) == 0:
            raise InvalidFile('File must contain valid scan data')

        # Sort list of frequencies
        self.frequencies.sort()

        # Get file details
        self.start_frequency = self.frequencies[0][0]
        self.stop_frequency = self.frequencies[-1][0]
        self.data_points = len(self.frequencies)
        self.resolution = ((self.stop_frequency - self.start_frequency)
                          / (self.data_points - 1))
    
    # Parse an XML scan created by Shure WWB6 and hardware
    def _parse_shure_scan(self, fp):
        tree = xml.etree.ElementTree.parse(fp)
        xmldoc = tree.getroot()
        model = xmldoc.attrib['model']
        if model == 'TODO' or model == '':
            self.model = 'Shure AXT600'
        else:
            self.model = 'Shure {} ({})'.format(model, xmldoc.attrib['band'])
        for freq, level in zip(xmldoc[0][0], xmldoc[0][1]):
            self.frequencies.append((float(freq.text) / 1000, float(level.text)))
        self.creation_date = datetime.datetime.fromtimestamp(
                            float(xmldoc[0][1].attrib['date_time']) / 1000)
            
    # Parse a CSV file
    def _parse_csv_scan(self, fp, model):
        self.model = model
        for line in fp:
            splitLine = re.split('[\t,;]', line)
            try:
                freq = float(splitLine[0].strip())
                value = float(splitLine[1].strip())
                self.frequencies.append((freq, value))
            except ValueError:
                pass
        self._get_creation_date()
            
    # Parse a WSM file
    def _parse_wsm_scan(self, fp):
        self.model = 'Sennheiser WSM'
        wsm_low_limit = -99
        wsm_high_limit = -30
        wsm_multiplier = wsm_low_limit - wsm_high_limit # -69
        for line in fp:
            splitLine = re.split('[    ,; ]', line)
            try:
                freq = float(splitLine[0]) / 1000
                value = wsm_low_limit - (float(splitLine[2]) * 0.0065 * wsm_multiplier)
                # -34.2 = -99 - (9988 * ? * -69)
                # -64.8 / (9988 * -69) = 0,0065

                if freq > 1:
                    self.frequencies.append((freq, value))
            except (ValueError, IndexError):
                pass
        self._get_creation_date()
    
    # Method to return creation date from file
    def _get_creation_date(self):
        if data.system == 'Mac':
            self.creation_date = datetime.datetime.fromtimestamp(os.stat(self.full_filename).st_birthtime)
        elif data.system == 'Windows':
            self.creation_date = datetime.datetime.fromtimestamp(os.stat(self.full_filename).st_ctime)

    # Method to get TV channels
    def _update__tv_channels(self, country):
        if country != 'United States of America':
            country = 'UK'
        self.start_tv_channel = None
        self.stop_tv_channel = None
        for chan in data.tv_channels[country]:
            if self.start_tv_channel == None:
                if (self.start_frequency >= float(chan[1]) and
                    self.start_frequency < float(chan[2])):
                    self.start_tv_channel = chan[0]
            else:
                if (self.stop_frequency > float(chan[1]) and
                    self.stop_frequency <= float(chan[2])):
                    self.stop_tv_channel = chan[0]
                    break
        
    # Method to get new filename based on BestAudio naming structure
    def _get_new_filename(self):
        if 80 <= self.start_frequency <= 120:
            base_filename = 'FM'
        elif 54 <= self.start_frequency <= 88:
            base_filename = '{:02d}'.format(int(self.start_frequency - 42) // 6)
        elif 174 <= self.start_frequency <= 216:
            base_filename = '{:02d}'.format(int(self.start_frequency - 132) // 6)
        elif 470 <= self.start_frequency <= 890:
            base_filename = '{:02d}'.format(int(self.start_frequency - 386) // 6)
        elif 902 <= self.start_frequency <= 928:
            base_filename = '900'
        elif 944 <= self.start_frequency <= 952:
            base_filename = 'X1'
        elif 1920 <= self.start_frequency <= 1930:
            base_filename = 'DUSA'
        elif 1910 <= self.start_frequency <= 1930:
            base_filename = 'DSA'
        elif 1910 <= self.start_frequency <= 1920:
            base_filename = 'DBRA'
        elif 1893 <= self.start_frequency <= 1906:
            base_filename = 'DJAP'
        elif 1880 <= self.start_frequency <= 1900:
            base_filename = 'DEUR'
        else:
            base_filename = '{:.0f}MHz'.format(self.start_frequency)
        return '{}.csv'.format(base_filename)
    
    # Method to guess whether scan is inside or outside
    def _in_out_read(self):
        if 'in' in self.file.lower():
            return 1
        elif 'out' in self.file.lower():
            return -1
        else:
            return 0
