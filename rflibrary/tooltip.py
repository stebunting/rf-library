import tkinter as tk
from tkinter import ttk

# SOURCE:
# https://stackoverflow.com/questions/3221956/what-is-the-simplest-way-to-make-tooltips-in-tkinter

class ToolTip:
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # milliseconds
        self.wraplength = 250   # pixels
        self.text = text
        self.widget = widget
        self.id_value = None
        self.top_level = None

    def bind(self):
        self.widget.bind('<Enter>', self._enter)
        self.widget.bind('<Leave>', self._leave)
        self.widget.bind('<ButtonPress>', self._leave)

    def _enter(self, _=None):
        self._schedule()

    def _leave(self, _=None):
        self._unschedule()
        self._hide_tip()

    def _schedule(self):
        self._unschedule()
        self.id_value = self.widget.after(self.waittime, self._show_tip)

    def _unschedule(self):
        id_value = self.id_value
        self.id_value = None
        if id_value:
            self.widget.after_cancel(id_value)

    def _show_tip(self):
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

    def _hide_tip(self):
        top_level = self.top_level
        self.top_level = None
        if top_level:
            top_level.destroy()
