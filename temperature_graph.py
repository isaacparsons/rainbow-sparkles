import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import time

class TemperatureGraph(tk.Frame):
    def __init__(self, parent, data_queue, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_queue = data_queue

        self.update_interval = 100

        self.figure = Figure(figsize=(2, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.line, = self.ax.plot([], [], marker='o')
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (c)")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.x_data = []
        self.y_data = []

        self.update_plot()

    def update_plot(self):
        while not self.data_queue.empty():
            new_value = self.data_queue.get()
            self.x_data.append(len(self.x_data))
            self.y_data.append(new_value)

            # Limit data to the last 5000 points
            self.x_data = self.x_data[-1000:]
            self.y_data = self.y_data[-1000:]

            x = self.x_data[-100:]
            y = self.y_data[-100:]
            self.line.set_xdata(x)
            self.line.set_ydata(y)
            self.ax.set_xlim(min(x), max(x))

            min_y = min(y) - 1
            max_y = max(y) + 1
            self.ax.set_ylim(min_y, max_y)

        self.canvas.draw()
        self.after(100, self.update_plot)
