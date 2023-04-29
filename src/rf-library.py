#!/usr/bin/env python3

# Import Python Modules
import platform
import os
import sys
import datetime
import xml.etree.ElementTree
import plistlib
import webbrowser

# Import Tkinter GUI functions
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkfiledialog
import tkinter.font as tkfont
import tkinter.messagebox as tkmessagebox

import csv
from PIL import Image, ImageTk
import requests
import keyring

# Import Matplotlib graph plotting functions
import matplotlib
import matplotlib.figure
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import program data and modules
import data
from file import File
from tooltip import CreateToolTip

# Helper function to set dateFormat
def set_date_format():
    if data.dateFormats.get(plist['default_date_format']):
        return data.dateFormats.get(plist['default_date_format'])
    return data.dateFormats.get(default_date_format)

# Helper function to format directory nicely
def dir_format(display_location, max_length):
    display_location = display_location.replace(os.path.expanduser('~'), '~', 1)
    while len(display_location) > max_length:
        display_location = os.path.join(
            '...',
            os.path.normpath(display_location.split(os.sep, 2)[2]))
    return display_location

# Load settings plist if it exists yet
errors = []
SETTINGS_EXISTS = True
NEW_SETTINGS_FILE = False
if not os.path.isfile(data.plist_name):
    SETTINGS_EXISTS = False
    try:
        os.makedirs(data.plistPath, exist_ok=True)
    except PermissionError:
        errors.append(2)
    try:
        file = open(data.plist_name, 'wb')
        file.close()
        os.chmod(data.plist_name, 0o600)
        NEW_SETTINGS_FILE = True
    except (PermissionError, FileNotFoundError):
        errors.append(3)
    plist = dict()
else:
    try:
        with open(data.plist_name, 'rb') as file:
            plist = plistlib.load(file)
    except PermissionError:
        errors.append(1)
        plist = dict()

# Check for preferences and add default if not there
vars = [
    'create_log',
    'logFolder',
    'forename',
    'surname',
    'dir_structure',
    'file_structure',
    'defaultOfcomInclude',
    'default_date_format',
    'low_freq_limit',
    'high_freq_limit',
    'defaultVenue',
    'defaultTown',
    'defaultCountry',
    'defaultCopy',
    'defaultDelete',
    'defaultSourceLocation',
    'default_library_location',
    'auto_update_check']
defaults = [
    True,
    data.default_log_folder,
    '',
    '',
    data.default_directory_structure,
    data.default_filename_structure,
    False,
    data.default_date_format,
    0,
    0,
    'Venue',
    'Town',
    'United Kingdom',
    True,
    False,
    os.path.expanduser('~'),
    data.default_library_location,
    True]
for var, default in zip(vars, defaults):
    if var not in plist:
        plist[var] = default

if NEW_SETTINGS_FILE:
    with open(data.plist_name, 'wb') as file:
        plistlib.dump(plist, file)

dateFormat = set_date_format()

################################################################################
##########                  SETTINGS WINDOW OBJECT                    ##########
################################################################################

