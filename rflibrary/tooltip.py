################################################################################
##########                      TOOLTIP OBJECT                        ##########
################################################################################

import tkinter as tk
from tkinter import ttk

# SOURCE:
# https://stackoverflow.com/questions/3221956/what-is-the-simplest-way-to-make-tooltips-in-tkinter

class CreateToolTip:
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # miliseconds
        self.wraplength = 250   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)
        self.widget.bind('<ButtonPress>', self.leave)
        self.id_value = None
        self.top_level = None

    def enter(self, _=None):
        self.schedule()

    def leave(self, _=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id_value = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id_value = self.id_value
        self.id_value = None
        if id_value:
            self.widget.after_cancel(id)

    def showtip(self):
        return
        x_pnt = y_pnt = 0
        x_pnt, y_pnt, _, _ = self.widget.bbox('insert')
        x_pnt += self.widget.winfo_rootx() + 25
        y_pnt += self.widget.winfo_rooty() + 20
        self.top_level = tk.Toplevel(self.widget)
        self.top_level.wm_geometry(f'+{x_pnt}+{y_pnt}')

        # Leaves only the label and removes the app window
        self.top_level.overrideredirect(True)
        label = ttk.Label(
            self.top_level,
            text=self.text,
            justify='left',
            background='#b0b0b0',
            relief='solid',
            borderwidth=1,
            padding=2,
            foreground='#4040ff',
            wraplength = self.wraplength)
        label.pack(ipadx=1)
        self.top_level.update()
        self.top_level.lift()

    def hidetip(self):
        top_level = self.top_level
        self.top_level = None
        if top_level:
            top_level.destroy()
