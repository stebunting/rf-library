import os
import data

class Writer:
    def get_filename(self, directory, filename):
        target = os.path.join(directory, filename)
        file, ext = os.path.splitext(filename)
        duplicate_counter = 0
        while os.path.isfile(target):
            duplicate_counter += 1
            filename = f'{file}-{duplicate_counter}{ext}'
            target = os.path.join(directory, filename)
        return os.path.join(directory, filename)

    def get_wsm_filename(self, directory, filename):
        file, ext = os.path.splitext(filename)
        return self.get_filename(directory, f'{file}-WSM.{ext}')

    # Method to create directory structure
    def create_directory(self, location):
        os.makedirs(location)

    # Method to write file to disk
    def write_file(self, filename, string):
        try:
            with open(filename, 'w', encoding='UTF-8') as file:
                file.write(string)
            return True
        except IOError:
            return False

    # Method to write file to disk
    def write_file_from_list(self, filename, array):
        with open(filename, 'w', encoding='UTF-8') as file:
            for freq, value in array:
                file.write(f'{freq:09.4f},{value:09.4f}\n')

    # Method to write WSM file to disk
    def write_wsm_file(self, filename, array, wsm_date, limits):
        with open(filename, 'w', encoding='UTF-8') as file:
            wsm_date = wsm_date.strftime('%Y-%m-%d 00:00:00')
            file.write(f'Receiver;{data.TITLE}\n'
                       f'Date/Time;{wsm_date}\n'
                       'RFUnit;dBm\n\n\nFrequency Range [kHz];'
                       f'{(limits[0] * 1000):06d};'
                       f'{limits[1] * 1000:06d};\n')
            file.write('Frequency;RF level (%);RF level\n')
            for freq, value in reversed(array):
                file.write(f'{int(freq * 1000):06d};;{value:04.1f}\n')