class SettingsWindow():

    # Initialise class
    def __init__(self):

        # Variables
        self.move_old_log = False

        self.settings_window = tk.Toplevel(takefocus=True)

        self.settings_window.title('Settings')
        self.settings_window.resizable(width=False, height=False)

        self._create_settings_frames()
        self._create_settings_widgets()

    # Create settings frames
    def _create_settings_frames(self):
        self.settings_master_frame = ttk.Frame(self.settings_window)
        self.settings_master_frame.grid(padx=0, pady=0, sticky='NWSE')

        self.output_preferences = ttk.LabelFrame(
            self.settings_master_frame, text='Output Preferences')
        self.output_preferences.grid(padx=16, pady=16, sticky='NWSE')

        self.logging_preferences = ttk.LabelFrame(
            self.settings_master_frame, text='Logging')
        self.logging_preferences.grid(padx=16, pady=16, sticky='NWSE')

        self.personal_data = ttk.LabelFrame(
            self.settings_master_frame, text='Personal Data')
        self.personal_data.grid(padx=16, pady=16, sticky='NWSE')

        self.app_data = ttk.LabelFrame(
            self.settings_master_frame, text='Application Data')
        self.app_data.grid(padx=16, pady=16, sticky='NWSE')

        self.settings_buttons_frame = ttk.Frame(self.settings_master_frame)
        self.settings_buttons_frame.grid(
            padx=16, pady=16, columnspan=2, sticky='NWSE')

    # Create settings widgets
    def _create_settings_widgets(self):

        # Initialise Tk variables
        self.scans_folder_display = tk.StringVar()
        self.dir_structure = tk.StringVar()
        self.file_structure = tk.StringVar()
        self.low_freq_limit = tk.StringVar()
        self.high_freq_limit = tk.StringVar()
        self.default_date_format = tk.StringVar()
        self.create_log = tk.BooleanVar()
        self.log_folder_display = tk.StringVar()
        self.forename = tk.StringVar()
        self.surname = tk.StringVar()
        self.auto_update_check = tk.BooleanVar()

        # Set Variables
        vars = [plist['dir_structure'], plist['file_structure'],
                dir_format(plist['default_library_location'], 50),
                plist['low_freq_limit'], plist['high_freq_limit'],
                plist['create_log'], dir_format(plist['logFolder'], 50),
                plist['default_date_format'], plist['forename'], plist['surname'],
                plist['auto_update_check']]
        fields = [self.dir_structure, self.file_structure,
                  self.scans_folder_display, self.low_freq_limit, self.high_freq_limit,
                  self.create_log, self.log_folder_display,
                  self.default_date_format, self.forename, self.surname,
                  self.auto_update_check]
        for field, var in zip(fields, vars):
            field.set(var)
        self.default_library_location = plist['default_library_location']
        self.log_folder = plist['logFolder']

        # Scans Folder
        ttk.Label(
            self.output_preferences,
            text='Scans Folder',
            width='16'
        ).grid(column=0, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.scans_folder_label = ttk.Label(
            self.output_preferences,
            textvariable=self.scans_folder_display,
            width='36')
        self.scans_folder_label.grid(
            column=1,
            row=0,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        CreateToolTip(self.scans_folder_label, 'Scan library base folder')
        self.change_base_folder_button = ttk.Button(
            self.output_preferences,
            text='Change Folder',
            command=self._change_base_folder)
        self.change_base_folder_button.grid(column=1, row=1)

        # Directory Structure
        ttk.Label(
            self.output_preferences,
            text='Directory Structure',
            width='16'
        ).grid(column=0, row=2, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.dir_structure_entry = ttk.Entry(
            self.output_preferences,
            textvariable=self.dir_structure,
            width='35')
        self.dir_structure_entry.grid(
            column=1,
            row=2,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        CreateToolTip(
            self.dir_structure_entry,
            'Default library directory structure (see docs for more details')

        # Filename Structure
        ttk.Label(
            self.output_preferences,
            text='Filename Structure',
            width='16'
        ).grid(column=0, row=3, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.file_structure_entry = ttk.Entry(
            self.output_preferences,
            textvariable=self.file_structure,
            width='35')
        self.file_structure_entry.grid(
            column=1,
            row=3,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        CreateToolTip(
            self.file_structure_entry,
            'Default library filename structure (see docs for more details')

        # Date Format
        ttk.Label(
            self.output_preferences,
            text='Date Format',
            width='16'
        ).grid(column=0, row=4, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.date_format_box = ttk.Combobox(
            self.output_preferences,
            textvariable=self.default_date_format)
        self.date_format_box['values'] = [key for key in data.dateFormats]
        self.date_format_box.grid(
            column=1,
            row=4,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        CreateToolTip(self.date_format_box, 'Preferred date format')

        # Low Frequency Limit
        ttk.Label(
            self.output_preferences,
            text='Low Frequency Limit',
            width='16'
        ).grid(column=0, row=5, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.low_freq_limit_entry = ttk.Entry(
            self.output_preferences,
            textvariable=self.low_freq_limit)
        self.low_freq_limit_entry.grid(column=1, row=5)
        CreateToolTip(
            self.low_freq_limit_entry,
            'Low frequency limit for the output file (set to 0 for no limit)')

        # High Frequency Limit
        ttk.Label(
            self.output_preferences,
            text='High Frequency Limit',
            width='16'
        ).grid(column=0, row=6, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.high_freq_limit_entry = ttk.Entry(
            self.output_preferences,
            textvariable=self.high_freq_limit)
        self.high_freq_limit_entry.grid(column=1, row=6)
        CreateToolTip(
            self.high_freq_limit_entry,
            'High frequency limit for the output file (set to 0 for no limit)')

        # Create Log
        ttk.Label(
            self.logging_preferences,
            text='Write To Log File',
            width='16'
        ).grid(column=0, row=0, sticky='w', padx=data.padx_default, pady=data.pady_default)
        self.create_log_check = ttk.Checkbutton(
            self.logging_preferences,
            variable=self.create_log)
        self.create_log_check.grid(
            column=1,
            row=0,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        CreateToolTip(self.create_log_check, 'Turn log file writing on/off')

        # Log Location
        ttk.Label(
            self.logging_preferences,
            text='Log Location',
            width='16'
        ).grid(column=0, row=1, sticky='w', padx=data.padx_default, pady=data.pady_default)
        self.log_location_entry = ttk.Label(
            self.logging_preferences,
            textvariable=self.log_folder_display,
            width='36')
        self.log_location_entry.grid(
            column=1,
            row=1,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        CreateToolTip(self.log_location_entry, 'Log file location')
        self.change_log_location = ttk.Button(
            self.logging_preferences,
            text='Change Folder',
            command=self._change_log_folder)
        self.change_log_location.grid(
            column=1,
            row=2,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)

        # Forename Entry
        ttk.Label(
            self.personal_data,
            text='Forename',
            width='16'
        ).grid(column=0, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.forename_entry = ttk.Entry(self.personal_data, textvariable=self.forename)
        self.forename_entry.grid(column=1, row=0)
        CreateToolTip(self.forename_entry, 'Your forename')

        # Surname Entry
        ttk.Label(
            self.personal_data,
            text='Surname',
            width='16'
        ).grid(column=0, row=1, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.surname_entry = ttk.Entry(self.personal_data, textvariable=self.surname)
        self.surname_entry.grid(column=1, row=1)
        CreateToolTip(self.surname_entry, 'Your surname')

        # Check for Updates
        ttk.Label(
            self.app_data,
            text='Auto Update Check',
            width='16'
        ).grid(column=0, row=0, sticky='w', padx=data.padx_default, pady=data.pady_default)
        self.check_for_updates_check = ttk.Checkbutton(
            self.app_data,
            variable=self.auto_update_check)
        self.check_for_updates_check.grid(
            column=1,
            row=0,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        CreateToolTip(self.check_for_updates_check, 'Automatically check for updates on startup')

        # Buttons
        self.save_settings_button = ttk.Button(
            self.settings_buttons_frame,
            text='Save',
            command=self._save_settings)
        self.save_settings_button.grid(column=0, row=0)
        CreateToolTip(self.save_settings_button, 'Save changes')
        self.cancel_settings_button = ttk.Button(
            self.settings_buttons_frame,
            text='Cancel',
            command=self._close_settings)
        self.cancel_settings_button.grid(column=1, row=0)
        CreateToolTip(self.cancel_settings_button, 'Discard changes')

        # Bindings
        self.settings_window.bind_all('<Return>', self._save_settings)
        self.settings_window.bind_all('<Escape>', self._close_settings)

        # Add padding to all entry boxes
        for widget in [
            self.change_base_folder_button,
            self.forename_entry,
            self.surname_entry,
            self.low_freq_limit_entry,
            self.high_freq_limit_entry,
            self.save_settings_button,
            self.cancel_settings_button]:
            widget.grid(sticky='W', padx=data.padx_default, pady=data.pady_default)

    # Method to select scans base folder
    def _change_base_folder(self):
        dir = tkfiledialog.askdirectory(
            parent=self.settings_master_frame,
            title='Select Scan Folder',
            initialdir=plist['default_library_location'])
        if dir != '':
            self.default_library_location = dir
            self.scans_folder_display.set(dir_format(self.default_library_location, 50))

    # Method to select default log folder
    def _change_log_folder(self):
        if os.path.exists(os.path.join(plist['logFolder'], data.log_filename)):
            self.move_old_log = True
            self.old_log_location = plist['logFolder']

        dir = tkfiledialog.askdirectory(
            parent=self.settings_master_frame,
            title='Select Source Folder',
            initialdir=plist['logFolder'])
        if dir != '':
            self.log_folder = dir
            self.log_folder_display.set(dir_format(self.log_folder, 50))

    # Method to save settings and close window
    def _save_settings(self):

        # Ensure limits are good ints else revert to default
        defaults = [plist['low_freq_limit'], plist['high_freq_limit']]
        for var, default in zip([self.low_freq_limit, self.high_freq_limit], defaults):
            if var.get() == '':
                var.set(0)
            else:
                try:
                    int(var.get())
                except ValueError:
                    var.set(default)
            if int(var.get()) < 0:
                var.set(0)
        if int(self.low_freq_limit.get()) > int(self.high_freq_limit.get()):
            self.low_freq_limit.set(self.high_freq_limit.get())
        elif int(self.high_freq_limit.get()) < int(self.low_freq_limit.get()):
            self.high_freq_limit.set(self.low_freq_limit.get())

        plist['default_library_location'] = self.default_library_location
        plist['forename'] = self.forename.get()
        plist['surname'] = self.surname.get()
        plist['dir_structure'] = self.dir_structure.get().strip('/')
        plist['file_structure'] = self.file_structure.get()
        plist['default_date_format'] = self.default_date_format.get()
        plist['low_freq_limit'] = int(self.low_freq_limit.get())
        plist['high_freq_limit'] = int(self.high_freq_limit.get())
        plist['create_log'] = self.create_log.get()
        plist['logFolder'] = self.log_folder
        plist['auto_update_check'] = self.auto_update_check.get()

        try:
            with open(data.plist_name, 'wb') as file:
                plistlib.dump(plist, file)
        except PermissionError:
            gui._display_error(1)

        # Move old log to new log location
        if self.move_old_log:
            os.rename(os.path.join(self.old_log_location, data.log_filename),
                      os.path.join(plist['logFolder'], data.log_filename))

        self._close_settings()

    # Method to close settings window
    def _close_settings(self):
        self.settings_window.quit()
        self.settings_window.destroy()

    # Method to bring settings window to front
    def bringtofront(self):
        self.settings_window.lift()

################################################################################
##########                         GUI OBJECT                         ##########
################################################################################

class GUI():

    # Initialise class
    def __init__(self, errors):

        # Variables
        self.files = []
        self.file_listbox_selection = None
        self.subdirectory = True
        self.settings_window_open = False
        self.io_guess = 0
        self.io_fixed = False
        self.custom_master_filename = False
        self.custom_subdirectory = False
        self.pmse_lookup_venues = [[], []]

        # Create instance
        self.window = tk.Tk()

        # Configure main window
        self.window.resizable(width=False, height=False)
        self.window.title(data.title)
        self.window.config(background='lightGrey')
        self.window.tk.call(
            'wm',
            'iconphoto',
            self.window._w,
            ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'logo.ico'))))

        # Build window
        self._create_styles()
        self._create_frames()
        self._create_menu()
        self._create_widgets()

        for error in errors:
            self._display_error(error)

        # Open settings if settings uninitialised
        if not SETTINGS_EXISTS:
            self._settings()

        if plist['auto_update_check']:
            self._check_for_updates(display=False)

    # Create styles for GUI
    def _create_styles(self):
        if data.system == 'Mac':
            self.font_size = 13
            self.header_size = 18
            self.left_indent = 12
        else:
            self.font_size = 10
            self.header_size = 14
            self.left_indent = 14
        default_font = tkfont.nametofont('TkDefaultFont')
        default_font.configure(size=self.font_size)
        self.sd_focus_colour = 'red'
        self.sd_no_focus_colour = 'darkgrey'
        self.base_background = '#dcdad5'

        self.gui_style = ttk.Style()
        self.gui_style.theme_use('clam')
        #self.gui_style.map('TCombobox', fieldbackground=[('readonly', 'white'), ('pressed', 'red')], foreground=[('readonly', 'black')])
        self.gui_style.configure('TLabelframe.Label', font=f'Arial {self.header_size}')
        self.gui_style.map('TCheckbutton', background=[('hover', self.base_background)])

    # Create GUI frames
    def _create_frames(self):
        self.master_frame = ttk.Frame(self.window)
        self.master_frame.grid(padx=0, pady=0, sticky='NWE')

        self.left_container = ttk.Frame(self.master_frame)
        self.left_container.grid(column=0, row=0, padx=0, pady=0, stick='NWE')

        self.right_container = ttk.Frame(self.master_frame)
        self.right_container.grid(column=1, row=0, padx=0, pady=0, sticky='NWE')

        self.input_frame = ttk.LabelFrame(self.left_container, text='Source Data')
        self.input_frame.grid(column=0, row=0, padx=10, pady=10, sticky='NWE')

        self.info_frame = ttk.LabelFrame(self.left_container, text='Scan Information')
        self.info_frame.grid(column=0, row=1, padx=8, pady=8, sticky='NWE')

        self.preview_frame = ttk.LabelFrame(self.right_container, text='Source Preview')
        self.preview_frame.grid(column=0, row=0, columnspan=2, padx=8, pady=8, sticky='NWE')
        CreateToolTip(self.preview_frame, 'Selected scan preview')

        self.output_frame = ttk.LabelFrame(self.master_frame, text='Output Data')
        self.output_frame.grid(column=0, row=1, columnspan=3, padx=8, pady=8, sticky='NWE')

        # Initialise graph window
        self.fig = matplotlib.figure.Figure(figsize=(3.2, 2.65), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_position([0.15, 0.1, 0.81, 0.81])
        self.canvas = FigureCanvasTkAgg(self.fig, self.preview_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._clear_preview()

    # Create GUI menu
    def _create_menu(self):

        # Create Menu Bar
        self.menu_bar = tk.Menu(self.window)

        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.file_menu.add_command(
            label=f'Add Files...',
            accelerator=f'{data.command_abbr}{data.modifier_abbr}A',
            command=self._add_files)
        self.file_menu.add_command(
            label='Add Directory...',
            accelerator=f'{data.command_abbr}{data.alt_abbr}A',
            command=self._add_directory)
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label='Set Date',
            accelerator=f'{data.command_abbr}D',
            command=self._use_date)
        self.file_menu.add_command(
            label='Set Destination...',
            accelerator=f'{data.command_abbr}{data.modifier_abbr}D',
            command=self._custom_destination)
        self.file_menu.add_command(
            label='Create File',
            accelerator=f'{data.command_abbr}Return',
            command=self._create_file)

        # Edit Menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.edit_menu.add_command(
            label='Copy',
            accelerator=f'{data.command_abbr}C',
            command=lambda: self.window.focus_get().event_generate("<<Copy>>"))
        self.edit_menu.add_command(
            label='Cut',
            accelerator=f'{data.command_abbr}X',
            command=lambda: self.window.focus_get().event_generate("<<Cut>>"))
        self.edit_menu.add_command(
            label='Paste',
            accelerator=f'{data.command_abbr}V',
            command=lambda: self.window.focus_get().event_generate("<<Paste>>"))
        self.edit_menu.add_command(
            label='Select All',
            accelerator=f'{data.command_abbr}A',
            command=lambda: self.window.focus_get().event_generate("<<SelectAll>>"))
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label='Remove File',
            accelerator='BackSpace',
            command=self._remove_file)
        self.edit_menu.add_command(
            label='Clear Files',
            accelerator=f'{data.command_abbr}BackSpace',
            command=self._clear_files)

        # Help Menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=False, name='help')

        # Application Menu (OS X only)
        if data.system == 'Mac':
            self.app_menu = tk.Menu(self.menu_bar, tearoff=False, name='apple')
            self.app_menu.add_command(
                label='About RF Library',
                command=self._about)
            self.app_menu.add_command(
                label='Check for Updates...',
                command=self._check_for_updates)
            self.app_menu.add_separator()
            self.menu_bar.add_cascade(menu=self.app_menu)

            # Configure OS X Built-in menu options
            self.window.createcommand('::tk::mac::ShowPreferences', self._settings)
            self.window.createcommand('::tk::mac::ShowHelp', self._open_http)

        # Extra menus for Windows only
        if data.system == 'Windows':
            self.file_menu.add_separator()
            self.file_menu.add_command(
                label='Exit',
                accelerator=f'{data.command_abbr}Q',
                command=self._quit)
            self.tools_menu = tk.Menu(self.menu_bar, tearoff=False)
            self.tools_menu.add_command(
                label='Preferences...',
                command=self._settings)
            self.help_menu.add_command(
                label='Documentation',
                command=self._open_http)
            self.help_menu.add_separator()
            self.help_menu.add_command(
                label='Check for Updates...',
                command=self._check_for_updates)
            self.help_menu.add_command(
                label='About RF Library',
                command=self._about)

        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.menu_bar.add_cascade(label='Edit', menu=self.edit_menu)

        # Window Menu (OS X Only)
        if data.system == 'Mac':
            self.window_menu = tk.Menu(self.menu_bar, name='window')
            self.menu_bar.add_cascade(menu=self.window_menu, label='Window')

        # Tools Menu (Windows Only)
        elif data.system == 'Windows':
            self.menu_bar.add_cascade(label='Tools', menu=self.tools_menu)

        self.menu_bar.add_cascade(label='Help', menu=self.help_menu)
        self.window.config(menu=self.menu_bar)

        # Bindings for Mac/Windows
        self.window.bind_all(f'<{data.command}{data.modifier}a>', self._add_files)

        # Bindings for Windows only
        if data.system == 'Windows':
            self.window.bind_all(f'<{data.command}{data.modifier}A>', self._add_files)
            self.window.bind_all(f'<{data.command}{data.alt}a>', self._add_directory)
            self.window.bind_all(f'<{data.command}{data.alt}A>', self._add_directory)
            self.window.bind_all(f'<{data.command}{data.modifier}d>', self._custom_destination)
            self.window.bind_all(f'<{data.command}{data.modifier}D>', self._custom_destination)
            self.window.bind_all(f'<{data.command}q>', self._quit)
            self.window.bind_all(f'<{data.command}Q>', self._quit)
            self.window.bind_all(f'<{data.command}BackSpace>', self._clear_files)

    # Create GUI widgets
    def _create_widgets(self):

        # Initialise tkinter variables
        self.num_files = tk.StringVar()
        self.venue = tk.StringVar()
        self.town = tk.StringVar()
        self.country = tk.StringVar()
        self.scan_date = tk.StringVar()
        self.in_out = tk.StringVar()
        self.scan_output_location_display = tk.StringVar()
        self.target_subdirectory = tk.StringVar()
        self.default_output_location = tk.BooleanVar()
        self.scan_master_filename = tk.StringVar()
        self.default_master_filename = tk.BooleanVar()
        self.copy_source_files = tk.BooleanVar()
        self.delete_source_files = tk.BooleanVar()

        # Set default values
        fields = [
            self.venue,
            self.town,
            self.country,
            self.copy_source_files,
            self.delete_source_files]
        vars = [
            plist['defaultVenue'],
            plist['defaultTown'],
            plist['defaultCountry'],
            plist['defaultCopy'],
            plist['defaultDelete']]
        for field, var in zip(fields, vars):
            field.set(var)

        # File List
        ttk.Label(self.input_frame, text='File List').grid(column=0, row=0, sticky='W')
        self.file_listbox = tk.Listbox(self.input_frame, height=8, width=20)
        self.file_listbox.bind('<<ListboxSelect>>', self._select_file_item)
        self.file_listbox.grid(column=0, row=1, padx=data.padx_default, pady=data.pady_default)

        # Data List
        ttk.Label(
            self.input_frame,
            text='Selected File Information'
        ).grid(column=1, row=0, sticky='W')
        self.data_listbox = tk.Listbox(self.input_frame, height=8, width=30)
        self.data_listbox.grid(column=1, row=1, padx=data.padx_default, pady=data.pady_default)
        self.data_listbox.configure(background='lightGrey')

        # File List Edit Buttons
        self.file_list_edit_frame = ttk.Frame(self.input_frame)
        self.file_list_edit_frame.grid(column=0, row=2, columnspan=2, sticky='E')

        calendar_image = ImageTk.PhotoImage(
            Image.open(os.path.join(data.icon_location, 'calendar_disabled.png')))
        self.use_date_button = ttk.Button(
            self.file_list_edit_frame,
            image=calendar_image,
            state='disabled',
            command=self._use_date)
        self.use_date_button.grid(column=4, row=0, sticky='E', padx=data.padx_default, pady=0)
        self.use_date_button.image = calendar_image
        CreateToolTip(
            self.use_date_button,
            f'Use currently selected file\'s creation date for scan date ({data.command_symbol}D)')

        bin_image = ImageTk.PhotoImage(
            Image.open(os.path.join(data.icon_location, 'bin_disabled.png')))
        self.clear_files_button = ttk.Button(
            self.file_list_edit_frame,
            image=bin_image,
            state='disabled',
            command=self._clear_files)
        self.clear_files_button.grid(
            column=3,
            row=0,
            sticky='E',
            padx=data.padx_default,
            pady=0)
        self.clear_files_button.image = bin_image
        CreateToolTip(
            self.clear_files_button,
            f'Remove all files from file list ({data.command_symbol}\u232b)')

        minus_image = ImageTk.PhotoImage(
            Image.open(os.path.join(data.icon_location, 'minus_disabled.png')))
        self.remove_file_button = ttk.Button(
            self.file_list_edit_frame,
            image=minus_image,
            state='disabled',
            command=self._remove_file)
        self.remove_file_button.grid(column=2, row=0, sticky='E', padx=data.padx_default, pady=0)
        self.remove_file_button.image = minus_image
        CreateToolTip(self.remove_file_button, 'Remove selected file from file list (\u232b)')

        folder_image = ImageTk.PhotoImage(
            Image.open(os.path.join(data.icon_location, 'folder.png')))
        self.add_directory_button = ttk.Button(
            self.file_list_edit_frame,
            image=folder_image,
            command=self._add_directory)
        self.add_directory_button.grid(
            column=1,
            row=0,
            sticky='E',
            padx=data.padx_default,
            pady=data.pady_default)
        self.add_directory_button.image = folder_image
        CreateToolTip(
            self.add_directory_button,
            f'Add directory to file list ({data.command_symbol}{data.alt_symbol}A)')

        plus_image = ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'plus.png')))
        self.add_files_button = ttk.Button(
            self.file_list_edit_frame,
            image=plus_image,
            command=self._add_files)
        self.add_files_button.grid(
            column=0,
            row=0,
            sticky='E',
            padx=data.padx_default,
            pady=data.pady_default)
        self.add_files_button.image = plus_image
        CreateToolTip(
            self.add_files_button,
            f'Add files to file list ({data.command_symbol}{data.modifier_symbol}A)')

        # File Info status
        self.file_status = ttk.Label(self.input_frame, textvariable=self.num_files)
        self.file_status.grid(
            column=0,
            row=2,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)

        # Source Venue Data
        ttk.Label(
            self.info_frame,
            text='Venue',
            width=self.left_indent
        ).grid(column=0, row=0, sticky='NW', padx=data.padx_default, pady=data.pady_default)
        self.venue_entry = ttk.Entry(
            self.info_frame,
            textvariable=self.venue,
            width=20,
            font=f'TkDefaultFont {self.font_size}')
        self.venue_entry.grid(column=1, row=0)
        CreateToolTip(self.venue_entry, 'Scan location name')

        # Source Town Data
        ttk.Label(
            self.info_frame,
            text='Town',
            width=self.left_indent
        ).grid(column=0, row=1, sticky='NW', padx=data.padx_default, pady=data.pady_default)
        self.town_entry = ttk.Entry(
            self.info_frame,
            textvariable=self.town,
            width=20,
            font=f'TkDefaultFont {self.font_size}')
        self.town_entry.grid(column=1, row=1)
        CreateToolTip(self.town_entry, 'Scan location town/city')

        # Source Country Data
        ttk.Label(
            self.info_frame,
            text='Country',
            width=self.left_indent
        ).grid(column=0, row=2, sticky='NW', padx=data.padx_default, pady=data.pady_default)
        self.country_box = ttk.Combobox(
            self.info_frame,
            textvariable=self.country,
            width=20,
            font=f'TkDefaultFont {self.font_size}')
        self.country_box['values'] = data.countries
        self.country_box.grid(
            column=1,
            row=2,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        self.country_box.bind('<<ComboboxSelected>>', self._refresh)
        CreateToolTip(self.country_box, 'Scan location country')

        # Source Scan Date
        ttk.Label(
            self.info_frame,
            text='Scan Date',
            width=self.left_indent
        ).grid(column=0, row=3, sticky='NW', padx=data.padx_default, pady=data.pady_default)
        self.date_entry = ttk.Entry(
            self.info_frame,
            textvariable=self.scan_date,
            width=20,
            font=f'TkDefaultFont {self.font_size}')
        self.date_entry.grid(column=1, row=3)
        self.date_entry.config(state='readonly')
        CreateToolTip(self.date_entry, 'Date scan was taken')

        # Inside / Outside
        ttk.Label(
            self.info_frame,
            text='Inside/Outside',
            width=self.left_indent
        ).grid(column=0, row=4, sticky='NW', padx=data.padx_default, pady=data.pady_default)
        self.io_box = ttk.Combobox(
            self.info_frame,
            textvariable=self.in_out,
            width=20,
            state='readonly',
            font=f'TkDefaultFont {self.font_size}')
        self.io_box['values'] = ['Inside', 'Outside']
        self.io_box.grid(column=1, row=4)
        self.io_box.current(0)
        self.io_box.bind('<<ComboboxSelected>>', self._io_box_edit)
        CreateToolTip(self.io_box, 'Was the scan taken inside or outside?')

        # Output Location
        reset_image = ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'reset.png')))
        self.target_subdirectory.set(self.in_out.get())
        ttk.Label(
            self.output_frame,
            text='Destination',
            width=self.left_indent
        ).grid(column=0, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.default_output_location.set(1)
        self.default_output_check = ttk.Button(
            self.output_frame,
            image=reset_image,
            command=self._reset_output_location)
        self.default_output_check.grid(column=1, row=0, sticky='W', padx=0, pady=0)
        self.default_output_check.image = reset_image
        CreateToolTip(self.default_output_check, 'Check to use default library destination folder')
        self.target_directory = ttk.Label(
            self.output_frame,
            textvariable=self.scan_output_location_display,
            width=77)
        self.target_directory.grid(column=2, row=0, sticky='W')
        CreateToolTip(self.target_directory, 'Output scan folder')

        # Subdirectory
        ttk.Label(
            self.output_frame,
            text='Subdirectory', 
            width=self.left_indent
        ).grid(column=0, row=1, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.target_subdirectory_entry = ttk.Entry(
            self.output_frame,
            textvariable=self.target_subdirectory,
            width=20,
            font=f'TkDefaultFont {self.font_size}',
            style='Subdirectory.TEntry')
        self.target_subdirectory_entry.grid(
            column=2,
            row=1,
            sticky='W',
            padx=0,
            pady=data.pady_default)
        self.target_subdirectory_entry.bind('<KeyRelease>', self._custom_subdirectory)
        CreateToolTip(self.target_subdirectory_entry, 'Optional subdirectory')

        # Output Master Filename
        ttk.Label(
            self.output_frame,
            text='Master Filename',
            width=self.left_indent
        ).grid(column=0, row=2, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.default_master_filename.set(1)
        self.default_master_filename_reset = ttk.Button(
            self.output_frame,
            image=reset_image,
            command=self._standard_master_filename)
        self.default_master_filename_reset.grid(column=1, row=2, sticky='W', padx=0, pady=0)
        self.default_master_filename_reset.image = reset_image
        CreateToolTip(self.default_master_filename_reset, 'Check to use default filename')
        self.scan_master_filename_entry = ttk.Entry(
            self.output_frame,
            textvariable=self.scan_master_filename,
            font=f'TkDefaultFont {self.font_size}')
        self.scan_master_filename_entry.grid(
            column=2,
            row=2,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        self.scan_master_filename_entry.config(width=60)
        self.scan_master_filename_entry.bind('<KeyRelease>', self._custom_master_filename)
        CreateToolTip(self.scan_master_filename_entry, 'Master output filename')

        # Options
        self.copy_source_files_check = ttk.Checkbutton(self.output_frame, variable=self.copy_source_files)
        self.copy_source_files_check.grid(column=1, row=3, sticky='E', padx=data.padx_default, pady=data.pady_default)
        ttk.Label(self.output_frame, text='Duplicate Source Files').grid(column=2, row=3, sticky='W')
        CreateToolTip(self.copy_source_files_check, 'Duplicate source files in library')
        self.delete_source_files_check = ttk.Checkbutton(self.output_frame, variable=self.delete_source_files)
        self.delete_source_files_check.grid(column=1, row=4, sticky='E', padx=data.padx_default, pady=data.pady_default)
        ttk.Label(self.output_frame, text='Delete Source Files').grid(column=2, row=4, sticky='W')
        CreateToolTip(self.delete_source_files_check, 'Delete source files on file creation')

        # Output Buttons
        self.output_buttons = ttk.Frame(self.output_frame)
        self.output_buttons.grid(column=2, row=5, sticky='W')
        self.create_file_button = ttk.Button(
            self.output_buttons,
            text='Create File',
            command=self._create_file)
        self.create_file_button.grid(
            column=0,
            row=0,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        CreateToolTip(
            self.create_file_button,
            f'Create master file ({data.command_symbol}\u23ce)')
        self.custom_output_button = ttk.Button(
            self.output_buttons,
            text='Set Destination',
            command=self._custom_destination)
        self.custom_output_button.grid(
            column=1,
            row=0,
            sticky='W',
            padx=data.padx_default,
            pady=data.pady_default)
        CreateToolTip(
            self.custom_output_button,
            f'Set custom destination for output files ({data.command_symbol}{data.modifier_symbol}D)')

        # Add styling to all entry boxes
        for x in [
            self.venue_entry,
            self.town_entry,
            self.country_box,
            self.date_entry,
            self.io_box]:
            x.grid(sticky='NW', padx=data.padx_default, pady=data.pady_default)
            x.bind('<KeyRelease>', self._get_master_filename)

        # Key Bindings
        self.window.bind_all(f'<{data.command}Return>', self._create_file)
        self.file_listbox.bind('<Escape>', self._deselect_file_listbox)
        self.file_listbox.bind('<BackSpace>', self._remove_file)

        # Initialise Lists
        self._print_files()

################################################################################
##########                       GUI METHODS                          ##########
################################################################################

    # Method to update filelist
    def _print_files(self, event=None):
        self.file_listbox.delete(0, tk.END)
        for file in self.files:
            self.file_listbox.insert(tk.END, file.filename)
        self._select_file_item(event)
        self._update_file_status()
        self._get_scan_date()
        self._get_master_filename()

    # Method to select file_listbox item
    """def _select_file_item(self, event=None):
        if event:
            try:
                self.file_listbox_selection = int(event.widget.curselection()[0])
            except (AttributeError, IndexError):
                pass
        #self.file_listbox.selection_clear(0, tk.END)
        #if self.file_listbox_selection != None:
        #    self.file_listbox.select_set(self.file_listbox_selection)
        #    self.file_listbox.activate(self.file_listbox_selection)
        #if self.file_listbox_selection:
        #    self.file_listbox.see(self.file_listbox_selection)
        self._print_file_data()"""

    def _select_file_item(self, event=None):
        if event:
            try:
                self.file_listbox_selection = int(event.widget.curselection()[0])
            except (AttributeError, IndexError):
                pass
        self._print_file_data()

    # Method to print file data to data_listbox
    def _print_file_data(self):
        self.data_listbox.delete(0, tk.END)
        if self.file_listbox_selection is None:
            self.data_listbox.insert(tk.END, 'No file selected')
            self._clear_preview()
        else:
            self.data_listbox.insert(
                tk.END,
                f'Filename: {self.files[self.file_listbox_selection].filename}')
            self.data_listbox.insert(
                tk.END,
                f'Date: {self.files[self.file_listbox_selection].creationDate.strftime(dateFormat)}')
            self.data_listbox.insert(
                tk.END,
                f'Scanner: {self.files[self.file_listbox_selection].model}')
            if self.files[self.file_listbox_selection].start_tv_channel is None:
                start_tv = ''
            else:
                start_tv = f' (TV{self.files[self.file_listbox_selection].start_tv_channel})'
            self.data_listbox.insert(
                tk.END,
                f'Start Frequency: {self.files[self.file_listbox_selection].startFrequency:.3f}MHz{start_tv}')
            if self.files[self.file_listbox_selection].stop_tv_channel is None:
                stop_tv = ''
            else:
                stop_tv = f' (TV{self.files[self.file_listbox_selection].stop_tv_channel})'
            self.data_listbox.insert(
                tk.END,
                f'Stop Frequency: {self.files[self.file_listbox_selection].stopFrequency:.3f}MHz{stop_tv}')
            self.data_listbox.insert(
                tk.END,
                f'Data Points: {self.files[self.file_listbox_selection].dataPoints}')
            self.data_listbox.insert(
                tk.END,
                f'Mean Resolution: {self.files[self.file_listbox_selection].resolution:.3f}MHz')
            self.data_listbox.insert(
                tk.END,
                f'New Filename: {self.files[self.file_listbox_selection].new_filename}')
            self._update_preview()
        self._button_disable()

    # Method to decide if buttons should be disabled or not
    def _button_disable(self):
        if len(self.files) == 0 :
            self._button_status('disabled', 'disabled')
        elif self.file_listbox_selection is None:
            self._button_status('disabled', 'enabled')
        else:
            self._button_status('enabled', 'enabled')

    # Method to print number of files chosen
    def _update_file_status(self):
        plural = '' if len(self.files) == 1 else 's'
        if len(self.files) == 0:
            self.file_status.configure(foreground='red')
        else:
            self.file_status.configure(foreground='black')
        self.num_files.set(f'{len(self.files)} file{plural} added')

    # Method to get earliest date from all files or todays date (default)
    def _get_scan_date(self):
        if len(self.files) == 0:
            self.scan_datetimestamp = datetime.date.today()
        else:
            self.scan_datetimestamp = min([file.creationDate for file in self.files])
        self.scan_date.set(self.scan_datetimestamp.strftime(dateFormat))

    # Method to convert user input directory structure into path
    def parse_structure(self, s):
        for old, new in [
            ('%c', self.country.get()),
            ('%t', self.town.get()),
            ('%v', self.venue.get()),
            ('%y', str(self.scan_datetimestamp.year)),
            ('%i', self.in_out.get()),
            ('%s', self.target_subdirectory.get()),
            ('%f', plist['forename']),
            ('%n', plist['surname']),
            ('%m', f'{self.scan_datetimestamp.month:02d}'),
            ('%M', self.scan_datetimestamp.strftime('%B')),
            ('%d', f'{self.scan_datetimestamp.day:02d}')]:
            s = s.replace(old, new)
        return s

    # Method to create master filename
    def _get_master_filename(self):

        # Return if user has entered a custom master filename
        if self.custom_master_filename:
            return

        self.scan_master_filename.set(self.parse_structure(plist['file_structure'] + '.csv'))
        if self.default_output_location.get() == 1:
            self.library_location = plist['default_library_location']
            self.target_location = self.parse_structure(
                os.path.join(plist['dir_structure'],'%s'))
        else:
            self.target_location = self.target_subdirectory.get()
            if self.target_subdirectory.get() != '':
                self.target_location = self.target_location
        self.scan_output_location = os.path.join(self.library_location, self.target_location)
        self.scan_output_location_display.set(dir_format(self.scan_output_location, 90))

    # Method to disable/enable buttons/menu items based on selected files
    def _button_status(self, input_status=None, output_status=None):
        if input_status is not None:
            for x in [(self.remove_file_button, 'minus'), (self.use_date_button, 'calendar')]:
                img = ImageTk.PhotoImage(Image.open(
                    os.path.join(data.icon_location, f'{x[1]}_{input_status}.png')))
                x[0].config(state=input_status, image=img)
                x[0].image = img
            if input_status == 'enabled':
                input_status = 'normal'
            for (menu, item) in [(self.edit_menu, 'Remove File'), (self.file_menu, 'Set Date')]:
                menu.entryconfig(item, state=input_status)

        if output_status is not None:
            img = ImageTk.PhotoImage(Image.open(
                os.path.join(data.icon_location, f'bin_{output_status}.png')))
            self.clear_files_button.config(state=output_status, image=img)
            self.clear_files_button.image = img
            if output_status == 'enabled':
                self.window.bind_all(f'<{data.command}d>', self._use_date)
                self.window.bind_all(f'<{data.command}D>', self._use_date)
                self.edit_menu.entryconfig('Clear Files', state='normal')
                self.file_menu.entryconfig('Create File', state='normal')
            else:
                self.window.unbind_all(f'<{data.command}d>')
                self.window.unbind_all(f'<{data.command}D>')
                self.edit_menu.entryconfig('Clear Files', state='disabled')
                self.file_menu.entryconfig('Create File', state='disabled')

    # Method to change destination to custom destination
    def _custom_destination(self):
        custom_location = tkfiledialog.askdirectory(
            parent=self.master_frame,
            title='Select Destination Folder')
        if custom_location != '':
            self.library_location = custom_location
            self.scan_output_location = self.library_location
            self.scan_output_location_display.set(dir_format(self.scan_output_location, 90))
            self.default_output_location.set(0)
            self._update_subdirectory()

    # Method to refresh file data, for use when country or settings change
    def _refresh(self):
        global dateFormat
        dateFormat = set_date_format()
        for file in self.files:
            file.updateTVChannels(self.country.get())
        self._print_files()

    # Method to deselect file_listbox
    def _deselect_file_listbox(self):
        self.file_listbox_selection = None
        self.file_listbox.selection_clear(0, tk.END)
        self._select_file_item()

    # Method called after IO_box edited
    def _io_box_edit(self):
        self.io_fixed = True
        if not self.custom_subdirectory:
            self._update_subdirectory()

    # Method called after subdirectory edited
    def _custom_subdirectory(self):
        self.custom_subdirectory = True
        self._get_master_filename()

    # Method to declare user has entered a custom Master Filename
    def _custom_master_filename(self):
        self.custom_master_filename = True
        self.default_master_filename.set(0)

    # Method to declare user wants to use the standard Filename
    def _standard_master_filename(self):
        self.custom_master_filename = False
        self.default_master_filename.set(1)
        self._get_master_filename()

    # Method to update output location to standard location
    def _reset_output_location(self):
        self.default_output_location.set(1)
        self._update_subdirectory()

    # Method to update subdirectory name when standard destination called
    def _update_subdirectory(self):
        if self.default_output_location.get() == 1:
            self.target_subdirectory.set(self.in_out.get())
            self.subdirectory = True
        else:
            self.target_subdirectory.set('')
            self.subdirectory = False
        self._get_master_filename()

    # Method to update io_box and Subdirectory when Inside v Outside changes
    def _set_io(self):
        if not self.io_fixed:
            if self.io_guess >= 0:
                self.io_box.current(0)
            else:
                self.io_box.current(1)
            self._update_subdirectory()

    # Method to open file dialogue and allow selection of files
    def _add_files(self, selected_files=None, suppress_errors=False):
        if selected_files is None:
            selected_files = tkfiledialog.askopenfilenames(
                parent=self.input_frame,
                title='Add files',
                initialdir=plist['defaultSourceLocation'])
        for file in selected_files:
            new_file = File(file, self.country.get())
            if new_file.valid:
                self.io_guess += new_file.io
                self.files.append(new_file)
                plist['defaultSourceLocation'] = os.path.dirname(file)
            elif not suppress_errors:
                tkmessagebox.showwarning(
                    'Invalid File',
                    f'{new_file.filename} is not a valid scan file and will not be added to the file list')
        self._set_io()
        self._print_files()

    # Method to open file dialogue and allow selection of all files in a directory
    def _add_directory(self):
        dir_files = []
        selected_dir = tkfiledialog.askdirectory(
            parent=self.input_frame, title='Add directory',
            initialdir=plist['defaultSourceLocation'])
        if selected_dir != '':
            plist['defaultSourceLocation'] = selected_dir
            for file in os.listdir(selected_dir):
                fullfilename = os.path.join(selected_dir, file)
                if not file.startswith('.') and not os.path.isdir(fullfilename):
                    dir_files.append(fullfilename)
        if len(dir_files) != 0:
            self._add_files(None, dir_files, True)

    # Method to remove file
    def _remove_file(self, event=None):
        if event is None or (event.widget.winfo_class() != 'TEntry' and event.widget.winfo_class() != 'TCombobox'):
            if self.file_listbox_selection is None:
                return
            self.io_guess -= self.files[self.file_listbox_selection].io
            self._set_io()
            self.files.remove(self.files[self.file_listbox_selection])
            if len(self.files) == 0:
                self.file_listbox_selection = None
            elif self.file_listbox_selection > len(self.files) - 1:
                self.file_listbox_selection = len(self.files) - 1
            self._print_files(event)

    # Method to remove all files
    def _clear_files(self, confirm_required=True):
        self.edit_menu.entryconfig('Clear Files', state='disabled')
        if confirm_required:
            if not tkmessagebox.askyesno(
                'Are you sure?',
                'Are you sure you want to clear the file list?'):
                self.edit_menu.entryconfig('Clear Files', state='normal')
                return
        del self.files[:]
        self.file_listbox_selection = None
        self.io_fixed = False
        self.io_guess = 0
        self._print_files()

    # Method to use date from selected file
    def _use_date(self):
        self.scan_datetimestamp = self.files[self.file_listbox_selection].creationDate
        self.scan_date.set(self.scan_datetimestamp.strftime(dateFormat))
        self._get_master_filename()

    # Method to create master file
    def _create_file(self):
        if len(self.files) == 0:
            tkmessagebox.showinfo('No Files To Create', 'No files to create.')
            return

        # Check if user really wants to delete source files
        if self.delete_source_files.get() == 1 and tkmessagebox.askyesno(
            'Are you sure?',
            'Are you sure you want to delete the input files?'):
            del_source_confirmed = True
        else:
            del_source_confirmed = False

        # Add all files into output_file list if within limits
        output_file = []
        files_written = 0
        statement = f'The following files were successfully written!\n\nDIRECTORY:\n{self.scan_output_location}\n\n'
        for file in self.files:
            for freq, value in file.frequencies:
                if freq >= plist['low_freq_limit'] and (plist['high_freq_limit'] == 0 or freq <= plist['high_freq_limit']):
                    output_file.append([float(freq), float(value)])

        # Remove duplicates
        output_file = sorted(output_file)
        i = 1
        while i < len(output_file):
            if output_file[i][0] == output_file[i - 1][0]:
                output_file.remove(output_file[i - 1])
            else:
                i += 1

        # Write original files with new filenames
        if self._create_directory():
            if self.copy_source_files.get():
                for file in self.files:
                    written_filename = self._write_file(
                        self.scan_output_location,
                        file.new_filename,
                        file.frequencies)
                    if not written_filename:
                        return False
                    files_written += 1
                    statement += f'{written_filename}\n'

            # Write master file
            if len(output_file) > 0:
                written_filename = self._write_file(
                    self.scan_output_location,
                    self.scan_master_filename.get(),
                    output_file)
                if not written_filename:
                    return False
                files_written += 1
                statement += f'{written_filename}\n'

            # Write WSM file
            if (data.makeWSM and len(output_file) > 0):
                written_filename = self._write_wsm_file(
                    self.scan_output_location,
                    self.scan_master_filename.get(),
                    output_file)
                if not written_filename:
                    return False
                files_written += 1
                statement += f'{written_filename}\n'

            statement += f'\n{files_written} files written to disk.\n'

            if files_written == 0:
                tkmessagebox.showinfo('No Files To Create', 'No files to create.')
                return

            # Write defaults to plist
            plist['defaultVenue'] = self.venue.get()
            plist['defaultTown'] = self.town.get()
            plist['defaultCountry'] = self.country.get()
            plist['defaultCopy'] = self.copy_source_files.get()
            plist['defaultDelete'] = self.delete_source_files.get()

            try:
                with open(data.plist_name, 'wb') as file:
                    plistlib.dump(plist, file)
            except PermissionError:
                gui._display_error(1)

            if plist['create_log']:
                if self._write_to_log():
                    statement += 'Log file updated.\n'
                else:
                    statement += f'WARNING: Log could not be updated at {plist["logFolder"]}\n'

            if del_source_confirmed:
                statement += '\nThe following files were deleted:\n'
                for file in self.files:
                    os.remove(file.fullfilename)
                    statement += f'{file.filename}\n'
                self._clear_files(None, False)
                tkmessagebox.showinfo('Success!', statement)
            else:
                if tkmessagebox.askyesno(
                    'Success!',
                    f'{statement}\nWould you like to clear the file list?'):
                    self._clear_files(None, False)

    # Method to write to log file
    def _write_to_log(self):
        log_file = os.path.join(plist['logFolder'], data.log_filename)

        if not os.path.exists(log_file):
            new_file = True
        else:
            new_file = False

        with open(log_file, 'a', newline='') as csvfile:
            log_writer = csv.writer(
                csvfile,
                delimiter=',',
                quotechar="\"",
                quoting=csv.QUOTE_MINIMAL)
            if new_file:
                log_writer.writerow(['Date', 'Country', 'City', 'Venue', 'Inside/Outside'])
            log_writer.writerow([
                self.scan_date.get(),
                self.country.get(),
                self.town.get(),
                self.venue.get(),
                self.in_out.get()])

        return True

    def _find_unused_file(self, directory, filename):
        target = os.path.join(directory, filename)
        file, ext = os.path.splitext(filename)
        duplicate_counter = 0
        while os.path.isfile(target):
            duplicate_counter += 1
            filename = f'{file}-{duplicate_counter}{ext}'
            target = os.path.join(directory, filename)
        return filename

    # Method to write file to disk
    def _write_file(self, directory, filename, array):
        filename = self._find_unused_file(directory, filename)
        target = os.path.join(directory, filename)
        try:
            with open(target, 'w') as file:
                for freq, value in array:
                    file.write(f'{freq:09.4f},{value:09.4f}\n')
            return filename
        except IOError:
            tkmessagebox.showwarning(f'Fail!', '{target} could not be written.')
            return False

    # Method to write WSM file to disk
    def _write_wsm_file(self, directory, filename, array):
        file, ext = os.path.splitext(filename)
        filename = f'{file}-WSM.{ext}'

        filename = self._find_unused_file(directory, filename)
        target = os.path.join(directory, filename)
        try:
            with open(target, 'w') as file:
                wsm_date = self.scan_datetimestamp.strftime('%Y-%m-%d 00:00:00')
                file.write(f'Receiver;{data.title}\nDate/Time;{wsm_date}\nRFUnit;dBm\n\n\nFrequency Range [kHz];{(plist["low_freq_limit"] * 1000):06d};{plist["high_freq_limit"] * 1000:06d};\n')
                file.write('Frequency;RF level (%);RF level\n')
                for freq, value in reversed(array):
                    file.write(f'{int(freq * 1000):06d};;{value:04.1f}\n')
            return filename
        except IOError:
            tkmessagebox.showwarning('Fail!', f'{target} could not be written.')
            return False

    # Method to create directory structure
    def _create_directory(self):
        try:
            os.makedirs(f'{self.scan_output_location}')
            return True
        except OSError:
            return tkmessagebox.askyesno(
                'Directory already exists',
                f'{self.scan_output_location} already exists. Are you sure?')

    # Method to remove current preview
    def _clear_preview(self):

        # Clear Graph
        self.ax.clear()

        # Set Style
        self.ax.set_facecolor('lightGrey')
        self.ax.grid(linestyle='None')
        self.ax.set_axisbelow(True)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlabel('Frequency /MHz')
        self.ax.set_ylabel('Level /dBm')

        # Set Font
        matplotlib.rcParams.update({'font.size': 9 })

        # Draw Canvas
        self.canvas.draw()

    # Method to draw preview of self.file_listbox_selection
    def _update_preview(self):

        # Get x,y values
        mean = 0
        for x in self.files[self.file_listbox_selection].frequencies:
            try:
                previous
            except:
                previous = [x[0], x[1]]
                x_values = []
                y_values = []
            mean += x[1]
            if previous[0] + (self.files[self.file_listbox_selection].resolution * 2) < x[0]:
                x_values.append(previous[0] + self.files[self.file_listbox_selection].resolution)
                y_values.append(-200)
                x_values.append(x[0] - self.files[self.file_listbox_selection].resolution)
                y_values.append(-200)
            x_values.append(x[0])
            y_values.append(x[1])
            previous = x

        # Calculate mean value for potential scaling
        mean /= len(self.files[self.file_listbox_selection].frequencies)

        # Get axis values
        ymin = min(i for i in y_values if i > -120)
        ymax = max(y_values)
        ymin = int((ymin - 5) / 5) * 5 if ymin > -95 or ymin < -105 else -105
        ymax = int((ymax + 5) / 5) * 5 if ymax > ymin + 45 else ymin + 45
        xmin = x_values[0]
        xmax = x_values[-1]

        # Get x tick values
        min_pixel_distance = 25
        axeswidth = self.ax.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted()).width * self.fig.dpi
        min_tick_distance = ((xmax - xmin) * min_pixel_distance) / axeswidth
        x_ticks = []
        prev = 0
        tv_country = self.country.get() if self.country.get() == 'United States of America' else 'UK'
        for channel in data.TVChannels[tv_country]:
            if channel[1] - prev >= min_tick_distance and self.files[self.file_listbox_selection].frequencies[0][0] <= channel[1] and self.files[self.file_listbox_selection].frequencies[-1][0] >= channel[1]:
                x_ticks.append(channel[1])
                prev = channel[1]

        # Clear previous graph
        self.ax.clear()

        # Set Style
        self.ax.get_yaxis().set_visible(True)
        self.ax.get_xaxis().set_visible(True)
        self.ax.grid(linestyle='-', color='grey')
        self.ax.fill_between(x_values, int(ymin) - 1, y_values, facecolor='lightGreen')

        # Set axis/ticks
        self.ax.axis([xmin, xmax, ymin, ymax])
        self.ax.set_xticks(x_ticks, minor=False)

        # Draw Graph
        self.ax.plot(x_values, y_values, color='green')
        self.canvas.draw()

    # Method to quit application
    def _quit(self):
        try:
            self.pmse_lookup.logout()
        except AttributeError:
            pass
        self.window.quit()
        self.window.destroy()
        sys.exit()

    # Method to display about information
    def _about(self):
        tkmessagebox.showinfo(
            'About',
            f'{data.title} v{data.version}\n\n{chr(169)} Stephen Bunting 2019\n{data.website_uri}')

    # Method to open docs in web browser
    def _open_http(self):
        webbrowser.open(f'{data.website_uri}documentation.php', new=2, autoraise=True)

    # Method to display settings box
    def _settings(self):
        global SETTINGS_EXISTS, settings

        if self.settings_window_open:
            self.settings.bringtofront()
        else:
            self.settings_window_open = True
            self.settings = SettingsWindow()
            self.settings.settings_window.mainloop()
            self.settings_window_open = False
            self._refresh()

    # Check for latest version of software
    def _check_for_updates(self, **kwargs):
        if 'display' in kwargs.keys():
            display = kwargs['display']
        else:
            display = True

        try:
            r = requests.get(data.update_file_location)
            update_connection = True
        except requests.exceptions.ConnectionError:
            update_connection = False

        if update_connection:
            root = xml.etree.ElementTree.fromstring(r.text)
            latest = root[0][0].text
            download_uri = root[0][2].text
            if latest == data.version:
                if display:
                    tkmessagebox.showinfo(
                        "Check for Updates",
                        "No updates found. You have the latest version of RF Library.")
            else:
                if (tkmessagebox.askyesno(
                    "Check for Updates",
                    f'There is a new version of RF Library available. Would you like to download v{latest}?')):
                    webbrowser.open(download_uri, new=2 , autoraise=False)
        else:
            if display:
                self._display_error(4)

    # Method to show an error message
    def _display_error(self, code):
        if code == 1:
            message = f'Could not read from preferences file {data.plist_name}'
        elif code == 2:
            message = f'Could not create preferences path {data.plistPath}'
        elif code == 3:
            message = f'Could not write preferences file {data.plist_name}'
        elif code == 4:
            message = "Could not connect to update server."
        else:
            message = "Undefined"
        tkmessagebox.showerror("RF Library Error", message)

################################################################################
##########                         START GUI                          ##########
################################################################################

if __name__ == '__main__':
    gui = GUI(errors=errors)
    gui.window.mainloop()
