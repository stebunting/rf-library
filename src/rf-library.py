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
import keyring
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
import data
from file import File
from tooltip import CreateToolTip
import ofcom

# Helper function to set dateFormat
def set_date_format():
    if data.dateFormats.get(plist['defaultDateFormat']):
        return data.dateFormats.get(plist['defaultDateFormat'])
    else:
        return data.dateFormats.get(defaultDateFormat)
        
# Helper function to format directory nicely
def dir_format(display_location, max_length):
    display_location = display_location.replace(os.path.expanduser('~'), '~', 1)
    while len(display_location) > max_length:
        display_location = os.path.join('...', os.path.normpath(display_location.split(os.sep, 2)[2]))
    return display_location

# Load settings plist if it exists yet
errors = []
settingsExists = True
newSettingsFile = False
if not os.path.isfile(data.plistName):
    settingsExists = False
    try:
        os.makedirs(data.plistPath, exist_ok=True)
    except PermissionError:
        errors.append(2)
    try:
        fp = open(data.plistName, 'wb')
        fp.close()
        os.chmod(data.plistName, 0o600)
        newSettingsFile = True
    except (PermissionError, FileNotFoundError):
        errors.append(3)
    plist = dict()
else:
    try:
        with open(data.plistName, 'rb') as fp:
            plist = plistlib.load(fp)
    except PermissionError:
        errors.append(1)
        plist = dict()

# Check for preferences and add default if not there
vars = ['ofcomAccountName', 'ofcomUserName', 'createLog', 'logFolder', 'forename', 'surname', 'dirStructure', 'fileStructure', 'defaultOfcomInclude', 'defaultDateFormat', 'lowFreqLimit', 'highFreqLimit', 'defaultVenue', 'defaultTown', 'defaultCountry', 'defaultCopy', 'defaultDelete', 'defaultSourceLocation', 'defaultLibraryLocation', 'autoUpdateCheck']
defaults = ['', '', True, data.defaultLogFolder, '', '', data.defaultDirectoryStructure, data.defaultFilenameStructure, False, data.defaultDateFormat, 0, 0, 'Venue', 'Town', 'United Kingdom', True, False, os.path.expanduser('~'), data.defaultLibraryLocation, True]
for var, default in zip(vars, defaults):
    if var not in plist:
        plist[var] = default

if newSettingsFile:
    with open(data.plistName, 'wb') as fp:
        plistlib.dump(plist, fp)

dateFormat = set_date_format()

################################################################################
##########                  SETTINGS WINDOW OBJECT                    ##########
################################################################################

