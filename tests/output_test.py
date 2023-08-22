import unittest
import os
import pathlib

import settings
import data
from output import Output

data_directory = os.path.join(pathlib.Path(__file__).parent.resolve(), 'data')

class TestOutput(unittest.TestCase):
    def test(self):
        tests = [{
            'venue': 'Hammersmith Apollo',
            'town': 'London',
            'country': 'United States of America',
            'file_structure': settings.DEFAULT_FILENAME_STRUCTURE,
            'default_library_location': data.default_library_location,
            'dir_structure': settings.DEFAULT_DIRECTORY_STRUCTURE,
            'date_format': settings.DEFAULT_DATE_FORMAT,
            'forename': 'John',
            'surname': 'Smith',
            'copy_source_files': True,
            'delete_source_files': True,
            'low_freq_limit': 470,
            'high_freq_limit': 900,
            'files': ['IN_001.csv', 'IN_002.csv', 'IN_003.csv', 'IN_004.csv', 'IN_005.csv'],
            'expected_num_files': 5,
            # 'expected_filename': "London United States of America-Hammersmith Apollo-20230806-Inside John Smith.csv",
            'expected_output_lines': 542
        }]

        for test in tests:
            output = Output(
                venue=test['venue'],
                town=test['town'],
                country=test['country'],
                file_structure=test['file_structure'],
                default_library_location=test['default_library_location'],
                dir_structure=test['dir_structure'],
                date_format=test['date_format'],
                forename=test['forename'],
                surname=test['surname'],
                copy_source_files=test['copy_source_files'],
                delete_source_files=test['delete_source_files'],
                low_freq_limit=test['low_freq_limit'],
                high_freq_limit=test['high_freq_limit'])
            for file in test['files']:
                output.add_file(os.path.join(data_directory, file), test['country'])

            self.assertEqual(
                output.num_files(),
                test['expected_num_files'],
                (f'Expected num_files to equal {test["expected_num_files"]}, '
                 f'got {output.num_files()}'))
            # self.assertEqual(
            #     output.scan_master_filename,
            #     test['expected_filename'],
            #     (f'Expected default_filename to equal {test["expected_filename"]}, '
            #      f'got {output.scan_master_filename}'))

            output_file = output.write_output_file()
            num_lines = len(output_file.split("\n"))
            self.assertEqual(
                num_lines,
                test['expected_output_lines'],
                (f'Expected number of lines in output to equal {test["expected_output_lines"]}, '
                 f'got {num_lines}'))
