#!/usr/bin/env python3

# Import Python Modules
import platform
import os
import sys
import datetime
import xml.etree.ElementTree
import plistlib
import webbrowser
import requests
import csv

# Import Tkinter GUI functions
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import tkinter.messagebox as tkmessagebox
import tkinter.filedialog as tkfiledialog
from PIL import Image, ImageTk

# Import Matplotlib graph plotting functions
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import program data and modules
import config
import scanfile
import output
import tooltip
import ofcom

# Helper function to set date_format
def set_date_format():
    if config.date_formats.get(settings.plist['defaultDateFormat']):
        return config.date_formats.get(settings.plist['defaultDateFormat'])
    else:
        return config.date_formats.get(defaultDateFormat)
        
# Helper function to format directory nicely
def dir_format(display_location, max_length):
    display_location = display_location.replace(os.path.expanduser('~'), '~', 1)
    while len(display_location) > max_length:
        display_location = os.path.join('...', os.path.normpath(display_location.split(os.sep, 2)[2]))
    return display_location

# Load Settings
settings = config.Settings()

# Set Date Format
date_format = set_date_format()

################################################################################
##########                  SETTINGS WINDOW OBJECT                    ##########
################################################################################

class SettingsWindow():

    # Initialise class
    def __init__(self):

        # Variables
        self.password_changed = False
        self.moveOldLog = False

        self.settingsWindow = tk.Toplevel(takefocus=True)
        
        self.settingsWindow.title('Settings')
        self.settingsWindow.resizable(width=False, height=False)
        
        self._createSettingsFrames()
        self._createSettingsWidgets()
    
    # Create settings frames
    def _createSettingsFrames(self):
        self.settingsMasterFrame = ttk.Frame(self.settingsWindow)
        self.settingsMasterFrame.grid(padx=0, pady=0, sticky='NWSE')
        
        self.outputPreferences = ttk.LabelFrame(
            self.settingsMasterFrame, text='Output Preferences')
        self.outputPreferences.grid(padx=16, pady=16, sticky='NWSE')

        self.loggingPreferences = ttk.LabelFrame(
            self.settingsMasterFrame, text='Logging')
        self.loggingPreferences.grid(padx=16, pady=16, sticky='NWSE')
        
        self.personalData = ttk.LabelFrame(
            self.settingsMasterFrame, text='Personal Data')
        self.personalData.grid(padx=16, pady=16, sticky='NWSE')
        
        self.appData = ttk.LabelFrame(
            self.settingsMasterFrame, text='Application Data')
        self.appData.grid(padx=16, pady=16, sticky='NWSE')
        
        if config.show_ofcom:
            self.ofcomLogin = ttk.LabelFrame(
                self.settingsMasterFrame, text='OFCOM Login Data')
            self.ofcomLogin.grid(padx=16, pady=16, sticky='NWSE')
        
        self.settingsButtonsFrame = ttk.Frame(self.settingsMasterFrame)
        self.settingsButtonsFrame.grid(
            padx=16, pady=16, columnspan=2, sticky='NWSE')
    
    # Create settings widgets
    def _createSettingsWidgets(self):
    
        # Initialise Tk variables
        self.scansFolderDisplay = tk.StringVar()
        self.dirStructure = tk.StringVar()
        self.fileStructure = tk.StringVar()
        self.lowFreqLimit = tk.StringVar()
        self.highFreqLimit = tk.StringVar()
        self.defaultDateFormat = tk.StringVar()
        self.createLog = tk.BooleanVar()
        self.logFolderDisplay = tk.StringVar()
        self.forename = tk.StringVar()
        self.surname = tk.StringVar()
        self.autoUpdateCheck = tk.BooleanVar()
        self.ofcomAccountName = tk.StringVar()
        self.ofcomUserName = tk.StringVar()
        self.ofcomPassword = tk.StringVar()

        # Set Variables
        vars = [settings.plist['dirStructure'], settings.plist['fileStructure'],
                dir_format(settings.plist['defaultLibraryLocation'], 50),
                settings.plist['lowFreqLimit'], settings.plist['highFreqLimit'],
                settings.plist['createLog'], dir_format(settings.plist['logFolder'], 50),
                settings.plist['defaultDateFormat'], settings.plist['forename'], settings.plist['surname'],
                settings.plist['ofcomAccountName'], settings.plist['ofcomUserName'], ' ' * 8,
                settings.plist['autoUpdateCheck']]
        fields = [self.dirStructure, self.fileStructure,
                  self.scansFolderDisplay, self.lowFreqLimit, self.highFreqLimit,
                  self.createLog, self.logFolderDisplay,
                  self.defaultDateFormat, self.forename, self.surname,
                  self.ofcomAccountName, self.ofcomUserName, self.ofcomPassword,
                  self.autoUpdateCheck]
        for field, var in zip(fields, vars):
            field.set(var)
        self.defaultLibraryLocation = settings.plist['defaultLibraryLocation']
        self.logFolder = settings.plist['logFolder']
        
        # Scans Folder
        ttk.Label(self.outputPreferences, text='Scans Folder', width='16').grid(column=0, row=0, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.scansFolderLabel = ttk.Label(self.outputPreferences, textvariable=self.scansFolderDisplay, width='36')
        self.scansFolderLabel.grid(column=1, row=0, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        tooltip.CreateToolTip(self.scansFolderLabel, 'Scan library base folder')
        self.changeBaseFolderButton = ttk.Button(self.outputPreferences, text='Change Folder', command=self._changeBaseFolder)
        self.changeBaseFolderButton.grid(column=1, row=1)
        
        # Directory Structure
        ttk.Label(self.outputPreferences, text='Directory Structure', width='16').grid(column=0, row=2, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.dirStructureEntry = ttk.Entry(self.outputPreferences, textvariable=self.dirStructure, width='35')
        self.dirStructureEntry.grid(column=1, row=2, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        tooltip.CreateToolTip(self.dirStructureEntry, 'Default library directory structure (see docs for more details')
        
        # Filename Structure
        ttk.Label(self.outputPreferences, text='Filename Structure', width='16').grid(column=0, row=3, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.fileStructureEntry = ttk.Entry(self.outputPreferences, textvariable=self.fileStructure, width='35')
        self.fileStructureEntry.grid(column=1, row=3, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        tooltip.CreateToolTip(self.fileStructureEntry, 'Default library filename structure (see docs for more details')
        
        # Date Format
        ttk.Label(self.outputPreferences, text='Date Format', width='16').grid(column=0, row=4, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.dateFormatBox = ttk.Combobox(self.outputPreferences, textvariable=self.defaultDateFormat)
        self.dateFormatBox['values'] = [key for key in config.date_formats]
        self.dateFormatBox.grid(column=1, row=4, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        tooltip.CreateToolTip(self.dateFormatBox, 'Preferred date format')
        
        # Low Frequency Limit
        ttk.Label(self.outputPreferences, text='Low Frequency Limit', width='16').grid(column=0, row=5, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.lowFreqLimitEntry = ttk.Entry(self.outputPreferences, textvariable=self.lowFreqLimit)
        self.lowFreqLimitEntry.grid(column=1, row=5)
        tooltip.CreateToolTip(self.lowFreqLimitEntry, 'Low frequency limit for the output file (set to 0 for no limit)')
        
        # High Frequency Limit
        ttk.Label(self.outputPreferences, text='High Frequency Limit', width='16').grid(column=0, row=6, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.highFreqLimitEntry = ttk.Entry(self.outputPreferences, textvariable=self.highFreqLimit)
        self.highFreqLimitEntry.grid(column=1, row=6)
        tooltip.CreateToolTip(self.highFreqLimitEntry, 'High frequency limit for the output file (set to 0 for no limit)')

        # Create Log
        ttk.Label(self.loggingPreferences, text='Write To Log File', width='16').grid(column=0, row=0, sticky='w', padx=config.PAD_X, pady=config.PAD_Y)
        self.createLogCheck = ttk.Checkbutton(self.loggingPreferences, variable=self.createLog)
        self.createLogCheck.grid(column=1, row=0, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        tooltip.CreateToolTip(self.createLogCheck, 'Turn log file writing on/off')

        # Log Location
        ttk.Label(self.loggingPreferences, text='Log Location', width='16').grid(column=0, row=1, sticky='w', padx=config.PAD_X, pady=config.PAD_Y)
        self.logLocationEntry = ttk.Label(self.loggingPreferences, textvariable=self.logFolderDisplay, width='36')
        self.logLocationEntry.grid(column=1, row=1, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        tooltip.CreateToolTip(self.logLocationEntry, 'Log file location')
        self.changeLogLocation = ttk.Button(self.loggingPreferences, text='Change Folder', command=self._changeLogFolder)
        self.changeLogLocation.grid(column=1, row=2, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        
        # Forename Entry
        ttk.Label(self.personalData, text='Forename', width='16').grid(column=0, row=0, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.forenameEntry = ttk.Entry(self.personalData, textvariable=self.forename)
        self.forenameEntry.grid(column=1, row=0)
        tooltip.CreateToolTip(self.forenameEntry, 'Your forename')
        
        # Surname Entry
        ttk.Label(self.personalData, text='Surname', width='16').grid(column=0, row=1, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.surnameEntry = ttk.Entry(self.personalData, textvariable=self.surname)
        self.surnameEntry.grid(column=1, row=1)
        tooltip.CreateToolTip(self.surnameEntry, 'Your surname')

        # Check for Updates
        ttk.Label(self.appData, text='Auto Update Check', width='16').grid(column=0, row=0, sticky='w', padx=config.PAD_X, pady=config.PAD_Y)
        self.checkForUpdatesCheck = ttk.Checkbutton(self.appData, variable=self.autoUpdateCheck)
        self.checkForUpdatesCheck.grid(column=1, row=0, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        tooltip.CreateToolTip(self.checkForUpdatesCheck, 'Automatically check for updates on startup')
        
        if config.show_ofcom:

            # OFCOM Account Name Entry
            ttk.Label(self.ofcomLogin, text='Account Name', width='16').grid(column=0, row=0, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
            self.ofcomAccountNameEntry = ttk.Entry(self.ofcomLogin, textvariable=self.ofcomAccountName)
            self.ofcomAccountNameEntry.grid(column=1, row=0)
            tooltip.CreateToolTip(self.ofcomAccountNameEntry, 'Your OFCOM Account Name')
            
            # OFCOM User Name Entry
            ttk.Label(self.ofcomLogin, text='User Name', width='16').grid(column=0, row=1, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
            self.ofcomUsernameEntry = ttk.Entry(self.ofcomLogin, textvariable=self.ofcomUserName)
            self.ofcomUsernameEntry.grid(column=1, row=1)
            tooltip.CreateToolTip(self.ofcomUsernameEntry, 'Your OFCOM User Name')
            
            # OFCOM Password Entry
            ttk.Label(self.ofcomLogin, text='Password', width='16').grid(column=0, row=2, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
            self.ofcomPasswordEntry = ttk.Entry(self.ofcomLogin, show="\u2022", textvariable=self.ofcomPassword)
            self.ofcomPasswordEntry.grid(column=1, row=2)
            tooltip.CreateToolTip(self.ofcomPasswordEntry, 'Your OFCOM Password')

            self.ofcomPasswordEntry.bind('<KeyRelease>', self._passwordEntry)
        
        # Buttons
        self.saveSettingsButton = ttk.Button(self.settingsButtonsFrame, text='Save', command=self._saveSettings)
        self.saveSettingsButton.grid(column=0, row=0)
        tooltip.CreateToolTip(self.saveSettingsButton, 'Save changes')
        self.cancelSettingsButton = ttk.Button(self.settingsButtonsFrame, text='Cancel', command=self._closeSettings)
        self.cancelSettingsButton.grid(column=1, row=0)
        tooltip.CreateToolTip(self.cancelSettingsButton, 'Discard changes')
        
        # Bindings
        self.settingsWindow.bind_all('<Return>', self._saveSettings)
        self.settingsWindow.bind_all('<Escape>', self._closeSettings)
        
        # Add padding to all entry boxes
        for widget in [self.changeBaseFolderButton, self.forenameEntry, self.surnameEntry, self.lowFreqLimitEntry, self.highFreqLimitEntry, self.saveSettingsButton, self.cancelSettingsButton]:
            widget.grid(sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
    
    # Method to detect if password is amended
    def _passwordEntry(self, event=None):
        if not self.password_changed:
            self.password_changed = True
            self.ofcomPassword.set(self.ofcomPassword.get().lstrip())
            
    # Method to select scans base folder
    def _changeBaseFolder(self):
        dir = tkfiledialog.askdirectory(parent=self.settingsMasterFrame, title='Select Scan Folder', initialdir=settings.plist['defaultLibraryLocation'])
        if dir != '':
            self.defaultLibraryLocation = dir
            self.scansFolderDisplay.set(dir_format(self.defaultLibraryLocation, 50))

    # Method to select default log folder
    def _changeLogFolder(self):
        if os.path.exists(os.path.join(settings.plist['logFolder'], config.logFileName)):
            self.moveOldLog = True
            self.oldLogLocation = settings.plist['logFolder']

        dir = tkfiledialog.askdirectory(parent=self.settingsMasterFrame, title='Select Source Folder', initialdir=settings.plist['logFolder'])
        if dir != '':
            self.logFolder = dir
            self.logFolderDisplay.set(dir_format(self.logFolder, 50))
    
    # Method to save settings and close window    
    def _saveSettings(self, event=None):
        
        # Ensure limits are good ints else revert to default
        defaults = [settings.plist['lowFreqLimit'], settings.plist['highFreqLimit']]
        for var, default in zip([self.lowFreqLimit, self.highFreqLimit], defaults):
            if var.get() == '':
                var.set(0)
            else:
                try:
                    int(var.get())
                except ValueError:
                    var.set(default)
            if int(var.get()) < 0:
                var.set(0)
        if int(self.lowFreqLimit.get()) > int(self.highFreqLimit.get()):
            self.lowFreqLimit.set(self.highFreqLimit.get())
        elif int(self.highFreqLimit.get()) < int(self.lowFreqLimit.get()):
            self.highFreqLimit.set(self.lowFreqLimit.get())

        settings.plist['ofcomAccountName'] = self.ofcomAccountName.get()
        settings.plist['ofcomUserName'] = self.ofcomUserName.get()
        settings.plist['defaultLibraryLocation'] = self.defaultLibraryLocation
        settings.plist['forename'] = self.forename.get()
        settings.plist['surname'] = self.surname.get()
        settings.plist['dirStructure'] = self.dirStructure.get().strip('/')
        settings.plist['fileStructure'] = self.fileStructure.get()
        settings.plist['defaultDateFormat'] = self.defaultDateFormat.get()
        settings.plist['lowFreqLimit'] = int(self.lowFreqLimit.get())
        settings.plist['highFreqLimit'] = int(self.highFreqLimit.get())
        settings.plist['createLog'] = self.createLog.get()
        settings.plist['logFolder'] = self.logFolder
        settings.plist['autoUpdateCheck'] = self.autoUpdateCheck.get()

        # Save Settings
        settings.dump()
        if self.password_changed:
            settings.set_ofcom_password(self.ofcomAccountName.get(), self.ofcomPassword.get())

        # Move old log to new log location
        if self.moveOldLog:
            os.rename(os.path.join(self.oldLogLocation, config.logFileName),
                      os.path.join(settings.plist['logFolder'], config.logFileName))

        self._closeSettings()
    
    # Method to close settings window
    def _closeSettings(self, event=None):
        self.settingsWindow.quit()
        self.settingsWindow.destroy()
    
    # Method to bring settings window to front
    def bringtofront(self):
        self.settingsWindow.lift()
   
################################################################################
##########                         GUI OBJECT                         ##########
################################################################################

class GUI():

    # Initialise class
    def __init__(self):
 
        # Variables
        self.op = output.Output()
        
        # Create instance
        self.window = tk.Tk()
        
        # Configure main window
        self.window.resizable(width=False, height=False)
        self.window.title(config.APPLICATION_NAME)
        self.window.config(background='lightGrey')
        self.window.tk.call(
            'wm', 'iconphoto', self.window._w,
            ImageTk.PhotoImage(Image.open(os.path.join(config.ICON_LOCATION,
            'logo.ico'))))
        
        # Build window
        self._createStyles()
        self._createFrames()
        self._createMenu()
        self._createWidgets()

        # Show startup errors
        while settings.has_error():
            self._displayError(settings.display_error())
        
        # Open settings if settings un-initialised
        if not settings.exists:
            self._settings()

        if settings.plist['autoUpdateCheck']:
            self._check_for_updates(display=False)
    
    # Create styles for GUI
    def _createStyles(self):
        if config.system == 'Mac':
            self.font_size = 13
            self.header_size = 18
            self.left_indent = 12
        else:
            self.font_size = 10
            self.header_size = 14
            self.left_indent = 14
        default_font = tkfont.nametofont('TkDefaultFont')
        default_font.configure(size=self.font_size)
        #self.sdFocusColor = 'red'
        #self.sdNoFocusColor = 'darkgrey'
        self.base_background = '#dcdad5'
     
        self.gui_style = ttk.Style()
        self.gui_style.theme_use('clam')
        self.gui_style.configure('TLabelframe.Label', font='Arial {}'.format(self.header_size))
        self.gui_style.map('TCheckbutton', background=[('hover', self.base_background)])
        
    # Create GUI frames
    def _createFrames(self):
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
        tooltip.CreateToolTip(self.preview_frame, 'Selected scan preview')
        
        if config.show_ofcom:
            self.ofcom_frame = ttk.LabelFrame(self.right_container, text='OFCOM')
            self.ofcom_frame.grid(column=0, row=1, padx=8, pady=8, sticky='NWE')
     
        self.output_frame = ttk.LabelFrame(self.master_frame, text='Output Data')
        self.output_frame.grid(column=0, row=1, columnspan=3, padx=8, pady=8, sticky='NWE')
        
        # Initialise graph window
        self.fig = matplotlib.figure.Figure(figsize=(3.2, 2.65), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_position([0.15, 0.1, 0.81, 0.81])
        self.canvas = FigureCanvasTkAgg(self.fig, self.preview_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        #self._clearPreview()
    
    # Create GUI menu
    def _createMenu(self):
        
        # Create Menu Bar
        self.menu_bar = tk.Menu(self.window)

        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.file_menu.add_command(
            label='Add Files...',
            accelerator='{}{}A'.format(config.command_abbr, config.modifier_abbr),
            command=self._add_files)
        self.file_menu.add_command(
            label='Add Directory...',
            accelerator='{}{}A'.format(config.command_abbr, config.alt_abbr),
            command=self._add_directory)
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label='Set Date',
            accelerator='{}D'.format(config.command_abbr),
            command=self._use_date)
        self.file_menu.add_command(
            label='Set Destination...',
            accelerator='{}{}D'.format(config.command_abbr, config.modifier_abbr),
            command=self._custom_destination)
        self.file_menu.add_command(
            label='Create File',
            accelerator='{}Return'.format(config.command_abbr),
            command=self._create_file)
        
        # Edit Menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.edit_menu.add_command(
            label='Copy',
            accelerator='{}C'.format(config.command_abbr),
            command=lambda: self.window.focus_get().event_generate("<<Copy>>"))
        self.edit_menu.add_command(
            label='Cut',
            accelerator='{}X'.format(config.command_abbr),
            command=lambda: self.window.focus_get().event_generate("<<Cut>>"))
        self.edit_menu.add_command(
            label='Paste',
            accelerator='{}V'.format(config.command_abbr),
            command=lambda: self.window.focus_get().event_generate("<<Paste>>"))
        self.edit_menu.add_command(
            label='Select All',
            accelerator='{}A'.format(config.command_abbr),
            command=lambda: self.window.focus_get().event_generate("<<SelectAll>>"))
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label='Remove File',
            accelerator='BackSpace',
            command=self._remove_file)
        self.edit_menu.add_command(
            label='Clear Files',
            accelerator='{}BackSpace'.format(config.command_abbr),
            command=self._clear_files)

        # Help Menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=False, name='help')

        # Application Menu (OS X only)
        if config.system == 'Mac':
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
        if config.system == 'Windows':
            self.file_menu.add_separator()
            self.file_menu.add_command(
                label='Exit',
                accelerator='{}Q'.format(config.command_abbr),
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
        if config.system == 'Mac':
            self.window_menu = tk.Menu(self.menu_bar, name='window')
            self.menu_bar.add_cascade(menu=self.window_menu, label='Window')

        # Tools Menu (Windows Only)
        elif config.system == 'Windows':
            self.menu_bar.add_cascade(label='Tools', menu=self.tools_menu)

        self.menu_bar.add_cascade(label='Help', menu=self.help_menu)
        self.window.config(menu=self.menu_bar)
        
        # Bindings for Mac/Windows
        self.window.bind_all('<{}{}a>'.format(config.command, config.modifier), self._add_files)

        # Bindings for Windows only
        if config.system == 'Windows':
            self.window.bind_all('<{}{}A>'.format(config.command, config.modifier), self._add_files)
            self.window.bind_all('<{}{}a>'.format(config.command, config.alt), self._add_directory)
            self.window.bind_all('<{}{}A>'.format(config.command, config.alt), self._add_directory)
            self.window.bind_all('<{}{}d>'.format(config.command, config.modifier), self._custom_destination)
            self.window.bind_all('<{}{}D>'.format(config.command, config.modifier), self._custom_destination)
            self.window.bind_all('<{}q>'.format(config.command), self._quit)
            self.window.bind_all('<{}Q>'.format(config.command), self._quit)
            self.window.bind_all('<{}BackSpace>'.format(config.command), self._clear_files)
    
    # Create GUI widgets
    def _createWidgets(self):
    
        # Initialise tkinter variables
        self.tk_num_files = tk.StringVar()
        self.tk_venue = tk.StringVar()
        self.tk_town = tk.StringVar()
        self.tk_country = tk.StringVar()
        self.tk_scan_date = tk.StringVar()
        self.tk_io = tk.StringVar()
        self.tk_ofcom_search = tk.StringVar()
        self.tk_ofcom_venue = tk.StringVar()
        self.tk_include_ofcom_data = tk.BooleanVar()
        self.tk_output_path_display = tk.StringVar()
        self.tk_target_subdirectory = tk.StringVar()
        self.tk_default_output_path = tk.BooleanVar()
        self.tk_output_filename = tk.StringVar()
        self.tk_default_output_filename = tk.BooleanVar()
        self.tk_copy_source_files = tk.BooleanVar()
        self.tk_delete_source_files = tk.BooleanVar()
        
        # Set default values
        fields = (self.tk_venue, self.tk_town,
                  self.tk_country, self.tk_copy_source_files,
                  self.tk_delete_source_files, self.tk_include_ofcom_data)
        vars = (self.op.venue, self.op.town,
                self.op.country, self.op.copy_source_files,
                self.op.delete_source_files, self.op.include_ofcom_data)
        for field, var in zip(fields, vars):
            field.set(var)
        self.tk_ofcom_venueList = ['No venues found...']
        
        # File List
        ttk.Label(self.input_frame, text='File List').grid(column=0, row=0, sticky='W')
        self.file_list = tk.Listbox(self.input_frame, height=8, width=20)
        self.file_list.bind('<<ListboxSelect>>', self._select_file)
        self.file_list.grid(column=0, row=1, padx=config.PAD_X, pady=config.PAD_Y)
        
        # Data List
        ttk.Label(self.input_frame, text='Selected File Information').grid(column=1, row=0, sticky='W')
        self.dataListbox = tk.Listbox(self.input_frame, height=8, width=30)
        self.dataListbox.grid(column=1, row=1, padx=config.PAD_X, pady=config.PAD_Y)
        self.dataListbox.configure(background='lightGrey')
     
        # File List Edit Buttons
        self.fileListEditFrame = ttk.Frame(self.input_frame)
        self.fileListEditFrame.grid(column=0, row=2, columnspan=2, sticky='E')
        
        calendar_image = ImageTk.PhotoImage(Image.open(os.path.join(config.ICON_LOCATION, 'calendar_disabled.png')))
        self.useDateButton = ttk.Button(self.fileListEditFrame, image=calendar_image, state='disabled', command=self._use_date)
        self.useDateButton.grid(column=4, row=0, sticky='E', padx=config.PAD_X, pady=0)
        self.useDateButton.image = calendar_image
        tooltip.CreateToolTip(self.useDateButton, 'Use currently selected file\'s creation date for scan date ({}D)'.format(config.command_symbol))
        
        bin_image = ImageTk.PhotoImage(Image.open(os.path.join(config.ICON_LOCATION, 'bin_disabled.png')))
        self.clearFilesButton = ttk.Button(self.fileListEditFrame, image=bin_image, state='disabled', command=self._clear_files)
        self.clearFilesButton.grid(column=3, row=0, sticky='E', padx=config.PAD_X, pady=0)

        self.clearFilesButton.image = bin_image
        tooltip.CreateToolTip(self.clearFilesButton, 'Remove all files from file list ({}\u232b)'.format(config.command_symbol))
        
        minus_image = ImageTk.PhotoImage(Image.open(os.path.join(config.ICON_LOCATION, 'minus_disabled.png')))
        self.removeFileButton = ttk.Button(self.fileListEditFrame, image=minus_image, state='disabled', command=self._remove_file)
        self.removeFileButton.grid(column=2, row=0, sticky='E', padx=config.PAD_X, pady=0)
        self.removeFileButton.image = minus_image
        tooltip.CreateToolTip(self.removeFileButton, 'Remove selected file from file list (\u232b)')
        
        folder_image = ImageTk.PhotoImage(Image.open(os.path.join(config.ICON_LOCATION, 'folder.png')))
        self.addDirectoryButton = ttk.Button(self.fileListEditFrame, image=folder_image, command=self._add_directory)
        self.addDirectoryButton.grid(column=1, row=0, sticky='E', padx=config.PAD_X, pady=config.PAD_Y)
        self.addDirectoryButton.image = folder_image
        tooltip.CreateToolTip(self.addDirectoryButton, 'Add directory to file list ({}{}A)'.format(config.command_symbol, config.alt_symbol))

        plus_image = ImageTk.PhotoImage(Image.open(os.path.join(config.ICON_LOCATION, 'plus.png')))
        self.addFilesButton = ttk.Button(self.fileListEditFrame, image=plus_image, command=self._add_files)
        self.addFilesButton.grid(column=0, row=0, sticky='E', padx=config.PAD_X, pady=config.PAD_Y)
        self.addFilesButton.image = plus_image
        tooltip.CreateToolTip(self.addFilesButton, 'Add files to file list ({}{}A)'.format(config.command_symbol, config.modifier_symbol))
        
        # File Info status
        self.fileStatus = ttk.Label(self.input_frame, textvariable=self.tk_num_files)
        self.fileStatus.grid(column=0, row=2, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
     
        # Source Venue Data
        ttk.Label(self.info_frame, text='Venue', width=self.left_indent).grid(column=0, row=0, sticky='NW', padx=config.PAD_X, pady=config.PAD_Y)
        self.venueEntry = ttk.Entry(self.info_frame, textvariable=self.tk_venue, width=20, font='TkDefaultFont {}'.format(self.font_size))
        self.venueEntry.grid(column=1, row=0)
        tooltip.CreateToolTip(self.venueEntry, 'Scan location name')

        # Source Town Data
        ttk.Label(self.info_frame, text='Town', width=self.left_indent).grid(column=0, row=1, sticky='NW', padx=config.PAD_X, pady=config.PAD_Y)
        self.townEntry = ttk.Entry(self.info_frame, textvariable=self.tk_town, width=20, font='TkDefaultFont {}'.format(self.font_size))
        self.townEntry.grid(column=1, row=1)
        tooltip.CreateToolTip(self.townEntry, 'Scan location town/city')

        # Source Country Data
        ttk.Label(self.info_frame, text='Country', width=self.left_indent).grid(column=0, row=2, sticky='NW', padx=config.PAD_X, pady=config.PAD_Y)
        self.countryBox = ttk.Combobox(self.info_frame, textvariable=self.tk_country, width=20, font='TkDefaultFont {}'.format(self.font_size))
        self.countryBox['values'] = config.countries
        self.countryBox.grid(column=1, row=2, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.countryBox.bind('<<ComboboxSelected>>', self._refresh)
        tooltip.CreateToolTip(self.countryBox, 'Scan location country')
     
        # Source Scan Date
        ttk.Label(self.info_frame, text='Scan Date', width=self.left_indent).grid(column=0, row=3, sticky='NW', padx=config.PAD_X, pady=config.PAD_Y)
        self.dateEntry = ttk.Entry(self.info_frame, textvariable=self.tk_scan_date, width=20, font='TkDefaultFont {}'.format(self.font_size))
        self.dateEntry.grid(column=1, row=3)
        self.dateEntry.config(state='readonly')
        tooltip.CreateToolTip(self.dateEntry, 'Date scan was taken')
     
        # Inside / Outside
        ttk.Label(self.info_frame, text='Inside/Outside', width=self.left_indent).grid(column=0, row=4, sticky='NW', padx=config.PAD_X, pady=config.PAD_Y)
        self.ioBox = ttk.Combobox(self.info_frame, textvariable=self.tk_io, width=20, state='readonly', font='TkDefaultFont {}'.format(self.font_size))
        self.ioBox['values'] = ['Inside', 'Outside']
        self.ioBox.grid(column=1, row=4)
        self.ioBox.current(0)
        self.ioBox.bind('<<ComboboxSelected>>', self._ioBoxEdit)
        tooltip.CreateToolTip(self.ioBox, 'Was the scan taken inside or outside?')
        
        # Output Location
        reset_image = ImageTk.PhotoImage(Image.open(os.path.join(config.ICON_LOCATION, 'reset.png')))
        self.tk_target_subdirectory.set(self.tk_io.get())
        ttk.Label(self.output_frame, text='Destination', width=self.left_indent).grid(column=0, row=0, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.tk_default_output_path.set(1)
        self.defaultOutputCheck = ttk.Button(self.output_frame, image=reset_image, command=self._resetOutputLocation)
        self.defaultOutputCheck.grid(column=1, row=0, sticky='W', padx=0, pady=0)
        self.defaultOutputCheck.image = reset_image
        tooltip.CreateToolTip(self.defaultOutputCheck, 'Check to use default library destination folder')
        self.targetDirectory = ttk.Label(self.output_frame, textvariable=self.tk_output_path_display, width=77)
        self.targetDirectory.grid(column=2, row=0, sticky='W')
        tooltip.CreateToolTip(self.targetDirectory, 'Output scan folder')
        
        # Subdirectory
        ttk.Label(self.output_frame, text='Subdirectory', width=self.left_indent).grid(column=0, row=1, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.targetSubdirectoryEntry = ttk.Entry(self.output_frame, textvariable=self.tk_target_subdirectory, width=20, font='TkDefaultFont {}'.format(self.font_size), style='Subdirectory.TEntry')
        self.targetSubdirectoryEntry.grid(column=2, row=1, sticky='W', padx=0, pady=config.PAD_Y)
        self.targetSubdirectoryEntry.bind('<KeyRelease>', self._customSubDirectory)
        tooltip.CreateToolTip(self.targetSubdirectoryEntry, 'Optional subdirectory')
     
        # Output Master Filename
        ttk.Label(self.output_frame, text='Master Filename', width=self.left_indent).grid(column=0, row=2, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.tk_default_output_filename.set(1)
        self.defaultMasterFilenameReset = ttk.Button(self.output_frame, image=reset_image, command=self._standardMasterFilename)
        self.defaultMasterFilenameReset.grid(column=1, row=2, sticky='W', padx=0, pady=0)
        self.defaultMasterFilenameReset.image = reset_image
        tooltip.CreateToolTip(self.defaultMasterFilenameReset, 'Check to use default filename')
        self.scanMasterFilenameEntry = ttk.Entry(self.output_frame, textvariable=self.tk_output_filename, font='TkDefaultFont {}'.format(self.font_size))
        self.scanMasterFilenameEntry.grid(column=2, row=2, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        self.scanMasterFilenameEntry.config(width=60)
        self.scanMasterFilenameEntry.bind('<KeyRelease>', self._customMasterFilename)
        tooltip.CreateToolTip(self.scanMasterFilenameEntry, 'Master output filename')
        
        # Options
        self.copySourceFilesCheck = ttk.Checkbutton(self.output_frame, variable=self.tk_copy_source_files)
        self.copySourceFilesCheck.grid(column=1, row=3, sticky='E', padx=config.PAD_X, pady=config.PAD_Y)
        ttk.Label(self.output_frame, text='Duplicate Source Files').grid(column=2, row=3, sticky='W')
        tooltip.CreateToolTip(self.copySourceFilesCheck, 'Duplicate source files in library')
        self.deleteSourceFilesCheck = ttk.Checkbutton(self.output_frame, variable=self.tk_delete_source_files)
        self.deleteSourceFilesCheck.grid(column=1, row=4, sticky='E', padx=config.PAD_X, pady=config.PAD_Y)
        ttk.Label(self.output_frame, text='Delete Source Files').grid(column=2, row=4, sticky='W')
        tooltip.CreateToolTip(self.deleteSourceFilesCheck, 'Delete source files on file creation')

        # Output Buttons
        self.outputButtons = ttk.Frame(self.output_frame)
        self.outputButtons.grid(column=2, row=5, sticky='W')
        self.createFileButton = ttk.Button(self.outputButtons, text='Create File', command=self._create_file)
        self.createFileButton.grid(column=0, row=0, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        tooltip.CreateToolTip(self.createFileButton, 'Create master file ({}\u23ce)'.format(config.command_symbol))
        self.customOutputButton = ttk.Button(self.outputButtons, text='Set Destination', command=self._custom_destination)
        self.customOutputButton.grid(column=1, row=0, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
        tooltip.CreateToolTip(self.customOutputButton, 'Set custom destination for output files ({}{}D)'.format(config.command_symbol, config.modifier_symbol))
        
        if config.show_ofcom:

            # OFCOM Search Bar
            ttk.Label(self.right_container, text='OFCOM Search', width=self.left_indent).grid(column=0, row=1, sticky='NW', padx=config.PAD_X, pady=config.PAD_Y)
            self.ofcomSearchEntry = ttk.Entry(self.right_container, textvariable=self.tk_ofcom_search, width=20, font='TkDefaultFont {}'.format(self.font_size))
            self.ofcomSearchEntry.grid(column=1, row=1, sticky='NW')
            tooltip.CreateToolTip(self.ofcomSearchEntry, 'OFCOM Database Search')

            # OFCOM Search Buton
            self.ofcomSearchButton = ttk.Button(self.right_container, text='OFCOM Search', command=self._ofcomSearch)
            self.ofcomSearchButton.grid(column=1, row=2, sticky='NW', padx=config.PAD_X, pady=config.PAD_Y)
            tooltip.CreateToolTip(self.ofcomSearchButton, 'Search OFCOM database ({}S)'.format(config.command_symbol))
            
            # OFCOM Venue List
            ttk.Label(self.right_container, text='Venue Check', width=self.left_indent).grid(column=0, row=3, sticky='NW', padx=config.PAD_X, pady=config.PAD_Y)
            self.ofcomBox = ttk.Combobox(self.right_container, textvariable=self.tk_ofcom_venue, width=20, state='readonly', font='TkDefaultFont {}'.format(self.font_size))
            self.ofcomBox['values'] = self.tk_ofcom_venue_list
            self.ofcomBox.grid(column=1, row=3, sticky='NW')
            self.ofcomBox.current(0)
            self.ofcomBox.config(state='disabled')
            tooltip.CreateToolTip(self.ofcomBox, 'Select the correct venue from the list')

            # OFCOM Include Button
            self.includeOfcomDataCheck = ttk.Checkbutton(self.right_container, text='Include Exclusion Files', variable=self.tk_include_ofcom_data)
            self.includeOfcomDataCheck.grid(column=1, row=4, sticky='W', padx=config.PAD_X, pady=config.PAD_Y)
            tooltip.CreateToolTip(self.includeOfcomDataCheck, 'Include OFCOM Exclusion Data')

            self.window.bind_all('<{}s>'.format(config.command), self._ofcomSearch)
     
        # Add styling to all entry boxes
        for x in [self.venueEntry, self.townEntry, self.countryBox, self.dateEntry, self.ioBox]:
            x.grid(sticky='NW', padx=config.PAD_X, pady=config.PAD_Y)
            x.bind('<KeyRelease>', self._getMasterFilename)
        
        # Key Bindings
        self.window.bind_all('<{}Return>'.format(config.command), self._create_file)
        self.file_list.bind('<Escape>', self._deselectFileListbox)
        self.file_list.bind('<BackSpace>', self._remove_file)
         
        # Initialise Lists
        self._printFiles()

################################################################################
##########                       GUI METHODS                          ##########
################################################################################

    # Method to display about information
    def _about(self):
        tkmessagebox.showinfo(
            'About',
            '{} v{}\n\n{} Stephen Bunting 2019\n{}'
            .format(config.APPLICATION_NAME, config.APPLICATION_VERSION,
                    chr(169), config.WEBSITE_URI))

    # Method to open docs in web browser
    def _open_http(self):
        webbrowser.open(
            "{}documentation.php"
            .format(config.WEBSITE_URI), new=2, autoraise=True)

    # Method to update filelist
    def _update_file_list(self):
        self.file_list.delete(0, tk.END)
        for file in self.op.files:
            self.file_list.insert(tk.END, file.filename)

    def _select_file(self, event=None):
        if event:
            try:
                self.file_list_selection = int(event.widget.curselection()[0])
            except (AttributeError, IndexError):
                pass
        #self._printFileData()

    # Methods to interface with output
    # Add selected files
    def _add_files(self):
        selected_files = tkfiledialog.askopenfilenames(
            parent=self.input_frame,
            title='Add files',
            initialdir=settings.plist['defaultSourceLocation'])

        # Throw an error if invalid file added
        for filename in selected_files:
            try:
                self.op.add_file(filename)
            except scanfile.InvalidFile as err:
                self._display_error(5, error=err)

        # Set default directory to last used
        settings.plist['defaultSourceLocation'] = os.path.dirname(selected_files[-1])

        # Update file list
        self._update_file_list()

    # Add all valid files from a directory
    def _add_directory(self):
        selected_dir = tkfiledialog.askdirectory(
            parent=self.input_frame,
            title='Add directory',
            initialdir=settings.plist['defaultSourceLocation'])
        self.op.add_directory(selected_dir)

        # Update file list
        self._update_file_list()

    def _use_date(self):
        pass

    def _custom_destination(self):
        pass

    def _create_file(self):
        pass

    def _remove_file(self):
        pass

    def _clear_files(self):
        pass

    def _check_for_updates(self):
        pass

    def _settings(self):
        pass

    def _refresh(self):
        pass

    def _ioBoxEdit(self):
        pass

    def _resetOutputLocation(self):
        pass

    def _customSubDirectory(self):
        pass

    def _standardMasterFilename(self):
        pass

    def _customMasterFilename(self):
        pass

    def _getMasterFilename(self):
        pass

    def _deselectFileListbox(self):
        pass

    def _printFiles(self):
        pass

    # Method to show an error message
    def _display_error(self, code, **kwargs):
        if 'error' in kwargs:
            error = kwargs['error']
        else:
            error = ''
        if code == 1:
            message = "Could not read from preferences file:\n{}".format(settings.plistName)
        elif code == 2:
            message = "Could not create preferences path:\n{}".format(settings.plistPath)
        elif code == 3:
            message = "Could not write preferences file:\n{}".format(settings.plistName)
        elif code == 4:
            message = "Could not connect to update server."
        elif code == 5:
            message = "Invalid file:\n{}".format(error)
        else:
            message = "Undefined"
        tkmessagebox.showerror("RF Library Error", message)


################################################################################
##########                         START GUI                          ##########
################################################################################

if __name__ == '__main__':
    gui = GUI()
    gui.window.mainloop()
