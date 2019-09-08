#!/usr/bin/env python3

################################################################################
##########                       OUTPUT OBJECT                        ##########
################################################################################

import os
import scanfile

# Define Output class
class Output:

	# Initialise class
	def __init__(self):

		# List to store files
		self.files = list()

		# Variable to guess whether scans are inside or outside
		# Postive is inside, negative is outside
		self.in_out_guess = 0

	# Method to add file
	# Returns false if file is invalid and not added, otherwise true
	def add_file(self, name, country):
		newFile = scanfile.ScanFile(name, country)
		self.files.append(newFile)
		self.in_out_guess += newFile.io

	# Method that takes a list/tuple and adds all files
	def add_files(self, files, country):
		errors = list()
		for file in files:
			try:
				self.add_file(file, country)
			except scanfile.InvalidFile as err:
				errors.append((file, err))
		return errors

	# Method to add whole directory
	def add_directory(self, dir, country):
		with os.scandir(dir) as directory:
			for file in directory:
				if not file.name.startswith('.') and not file.is_dir():
					try:
						self.add_file(file.path, country)
					except scanfile.InvalidFile:
						pass

    # Method to remove file
	def remove_file(self, i):
		self.in_out_guess -= self.files[i].io
		self.files.pop(i)

	# Method to clear all files
	def clear_all_files(self):
		self.files = list()
		self.in_out_guess = 0
					

output = Output()
files = ('/Users/stebunting/Dropbox/RF/Test/OUT_001.CSV',
		'/Users/stebunting/Dropbox/RF/Test/OUT_002.CSV',
		'/Users/stebunting/Dropbox/RF/Test/Invalid.csv',
		'/Users/stebunting/Dropbox/RF/Test/Notcsv.xls')
errors = output.add_files(files, 'United Kingdom')
for err in errors:
	print(err[1])
#try:
#	output.add_file(filename, 'United Kingdom')
#except InvalidFile as err:
#	print('{} could not be added: {}'.format(filename, err))
output.add_directory('/Users/stebunting/Dropbox/RF/Test', 'United Kingdom')
output.remove_file(1)
output.clear_all_files()
print(len(output.files))
print(output.in_out_guess)