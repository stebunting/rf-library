#!/usr/bin/env python3

################################################################################
##########                       OUTPUT OBJECT                        ##########
################################################################################

from file import File

# Define Output class
class Output:

	# Initialise class
	def __init__(self):
		self.files = []

	# Method to add file
	def add(self, File):
		self.files.append(File)

output = Output()
output.add(File('/Users/stebunting/Dropbox/RF/Test/OUT_001.CSV', 'United Kingdom'))