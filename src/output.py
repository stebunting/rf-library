#!/usr/bin/env python3

################################################################################
##########                       OUTPUT CLASS                         ##########
################################################################################

import os
import datetime
import config
import scanfile

# Load Settings
settings = config.Settings()

# Define Output class
class Output:

    # Initialise class
    def __init__(self):

        # List to store files
        self.files = list()

        # Variable to guess whether scans are inside or outside
        # Postive is inside, negative is outside
        self.in_out_guess = 0

        # Scan Date
        self.scan_date_timestamp = datetime.date.today()

        self.venue = settings.plist['defaultVenue']
        self.town = settings.plist['defaultTown']
        self.country = settings.plist['defaultCountry']
        self.copy_source_files = settings.plist['defaultCopy']
        self.delete_source_files = settings.plist['defaultDelete']
        self.include_ofcom_data = settings.plist['defaultOfcomInclude']

        if self.country != 'United States of America':
            self.tv_country = 'UK'
        else:
            self.tv_country = 'United States of America'

    # Return number of scan files in list
    def num_files(self):
        assert len(self.files) >= 0
        return len(self.files)

    # Method to add file
    # Returns false if file is invalid and not added, otherwise true
    def add_file(self, name):
        newFile = scanfile.ScanFile(name, self.tv_country)
        self.files.append(newFile)
        self.in_out_guess += newFile.io
        if newFile.creation_date < self.scan_date_timestamp:
            self.scan_date_timestamp = newFile.creation_date

    # Method that takes a list/tuple and adds all files
    def add_files(self, files):
        errors = list()
        for file in files:
            try:
                self.add_file(file, self.tv_country)
            except scanfile.InvalidFile as err:
                errors.append((file, err))
        return errors

    # Method to add whole directory
    def add_directory(self, dir):
        if dir == '':
            return
        with os.scandir(dir) as directory:
            for file in directory:
                if not file.name.startswith('.') and not file.is_dir():
                    try:
                        self.add_file(file.path)
                    except scanfile.InvalidFile:
                        pass

    # Method to remove file
    def remove_file(self, i):
        self.in_out_guess -= self.files[i].io
        self.files.pop(i)
        self._get_scan_date()

    # Method to clear all files
    def clear_all_files(self):
        self.files = list()
        self.in_out_guess = 0
        self.scan_date_timestamp = datetime.date.today()

    # Method to get earliest date from all files or todays date (default)
    def _get_scan_date(self):
        if self.num_files() == 0:
            self.scan_date_timestamp = datetime.date.today()
        else:
            self.scan_date_timestamp = min([file.creation_date for file in self.files])
