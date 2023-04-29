import tkinter as tk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from file import TV_CHANNELS

class Chart:
    def __init__(self, frame):
        self.x_values = []
        self.y_values = []

        self.fig = matplotlib.figure.Figure(figsize=(3.2, 2.65), dpi=100, facecolor='white')
        self.axis = self.fig.add_subplot(111)
        self.axis.set_position([0.15, 0.1, 0.81, 0.81])
        self.canvas = FigureCanvasTkAgg(self.fig, frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.clear()

    def update(self, file, country):
        # Get x,y values
        previous = None
        self.x_values.clear()
        self.y_values.clear()

        for point in file.frequencies:
            if previous is None:
                previous = [point[0], point[1]]
            if previous[0] + (file.resolution * 2) < point[0]:
                self.x_values.append(previous[0] + file.resolution)
                self.y_values.append(-200)
                self.x_values.append(point[0] - file.resolution)
                self.y_values.append(-200)
            self.x_values.append(point[0])
            self.y_values.append(point[1])
            previous = point

        # Get axis values
        ymin = min(i for i in self.y_values if i > -120)
        ymax = max(self.y_values)
        ymin = int((ymin - 5) / 5) * 5 if ymin > -95 or ymin < -105 else -105
        ymax = int((ymax + 5) / 5) * 5 if ymax > ymin + 45 else ymin + 45

        # Get x tick values
        min_pixel_distance = 25
        axeswidth = self.axis.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted()).width * self.fig.dpi
        min_tick_distance = ((self.x_values[-1] - self.x_values[0]) * min_pixel_distance) / axeswidth
        x_ticks = []
        prev = 0
        tv_country = country if country == 'United States of America' else 'UK'
        for channel in TV_CHANNELS[tv_country]:
            if channel[1] - prev >= min_tick_distance \
                and file.frequencies[0][0] <= channel[1] \
                and file.frequencies[-1][0] >= channel[1]:
                x_ticks.append(channel[1])
                prev = channel[1]

        # Clear previous graph
        self.axis.clear()

        # Set Style
        self.axis.get_yaxis().set_visible(True)
        self.axis.get_xaxis().set_visible(True)
        self.axis.grid(linestyle='-', color='grey')
        self.axis.fill_between(self.x_values, int(ymin) - 1, self.y_values, facecolor='lightGreen')

        # Set axis/ticks
        self.axis.axis([self.x_values[0], self.x_values[-1], ymin, ymax])
        self.axis.set_xticks(x_ticks, minor=False)

        # Draw Graph
        self.axis.plot(self.x_values, self.y_values, color='green')
        self.canvas.draw()

    def clear(self):
        # Clear Graph
        self.axis.clear()

        # Set Style
        self.axis.set_facecolor('lightGrey')
        self.axis.grid(linestyle='None')
        self.axis.set_axisbelow(True)
        self.axis.set_xticks([])
        self.axis.set_yticks([])
        self.axis.set_xlabel('Frequency /MHz')
        self.axis.set_ylabel('Level /dBm')

        # Set Font
        matplotlib.rcParams.update({ 'font.size': 9 })

        # Draw Canvas
        self.canvas.draw()
