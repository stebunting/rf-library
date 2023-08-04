# Standard library imports
import os
import sys
import xml.etree.ElementTree
import webbrowser

# Tkinter GUI imports
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfiledialog
import tkinter.font as tkfont
import tkinter.messagebox as tkmessagebox

# Third party imports
from PIL import Image, ImageTk
import requests

# Matplotlib graph plotting imports
import matplotlib
import matplotlib.figure

# Program data and module imports
import data
from output import Output
import output
from log import Log
import log
from writer import Writer
from tooltip import CreateToolTip
from settings_window import SettingsWindow
from helpers import dir_format
import settings
from chart import Chart
from file import InvalidFileError

matplotlib.use('TkAgg')

class GUI:
    # Initialise class
    def __init__(self):
        # Variables
        self.output = Output(
            venue=settings.plist['defaultVenue'],
            town=settings.plist['defaultTown'],
            country=settings.plist['defaultCountry'],
            date_format=settings.plist['default_date_format'],
            forename=settings.plist['forename'],
            surname=settings.plist['surname'],
            file_structure=settings.plist['file_structure'],
            copy_source_files=settings.plist['defaultCopy'],
            delete_source_files=settings.plist['defaultDelete'],
            default_library_location=settings.plist['default_library_location'],
            dir_structure=settings.plist['dir_structure'],
            low_freq_limit=settings.plist['low_freq_limit'],
            high_freq_limit=settings.plist['high_freq_limit'])

        self.log = Log(settings.plist['logFolder'])

        self.writer = Writer()

        self.file_listbox_selection = None
        self.settings_window_open = False

        # Create instance
        self.window = tk.Tk()

        # Configure main window
        self.window.resizable(width=False, height=False)
        self.window.title(data.TITLE)
        self.window.config(background='lightGrey')
        self.window.tk.call(
            'wm',
            'iconphoto',
            self.window._w,
            ImageTk.PhotoImage(Image.open(os.path.join(data.ICON_LOCATION, 'logo.ico'))))

        # Build window
        self._create_styles()
        self._create_frames()
        self._create_menu()
        self._init_tk_vars()
        self._create_input_frame()
        self._create_info_frame()
        self._create_output_frame()

        for error in settings.errors_to_display:
            self._display_error(error)

        # Open settings if settings uninitialised
        if not settings.SETTINGS_EXISTS:
            self._settings()

        if settings.plist['auto_update_check']:
            self._check_for_updates(display=False)

    def start(self):
        self.window.mainloop()

    # Create styles for GUI
    def _create_styles(self):
        if data.SYSTEM == 'Mac':
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

        self.chart = Chart(self.preview_frame)

    # Create GUI menu
    def _create_menu(self):
        self.menu_bar = tk.Menu(self.window)

        # Application Menu (OS X only)
        if data.SYSTEM == 'Mac':
            self.app_menu = self._create_app_menu()
            self.menu_bar.add_cascade(menu=self.app_menu)

            # Configure OS X Built-in menu options
            self.window.createcommand('::tk::mac::ShowPreferences', self._settings)
            self.window.createcommand('::tk::mac::ShowHelp', self._open_http)

        self.file_menu = self._create_file_menu()
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)

        self.edit_menu = self._create_edit_menu()
        self.menu_bar.add_cascade(label='Edit', menu=self.edit_menu)

        # Window Menu (OS X Only)
        if data.SYSTEM == 'Mac':
            self.window_menu = tk.Menu(self.menu_bar, name='window')
            self.menu_bar.add_cascade(menu=self.window_menu, label='Window')

        # Tools Menu (Windows Only)
        elif data.SYSTEM == 'Windows':
            self.tools_menu = self._create_tools_menu()
            self.menu_bar.add_cascade(label='Tools', menu=self.tools_menu)

        self.help_menu = self._create_help_menu()
        self.menu_bar.add_cascade(label='Help', menu=self.help_menu)
        self.window.config(menu=self.menu_bar)

        # Bindings for Mac/Windows
        self.window.bind_all(f'<{data.COMMAND}{data.MODIFIER}a>', self._add_files)

        # Bindings for Windows only
        if data.SYSTEM == 'Windows':
            self.window.bind_all(f'<{data.COMMAND}{data.MODIFIER}A>', self._add_files)
            self.window.bind_all(f'<{data.COMMAND}{data.ALT}a>', self._add_directory)
            self.window.bind_all(f'<{data.COMMAND}{data.ALT}A>', self._add_directory)
            self.window.bind_all(f'<{data.COMMAND}{data.MODIFIER}d>', self._custom_destination)
            self.window.bind_all(f'<{data.COMMAND}{data.MODIFIER}D>', self._custom_destination)
            self.window.bind_all(f'<{data.COMMAND}q>', self._quit)
            self.window.bind_all(f'<{data.COMMAND}Q>', self._quit)
            self.window.bind_all(f'<{data.COMMAND}BackSpace>', self._clear_files)

    def _create_file_menu(self):
        menu = tk.Menu(self.menu_bar, tearoff=False)
        menu.add_command(
            label='Add Files...',
            accelerator=f'{data.COMMAND_ABBR}{data.MODIFIER_ABBR}A',
            command=self._add_files)
        menu.add_command(
            label='Add Directory...',
            accelerator=f'{data.COMMAND_ABBR}{data.ALT_ABBR}A',
            command=self._add_directory)
        menu.add_separator()
        menu.add_command(
            label='Set Date',
            accelerator=f'{data.COMMAND_ABBR}D',
            command=self._use_date)
        menu.add_command(
            label='Set Destination...',
            accelerator=f'{data.COMMAND_ABBR}{data.MODIFIER_ABBR}D',
            command=self._custom_destination)
        menu.add_command(
            label='Create File',
            accelerator=f'{data.COMMAND_ABBR}Return',
            command=self._create_file)

        if data.SYSTEM == 'Windows':
            menu.add_separator()
            menu.add_command(
                label='Exit',
                accelerator=f'{data.COMMAND_ABBR}Q',
                command=self._quit)
        return menu

    def _create_edit_menu(self):
        menu = tk.Menu(self.menu_bar, tearoff=False)
        menu.add_command(
            label='Copy',
            accelerator=f'{data.COMMAND_ABBR}C',
            command=lambda: self.window.focus_get().event_generate("<<Copy>>"))
        menu.add_command(
            label='Cut',
            accelerator=f'{data.COMMAND_ABBR}X',
            command=lambda: self.window.focus_get().event_generate("<<Cut>>"))
        menu.add_command(
            label='Paste',
            accelerator=f'{data.COMMAND_ABBR}V',
            command=lambda: self.window.focus_get().event_generate("<<Paste>>"))
        menu.add_command(
            label='Select All',
            accelerator=f'{data.COMMAND_ABBR}A',
            command=lambda: self.window.focus_get().event_generate("<<SelectAll>>"))
        menu.add_separator()
        menu.add_command(
            label='Remove File',
            accelerator='BackSpace',
            command=self._remove_file)
        menu.add_command(
            label='Clear Files',
            accelerator=f'{data.COMMAND_ABBR}BackSpace',
            command=self._clear_files)
        return menu

    def _create_help_menu(self):
        menu = tk.Menu(self.menu_bar, tearoff=False, name='help')

        if data.SYSTEM == 'Windows':
            menu.add_command(
                label='Documentation',
                command=self._open_http)
            menu.add_separator()
            menu.add_command(
                label='Check for Updates...',
                command=self._check_for_updates)
            menu.add_command(
                label='About RF Library',
                command=self._about)
        return menu

    def _create_app_menu(self):
        menu = tk.Menu(self.menu_bar, tearoff=False, name='apple')
        menu.add_command(
            label='About RF Library',
            command=self._about)
        menu.add_command(
            label='Check for Updates...',
            command=self._check_for_updates)
        menu.add_separator()
        return menu

    def _create_tools_menu(self):
        menu = tk.Menu(self.menu_bar, tearoff=False)
        menu.add_command(
            label='Preferences...',
            command=self._settings)
        return menu

    def _init_tk_vars(self):
        # Initialise tkinter variables
        self.num_files = tk.StringVar()
        self.venue = tk.StringVar(value=self.output.venue)
        self.town = tk.StringVar(value=self.output.town)
        self.country = tk.StringVar(value=self.output.country)
        self.scan_date = tk.StringVar()
        self.in_out = tk.StringVar(value=self.output.in_out)
        self.scan_output_location_display = tk.StringVar()
        self.target_subdirectory = tk.StringVar(value=self.output.target_subdirectory)
        self.scan_master_filename = tk.StringVar(value=self.output.scan_master_filename)
        self.copy_source_files = tk.BooleanVar(value=self.output.copy_source_files)
        self.delete_source_files = tk.BooleanVar(value=self.output.delete_source_files)

        # Set tracers to update output object
        self.venue.trace('w', lambda *_: self.output.set_venue(self.venue.get()))
        self.town.trace('w', lambda *_: self.output.set_town(self.town.get()))
        self.country.trace('w', lambda *_: self.output.set_country(self.country.get()))
        self.in_out.trace('w', lambda *_: self.output.set_in_out(self.in_out.get()))
        self.target_subdirectory.trace('w',
            lambda *_: setattr(self.output, 'target_subdirectory', self.target_subdirectory.get()))
        self.copy_source_files.trace('w',
            lambda *_: setattr(self.output, 'copy_source_files', self.copy_source_files.get()))
        self.delete_source_files.trace('w',
            lambda *_: setattr(self.output, 'delete_source_files', self.delete_source_files.get()))

    # Create GUI widgets
    def _create_input_frame(self):
        ttk.Label(self.input_frame, text='File List').grid(column=0, row=0, sticky='W')
        self.file_listbox = tk.Listbox(self.input_frame, height=8, width=20)
        self.file_listbox.bind('<<ListboxSelect>>', self._select_file_item)
        self.file_listbox.grid(column=0, row=1, padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)

        ttk.Label(
            self.input_frame,
            text='Selected File Information'
        ).grid(column=1, row=0, sticky='W')
        self.data_listbox = tk.Listbox(self.input_frame, height=8, width=30)
        self.data_listbox.grid(column=1, row=1, padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        self.data_listbox.configure(background='lightGrey')

        # File List Edit Buttons
        self.file_list_edit_frame = ttk.Frame(self.input_frame)
        self.file_list_edit_frame.grid(column=0, row=2, columnspan=2, sticky='E')

        self.use_date_button = self._make_ip_button(
            'calendar_enabled.png',
            f'Use currently selected file\'s creation date for scan date ({data.COMMAND_SYMBOL}D)',
            self._use_date,
            4)
        self.clear_files_button = self._make_ip_button(
            'bin_enabled.png',
            f'Remove all files from file list ({data.COMMAND_SYMBOL}\u232b)',
            self._clear_files,
            3)
        self.remove_file_button = self._make_ip_button(
            'minus_enabled.png',
            'Remove selected file from file list (\u232b)',
            self._remove_file,
            2)
        self.add_directory_button = self._make_ip_button(
            'folder.png',
            f'Add directory to file list ({data.COMMAND_SYMBOL}{data.ALT_SYMBOL}A)',
            self._add_directory,
            1)
        self.add_files_button = self._make_ip_button(
            'plus.png',
            f'Add files to file list ({data.COMMAND_SYMBOL}{data.MODIFIER_SYMBOL}A)',
            self._add_files,
            0)

        self.file_status = ttk.Label(self.input_frame, textvariable=self.num_files)
        self.file_status.grid(
            column=0,
            row=2,
            sticky='W',
            padx=data.PAD_X_DEFAULT,
            pady=data.PAD_Y_DEFAULT)

        self.file_listbox.bind('<Escape>', self._deselect_file_listbox)
        self.file_listbox.bind('<BackSpace>', self._remove_file)

    def _create_info_frame(self):
        self.venue_entry = self._make_entry_box('Venue', 'Scan location name', self.venue, 0)
        self.town_entry = self._make_entry_box('Town', 'Scan location town/city', self.town, 1)
        self.country_box = self._make_combobox('Country', 'Scan location country', self.country, 2)
        self.country_box['values'] = output.country_list
        self.country_box.bind('<<ComboboxSelected>>', self._refresh)
        self.date_entry = self._make_entry_box('Scan Date', 'Date scan was taken', self.scan_date, 3)
        self.date_entry.config(state='readonly')
        self.io_box = self._make_combobox('Inside/Outside', 'Was the scan taken inside or outside?', self.in_out, 4)
        self.io_box['values'] = output.io_list
        self.io_box.bind('<<ComboboxSelected>>', self._io_box_edit)

    def _create_output_frame(self):
        reset_image = ImageTk.PhotoImage(Image.open(os.path.join(data.ICON_LOCATION, 'reset.png')))
        ttk.Label(
            self.output_frame,
            text='Destination',
            width=self.left_indent
        ).grid(column=0, row=0, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
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

        ttk.Label(
            self.output_frame,
            text='Subdirectory',
            width=self.left_indent
        ).grid(column=0, row=1, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
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
            pady=data.PAD_Y_DEFAULT)
        self.target_subdirectory_entry.bind('<KeyRelease>', self._custom_subdirectory)
        CreateToolTip(self.target_subdirectory_entry, 'Optional subdirectory')

        ttk.Label(
            self.output_frame,
            text='Master Filename',
            width=self.left_indent
        ).grid(column=0, row=2, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        self.default_master_filename_reset = ttk.Button(
            self.output_frame,
            image=reset_image,
            command=self._set_master_filename)
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
            padx=data.PAD_X_DEFAULT,
            pady=data.PAD_Y_DEFAULT)
        self.scan_master_filename_entry.config(width=60)
        self.scan_master_filename_entry.bind('<KeyRelease>', self.output.set_custom_master_filename)
        CreateToolTip(self.scan_master_filename_entry, 'Master output filename')

        self._make_checkbox('Duplicate Source Files', 'Duplicate source files in library', self.copy_source_files, 3)
        self._make_checkbox('Delete Source Files', 'Delete source files on file creation', self.delete_source_files, 4)

        self.output_buttons = ttk.Frame(self.output_frame)
        self.output_buttons.grid(column=2, row=5, sticky='W')

        self._make_op_button('Create File', f'Create master file ({data.COMMAND_SYMBOL}\u23ce)', self._create_file, 0)
        self._make_op_button(
            'Set Destination',
            f'Set custom destination for output files ({data.COMMAND_SYMBOL}{data.MODIFIER_SYMBOL}D)',
            self._custom_destination,
            1)

        self.window.bind_all(f'<{data.COMMAND}Return>', self._create_file)

        # Initialise Lists
        self._print_files()

    def _make_ip_button(self, icon, description, cmd, col):
        img = ImageTk.PhotoImage(Image.open(os.path.join(data.ICON_LOCATION, icon)))
        button = ttk.Button(self.file_list_edit_frame, image=img, command=cmd)
        button.grid(
            column=col,
            row=0,
            sticky='E',
            padx=data.PAD_X_DEFAULT,
            pady=data.PAD_Y_DEFAULT)
        button.image = img
        CreateToolTip(button, description)
        return button

    def _make_entry_box(self, label, description, var, row):
        ttk.Label(
            self.info_frame,
            text=label,
            width=self.left_indent
        ).grid(column=0, row=row, sticky='NW', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        box = ttk.Entry(
            self.info_frame,
            textvariable=var,
            width=20,
            font=f'TkDefaultFont {self.font_size}')
        box.grid(column=1, row=row, sticky='NW', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        CreateToolTip(box, description)
        box.bind('<KeyRelease>', self._set_master_filename)
        return box

    def _make_combobox(self, label, description, var, row):
        ttk.Label(
            self.info_frame,
            text=label,
            width=self.left_indent
        ).grid(column=0, row=row, sticky='NW', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        box = ttk.Combobox(
            self.info_frame,
            textvariable=var,
            width=20,
            state='readonly',
            font=f'TkDefaultFont {self.font_size}')
        box.grid(column=1, row=row, sticky='NW', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        CreateToolTip(box, description)
        box.bind('<KeyRelease>', self._set_master_filename)
        return box

    def _make_checkbox(self, label, description, var, row):
        box = ttk.Checkbutton(self.output_frame, variable=var)
        box.grid(column=1, row=row, sticky='E', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        ttk.Label(self.output_frame, text=label).grid(column=2, row=row, sticky='W')
        CreateToolTip(box, description)

    def _make_op_button(self, label, description, cmd, col):
        button = ttk.Button(self.output_buttons, text=label, command=cmd)
        button.grid(column=col, row=0, sticky='W', padx=data.PAD_X_DEFAULT, pady=data.PAD_Y_DEFAULT)
        CreateToolTip(button, description)
        return button

    # Method to update filelist
    def _print_files(self, event=None):
        self.file_listbox.delete(0, tk.END)
        for file in self.output.files:
            self.file_listbox.insert(tk.END, file.filename)
        self.scan_date.set(self.output.formatted_date())
        self._select_file_item(event)
        self._update_file_status()
        self._set_master_filename()

    # Method to select file_listbox item
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
            self.chart.clear()
        else:
            selected_file = self.output.files[self.file_listbox_selection]
            self.data_listbox.insert(tk.END, f'Filename: {selected_file.filename}')
            self.data_listbox.insert(tk.END, f'Date: {selected_file.date_format(self.output.date_format)}')
            self.data_listbox.insert(tk.END, f'Scanner: {selected_file.model}')
            start_tv = '' if selected_file.start_tv_channel is None else f' (TV{selected_file.start_tv_channel})'
            self.data_listbox.insert(tk.END, f'Start Frequency: {selected_file.start_frequency_format()}{start_tv}')
            stop_tv = '' if selected_file.stop_tv_channel is None else f' (TV{selected_file.stop_tv_channel})'
            self.data_listbox.insert(tk.END, f'Stop Frequency: {selected_file.stop_frequency_format()}{stop_tv}')
            self.data_listbox.insert(tk.END, f'Data Points: {selected_file.data_points}')
            self.data_listbox.insert(tk.END, f'Mean Resolution: {selected_file.resolution_format()}')
            self.data_listbox.insert(tk.END, f'New Filename: {selected_file.new_filename}')
            self.chart.update(selected_file, self.output.country)
        self._button_disable()

    # Method to decide if buttons should be disabled or not
    def _button_disable(self):
        if self.output.num_files() == 0:
            self._button_status('disabled', 'disabled')
        elif self.file_listbox_selection is None:
            self._button_status('disabled', 'enabled')
        else:
            self._button_status('enabled', 'enabled')

    # Method to print number of files chosen
    def _update_file_status(self):
        plural = '' if self.output.num_files() == 1 else 's'
        self.file_status.configure(foreground='red' if self.output.num_files() == 0 else 'black')
        self.num_files.set(f'{self.output.num_files()} file{plural} added')

    # Method to create master filename
    def _set_master_filename(self, _=None):
        self.scan_master_filename.set(self.output.scan_master_filename)
        self.scan_output_location_display.set(dir_format(self.output.scan_output_location, 90))

    # Method to disable/enable buttons/menu items based on selected files
    def _button_status(self, input_status=None, output_status=None):
        if input_status is not None:
            for btn in [(self.remove_file_button, 'minus'), (self.use_date_button, 'calendar')]:
                img = ImageTk.PhotoImage(Image.open(
                    os.path.join(data.ICON_LOCATION, f'{btn[1]}_{input_status}.png')))
                btn[0].config(state=input_status, image=img)
                btn[0].image = img
            if input_status == 'enabled':
                input_status = 'normal'
            for (menu, item) in [(self.edit_menu, 'Remove File'), (self.file_menu, 'Set Date')]:
                menu.entryconfig(item, state=input_status)

        if output_status is not None:
            img = ImageTk.PhotoImage(Image.open(
                os.path.join(data.ICON_LOCATION, f'bin_{output_status}.png')))
            self.clear_files_button.config(state=output_status, image=img)
            self.clear_files_button.image = img
            if output_status == 'enabled':
                self.window.bind_all(f'<{data.COMMAND}d>', self._use_date)
                self.window.bind_all(f'<{data.COMMAND}D>', self._use_date)
                self.edit_menu.entryconfig('Clear Files', state='normal')
                self.file_menu.entryconfig('Create File', state='normal')
            else:
                self.window.unbind_all(f'<{data.COMMAND}d>')
                self.window.unbind_all(f'<{data.COMMAND}D>')
                self.edit_menu.entryconfig('Clear Files', state='disabled')
                self.file_menu.entryconfig('Create File', state='disabled')

    # Method to change destination to custom destination
    def _custom_destination(self):
        custom_location = tkfiledialog.askdirectory(
            parent=self.master_frame,
            title='Select Destination Folder')
        if custom_location != '':
            self.output.set_custom_destination(custom_location)
            self.scan_output_location_display.set(dir_format(self.output.scan_output_location, 90))
            self.target_subdirectory.set(self.output.target_subdirectory)
            self._set_master_filename()

    # Method to refresh file data, for use when country or settings change
    def _refresh(self, _=None):
        self.output.set_date_format(settings.plist['default_date_format'])
        log.folder = settings.plist['logFolder']
        for file in self.output.files:
            file.update_tv_channels(self.output.country)
        self._print_files()

    # Method to deselect file_listbox
    def _deselect_file_listbox(self):
        self.file_listbox_selection = None
        self.file_listbox.selection_clear(0, tk.END)
        self._select_file_item()

    # Method called after IO_box edited
    def _io_box_edit(self, _=None):
        self.output.io_fixed = True
        if not self.output.custom_subdirectory:
            self._update_subdirectory()

    # Method called after subdirectory edited
    def _custom_subdirectory(self, _=None):
        self.output.set_custom_subdirectory()
        self._set_master_filename()

    # Method to update output location to standard location
    def _reset_output_location(self):
        self.target_subdirectory.set(self.output.reset_output_location())
        self._set_master_filename()

    # Method to update subdirectory name when standard destination called
    def _update_subdirectory(self):
        self.target_subdirectory.set(self.output.target_subdirectory)
        self._set_master_filename()

    # Method to update io_box and Subdirectory when Inside v Outside changes
    def _set_io(self):
        if not self.output.io_fixed:
            self.io_box.current(0 if self.output.io_guess >= 0 else 1)
            self._update_subdirectory()

    # Method to open file dialogue and allow selection of files
    def _add_files(self, selected_files=None, suppress_errors=False):
        if selected_files is None:
            selected_files = tkfiledialog.askopenfilenames(
                parent=self.input_frame,
                title='Add files',
                initialdir=settings.plist['defaultSourceLocation'])
        for file in selected_files:
            try:
                self.output.add_file(file, self.output.country)
                settings.plist['defaultSourceLocation'] = os.path.dirname(file)
            except InvalidFileError:
                if not suppress_errors:
                    tkmessagebox.showwarning(
                        'Invalid File',
                        f'{file} is not a valid scan file and will not be added to the file list')
        self._set_io()
        self._print_files()

    # Method to open file dialogue and allow selection of all files in a directory
    def _add_directory(self):
        dir_files = []
        selected_dir = tkfiledialog.askdirectory(
            parent=self.input_frame, title='Add directory',
            initialdir=settings.plist['defaultSourceLocation'])
        if selected_dir != '':
            settings.plist['defaultSourceLocation'] = selected_dir
            for file in os.listdir(selected_dir):
                fullfilename = os.path.join(selected_dir, file)
                if not file.startswith('.') and not os.path.isdir(fullfilename):
                    dir_files.append(fullfilename)
        if len(dir_files) != 0:
            self._add_files(dir_files, True)

    # Method to remove file
    def _remove_file(self, event=None):
        if event is None or (event.widget.winfo_class() != 'TEntry' and event.widget.winfo_class() != 'TCombobox'):
            if self.file_listbox_selection is None:
                return
            self.output.remove_file(self.output.files[self.file_listbox_selection])
            self._set_io()
            if self.output.num_files() == 0:
                self.file_listbox_selection = None
            elif self.file_listbox_selection > len(self.output.files) - 1:
                self.file_listbox_selection = len(self.output.files) - 1
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
        self.output.clear_files()
        self.file_listbox_selection = None
        self._print_files()

    # Method to use date from selected file
    def _use_date(self):
        self.scan_date.set(self.output.use_date(self.file_listbox_selection))
        self._set_master_filename()

    # Method to create master file
    def _create_file(self):
        if self.output.num_files() == 0:
            tkmessagebox.showinfo('No Files To Create', 'No files to create.')
            return

        # Check if user really wants to delete source files
        del_source_confirmed = bool(
            self.output.delete_source_files is True and tkmessagebox.askyesno(
            'Are you sure?',
            'Are you sure you want to delete the input files?'))

        # Add all files into output_file list if within limits
        files_written = 0
        statement = ('The following files were successfully written!\n\n'
                     f'DIRECTORY:\n{self.output.scan_output_location}\n\n')
        output_file = self.output.write_output_file()

        # Write original files with new filenames
        if self._create_directory():
            if self.output.copy_source_files:
                for file in self.output.files:
                    written_filename = self._write_file(
                        self.output.scan_output_location,
                        file.new_filename,
                        file.get_output_file())
                    if not written_filename:
                        return False
                    files_written += 1
                    statement += f'{written_filename}\n'

            # Write master file
            if len(output_file) > 0:
                written_filename = self._write_file(
                    self.output.scan_output_location,
                    self.output.scan_master_filename,
                    output_file)
                if not written_filename:
                    return False
                files_written += 1
                statement += f'{written_filename}\n'

            # Write WSM file
            wsm_file = self.output.write_wsm_file(data.TITLE)
            if (data.MAKE_WSM and len(wsm_file) > 0):
                written_filename = self._write_file(
                    self.output.scan_output_location,
                    self.output.scan_master_filename,
                    wsm_file)
                if not written_filename:
                    return False
                files_written += 1
                statement += f'{written_filename}\n'

            statement += f'\n{files_written} files written to disk.\n'

            if files_written == 0:
                tkmessagebox.showinfo('No Files To Create', 'No files to create.')
                return

            # Write defaults to plist
            try:
                settings.set_new_defaults(
                    self.output.venue,
                    self.output.town,
                    self.output.country,
                    self.output.copy_source_files,
                    self.output.delete_source_files)
            except PermissionError:
                self._display_error(1)

            if settings.plist['create_log']:
                if self.log.write(self.output):
                    statement += 'Log file updated.\n'
                else:
                    statement += f'WARNING: Log could not be updated at {settings.plist["logFolder"]}\n'

            if del_source_confirmed:
                statement += '\nThe following files were deleted:\n'
                for file in self.output.files:
                    os.remove(file.fullfilename)
                    statement += f'{file.filename}\n'
                self._clear_files(False)
                tkmessagebox.showinfo('Success!', statement)
            else:
                if tkmessagebox.askyesno(
                    'Success!',
                    f'{statement}\nWould you like to clear the file list?'):
                    self._clear_files(False)

    # Method to write file to disk
    def _write_file(self, directory, filename, string):
        filename = self.writer.get_filename(directory, filename)
        value = self.writer.write_file(filename, string)
        if value is False:
            tkmessagebox.showwarning('Fail!', f'{filename} could not be written.')
        return value

    # Method to create directory structure
    def _create_directory(self):
        location = self.output.scan_output_location
        try:
            self.writer.create_directory(location)
            return True
        except OSError:
            return tkmessagebox.askyesno('Directory already exists', f'{location} already exists. Are you sure?')

    # Method to quit application
    def _quit(self):
        self.window.quit()
        self.window.destroy()
        sys.exit()

    # Method to display about information
    def _about(self):
        tkmessagebox.showinfo(
            'About',
            f'{data.TITLE} v{data.VERSION}\n\n{chr(169)} Stephen Bunting 2023\n{data.WEBSITE_URI}')

    # Method to open docs in web browser
    def _open_http(self):
        webbrowser.open(f'{data.WEBSITE_URI}documentation.php', new=2, autoraise=True)

    # Method to display settings box
    def _settings(self):
        if not self.settings_window_open:
            self.settings_window_open = True
            self.settings = SettingsWindow()
            self.settings.start()
            self.settings_window_open = False
            self._refresh()
        else:
            self.settings.bringtofront()

    # Check for latest version of software
    def _check_for_updates(self, **kwargs):
        display = kwargs['display'] if kwargs.get('display') is not None else True

        try:
            req = requests.get(data.UPDATE_FILE_LOCATION, timeout=3)
            update_connection = True
        except requests.exceptions.ConnectionError:
            update_connection = False

        if update_connection:
            root = xml.etree.ElementTree.fromstring(req.text)
            latest = root[0][0].text
            download_uri = root[0][2].text
            if latest == data.VERSION:
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
            message = f'Could not read from preferences file {data.PLIST_NAME}'
        elif code == 2:
            message = f'Could not create preferences path {data.PLIST_PATH}'
        elif code == 3:
            message = f'Could not write preferences file {data.PLIST_NAME}'
        elif code == 4:
            message = "Could not connect to update server."
        else:
            message = "Undefined"
        tkmessagebox.showerror("RF Library Error", message)
