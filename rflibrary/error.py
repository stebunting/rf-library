import tkinter.messagebox as tkmessagebox
import data

errors = {
    'READ_PREF_FILE': f'Could not read from preferences file {data.PLIST_NAME}',
    'CREATE_PREF_PATH': f'Could not create preferences path {data.PLIST_PATH}',
    'WRITE_PREF_FILE': f'Could not write preferences file {data.PLIST_NAME}',
    'CONN_UPDATE_SERVER': 'Could not connect to update server.',
    'UNDEFINED': 'Undefined error'
}

def display_error(code):
    try:
        message = errors[code]
    except KeyError:
        message = errors['UNDEFINED']
    tkmessagebox.showerror("RF Library Error", message)
