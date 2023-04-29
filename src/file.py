#!/usr/bin/env python3

################################################################################
##########                        FILE OBJECT                         ##########
################################################################################

import os
import re
import datetime
import xml.etree.ElementTree
import data

# Define Data class
class File():

    # Initialise class
    def __init__(self, name, tv_country):
        self.full_filename = name
        self.filename = os.path.basename(self.full_filename)
        self.file, self.ext = os.path.splitext(self.filename)
        self.path = os.path.dirname(self.full_filename)
        self.valid = True
        self.read_file()
        if self.valid:
            self.update_tv_channels(tv_country)
            self.get_new_filename()
            self.in_out_read()
        
    # Method to check validity and get file destails
    def read_file(self):
        # Ensure file has valid extension
        if self.ext.lower() != '.csv' and self.ext.lower() != '.sdb2':
            self.valid = False
            return
        
        # Read first line of file
        self.frequencies = []
        self.file = open(self.full_filename, 'r', encoding='utf-8')
        first_line = self.file.readline().rstrip()
        self.file.seek(0)
        
        # Identify type of scan file from first line and parse
        if first_line[0:11] == 'Model Type:':
            self.parse_csv_scan('TTi {}'.format(first_line[12:-1]))
        elif first_line[0:9] == 'Receiver;':
            self.parse_wsm_scan()
        elif first_line[0:38] == '<?xml version="1.0" encoding="UTF-8"?>':
            self.parse_shure_scan()
        else:
            self.parse_csv_scan('Generic')
        self.file.close()
        if len(self.frequencies) == 0:
            self.valid = False
            return
        
        # Get file details
        self.start_frequency = min(freq[0] for freq in self.frequencies)
        self.stop_frequency = max(freq[0] for freq in self.frequencies)
        self.data_points = len(self.frequencies)
        self.resolution = ((self.stop_frequency - self.start_frequency)
                          / (self.data_points - 1))
    
    # Parse an XML scan created by Shure WWB6 and hardware
    def parse_shure_scan(self):
        tree = xml.etree.ElementTree.parse(self.file)
        xmldoc = tree.getroot()
        model = xmldoc.attrib['model']
        if model == 'TODO' or model == '':
            self.model = 'Shure AXT600'
        else:
            self.model = 'Shure {} ({})'.format(model, xmldoc.attrib['band'])
        self.frequencies = []
        for freq, level in zip(xmldoc[0][0], xmldoc[0][1]):
            self.frequencies.append([float(freq.text) / 1000, float(level.text)])
        self.creation_date = datetime.datetime.fromtimestamp(
                            float(xmldoc[0][1].attrib['date_time']) / 1000)
            
    # Parse a CSV file
    def parse_csv_scan(self, model):
        self.model = model
        for line in self.file:
            split_line = re.split('[\t,;]', line)
            try:
                freq = float(split_line[0].strip())
                value = float(split_line[1].strip())
                self.frequencies.append([freq, value])
            except ValueError:
                pass
        self.get_creation_date()
            
    # Parse a WSM file
    def parse_wsm_scan(self):
        self.model = 'Sennheiser WSM'
        wsm_low_limit = -99
        wsm_high_limit = -30
        wsm_multiplier = wsm_low_limit - wsm_high_limit # -69
        for line in self.file:
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
        if data.system == 'Mac':
            self.creation_date = datetime.datetime.fromtimestamp(os.stat(self.full_filename).st_birthtime)
        elif data.system == 'Windows':
            self.creation_date = datetime.datetime.fromtimestamp(os.stat(self.full_filename).st_ctime)

    # Method to get TV channels
    def update_tv_channels(self, tv_country):
        if tv_country == 'United States of America':
            tv_country = tv_country
        else:
            tv_country = 'UK'
        self.start_tv_channel = None
        self.stop_tv_channel = None
        for chan in data.TVChannels[tv_country]:
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
    def get_new_filename(self):
        if 80 <= self.start_frequency <= 120:
            self.new_filename = 'FM'
        elif 54 <= self.start_frequency <= 88:
            self.new_filename = '{:02d}'.format(int(self.start_frequency - 42) // 6)
        elif 174 <= self.start_frequency <= 216:
            self.new_filename = '{:02d}'.format(int(self.start_frequency - 132) // 6)
        elif 470 <= self.start_frequency <= 890:
            self.new_filename = '{:02d}'.format(int(self.start_frequency - 386) // 6)
        elif 902 <= self.start_frequency <= 928:
            self.new_filename = '900'
        elif 944 <= self.start_frequency <= 952:
            self.new_filename = 'X1'
        elif 1920 <= self.start_frequency <= 1930:
            self.new_filename = 'DUSA'
        elif 1910 <= self.start_frequency <= 1930:
            self.new_filename = 'DSA'
        elif 1910 <= self.start_frequency <= 1920:
            self.new_filename = 'DBRA'
        elif 1893 <= self.start_frequency <= 1906:
            self.new_filename = 'DJAP'
        elif 1880 <= self.start_frequency <= 1900:
            self.new_filename = 'DEUR'
        else:
            self.new_filename = '{:.0f}MHz'.format(self.start_frequency)
        self.new_filename = '{}.csv'.format(self.new_filename)
    
    # Method to guess whether scan is inside or outside
    def io_read(self):
        self.in_out = 0
        lowercase_filename = self.file.lower()
        if 'in' in lowercase_filename:
            self.in_out = 1
        elif 'out' in lowercase_filename:
            self.in_out = -1
