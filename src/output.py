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

        self.custom_filename = False
        self.custom_subdirectory = False
        self.custom_destination = False
        self.copy_source_files = settings.plist['defaultCopy']
        self.del_source_files = settings.plist['defaultDelete']

        # Output Variables
        self.venue = settings.plist['defaultVenue']
        self.town = settings.plist['defaultTown']
        self.country = settings.plist['defaultCountry']
        self.date = datetime.date.today()
        self.io = 'Inside'
        self.subdirectory = self.io
        self.copy_source_files = settings.plist['defaultCopy']
        self.delete_source_files = settings.plist['defaultDelete']
        self.include_ofcom_data = settings.plist['defaultOfcomInclude']

        if self.country != 'United States of America':
            self.tv_country = 'UK'
        else:
            self.tv_country = 'United States of America'

        self.get_master_filename()

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
        if newFile.creation_date < self.date:
            self.set_date(newFile.creation_date)

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
        self.date = datetime.date.today()

    # Method to use date from a particular file
    def use_date(self, i):
        if i < 0 or i >= self.num_files():
            return

        self.date = self.files[i].creation_date

    # Method to get earliest date from all files or todays date (default)
    def _get_scan_date(self):
        if self.num_files() == 0:
            self.date = datetime.date.today()
        else:
            self.date = min([file.creation_date for file in self.files])

    # Method to return formatted date
    def get_formatted_date(self):
        return self.date.strftime(settings.date_format)

    # Method to convert user input directory structure into path
    def _parse_structure(self, s):
        for old, new in (('%c', self.country),
                         ('%t', self.town),
                         ('%v', self.venue),
                         ('%y', str(self.date.year)),
                         ('%i', self.io),
                         ('%s', self.subdirectory),
                         ('%f', settings.plist['forename']),
                         ('%n', settings.plist['surname']),
                         ('%m', '{:02d}'.format(self.date.month)),
                         ('%M', self.date.strftime('%B')),
                         ('%d', '{:02d}'.format(self.date.day))):
            s = s.replace(old, new)
        return s

    # Method to create master filename
    def get_master_filename(self):
        if not self.custom_filename:
            self.filename = self._parse_structure(settings.plist['fileStructure'] + '.csv')

    # Method to create destination path
    def get_destination(self):
        if not self.custom_destination:
            base_location = settings.plist['defaultLibraryLocation']
            path = self._parse_structure(os.path.join(settings.plist['dirStructure'], '%s'))
            self.destination = os.path.join(base_location, path)

    def set_date(self, d):
        if type(d) == datetime.date:
            self.date = d
        else:
            print("TRYING TO SET DATE WITH NO DATETIME CLASS")

    # Method to set destination
    def set_destination(self, destination, **kwargs):
        if kwargs.get('custom'):
            self.custom_destination = kwargs.get('custom')

        self.destination = destination
