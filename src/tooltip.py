#!/usr/bin/env python3

################################################################################
##########                      TOOLTIP OBJECT                        ##########
################################################################################

import tkinter as tk
import tkinter.ttk as ttk

# SOURCE: https://stackoverflow.com/questions/3221956/what-is-the-simplest-way-to-make-tooltips-in-tkinter

class CreateToolTip(object):
    
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # miliseconds
        self.wraplength = 250   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)
        self.widget.bind('<ButtonPress>', self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox('insert')
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_geometry('+%d+%d' % (x, y))

        # Leaves only the label and removes the app window
        self.tw.overrideredirect(True)
        label = ttk.Label(self.tw, text=self.text, justify='left',
                       background='#b0b0b0', relief='solid', borderwidth=1, padding=2, foreground='#4040ff',
                       wraplength = self.wraplength)
        label.pack(ipadx=1)
        self.tw.update()
        self.tw.lift()
        
    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()