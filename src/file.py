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
    def __init__(self, name, tvCountry):
        self.fullfilename = name
        self.filename = os.path.basename(self.fullfilename)
        self.file, self.ext = os.path.splitext(self.filename)
        self.path = os.path.dirname(self.fullfilename)
        self.valid = True
        self.readFile()
        if self.valid:
            self.updateTVChannels(tvCountry)
            self.getNewFilename()
            self.ioRead()
        
    # Method to check validity and get file destails
    def readFile(self):
        # Ensure file has valid extension
        if self.ext.lower() != '.csv' and self.ext.lower() != '.sdb2':
            self.valid = False
            return
        
        # Read first line of file
        self.frequencies = []
        self.fp = open(self.fullfilename, 'r', encoding='utf-8')
        firstLine = self.fp.readline().rstrip()
        self.fp.seek(0)
        
        # Identify type of scan file from first line and parse
        if firstLine[0:11] == 'Model Type:':
            self.parseCSVScan('TTi {}'.format(firstLine[12:-1]))
        elif firstLine[0:9] == 'Receiver;':
            self.parseWSMScan()
        elif firstLine[0:38] == '<?xml version="1.0" encoding="UTF-8"?>':
            self.parseShureScan()
        else:
            self.parseCSVScan('Generic')
        self.fp.close()
        if len(self.frequencies) == 0:
            self.valid = False
            return
        
        # Get file details
        self.startFrequency = min(freq[0] for freq in self.frequencies)
        self.stopFrequency = max(freq[0] for freq in self.frequencies)
        self.dataPoints = len(self.frequencies)
        self.resolution = ((self.stopFrequency - self.startFrequency)
                          / (self.dataPoints - 1))
    
    # Parse an XML scan created by Shure WWB6 and hardware
    def parseShureScan(self):
        tree = xml.etree.ElementTree.parse(self.fp)
        xmldoc = tree.getroot()
        model = xmldoc.attrib['model']
        if model == 'TODO' or model == '':
            self.model = 'Shure AXT600'
        else:
            self.model = 'Shure {} ({})'.format(model, xmldoc.attrib['band'])
        self.frequencies = []
        for freq, level in zip(xmldoc[0][0], xmldoc[0][1]):
            self.frequencies.append([float(freq.text) / 1000, float(level.text)])
        self.creationDate = datetime.datetime.fromtimestamp(
                            float(xmldoc[0][1].attrib['date_time']) / 1000)
            
    # Parse a CSV file
    def parseCSVScan(self, model):
        self.model = model
        for line in self.fp:
            splitLine = re.split('[\t,;]', line)
            try:
                freq = float(splitLine[0].strip())
                value = float(splitLine[1].strip())
                self.frequencies.append([freq, value])
            except ValueError:
                pass
        self.getCreationDate()
            
    # Parse a WSM file
    def parseWSMScan(self):
        self.model = 'Sennheiser WSM'
        wsmLowLimit = -99
        wsmHighLimit = -30
        wsmMultiplier = wsmLowLimit - wsmHighLimit # -69
        for line in self.fp:
            splitLine = re.split('[    ,; ]', line)
            try:
                freq = float(splitLine[0]) / 1000
                value = wsmLowLimit - (float(splitLine[2]) * 0.0065 * wsmMultiplier)
                # -34.2 = -99 - (9988 * ? * -69)
                # -64.8 / (9988 * -69) = 0,0065

                if freq > 1:
                    self.frequencies.append([freq, value])
            except (ValueError, IndexError):
                pass
        self.getCreationDate()
    
    # Method to return creation date from file
    def getCreationDate(self):
        if data.system == 'Mac':
            self.creationDate = datetime.datetime.fromtimestamp(os.stat(self.fullfilename).st_birthtime)
        elif data.system == 'Windows':
            self.creationDate = datetime.datetime.fromtimestamp(os.stat(self.fullfilename).st_ctime)

    # Method to get TV channels
    def updateTVChannels(self, tvCountry):
        if tvCountry == 'United States of America':
            tvCountry = tvCountry
        else:
            tvCountry = 'UK'
        self.startTVChannel = None
        self.stopTVChannel = None
        for chan in data.TVChannels[tvCountry]:
            if self.startTVChannel == None:
                if (self.startFrequency >= float(chan[1]) and
                    self.startFrequency < float(chan[2])):
                    self.startTVChannel = chan[0]
            else:
                if (self.stopFrequency > float(chan[1]) and
                    self.stopFrequency <= float(chan[2])):
                    self.stopTVChannel = chan[0]
                    break
        
    # Method to get new filename based on BestAudio naming structure
    def getNewFilename(self):
        if 80 <= self.startFrequency <= 120:
            self.newFilename = 'FM'
        elif 54 <= self.startFrequency <= 88:
            self.newFilename = '{:02d}'.format(int(self.startFrequency - 42) // 6)
        elif 174 <= self.startFrequency <= 216:
            self.newFilename = '{:02d}'.format(int(self.startFrequency - 132) // 6)
        elif 470 <= self.startFrequency <= 890:
            self.newFilename = '{:02d}'.format(int(self.startFrequency - 386) // 6)
        elif 902 <= self.startFrequency <= 928:
            self.newFilename = '900'
        elif 944 <= self.startFrequency <= 952:
            self.newFilename = 'X1'
        elif 1920 <= self.startFrequency <= 1930:
            self.newFilename = 'DUSA'
        elif 1910 <= self.startFrequency <= 1930:
            self.newFilename = 'DSA'
        elif 1910 <= self.startFrequency <= 1920:
            self.newFilename = 'DBRA'
        elif 1893 <= self.startFrequency <= 1906:
            self.newFilename = 'DJAP'
        elif 1880 <= self.startFrequency <= 1900:
            self.newFilename = 'DEUR'
        else:
            self.newFilename = '{:.0f}MHz'.format(self.startFrequency)
        self.newFilename = '{}.csv'.format(self.newFilename)
    
    # Method to guess whether scan is inside or outside
    def ioRead(self):
        self.io = 0
        lowercaseFilename = self.file.lower()
        if 'in' in lowercaseFilename:
            self.io = 1
        elif 'out' in lowercaseFilename:
            self.io = -1