class SettingsWindow():

    # Initialise class
    def __init__(self):

        # Variables
        self.passwordChanged = False
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
        
        if data.showOfcom:
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
        vars = [plist['dirStructure'], plist['fileStructure'],
                dir_format(plist['defaultLibraryLocation'], 50),
                plist['lowFreqLimit'], plist['highFreqLimit'],
                plist['createLog'], dir_format(plist['logFolder'], 50),
                plist['defaultDateFormat'], plist['forename'], plist['surname'],
                plist['ofcomAccountName'], plist['ofcomUserName'], ' ' * 8,
                plist['autoUpdateCheck']]
        fields = [self.dirStructure, self.fileStructure,
                  self.scansFolderDisplay, self.lowFreqLimit, self.highFreqLimit,
                  self.createLog, self.logFolderDisplay,
                  self.defaultDateFormat, self.forename, self.surname,
                  self.ofcomAccountName, self.ofcomUserName, self.ofcomPassword,
                  self.autoUpdateCheck]
        for field, var in zip(fields, vars):
            field.set(var)
        self.defaultLibraryLocation = plist['defaultLibraryLocation']
        self.logFolder = plist['logFolder']
        
        # Scans Folder
        ttk.Label(self.outputPreferences, text='Scans Folder', width='16').grid(column=0, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.scansFolderLabel = ttk.Label(self.outputPreferences, textvariable=self.scansFolderDisplay, width='36')
        self.scansFolderLabel.grid(column=1, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        CreateToolTip(self.scansFolderLabel, 'Scan library base folder')
        self.changeBaseFolderButton = ttk.Button(self.outputPreferences, text='Change Folder', command=self._changeBaseFolder)
        self.changeBaseFolderButton.grid(column=1, row=1)
        
        # Directory Structure
        ttk.Label(self.outputPreferences, text='Directory Structure', width='16').grid(column=0, row=2, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.dirStructureEntry = ttk.Entry(self.outputPreferences, textvariable=self.dirStructure, width='35')
        self.dirStructureEntry.grid(column=1, row=2, sticky='W', padx=data.padx_default, pady=data.pady_default)
        CreateToolTip(self.dirStructureEntry, 'Default library directory structure (see docs for more details')
        
        # Filename Structure
        ttk.Label(self.outputPreferences, text='Filename Structure', width='16').grid(column=0, row=3, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.fileStructureEntry = ttk.Entry(self.outputPreferences, textvariable=self.fileStructure, width='35')
        self.fileStructureEntry.grid(column=1, row=3, sticky='W', padx=data.padx_default, pady=data.pady_default)
        CreateToolTip(self.fileStructureEntry, 'Default library filename structure (see docs for more details')
        
        # Date Format
        ttk.Label(self.outputPreferences, text='Date Format', width='16').grid(column=0, row=4, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.dateFormatBox = ttk.Combobox(self.outputPreferences, textvariable=self.defaultDateFormat)
        self.dateFormatBox['values'] = [key for key in data.dateFormats]
        self.dateFormatBox.grid(column=1, row=4, sticky='W', padx=data.padx_default, pady=data.pady_default)
        CreateToolTip(self.dateFormatBox, 'Preferred date format')
        
        # Low Frequency Limit
        ttk.Label(self.outputPreferences, text='Low Frequency Limit', width='16').grid(column=0, row=5, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.lowFreqLimitEntry = ttk.Entry(self.outputPreferences, textvariable=self.lowFreqLimit)
        self.lowFreqLimitEntry.grid(column=1, row=5)
        CreateToolTip(self.lowFreqLimitEntry, 'Low frequency limit for the output file (set to 0 for no limit)')
        
        # High Frequency Limit
        ttk.Label(self.outputPreferences, text='High Frequency Limit', width='16').grid(column=0, row=6, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.highFreqLimitEntry = ttk.Entry(self.outputPreferences, textvariable=self.highFreqLimit)
        self.highFreqLimitEntry.grid(column=1, row=6)
        CreateToolTip(self.highFreqLimitEntry, 'High frequency limit for the output file (set to 0 for no limit)')

        # Create Log
        ttk.Label(self.loggingPreferences, text='Write To Log File', width='16').grid(column=0, row=0, sticky='w', padx=data.padx_default, pady=data.pady_default)
        self.createLogCheck = ttk.Checkbutton(self.loggingPreferences, variable=self.createLog)
        self.createLogCheck.grid(column=1, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        CreateToolTip(self.createLogCheck, 'Turn log file writing on/off')

        # Log Location
        ttk.Label(self.loggingPreferences, text='Log Location', width='16').grid(column=0, row=1, sticky='w', padx=data.padx_default, pady=data.pady_default)
        self.logLocationEntry = ttk.Label(self.loggingPreferences, textvariable=self.logFolderDisplay, width='36')
        self.logLocationEntry.grid(column=1, row=1, sticky='W', padx=data.padx_default, pady=data.pady_default)
        CreateToolTip(self.logLocationEntry, 'Log file location')
        self.changeLogLocation = ttk.Button(self.loggingPreferences, text='Change Folder', command=self._changeLogFolder)
        self.changeLogLocation.grid(column=1, row=2, sticky='W', padx=data.padx_default, pady=data.pady_default)
        
        # Forename Entry
        ttk.Label(self.personalData, text='Forename', width='16').grid(column=0, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.forenameEntry = ttk.Entry(self.personalData, textvariable=self.forename)
        self.forenameEntry.grid(column=1, row=0)
        CreateToolTip(self.forenameEntry, 'Your forename')
        
        # Surname Entry
        ttk.Label(self.personalData, text='Surname', width='16').grid(column=0, row=1, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.surnameEntry = ttk.Entry(self.personalData, textvariable=self.surname)
        self.surnameEntry.grid(column=1, row=1)
        CreateToolTip(self.surnameEntry, 'Your surname')

        # Check for Updates
        ttk.Label(self.appData, text='Auto Update Check', width='16').grid(column=0, row=0, sticky='w', padx=data.padx_default, pady=data.pady_default)
        self.checkForUpdatesCheck = ttk.Checkbutton(self.appData, variable=self.autoUpdateCheck)
        self.checkForUpdatesCheck.grid(column=1, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        CreateToolTip(self.checkForUpdatesCheck, 'Automatically check for updates on startup')
        
        if data.showOfcom:

            # OFCOM Account Name Entry
            ttk.Label(self.ofcomLogin, text='Account Name', width='16').grid(column=0, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
            self.ofcomAccountNameEntry = ttk.Entry(self.ofcomLogin, textvariable=self.ofcomAccountName)
            self.ofcomAccountNameEntry.grid(column=1, row=0)
            CreateToolTip(self.ofcomAccountNameEntry, 'Your OFCOM Account Name')
            
            # OFCOM User Name Entry
            ttk.Label(self.ofcomLogin, text='User Name', width='16').grid(column=0, row=1, sticky='W', padx=data.padx_default, pady=data.pady_default)
            self.ofcomUsernameEntry = ttk.Entry(self.ofcomLogin, textvariable=self.ofcomUserName)
            self.ofcomUsernameEntry.grid(column=1, row=1)
            CreateToolTip(self.ofcomUsernameEntry, 'Your OFCOM User Name')
            
            # OFCOM Password Entry
            ttk.Label(self.ofcomLogin, text='Password', width='16').grid(column=0, row=2, sticky='W', padx=data.padx_default, pady=data.pady_default)
            self.ofcomPasswordEntry = ttk.Entry(self.ofcomLogin, show="\u2022", textvariable=self.ofcomPassword)
            self.ofcomPasswordEntry.grid(column=1, row=2)
            CreateToolTip(self.ofcomPasswordEntry, 'Your OFCOM Password')

            self.ofcomPasswordEntry.bind('<KeyRelease>', self._passwordEntry)
        
        # Buttons
        self.saveSettingsButton = ttk.Button(self.settingsButtonsFrame, text='Save', command=self._saveSettings)
        self.saveSettingsButton.grid(column=0, row=0)
        CreateToolTip(self.saveSettingsButton, 'Save changes')
        self.cancelSettingsButton = ttk.Button(self.settingsButtonsFrame, text='Cancel', command=self._closeSettings)
        self.cancelSettingsButton.grid(column=1, row=0)
        CreateToolTip(self.cancelSettingsButton, 'Discard changes')
        
        # Bindings
        self.settingsWindow.bind_all('<Return>', self._saveSettings)
        self.settingsWindow.bind_all('<Escape>', self._closeSettings)
        
        # Add padding to all entry boxes
        for widget in [self.changeBaseFolderButton, self.forenameEntry, self.surnameEntry, self.lowFreqLimitEntry, self.highFreqLimitEntry, self.saveSettingsButton, self.cancelSettingsButton]:
            widget.grid(sticky='W', padx=data.padx_default, pady=data.pady_default)
    
    # Method to detect if password is amended
    def _passwordEntry(self, event=None):
        if not self.passwordChanged:
            self.passwordChanged = True
            self.ofcomPassword.set(self.ofcomPassword.get().lstrip())
            
    # Method to select scans base folder
    def _changeBaseFolder(self):
        dir = tkfiledialog.askdirectory(parent=self.settingsMasterFrame, title='Select Scan Folder', initialdir=plist['defaultLibraryLocation'])
        if dir != '':
            self.defaultLibraryLocation = dir
            self.scansFolderDisplay.set(dir_format(self.defaultLibraryLocation, 50))

    # Method to select default log folder
    def _changeLogFolder(self):
        if os.path.exists(os.path.join(plist['logFolder'], data.logFileName)):
            self.moveOldLog = True
            self.oldLogLocation = plist['logFolder']

        dir = tkfiledialog.askdirectory(parent=self.settingsMasterFrame, title='Select Source Folder', initialdir=plist['logFolder'])
        if dir != '':
            self.logFolder = dir
            self.logFolderDisplay.set(dir_format(self.logFolder, 50))
    
    # Method to save settings and close window    
    def _saveSettings(self, event=None):
        
        # Ensure limits are good ints else revert to default
        defaults = [plist['lowFreqLimit'], plist['highFreqLimit']]
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

        plist['ofcomAccountName'] = self.ofcomAccountName.get()
        plist['ofcomUserName'] = self.ofcomUserName.get()
        plist['defaultLibraryLocation'] = self.defaultLibraryLocation
        plist['forename'] = self.forename.get()
        plist['surname'] = self.surname.get()
        plist['dirStructure'] = self.dirStructure.get().strip('/')
        plist['fileStructure'] = self.fileStructure.get()
        plist['defaultDateFormat'] = self.defaultDateFormat.get()
        plist['lowFreqLimit'] = int(self.lowFreqLimit.get())
        plist['highFreqLimit'] = int(self.highFreqLimit.get())
        plist['createLog'] = self.createLog.get()
        plist['logFolder'] = self.logFolder
        plist['autoUpdateCheck'] = self.autoUpdateCheck.get()

        try:
            with open(data.plistName, 'wb') as fp:
                plistlib.dump(plist, fp)
            if self.passwordChanged:
                keyring.set_password(data.title, self.ofcomAccountName.get(), self.ofcomPassword.get())
        except PermissionError:
            gui._displayError(1)

        # Move old log to new log location
        if self.moveOldLog:
            os.rename(os.path.join(self.oldLogLocation, data.logFileName),
                      os.path.join(plist['logFolder'], data.logFileName))

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
    def __init__(self, errors):
 
        # Variables
        self.files = []                                         
        self.fileListboxSelection = None
        self.subdirectory = True
        self.settingsWindowOpen = False
        self.ioGuess = 0
        self.ioFixed = False
        self.customMasterFilename = False
        self.customSubdirectory = False
        self.pmseLookupVenues = [[], []]
        
        # Create instance
        self.window = tk.Tk()
        
        # Configure main window
        self.window.resizable(width=False, height=False)
        self.window.title(data.title)
        self.window.config(background='lightGrey')
        self.window.tk.call('wm', 'iconphoto', self.window._w, ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'logo.ico'))))
        
        # Build window
        self._createStyles()
        self._createFrames()
        self._createMenu()
        self._createWidgets()

        for error in errors:
            self._displayError(error)
        
        # Open settings if settings uninitialised
        if not settingsExists:
            self._settings()

        if plist['autoUpdateCheck']:
            self._checkForUpdates(display=False)
    
    # Create styles for GUI
    def _createStyles(self):
        if data.system == 'Mac':
            self.fontSize = 13
            self.header_size = 18
            self.left_indent = 12
        else:
            self.fontSize = 10
            self.header_size = 14
            self.left_indent = 14
        default_font = tkfont.nametofont('TkDefaultFont')
        default_font.configure(size=self.fontSize)
        self.sdFocusColor = 'red'
        self.sdNoFocusColor = 'darkgrey'
        self.baseBackground = '#dcdad5'
     
        self.guiStyle = ttk.Style()
        self.guiStyle.theme_use('clam')
        #self.guiStyle.map('TCombobox', fieldbackground=[('readonly', 'white'), ('pressed', 'red')], foreground=[('readonly', 'black')])
        self.guiStyle.configure('TLabelframe.Label', font='Arial {}'.format(self.header_size))
        self.guiStyle.map('TCheckbutton', background=[('hover', self.baseBackground)])
        
    # Create GUI frames
    def _createFrames(self):
        self.masterFrame = ttk.Frame(self.window)
        self.masterFrame.grid(padx=0, pady=0, sticky='NWE')
     
        self.leftContainer = ttk.Frame(self.masterFrame)
        self.leftContainer.grid(column=0, row=0, padx=0, pady=0, stick='NWE')

        self.rightContainer = ttk.Frame(self.masterFrame)
        self.rightContainer.grid(column=1, row=0, padx=0, pady=0, sticky='NWE')
     
        self.inputFrame = ttk.LabelFrame(self.leftContainer, text='Source Data')
        self.inputFrame.grid(column=0, row=0, padx=10, pady=10, sticky='NWE')
                          
        self.infoFrame = ttk.LabelFrame(self.leftContainer, text='Scan Information')
        self.infoFrame.grid(column=0, row=1, padx=8, pady=8, sticky='NWE')

        self.previewFrame = ttk.LabelFrame(self.rightContainer, text='Source Preview')
        self.previewFrame.grid(column=0, row=0, columnspan=2, padx=8, pady=8, sticky='NWE')
        CreateToolTip(self.previewFrame, 'Selected scan preview')
        
        if data.showOfcom:
            self.ofcomFrame = ttk.LabelFrame(self.rightContainer, text='OFCOM')
            self.ofcomFrame.grid(column=0, row=1, padx=8, pady=8, sticky='NWE')
     
        self.outputFrame = ttk.LabelFrame(self.masterFrame, text='Output Data')
        self.outputFrame.grid(column=0, row=1, columnspan=3, padx=8, pady=8, sticky='NWE')
        
        # Initialise graph window
        self.fig = matplotlib.figure.Figure(figsize=(3.2, 2.65), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_position([0.15, 0.1, 0.81, 0.81])
        self.canvas = FigureCanvasTkAgg(self.fig, self.previewFrame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._clearPreview()
    
    # Create GUI menu
    def _createMenu(self):
        
        # Create Menu Bar
        self.menuBar = tk.Menu(self.window)

        # File Menu
        self.fileMenu = tk.Menu(self.menuBar, tearoff=False)
        self.fileMenu.add_command(label='Add Files...', accelerator='{}{}A'.format(data.command_abbr, data.modifier_abbr), command=self._addFiles)
        self.fileMenu.add_command(label='Add Directory...', accelerator='{}{}A'.format(data.command_abbr, data.alt_abbr), command=self._addDirectory)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Set Date', accelerator='{}D'.format(data.command_abbr), command=self._useDate)
        self.fileMenu.add_command(label='Set Destination...', accelerator='{}{}D'.format(data.command_abbr, data.modifier_abbr), command=self._customDestination)
        self.fileMenu.add_command(label='Create File', accelerator='{}Return'.format(data.command_abbr), command=self._createFile)
        
        # Edit Menu
        self.editMenu = tk.Menu(self.menuBar, tearoff=False)
        self.editMenu.add_command(label='Copy', accelerator='{}C'.format(data.command_abbr), command=lambda: self.window.focus_get().event_generate("<<Copy>>"))
        self.editMenu.add_command(label='Cut', accelerator='{}X'.format(data.command_abbr), command=lambda: self.window.focus_get().event_generate("<<Cut>>"))
        self.editMenu.add_command(label='Paste', accelerator='{}V'.format(data.command_abbr), command=lambda: self.window.focus_get().event_generate("<<Paste>>"))
        self.editMenu.add_command(label='Select All', accelerator='{}A'.format(data.command_abbr), command=lambda: self.window.focus_get().event_generate("<<SelectAll>>"))
        self.editMenu.add_separator()
        self.editMenu.add_command(label='Remove File', accelerator='BackSpace', command=self._removeFile)
        self.editMenu.add_command(label='Clear Files', accelerator='{}BackSpace'.format(data.command_abbr), command=self._clearFiles)
        
        # Help Menu
        self.helpMenu = tk.Menu(self.menuBar, tearoff=False, name='help')

        # Application Menu (OS X only)
        if data.system == 'Mac':
            self.appMenu = tk.Menu(self.menuBar, tearoff=False, name='apple')
            self.appMenu.add_command(label='About RF Library', command=self._about)
            self.appMenu.add_command(label='Check for Updates...', command=self._checkForUpdates)
            self.appMenu.add_separator()
            self.menuBar.add_cascade(menu=self.appMenu)

            # Configure OS X Built-in menu options
            self.window.createcommand('::tk::mac::ShowPreferences', self._settings)
            self.window.createcommand('::tk::mac::ShowHelp', self._openHTTP)

        # Extra menus for Windows only
        if data.system == 'Windows':
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label='Exit', accelerator='{}Q'.format(data.command_abbr), command=self._quit)
            self.toolsMenu = tk.Menu(self.menuBar, tearoff=False)
            self.toolsMenu.add_command(label='Preferences...', command=self._settings)
            self.helpMenu.add_command(label='Documentation', command=self._openHTTP)
            self.helpMenu.add_separator()
            self.helpMenu.add_command(label='Check for Updates...', command=self._checkForUpdates)
            self.helpMenu.add_command(label='About RF Library', command=self._about)

        self.menuBar.add_cascade(label='File', menu=self.fileMenu)
        self.menuBar.add_cascade(label='Edit', menu=self.editMenu)

        # Window Menu (OS X Only)
        if data.system == 'Mac':
            self.windowMenu = tk.Menu(self.menuBar, name='window')
            self.menuBar.add_cascade(menu=self.windowMenu, label='Window')

        # Tools Menu (Windows Only)
        elif data.system == 'Windows':
            self.menuBar.add_cascade(label='Tools', menu=self.toolsMenu)

        self.menuBar.add_cascade(label='Help', menu=self.helpMenu)
        self.window.config(menu=self.menuBar)
        
        # Bindings for Mac/Windows
        self.window.bind_all('<{}{}a>'.format(data.command, data.modifier), self._addFiles)

        # Bindings for Windows only
        if data.system == 'Windows':
            self.window.bind_all('<{}{}A>'.format(data.command, data.modifier), self._addFiles)
            self.window.bind_all('<{}{}a>'.format(data.command, data.alt), self._addDirectory)
            self.window.bind_all('<{}{}A>'.format(data.command, data.alt), self._addDirectory)
            self.window.bind_all('<{}{}d>'.format(data.command, data.modifier), self._customDestination)
            self.window.bind_all('<{}{}D>'.format(data.command, data.modifier), self._customDestination)
            self.window.bind_all('<{}q>'.format(data.command), self._quit)
            self.window.bind_all('<{}Q>'.format(data.command), self._quit)
            self.window.bind_all('<{}BackSpace>'.format(data.command), self._clearFiles)
    
    # Create GUI widgets
    def _createWidgets(self):
    
        # Initialise tkinter variables
        self.numFiles = tk.StringVar()
        self.venue = tk.StringVar()
        self.town = tk.StringVar()
        self.country = tk.StringVar()
        self.scanDate = tk.StringVar()
        self.io = tk.StringVar()
        self.ofcomSearch = tk.StringVar()
        self.ofcomVenue = tk.StringVar()
        self.includeOfcomData = tk.BooleanVar()
        self.scanOutputLocationDisplay = tk.StringVar()
        self.targetSubdirectory = tk.StringVar()
        self.defaultOutputLocation = tk.BooleanVar()
        self.scanMasterFilename = tk.StringVar()
        self.defaultMasterFilename = tk.BooleanVar()
        self.copySourceFiles = tk.BooleanVar()
        self.deleteSourceFiles = tk.BooleanVar()
        
        # Set default values
        fields = [self.venue, self.town, self.country, self.copySourceFiles, self.deleteSourceFiles, self.includeOfcomData]
        vars = [plist['defaultVenue'], plist['defaultTown'], plist['defaultCountry'], plist['defaultCopy'], plist['defaultDelete'], plist['defaultOfcomInclude']]
        for field, var in zip(fields, vars):
            field.set(var)
        self.ofcomVenueList = ['No venues found...']
        
        # File List
        ttk.Label(self.inputFrame, text='File List').grid(column=0, row=0, sticky='W')
        self.fileListbox = tk.Listbox(self.inputFrame, height=8, width=20)
        self.fileListbox.bind('<<ListboxSelect>>', self._selectFileItem)
        self.fileListbox.grid(column=0, row=1, padx=data.padx_default, pady=data.pady_default)
        
        # Data List
        ttk.Label(self.inputFrame, text='Selected File Information').grid(column=1, row=0, sticky='W')
        self.dataListbox = tk.Listbox(self.inputFrame, height=8, width=30)
        self.dataListbox.grid(column=1, row=1, padx=data.padx_default, pady=data.pady_default)
        self.dataListbox.configure(background='lightGrey')
     
        # File List Edit Buttons
        self.fileListEditFrame = ttk.Frame(self.inputFrame)
        self.fileListEditFrame.grid(column=0, row=2, columnspan=2, sticky='E')
        
        calendar_image = ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'calendar_disabled.png')))
        self.useDateButton = ttk.Button(self.fileListEditFrame, image=calendar_image, state='disabled', command=self._useDate)
        self.useDateButton.grid(column=4, row=0, sticky='E', padx=data.padx_default, pady=0)
        self.useDateButton.image = calendar_image
        CreateToolTip(self.useDateButton, 'Use currently selected file\'s creation date for scan date ({}D)'.format(data.command_symbol))
        
        bin_image = ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'bin_disabled.png')))
        self.clearFilesButton = ttk.Button(self.fileListEditFrame, image=bin_image, state='disabled', command=self._clearFiles)
        self.clearFilesButton.grid(column=3, row=0, sticky='E', padx=data.padx_default, pady=0)
        self.clearFilesButton.image = bin_image
        CreateToolTip(self.clearFilesButton, 'Remove all files from file list ({}\u232b)'.format(data.command_symbol))
        
        minus_image = ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'minus_disabled.png')))
        self.removeFileButton = ttk.Button(self.fileListEditFrame, image=minus_image, state='disabled', command=self._removeFile)
        self.removeFileButton.grid(column=2, row=0, sticky='E', padx=data.padx_default, pady=0)
        self.removeFileButton.image = minus_image
        CreateToolTip(self.removeFileButton, 'Remove selected file from file list (\u232b)')
        
        folder_image = ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'folder.png')))
        self.addDirectoryButton = ttk.Button(self.fileListEditFrame, image=folder_image, command=self._addDirectory)
        self.addDirectoryButton.grid(column=1, row=0, sticky='E', padx=data.padx_default, pady=data.pady_default)
        self.addDirectoryButton.image = folder_image
        CreateToolTip(self.addDirectoryButton, 'Add directory to file list ({}{}A)'.format(data.command_symbol, data.alt_symbol))

        plus_image = ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'plus.png')))
        self.addFilesButton = ttk.Button(self.fileListEditFrame, image=plus_image, command=self._addFiles)
        self.addFilesButton.grid(column=0, row=0, sticky='E', padx=data.padx_default, pady=data.pady_default)
        self.addFilesButton.image = plus_image
        CreateToolTip(self.addFilesButton, 'Add files to file list ({}{}A)'.format(data.command_symbol, data.modifier_symbol))
        
        # File Info status
        self.fileStatus = ttk.Label(self.inputFrame, textvariable=self.numFiles)
        self.fileStatus.grid(column=0, row=2, sticky='W', padx=data.padx_default, pady=data.pady_default)
     
        # Source Venue Data
        ttk.Label(self.infoFrame, text='Venue', width=self.left_indent).grid(column=0, row=0, sticky='NW', padx=data.padx_default, pady=data.pady_default)
        self.venueEntry = ttk.Entry(self.infoFrame, textvariable=self.venue, width=20, font='TkDefaultFont {}'.format(self.fontSize))
        self.venueEntry.grid(column=1, row=0)
        CreateToolTip(self.venueEntry, 'Scan location name')

        # Source Town Data
        ttk.Label(self.infoFrame, text='Town', width=self.left_indent).grid(column=0, row=1, sticky='NW', padx=data.padx_default, pady=data.pady_default)
        self.townEntry = ttk.Entry(self.infoFrame, textvariable=self.town, width=20, font='TkDefaultFont {}'.format(self.fontSize))
        self.townEntry.grid(column=1, row=1)
        CreateToolTip(self.townEntry, 'Scan location town/city')

        # Source Country Data
        ttk.Label(self.infoFrame, text='Country', width=self.left_indent).grid(column=0, row=2, sticky='NW', padx=data.padx_default, pady=data.pady_default)
        self.countryBox = ttk.Combobox(self.infoFrame, textvariable=self.country, width=20, font='TkDefaultFont {}'.format(self.fontSize))
        self.countryBox['values'] = data.countries
        self.countryBox.grid(column=1, row=2, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.countryBox.bind('<<ComboboxSelected>>', self._refresh)
        CreateToolTip(self.countryBox, 'Scan location country')
     
        # Source Scan Date
        ttk.Label(self.infoFrame, text='Scan Date', width=self.left_indent).grid(column=0, row=3, sticky='NW', padx=data.padx_default, pady=data.pady_default)
        self.dateEntry = ttk.Entry(self.infoFrame, textvariable=self.scanDate, width=20, font='TkDefaultFont {}'.format(self.fontSize))
        self.dateEntry.grid(column=1, row=3)
        self.dateEntry.config(state='readonly')
        CreateToolTip(self.dateEntry, 'Date scan was taken')
     
        # Inside / Outside
        ttk.Label(self.infoFrame, text='Inside/Outside', width=self.left_indent).grid(column=0, row=4, sticky='NW', padx=data.padx_default, pady=data.pady_default)
        self.ioBox = ttk.Combobox(self.infoFrame, textvariable=self.io, width=20, state='readonly', font='TkDefaultFont {}'.format(self.fontSize))
        self.ioBox['values'] = ['Inside', 'Outside']
        self.ioBox.grid(column=1, row=4)
        self.ioBox.current(0)
        self.ioBox.bind('<<ComboboxSelected>>', self._ioBoxEdit)
        CreateToolTip(self.ioBox, 'Was the scan taken inside or outside?')
        
        # Output Location
        reset_image = ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'reset.png')))
        self.targetSubdirectory.set(self.io.get())
        ttk.Label(self.outputFrame, text='Destination', width=self.left_indent).grid(column=0, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.defaultOutputLocation.set(1)
        self.defaultOutputCheck = ttk.Button(self.outputFrame, image=reset_image, command=self._resetOutputLocation)
        self.defaultOutputCheck.grid(column=1, row=0, sticky='W', padx=0, pady=0)
        self.defaultOutputCheck.image = reset_image
        CreateToolTip(self.defaultOutputCheck, 'Check to use default library destination folder')
        self.targetDirectory = ttk.Label(self.outputFrame, textvariable=self.scanOutputLocationDisplay, width=77)
        self.targetDirectory.grid(column=2, row=0, sticky='W')
        CreateToolTip(self.targetDirectory, 'Output scan folder')
        
        # Subdirectory
        ttk.Label(self.outputFrame, text='Subdirectory', width=self.left_indent).grid(column=0, row=1, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.targetSubdirectoryEntry = ttk.Entry(self.outputFrame, textvariable=self.targetSubdirectory, width=20, font='TkDefaultFont {}'.format(self.fontSize), style='Subdirectory.TEntry')
        self.targetSubdirectoryEntry.grid(column=2, row=1, sticky='W', padx=0, pady=data.pady_default)
        self.targetSubdirectoryEntry.bind('<KeyRelease>', self._customSubDirectory)
        CreateToolTip(self.targetSubdirectoryEntry, 'Optional subdirectory')
     
        # Output Master Filename
        ttk.Label(self.outputFrame, text='Master Filename', width=self.left_indent).grid(column=0, row=2, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.defaultMasterFilename.set(1)
        self.defaultMasterFilenameReset = ttk.Button(self.outputFrame, image=reset_image, command=self._standardMasterFilename)
        self.defaultMasterFilenameReset.grid(column=1, row=2, sticky='W', padx=0, pady=0)
        self.defaultMasterFilenameReset.image = reset_image
        CreateToolTip(self.defaultMasterFilenameReset, 'Check to use default filename')
        self.scanMasterFilenameEntry = ttk.Entry(self.outputFrame, textvariable=self.scanMasterFilename, font='TkDefaultFont {}'.format(self.fontSize))
        self.scanMasterFilenameEntry.grid(column=2, row=2, sticky='W', padx=data.padx_default, pady=data.pady_default)
        self.scanMasterFilenameEntry.config(width=60)
        self.scanMasterFilenameEntry.bind('<KeyRelease>', self._customMasterFilename)
        CreateToolTip(self.scanMasterFilenameEntry, 'Master output filename')
        
        # Options
        self.copySourceFilesCheck = ttk.Checkbutton(self.outputFrame, variable=self.copySourceFiles)
        self.copySourceFilesCheck.grid(column=1, row=3, sticky='E', padx=data.padx_default, pady=data.pady_default)
        ttk.Label(self.outputFrame, text='Duplicate Source Files').grid(column=2, row=3, sticky='W')
        CreateToolTip(self.copySourceFilesCheck, 'Duplicate source files in library')
        self.deleteSourceFilesCheck = ttk.Checkbutton(self.outputFrame, variable=self.deleteSourceFiles)
        self.deleteSourceFilesCheck.grid(column=1, row=4, sticky='E', padx=data.padx_default, pady=data.pady_default)
        ttk.Label(self.outputFrame, text='Delete Source Files').grid(column=2, row=4, sticky='W')
        CreateToolTip(self.deleteSourceFilesCheck, 'Delete source files on file creation')

        # Output Buttons
        self.outputButtons = ttk.Frame(self.outputFrame)
        self.outputButtons.grid(column=2, row=5, sticky='W')
        self.createFileButton = ttk.Button(self.outputButtons, text='Create File', command=self._createFile)
        self.createFileButton.grid(column=0, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        CreateToolTip(self.createFileButton, 'Create master file ({}\u23ce)'.format(data.command_symbol))
        self.customOutputButton = ttk.Button(self.outputButtons, text='Set Destination', command=self._customDestination)
        self.customOutputButton.grid(column=1, row=0, sticky='W', padx=data.padx_default, pady=data.pady_default)
        CreateToolTip(self.customOutputButton, 'Set custom destination for output files ({}{}D)'.format(data.command_symbol, data.modifier_symbol))
        
        if data.showOfcom:

            # OFCOM Search Bar
            ttk.Label(self.rightContainer, text='OFCOM Search', width=self.left_indent).grid(column=0, row=1, sticky='NW', padx=data.padx_default, pady=data.pady_default)
            self.ofcomSearchEntry = ttk.Entry(self.rightContainer, textvariable=self.ofcomSearch, width=20, font='TkDefaultFont {}'.format(self.fontSize))
            self.ofcomSearchEntry.grid(column=1, row=1, sticky='NW')
            CreateToolTip(self.ofcomSearchEntry, 'OFCOM Database Search')

            # OFCOM Search Buton
            self.ofcomSearchButton = ttk.Button(self.rightContainer, text='OFCOM Search', command=self._ofcomSearch)
            self.ofcomSearchButton.grid(column=1, row=2, sticky='NW', padx=data.padx_default, pady=data.pady_default)
            CreateToolTip(self.ofcomSearchButton, 'Search OFCOM database ({}S)'.format(data.command_symbol))
            
            # OFCOM Venue List
            ttk.Label(self.rightContainer, text='Venue Check', width=self.left_indent).grid(column=0, row=3, sticky='NW', padx=data.padx_default, pady=data.pady_default)
            self.ofcomBox = ttk.Combobox(self.rightContainer, textvariable=self.ofcomVenue, width=20, state='readonly', font='TkDefaultFont {}'.format(self.fontSize))
            self.ofcomBox['values'] = self.ofcomVenueList
            self.ofcomBox.grid(column=1, row=3, sticky='NW')
            self.ofcomBox.current(0)
            self.ofcomBox.config(state='disabled')
            CreateToolTip(self.ofcomBox, 'Select the correct venue from the list')

            # OFCOM Include Button
            self.includeOfcomDataCheck = ttk.Checkbutton(self.rightContainer, text='Include Exclusion Files', variable=self.includeOfcomData)
            self.includeOfcomDataCheck.grid(column=1, row=4, sticky='W', padx=data.padx_default, pady=data.pady_default)
            CreateToolTip(self.includeOfcomDataCheck, 'Include OFCOM Exclusion Data')

            self.window.bind_all('<{}s>'.format(data.command), self._ofcomSearch)
     
        # Add styling to all entry boxes
        for x in [self.venueEntry, self.townEntry, self.countryBox, self.dateEntry, self.ioBox]:
            x.grid(sticky='NW', padx=data.padx_default, pady=data.pady_default)
            x.bind('<KeyRelease>', self._getMasterFilename)
        
        # Key Bindings
        self.window.bind_all('<{}Return>'.format(data.command), self._createFile)
        self.fileListbox.bind('<Escape>', self._deselectFileListbox)
        self.fileListbox.bind('<BackSpace>', self._removeFile)
         
        # Initialise Lists
        self._printFiles()

################################################################################
##########                       GUI METHODS                          ##########
################################################################################
             
    # Method to update filelist
    def _printFiles(self, event=None):
        self.fileListbox.delete(0, tk.END)
        for file in self.files:
            self.fileListbox.insert(tk.END, file.filename)
        self._selectFileItem(event)
        self._updateFileStatus()
        self._getScanDate()
        self._getMasterFilename()

    # Method to select fileListbox item
    """def _selectFileItem(self, event=None):
        if event:
            try:
                self.fileListboxSelection = int(event.widget.curselection()[0])
            except (AttributeError, IndexError):
                pass
        #self.fileListbox.selection_clear(0, tk.END)
        #if self.fileListboxSelection != None:
        #    self.fileListbox.select_set(self.fileListboxSelection)
        #    self.fileListbox.activate(self.fileListboxSelection)
        #if self.fileListboxSelection:
        #    self.fileListbox.see(self.fileListboxSelection)
        self._printFileData()"""

    def _selectFileItem(self, event=None):
        if event:
            try:
                self.fileListboxSelection = int(event.widget.curselection()[0])
            except (AttributeError, IndexError):
                pass
        self._printFileData()
        
    # Method to print file data to dataListbox
    def _printFileData(self):
        self.dataListbox.delete(0, tk.END)
        if self.fileListboxSelection == None:
            self.dataListbox.insert(tk.END, 'No file selected')
            self._clearPreview()
        else:
            self.dataListbox.insert(tk.END, 'Filename: {}'.format(self.files[self.fileListboxSelection].filename))
            self.dataListbox.insert(tk.END, 'Date: {}'.format(self.files[self.fileListboxSelection].creationDate.strftime(dateFormat)))
            self.dataListbox.insert(tk.END, 'Scanner: {}'.format(self.files[self.fileListboxSelection].model))
            if self.files[self.fileListboxSelection].startTVChannel == None:
                startTV = ''
            else:
                startTV = ' (TV{})'.format(self.files[self.fileListboxSelection].startTVChannel)
            self.dataListbox.insert(tk.END, 'Start Frequency: {:.3f}MHz{}'.format(self.files[self.fileListboxSelection].startFrequency, startTV))
            if self.files[self.fileListboxSelection].stopTVChannel == None:
                stopTV = ''
            else:
                stopTV = ' (TV{})'.format(self.files[self.fileListboxSelection].stopTVChannel)
            self.dataListbox.insert(tk.END, 'Stop Frequency: {:.3f}MHz{}'.format(self.files[self.fileListboxSelection].stopFrequency, stopTV))
            self.dataListbox.insert(tk.END, 'Data Points: {}'.format(self.files[self.fileListboxSelection].dataPoints))
            self.dataListbox.insert(tk.END, 'Mean Resolution: {:.3f}MHz'.format(self.files[self.fileListboxSelection].resolution))
            self.dataListbox.insert(tk.END, 'New Filename: {}'.format(self.files[self.fileListboxSelection].newFilename))
            self._updatePreview()
        self._buttonDisable()

    # Method to decide if buttons should be disabled or not
    def _buttonDisable(self):
        if len(self.files) == 0 :
            self._buttonStatus('disabled', 'disabled')
        elif self.fileListboxSelection == None:
            self._buttonStatus('disabled', 'enabled')
        else:
            self._buttonStatus('enabled', 'enabled')

    # Method to print number of files chosen
    def _updateFileStatus(self):
        plural = '' if len(self.files) == 1 else 's'
        if len(self.files) == 0:
            self.fileStatus.configure(foreground='red')
        else:
            self.fileStatus.configure(foreground='black')
        self.numFiles.set('{} file{} added'.format(len(self.files), plural))
 
    # Method to get earliest date from all files or todays date (default)
    def _getScanDate(self):
        if len(self.files) == 0:
            self.scanDateTimestamp = datetime.date.today()
        else:
            self.scanDateTimestamp = min([file.creationDate for file in self.files])
        self.scanDate.set(self.scanDateTimestamp.strftime(dateFormat))
    
    # Method to convert user input directory structure into path
    def parse_structure(self, s):
        for old, new in [('%c', self.country.get()),
                         ('%t', self.town.get()),
                         ('%v', self.venue.get()),
                         ('%y', str(self.scanDateTimestamp.year)),
                         ('%i', self.io.get()),
                         ('%s', self.targetSubdirectory.get()),
                         ('%f', plist['forename']),
                         ('%n', plist['surname']),
                         ('%m', '{:02d}'.format(self.scanDateTimestamp.month)),
                         ('%M', self.scanDateTimestamp.strftime('%B')),
                         ('%d', '{:02d}'.format(self.scanDateTimestamp.day))]:
            s = s.replace(old, new)
        return s
    
    # Method to create master filename
    def _getMasterFilename(self, event=None):
        
        # Return if user has entered a custom master filename
        if self.customMasterFilename:
            return
        
        self.scanMasterFilename.set(self.parse_structure(plist['fileStructure'] + '.csv'))
        if self.defaultOutputLocation.get() == 1:
            self.libraryLocation = plist['defaultLibraryLocation']
            self.targetLocation = self.parse_structure(os.path.join(plist['dirStructure'], '%s'))
        else:
            self.targetLocation = self.targetSubdirectory.get()
            if self.targetSubdirectory.get() != '':
                self.targetLocation = self.targetLocation
        self.scanOutputLocation = os.path.join(self.libraryLocation, self.targetLocation)
        self.scanOutputLocationDisplay.set(dir_format(self.scanOutputLocation, 90))

        # Set OFCOM Search box when venue edited
        self.ofcomSearch.set('{} {}'.format(self.town.get(), self.venue.get()))
        
    # Method to disable/enable buttons/menu items based on selected files
    def _buttonStatus(self, inputStatus=None, outputStatus=None):
        if inputStatus != None:
            for x in [(self.removeFileButton, 'minus'), (self.useDateButton, 'calendar')]:
                im = ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, '{}_{}.png'.format(x[1], inputStatus))))
                x[0].config(state=inputStatus, image=im)
                x[0].image = im
            if inputStatus == 'enabled':
                inputStatus = 'normal'
            for (menu, item) in [(self.editMenu, 'Remove File'), (self.fileMenu, 'Set Date')]:
                menu.entryconfig(item, state=inputStatus)
                
        if outputStatus != None:
            im = ImageTk.PhotoImage(Image.open(os.path.join(data.icon_location, 'bin_{}.png'.format(outputStatus))))
            self.clearFilesButton.config(state=outputStatus, image=im)
            self.clearFilesButton.image = im
            if outputStatus == 'enabled':
                self.window.bind_all('<{}d>'.format(data.command), self._useDate)
                self.window.bind_all('<{}D>'.format(data.command), self._useDate)
                self.editMenu.entryconfig('Clear Files', state='normal')
                self.fileMenu.entryconfig('Create File', state='normal')
            else:
                self.window.unbind_all('<{}d>'.format(data.command))
                self.window.unbind_all('<{}D>'.format(data.command))
                self.editMenu.entryconfig('Clear Files', state='disabled')
                self.fileMenu.entryconfig('Create File', state='disabled')
     
    # Method to change destination to custom destination    
    def _customDestination(self, event=None):
        customLocation = tkfiledialog.askdirectory(parent=self.masterFrame, title='Select Destination Folder')
        if customLocation != '':
            self.libraryLocation = customLocation
            self.scanOutputLocation = self.libraryLocation
            self.scanOutputLocationDisplay.set(dir_format(self.scanOutputLocation, 90))
            self.defaultOutputLocation.set(0)
            self._updateSubdirectory()
 
    # Method to refresh file data, for use when country or settings change
    def _refresh(self, event=None):
        global dateFormat
        dateFormat = set_date_format()
        for file in self.files:
            file.updateTVChannels(self.country.get())
        self._printFiles()

    # Method to deselect fileListbox
    def _deselectFileListbox(self, event=None):
        self.fileListboxSelection = None
        self.fileListbox.selection_clear(0, tk.END)
        self._selectFileItem()
     
    # Method called after IObox edited
    def _ioBoxEdit(self, event=None):
        self.ioFixed = True
        if not self.customSubdirectory:
            self._updateSubdirectory()
    
    # Method called after subdirectory edited
    def _customSubDirectory(self, event=None):
        self.customSubdirectory = True
        self._getMasterFilename()
    
    # Method to declare user has entered a custom Master Filename    
    def _customMasterFilename(self, event=None):
        self.customMasterFilename = True
        self.defaultMasterFilename.set(0)
    
    # Method to declare user wants to use the standard Filename    
    def _standardMasterFilename(self, event=None):
        self.customMasterFilename = False
        self.defaultMasterFilename.set(1)
        self._getMasterFilename()
            
    # Method to update output location to standard location
    def _resetOutputLocation(self):
        self.defaultOutputLocation.set(1)
        self._updateSubdirectory()

    # Method to update subdirectory name when standard destination called
    def _updateSubdirectory(self, event=None):
        if self.defaultOutputLocation.get() == 1:
            self.targetSubdirectory.set(self.io.get())
            self.subdirectory = True
        else:
            self.targetSubdirectory.set('')
            self.subdirectory = False
        self._getMasterFilename()

    # Method to update ioBox and Subdirectory when Inside v Outside changes
    def _setIO(self):
        if not self.ioFixed:
            if self.ioGuess >= 0:
                self.ioBox.current(0)
            else:
                self.ioBox.current(1)
            self._updateSubdirectory()

    # Method to open file dialogue and allow selection of files
    def _addFiles(self, event=None, selected_files=None, suppressErrors=False):
        if selected_files == None:
            selected_files = tkfiledialog.askopenfilenames(parent=self.inputFrame, title='Add files', initialdir=plist['defaultSourceLocation'])
        for file in selected_files:
            newFile = File(file, self.country.get())
            if newFile.valid:
                self.ioGuess += newFile.io
                self.files.append(newFile)
                plist['defaultSourceLocation'] = os.path.dirname(file)
            elif not suppressErrors:
                tkmessagebox.showwarning('Invalid File', '{} is not a valid scan file and will not be added to the file list'.format(newFile.filename))
        self._setIO()
        self._printFiles()

    # Method to open file dialogue and allow selection of all files in a directory
    def _addDirectory(self, event=None):
        dirFiles = []
        selectedDir = tkfiledialog.askdirectory(parent=self.inputFrame, title='Add directory', initialdir=plist['defaultSourceLocation'])
        if selectedDir != '':
            plist['defaultSourceLocation'] = selectedDir
            for file in os.listdir(selectedDir):
                fullfilename = os.path.join(selectedDir, file)
                if not file.startswith('.') and not os.path.isdir(fullfilename):
                    dirFiles.append(fullfilename)
        if len(dirFiles) != 0:
            self._addFiles(None, dirFiles, True)

    # Method to remove file
    def _removeFile(self, event=None):
        if event == None or (event.widget.winfo_class() != 'TEntry' and event.widget.winfo_class() != 'TCombobox'):
            if self.fileListboxSelection == None:
                return
            self.ioGuess -= self.files[self.fileListboxSelection].io
            self._setIO()
            self.files.remove(self.files[self.fileListboxSelection])
            if len(self.files) == 0:
                self.fileListboxSelection = None
            elif self.fileListboxSelection > len(self.files) - 1:
                self.fileListboxSelection = len(self.files) - 1
            self._printFiles(event)
 
    # Method to remove all files
    def _clearFiles(self, event=None, confirmRequired=True):
        self.editMenu.entryconfig('Clear Files', state='disabled')
        if confirmRequired:
            if not tkmessagebox.askyesno('Are you sure?', 'Are you sure you want to clear the file list?'):
                self.editMenu.entryconfig('Clear Files', state='normal')
                return
        del self.files[:]
        self.fileListboxSelection = None
        self.ioFixed = False
        self.ioGuess = 0
        self._printFiles()
         
    # Method to use date from selected file
    def _useDate(self, event=None):
        self.scanDateTimestamp = self.files[self.fileListboxSelection].creationDate
        self.scanDate.set(self.scanDateTimestamp.strftime(dateFormat))
        self._getMasterFilename()

    # Method to create master file
    def _createFile(self, event=None):
        if len(self.files) == 0 and not self.includeOfcomData.get():
            tkmessagebox.showinfo('No Files To Create', 'No files to create.')
            return
        
        # Check if user really wants to delete source files
        if self.deleteSourceFiles.get() == 1 and tkmessagebox.askyesno('Are you sure?', 'Are you sure you want to delete the input files?'):
            delSourceConfirmed = True
        else:
            delSourceConfirmed = False

        # Add all files into outputFile list if within limits
        outputFile = []
        filesWritten = 0
        statement = 'The following files were successfully written!\n\nDIRECTORY:\n{}\n\n'.format(self.scanOutputLocation)
        for file in self.files:
            for freq, value in file.frequencies:
                if freq >= plist['lowFreqLimit'] and (plist['highFreqLimit'] == 0 or freq <= plist['highFreqLimit']):
                    outputFile.append([float(freq), float(value)])
        
        # Remove duplicates
        outputFile = sorted(outputFile)
        i = 1
        while i < len(outputFile):
            if outputFile[i][0] == outputFile[i - 1][0]:
                outputFile.remove(outputFile[i - 1])
            else:
                i += 1

        # Write original files with new filenames
        if self._createDirectory():
            if self.copySourceFiles.get():
                for file in self.files:
                    writtenFilename = self._writeFile(self.scanOutputLocation, file.newFilename, file.frequencies)
                    if not writtenFilename:
                        return False
                    else:
                        filesWritten += 1
                        statement += '{}\n'.format(writtenFilename)
        
            # Write master file
            if len(outputFile) > 0:
                writtenFilename = self._writeFile(self.scanOutputLocation, self.scanMasterFilename.get(), outputFile)
                if not writtenFilename:
                    return False
                else:
                    filesWritten += 1
                    statement += '{}\n'.format(writtenFilename)

            # Write WSM file
            if (data.makeWSM and len(outputFile) > 0):
                writtenFilename = self._writeWSMFile(self.scanOutputLocation, self.scanMasterFilename.get(), outputFile)
                if not writtenFilename:
                    return False
                else:
                    filesWritten += 1
                    statement += '{}\n'.format(writtenFilename)

            # Write OFCOM Exclusion Files
            if (data.showOfcom and self.includeOfcomData.get()):
                filename = self._findUnusedFile(self.scanOutputLocation, '{}.cxl'.format(os.path.splitext(self.scanMasterFilename.get())[0]))
                target = os.path.join(self.scanOutputLocation, filename)
                
                writtenFilename = self._ofcomGenerate(None, self.io.get(), target)
                if writtenFilename:
                    filesWritten += 1
                    statement += '{}\n'.format(filename)
                else:
                    tkmessagebox.showwarning('Timeout', 'Could not connect to the JFMG service, please check your connection.')
                
            statement += '\n{} files written to disk.\n'.format(filesWritten)

            if filesWritten == 0:
                tkmessagebox.showinfo('No Files To Create', 'No files to create.')
                return

            # Write defaults to plist
            plist['defaultVenue'] = self.venue.get()
            plist['defaultTown'] = self.town.get()
            plist['defaultCountry'] = self.country.get()
            plist['defaultCopy'] = self.copySourceFiles.get()
            plist['defaultDelete'] = self.deleteSourceFiles.get()
            plist['defaultOfcomInclude'] = self.includeOfcomData.get()

            try:
                with open(data.plistName, 'wb') as fp:
                    plistlib.dump(plist, fp)
            except PermissionError:
                gui._displayError(1)
            
            if plist['createLog']:
                if self._writeToLog():
                    statement += 'Log file updated.\n'
                else:
                    statement += 'WARNING: Log could not be updated at {}\n'.format(plist['logFolder'])
         
            if delSourceConfirmed:
                statement += '\nThe following files were deleted:\n'
                for file in self.files:
                    os.remove(file.fullfilename)
                    statement += '{}\n'.format(file.filename)
                self._clearFiles(None, False)
                tkmessagebox.showinfo('Success!', statement)
            else:
                if tkmessagebox.askyesno('Success!', '{}\nWould you like to clear the file list?'.format(statement)):
                    self._clearFiles(None, False)

    # Method to write to log file
    def _writeToLog(self):
        logFile = os.path.join(plist['logFolder'], data.logFileName)

        if not os.path.exists(logFile):
            newFile = True
        else:
            newFile = False

        with open(logFile, 'a', newline='') as csvfile:
            logWriter = csv.writer(csvfile, delimiter=',', quotechar="\"", quoting=csv.QUOTE_MINIMAL)
            if newFile:
                logWriter.writerow(['Date', 'Country', 'City', 'Venue', 'Inside/Outside'])
            logWriter.writerow([self.scanDate.get(), self.country.get(), self.town.get(), self.venue.get(), self.io.get()])

        return True

    def _findUnusedFile(self, directory, filename):
        target = os.path.join(directory, filename)
        file, ext = os.path.splitext(filename)
        duplicateCounter = 0
        while os.path.isfile(target):
            duplicateCounter += 1
            filename = '{}-{}{}'.format(file, duplicateCounter, ext)
            target = os.path.join(directory, filename)
        return filename

    # Method to write file to disk
    def _writeFile(self, directory, filename, array):
        filename = self._findUnusedFile(directory, filename)
        target = os.path.join(directory, filename)
        try:
            with open(target, 'w') as fp:
                for freq, value in array:
                    fp.write('{:09.4f},{:09.4f}\n'.format(freq, value))
            return filename
        except IOError:
            tkmessagebox.showwarning('Fail!', '{} could not be written.'.format(target))
            return False

    # Method to write WSM file to disk
    def _writeWSMFile(self, directory, filename, array):
        file, ext = os.path.splitext(filename)
        filename = '{}-WSM.{}'.format(file, ext)

        filename = self._findUnusedFile(directory, filename)  
        target = os.path.join(directory, filename)
        try:
            with open(target, 'w') as fp:
                wsm_date = self.scanDateTimestamp.strftime('%Y-%m-%d 00:00:00')
                fp.write('Receiver;{}\nDate/Time;{}\nRFUnit;dBm\n\n\nFrequency Range [kHz];{:06d};{:06d};\n'.format(data.title, wsm_date, plist['lowFreqLimit'] * 1000, plist['highFreqLimit'] * 1000))
                fp.write('Frequency;RF level (%);RF level\n')
                for freq, value in reversed(array):
                    fp.write('{:06d};;{:04.1f}\n'.format(int(freq * 1000), value))
            return filename
        except IOError:
            tkmessagebox.showwarning('Fail!', '{} could not be written.'.format(target))
            return False
     
    # Method to create directory structure
    def _createDirectory(self):
        try:
            os.makedirs('{}'.format(self.scanOutputLocation))
            return True
        except OSError:
            return tkmessagebox.askyesno('Directory already exists', '{} already exists. Are you sure?'.format(self.scanOutputLocation))
            
    # Method to remove current preview
    def _clearPreview(self):
    
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
 
    # Method to draw preview of self.fileListboxSelection
    def _updatePreview(self):
        
        # Get x,y values
        mean = 0
        for x in self.files[self.fileListboxSelection].frequencies:
            try:
                previous
            except:
                previous = [x[0], x[1]]
                xValues = []
                yValues = []
            mean += x[1]
            if previous[0] + (self.files[self.fileListboxSelection].resolution * 2) < x[0]:
                xValues.append(previous[0] + self.files[self.fileListboxSelection].resolution)
                yValues.append(-200)
                xValues.append(x[0] - self.files[self.fileListboxSelection].resolution)
                yValues.append(-200)
            xValues.append(x[0])
            yValues.append(x[1])
            previous = x
        
        # Calculate mean value for potential scaling
        mean /= len(self.files[self.fileListboxSelection].frequencies)
        
        # Get axis values
        ymin = min(i for i in yValues if i > -120)
        ymax = max(yValues)
        ymin = int((ymin - 5) / 5) * 5 if ymin > -95 or ymin < -105 else -105
        ymax = int((ymax + 5) / 5) * 5 if ymax > ymin + 45 else ymin + 45
        xmin = xValues[0]
        xmax = xValues[-1]
        
        # Get x tick values
        minPixelDistance = 25
        axeswidth = self.ax.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted()).width * self.fig.dpi
        minTickDistance = ((xmax - xmin) * minPixelDistance) / axeswidth
        xTicks = []
        prev = 0
        tvCountry = self.country.get() if self.country.get() == 'United States of America' else 'UK'
        for channel in data.TVChannels[tvCountry]:
            if channel[1] - prev >= minTickDistance and self.files[self.fileListboxSelection].frequencies[0][0] <= channel[1] and self.files[self.fileListboxSelection].frequencies[-1][0] >= channel[1]:
                xTicks.append(channel[1])
                prev = channel[1]

        # Clear previous graph
        self.ax.clear()
        
        # Set Style
        self.ax.get_yaxis().set_visible(True)
        self.ax.get_xaxis().set_visible(True)
        self.ax.grid(linestyle='-', color='grey')
        self.ax.fill_between(xValues, int(ymin) - 1, yValues, facecolor='lightGreen')

        # Set axis/ticks
        self.ax.axis([xmin, xmax, ymin, ymax])
        self.ax.set_xticks(xTicks, minor=False)

        # Draw Graph
        self.ax.plot(xValues, yValues, color='green')
        self.canvas.draw()

    # Method to quit application
    def _quit(self, event=None):
        try:
            self.pmseLookup.logout()
        except AttributeError:
            pass
        self.window.quit()
        self.window.destroy()
        sys.exit()

    # Method to display about information
    def _about(self):
        tkmessagebox.showinfo('About', '{} v{}\n\n{} Stephen Bunting 2019\n{}'.format(data.title, data.version, chr(169), data.website_uri))

    # Method to open docs in web browser
    def _openHTTP(self):
        webbrowser.open("{}documentation.php".format(data.website_uri), new=2, autoraise=True)

    # Method to display settings box
    def _settings(self, event=None):
        global settingsExists, settings
        
        if self.settingsWindowOpen:
            self.settings.bringtofront()
        else:
            self.settingsWindowOpen = True
            self.settings = SettingsWindow()
            self.settings.settingsWindow.mainloop()
            self.settingsWindowOpen = False
            self._refresh()

    # Method to login to OFCOM Site
    def _ofcomLogin(self):
        lookup = ofcom.PMSELookup(plist['ofcomAccountName'], plist['ofcomUserName'], keyring.get_password(data.title, plist['ofcomAccountName']))
        
        # Login to OFCOM site
        try:
            lookup.login()
        except requests.exceptions.ConnectionError:
            tkmessagebox.showwarning('Connection Error', 'There was an error connecting to this service, please check your connection.')
            return False
        except ofcom.LoginError:
            if (tkmessagebox.askyesno('Login Fail', 'Could not login to pmse.ofcom.org.uk.\n\nWould you like to check your login details?')):
                self._settings()
            return False
        return lookup

    # Method to search OFCOM database and return a list of possible venues
    def _ofcomSearch(self, event=None):
        try:
            hasattr(self.pmseLookup, 'account_name')
        except AttributeError as e:
            self.pmseLookup = self._ofcomLogin()
            if not self.pmseLookup:
                return
        else:
            if not self.pmseLookup or not self.pmseLookup.loggedin:
                self.pmseLookup = self._ofcomLogin()
                if not self.pmseLookup:
                    return

        # Look up venues
        self.pmseLookupVenues = self.pmseLookup.getList(self.ofcomSearch.get())

        # Venues found
        if len(self.pmseLookupVenues[0]) > 0:
            self.ofcomBox['values'] = self.pmseLookupVenues[0]
            self.ofcomBox.config(state='enabled')

        # No venues found
        else:
            tkmessagebox.showwarning('No venues found', 'No venues found.\n\nTry editing your search term.')
            self.ofcomBox['values'] = self.ofcomVenueList
            self.ofcomBox.config(state='disabled')
        self.ofcomBox.current(0)

    # Method to retrieve data from OFCOM and generate exclusion file
    def _ofcomGenerate(self, event=None, io='Outside', filename=''):
        if len(self.pmseLookupVenues[0]) == 0:
            return False
        else:
            venueID = self.pmseLookupVenues[1][self.ofcomBox.current()]
            
            try:
                data = self.pmseLookup.getData(venueID)
            except requests.exceptions.Timeout:
                return False

            self.pmseLookup.xmlGenerate(data, io, filename)
            return filename

    # Check for latest version of software
    def _checkForUpdates(self, **kwargs):
        if 'display' in kwargs.keys():
            display = kwargs['display']
        else:
            display = True
        
        try:
            r = requests.get(data.update_file_location)
            updateConnection = True
        except requests.exceptions.ConnectionError:
            updateConnection = False

        if updateConnection:
            root = xml.etree.ElementTree.fromstring(r.text)
            latest = root[0][0].text
            download_uri = root[0][2].text
            if latest == data.version:
                if display:
                    tkmessagebox.showinfo("Check for Updates", "No updates found. You have the latest version of RF Library.")
            else:
                if (tkmessagebox.askyesno("Check for Updates", "There is a new version of RF Library available. Would you like to download v{}?".format(latest))):
                    webbrowser.open(download_uri, new=2 , autoraise=False)
        else:
            if display:
                    self._displayError(4)

    # Method to show an error message
    def _displayError(self, code):
        if code == 1:
            message = "Could not read from preferences file {}".format(data.plistName)
        elif code == 2:
            message = "Could not create preferences path {}".format(data.plistPath)
        elif code == 3:
            message = "Could not write preferences file {}".format(data.plistName)
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
