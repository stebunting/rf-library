import unittest
import os
import pathlib

from file import File

data_directory = os.path.join(pathlib.Path(__file__).parent.resolve(), 'data')

class TestFileParse(unittest.TestCase):
    def test(self):
        tests = [{
            'filename': 'IN_001.csv',
            'country': 'United States of America',
            'expected_validity': True,
            'expected_filename': 'IN_001.csv',
            'expected_model': "TTi PSA2702",
            'expected_start_frequency': '54.000MHz',
            'expected_stop_frequency': '88.000MHz',
            'expected_data_points': 271,
            'expected_resolution': 0.126,
            'expected_start_tv_channel': 2,
            'expected_stop_tv_channel': 6,
            'expected_new_filename': '02.csv',
            'expected_in_out': 1
        }, {
            'filename': 'RFExplorer_SingleSweepData_2016_05_28_16_57_56.csv',
            'country': 'United States of America',
            'expected_validity': True,
            'expected_filename': 'RFExplorer_SingleSweepData_2016_05_28_16_57_56.csv',
            'expected_model': 'Generic',
            'expected_start_frequency': '600.000MHz',
            'expected_stop_frequency': '659.464MHz',
            'expected_data_points': 112,
            'expected_resolution': 0.536,
            'expected_start_tv_channel': 35,
            'expected_stop_tv_channel': 45,
            'expected_new_filename': '35.csv',
            'expected_in_out': 1
        }, {
            'filename': 'Shure ULXD.sdb2',
            'country': 'United Kingdom',
            'expected_validity': True,
            'expected_filename': 'Shure ULXD.sdb2',
            'expected_model': 'Shure ULXD4Q (L51)',
            'expected_start_frequency': '632.125MHz',
            'expected_stop_frequency': '695.875MHz',
            'expected_data_points': 1276,
            'expected_resolution': 0.05,
            'expected_start_tv_channel': 41,
            'expected_stop_tv_channel': 49,
            'expected_new_filename': '41.csv',
            'expected_in_out': 0
        }, {
            'filename': 'Notcsv.xls',
            'country': 'United Kingdom',
            'expected_validity': False,
            'expected_filename': 'Notcsv.xls',
            'expected_model': '',
            'expected_start_frequency': None,
            'expected_stop_frequency': None,
            'expected_data_points': 0,
            'expected_resolution': 0,
            'expected_start_tv_channel': None,
            'expected_stop_tv_channel': None,
            'expected_new_filename': '',
            'expected_in_out': 0
        }]

        for test in tests:
            fut = File(
                os.path.join(data_directory, test['filename']),
                test['country'])

            self.assertEqual(
                fut.valid,
                test['expected_validity'],
                f'Expected {test["filename"]} valid to equal {test["expected_validity"]}, got {fut.valid}')
            self.assertEqual(
                fut.filename,
                test['expected_filename'],
                f'Expected {test["filename"]} filename to equal {test["expected_filename"]}, got {fut.filename}')
            self.assertEqual(
                fut.model,
                test['expected_model'],
                f'Expected {test["filename"]} model to equal {test["expected_model"]}, got {fut.model}')
            self.assertEqual(
                fut.start_frequency_format(),
                test['expected_start_frequency'],
                f'Expected {test["filename"]} start_frequency to equal {test["expected_start_frequency"]}, got {fut.start_frequency_format()}')
            self.assertEqual(
                fut.stop_frequency_format(),
                test['expected_stop_frequency'],
                f'Expected {test["filename"]} stop_frequency to equal {test["expected_stop_frequency"]}, got {fut.stop_frequency_format()}')
            self.assertEqual(
                fut.data_points,
                test['expected_data_points'],
                f'Expected {test["filename"]} data_points to equal {test["expected_data_points"]}, got {fut.data_points}')
            self.assertAlmostEqual(
                fut.resolution,
                test['expected_resolution'],
                3,
                f'Expected {test["filename"]} resolution to equal {test["expected_resolution"]}, got {fut.resolution}')
            self.assertEqual(
                fut.start_tv_channel,
                test['expected_start_tv_channel'],
                f'Expected {test["filename"]} start_tv_channel to equal {test["expected_start_tv_channel"]}, got {fut.start_tv_channel}')
            self.assertEqual(
                fut.stop_tv_channel,
                test['expected_stop_tv_channel'],
                f'Expected {test["filename"]} stop_tv_channel to equal {test["expected_stop_tv_channel"]}, got {fut.stop_tv_channel}')
            self.assertEqual(
                fut.new_filename,
                test['expected_new_filename'],
                f'Expected {test["filename"]} new_filename to equal {test["expected_new_filename"]}, got {fut.new_filename}')
            self.assertEqual(
                fut.in_out,
                test['expected_in_out'],
                f'Expected {test["filename"]} in_out to equal {test["expected_in_out"]}, got {fut.in_out}')
