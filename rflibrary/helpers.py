import os

# Helper function to format directory nicely
def dir_format(display_location, max_length):
    display_location = display_location.replace(os.path.expanduser('~'), '~', 1)
    while len(display_location) > max_length:
        display_location = os.path.join(
            '...',
            os.path.normpath(display_location.split(os.sep, 2)[2]))
    return display_location
