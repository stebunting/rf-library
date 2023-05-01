import os
import csv

FILENAME = 'rflibrary-log.csv'

class Log:
    def __init__(self, folder):
        self.folder = folder

    # Method to write to log file
    def write(self, output):
        log_file = os.path.join(self.folder, FILENAME)

        new_file = bool(not os.path.exists(log_file))

        with open(log_file, 'a', newline='', encoding='UTF-8') as csvfile:
            log_writer = csv.writer(
                csvfile,
                delimiter=',',
                quotechar="\"",
                quoting=csv.QUOTE_MINIMAL)
            if new_file:
                log_writer.writerow(['Date', 'Country', 'City', 'Venue', 'Inside/Outside'])
            log_writer.writerow([
                output.formatted_date(),
                output.country,
                output.town,
                output.venue,
                output.in_out])

        return True
