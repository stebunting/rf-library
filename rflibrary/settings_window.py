# Standard library imports
import os
import plistlib

# Tkinter GUI imports
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfiledialog

# Program data and module imports
import data
from tooltip import ToolTip
from output import date_formats
import log
from helpers import dir_format
import settings
from error import display_error

class SettingsWindow:
    def __init__(self):
        # Variables
        self._move_old_log = False
        self._log_folder = ''
        self._old_log_location = ''
        self._default_library_location = ''

        self._settings_window = tk.Toplevel(takefocus=True)

        self._settings_window.title('Settings')
        self._settings_window.resizable(width=False, height=False)

        self._create_settings_frames()
        self._init_tk_vars()
        self._create_settings_widgets()

    def start(self):
        self._settings_window.mainloop()

    # Method to bring settings window to front
    def bringtofront(self):
        self._settings_window.lift()

    # Create settings frames
    def _create_settings_frames(self):
        self._settings_master_frame = ttk.Frame(self._settings_window)
        self._settings_master_frame.grid(padx=0, pady=0, sticky='NWSE')

        self._output_preferences = ttk.LabelFrame(self._settings_master_frame, text='Output Preferences')
        self._output_preferences.grid(padx=16, pady=16, sticky='NWSE')

        self._logging_preferences = ttk.LabelFrame(self._settings_master_frame, text='Logging')
        self._logging_preferences.grid(padx=16, pady=16, sticky='NWSE')

        self._personal_data = ttk.LabelFrame(self._settings_master_frame, text='Personal Data')
        self._personal_data.grid(padx=16, pady=16, sticky='NWSE')

        self._app_data = ttk.LabelFrame(self._settings_master_frame, text='Application Data')
        self._app_data.grid(padx=16, pady=16, sticky='NWSE')

        self._settings_buttons_frame = ttk.Frame(self._settings_master_frame)
        self._settings_buttons_frame.grid(
            padx=16, pady=16, columnspan=2, sticky='NWSE')

    def _init_tk_vars(self):
        self._scans_folder_display = tk.StringVar(value=dir_format(settings.plist['default_library_location'], 50))
        self._dir_structure = tk.StringVar(value=settings.plist['dir_structure'])
        self._file_structure = tk.StringVar(value=settings.plist['file_structure'])
        self._low_freq_limit = tk.StringVar(value=settings.plist['low_freq_limit'])
        self._high_freq_limit = tk.StringVar(value=settings.plist['high_freq_limit'])
        self._default_date_format = tk.StringVar(value=settings.plist['default_date_format'])
        self._create_log = tk.BooleanVar(value=settings.plist['create_log'])
        self._log_folder_display = tk.StringVar(value=dir_format(settings.plist['logFolder'], 50))
        self._forename = tk.StringVar(value=settings.plist['forename'])
        self._surname = tk.StringVar(value=settings.plist['surname'])
        self._auto_update_check = tk.BooleanVar(value=settings.plist['auto_update_check'])

        # Set Variables
        self._default_library_location = settings.plist['default_library_location']
        self._log_folder = settings.plist['logFolder']

    # Create settings widgets
    def _create_settings_widgets(self):
        # Scans Folder
        ttk.Label(
            self._output_preferences,
            text='Scans Folder',
            width='16'
        ).grid(column=0, row=0, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        scans_folder_label = ttk.Label(self._output_preferences, textvariable=self._scans_folder_display, width='36')
        scans_folder_label.grid(column=1, row=0, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        ToolTip(scans_folder_label, 'Scan library base folder').bind()
        change_base_folder_button = ttk.Button(
            self._output_preferences,
            text='Change Folder',
            command=self._change_base_folder)
        change_base_folder_button.grid(column=1, row=1, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)

        # Directory Structure
        dir_structure = self._create_op_prefs_entry('Directory Structure', self._dir_structure, 2, '35')
        ToolTip(dir_structure, 'Default library directory structure (see docs for more details').bind()

        file_structure = self._create_op_prefs_entry('Filename Structure', self._file_structure, 3, '35')
        ToolTip(file_structure, 'Default library filename structure (see docs for more details').bind()

        # Date Format
        ttk.Label(
            self._output_preferences,
            text='Date Format',
            width='16'
        ).grid(column=0, row=4, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        date_format_box = ttk.Combobox(self._output_preferences, textvariable=self._default_date_format)
        date_format_box['values'] = list(date_formats)
        date_format_box.grid(column=1, row=4, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        ToolTip(date_format_box, 'Preferred date format').bind()

        # Frequency Limits
        low_freq_limit = self._create_op_prefs_entry('Low Frequency Limit', self._low_freq_limit, 5)
        ToolTip(low_freq_limit, 'Low frequency limit for the output file (set to 0 for no limit)').bind()

        high_freq_limit = self._create_op_prefs_entry('High Frequency Limit', self._high_freq_limit, 6)
        ToolTip(high_freq_limit, 'High frequency limit for the output file (set to 0 for no limit)').bind()

        # Create Log
        ttk.Label(
            self._logging_preferences,
            text='Write To Log File',
            width='16'
        ).grid(column=0, row=0, sticky='w', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        create_log_check = ttk.Checkbutton(self._logging_preferences, variable=self._create_log)
        create_log_check.grid(column=1, row=0, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        ToolTip(create_log_check, 'Turn log file writing on/off').bind()

        # Log Location
        ttk.Label(
            self._logging_preferences,
            text='Log Location',
            width='16'
        ).grid(column=0, row=1, sticky='w', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        log_location_entry = ttk.Label(self._logging_preferences, textvariable=self._log_folder_display, width='36')
        log_location_entry.grid(column=1, row=1, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        ToolTip(log_location_entry, 'Log file location').bind()
        change_log_location = ttk.Button(
            self._logging_preferences,
            text='Change Folder',
            command=self._change_log_folder)
        change_log_location.grid(column=1, row=2, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)

        # Forename Entry
        self._create_personal_entry('Forename', 'Your forename', self._forename, 0)
        self._create_personal_entry('Surname', 'Your surname', self._surname, 1)

        # Check for Updates
        ttk.Label(
            self._app_data,
            text='Auto Update Check',
            width='16'
        ).grid(column=0, row=0, sticky='w', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        check_for_updates_check = ttk.Checkbutton(self._app_data, variable=self._auto_update_check)
        check_for_updates_check.grid(column=1, row=0, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        ToolTip(check_for_updates_check, 'Automatically check for updates on startup').bind()

        # Buttons
        self._create_button('Save', 'Save changes', self._save_settings, 0)
        self._create_button('Cancel', 'Discard changes', self._close_settings, 1)

        # Bindings
        self._settings_window.bind_all('<Return>', self._save_settings)
        self._settings_window.bind_all('<Escape>', self._close_settings)

    def _create_op_prefs_entry(self, label, var, row, width='20'):
        ttk.Label(
            self._output_preferences,
            text=label,
            width='16'
        ).grid(column=0, row=row, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        box = ttk.Entry(self._output_preferences, textvariable=var, width=width)
        box.grid(column=1, row=row, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        return box

    def _create_personal_entry(self, label, description, var, row):
        ttk.Label(
            self._personal_data,
            text=label,
            width='16'
        ).grid(column=0, row=row, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        box = ttk.Entry(self._personal_data, textvariable=var, width='20')
        box.grid(column=1, row=row, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        ToolTip(box, description).bind()

    def _create_button(self, label, description, cmd, col):
        button = ttk.Button(
            self._settings_buttons_frame,
            text=label,
            command=cmd
        )
        button.grid(column=col, row=0, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        ToolTip(button, description).bind()

    # Method to select scans base folder
    def _change_base_folder(self):
        directory = tkfiledialog.askdirectory(
            parent=self._settings_master_frame,
            title='Select Scan Folder',
            initialdir=settings.plist['default_library_location'])
        if directory != '':
            self._default_library_location = directory
            self._scans_folder_display.set(dir_format(self._default_library_location, 50))

    # Method to select default log folder
    def _change_log_folder(self):
        if os.path.exists(os.path.join(settings.plist['logFolder'], log.FILENAME)):
            self._move_old_log = True
            self._old_log_location = settings.plist['logFolder']

        directory = tkfiledialog.askdirectory(
            parent=self._settings_master_frame,
            title='Select Source Folder',
            initialdir=settings.plist['logFolder'])
        if directory != '':
            self._log_folder = directory
            self._log_folder_display.set(dir_format(self._log_folder, 50))

    # Method to save settings and close window
    def _save_settings(self):
        # Ensure limits are good ints else revert to default
        defaults = [settings.plist['low_freq_limit'], settings.plist['high_freq_limit']]
        for var, default in zip([self._low_freq_limit, self._high_freq_limit], defaults):
            if var.get() == '':
                var.set(0)
            else:
                try:
                    int(var.get())
                except ValueError:
                    var.set(default)
            if int(var.get()) < 0:
                var.set(0)
        if int(self._low_freq_limit.get()) > int(self._high_freq_limit.get()):
            self._low_freq_limit.set(self._high_freq_limit.get())
        elif int(self._high_freq_limit.get()) < int(self._low_freq_limit.get()):
            self._high_freq_limit.set(self._low_freq_limit.get())

        settings.plist['default_library_location'] = self._default_library_location
        settings.plist['forename'] = self._forename.get()
        settings.plist['surname'] = self._surname.get()
        settings.plist['dir_structure'] = self._dir_structure.get().strip('/')
        settings.plist['file_structure'] = self._file_structure.get()
        settings.plist['default_date_format'] = self._default_date_format.get()
        settings.plist['low_freq_limit'] = int(self._low_freq_limit.get())
        settings.plist['high_freq_limit'] = int(self._high_freq_limit.get())
        settings.plist['create_log'] = self._create_log.get()
        settings.plist['logFolder'] = self._log_folder
        settings.plist['auto_update_check'] = self._auto_update_check.get()

        try:
            with open(data.PLIST_NAME, 'wb') as file:
                plistlib.dump(settings.plist, file)
        except PermissionError:
            display_error('READ_PREF_FILE')

        # Move old log to new log location
        if self._move_old_log:
            os.rename(os.path.join(self._old_log_location, log.FILENAME),
                      os.path.join(settings.plist['logFolder'], log.FILENAME))

        self._close_settings()

    # Method to close settings window
    def _close_settings(self):
        self._settings_window.quit()
        self._settings_window.destroy()
