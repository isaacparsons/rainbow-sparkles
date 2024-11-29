import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from queue import Queue
import threading
import time
import RPi.GPIO as GPIO
import max6675

# set the pin for communicate with MAX6675
cs = 38
sck = 40
so = 36

# max6675.set_pin(CS, SCK, SO, unit)   [unit : 0 - raw, 1 - Celsius, 2 - Fahrenheit]
max6675.set_pin(cs, sck, so, 1)


class TemperatureGraph(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_queue = Queue()

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

        self.is_running = False
        self.data_thread = None
        self.x_data = []
        self.y_data = []

        self.start_collection()

    def start_collection(self):
        if not self.is_running:
            self.is_running = True
            self.data_thread = threading.Thread(target=self.collect_data, daemon=True)
            self.data_thread.start()
            self.update_plot()

    def stop_collection(self):
        self.is_running = False

    def collect_data(self):
        while self.is_running:
            time.sleep(1)
            new_value = max6675.read_temp(cs)
            self.data_queue.put(new_value)

    def update_plot(self):
        if not self.is_running:
            return

        while not self.data_queue.empty():
            new_value = self.data_queue.get()
            self.x_data.append(len(self.x_data))
            self.y_data.append(new_value)

            # Limit data to the last 5000 points
            self.x_data = self.x_data[-5000:]
            self.y_data = self.y_data[-5000:]

            x = self.x_data[-50:]
            y = self.y_data[-50:]
            self.line.set_xdata(x)
            self.line.set_ydata(y)
            self.ax.set_xlim(min(x), max(x))

            min_y = min(y) - 5
            max_y = max(y) + 5
            self.ax.set_ylim(min_y, max_y)

        self.canvas.draw()
        self.after(100, self.update_plot)
