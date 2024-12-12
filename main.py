import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import max6675
from pump_controller import PumpController
from relay_controller import RelayController
from bme280_status import BME280Status
from temperature_graph import TemperatureGraph
from pid import PID

from queue import Queue
import threading
import time
import RPi.GPIO as GPIO
from smbus2 import SMBus
from bme280 import BME280

GPIO.setmode(GPIO.BOARD)

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

exhaust_relay_pin = 15 # exhaust control
coil_relay_pin = 13 # heating coil control
pump_pin = 12

cs = 38
sck = 40
so = 36

max6675.set_pin(cs, sck, so, 1) # 1 is for celsius


class TemperatureDataPoint:
    def __init__(self, timestamp, value):
        self.timestamp = timestamp
        self.value = value

class DataCollection:
    def __init__(self):
        self.timestamp = 0
        self.collection_interval = 1 
        self.temperature_queue = Queue
        self.running = False
        self.data_thread = None

    def start(self):
        self.data_thread = threading.Thread(target=self.collect_data, daemon=True)
        self.data_thread.start()

    def collect_data(self):
        while self.running:
            time.sleep(self.collection_interval)
            val = max6675.read_temp(cs)
            self.temperature_queue.put(TemperatureDataPoint(self.timestamp, val))
            self.timestamp += 1

    def stop(self):
        self.running = false


class Status(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(self, text="Status")
        self.label.pack()

class TemperatureControls(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("app")
        self.attributes('-fullscreen', True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.status = Status(self)
        self.exhaust = RelayController(self, "Exhaust", exhaust_relay_pin)
        self.heater = RelayController(self, "Heater", coil_relay_pin)
        self.tempGraph = TemperatureGraph(self)
        self.bmeStatus = BME280Status(self, bme280)
        self.pump_control = PumpController(self, pump_pin)

        self.status.grid(row=0, column=3, rowspan=1, stick="nsew")
        self.exhaust.grid(row=1, column=3, rowspan=1, sticky="nsew")
        self.heater.grid(row=2, column=3, rowspan=1, sticky="nsew")
        self.tempGraph.grid(row=0, column=0, rowspan=2, columnspan=3, sticky="nsew")
        self.bmeStatus.grid(row=2, column=0, rowspan=1, columnspan=2, sticky="nsew")
        self.pump_control.grid(row=3, column=3, rowspan=1, columnspan=1, stick="nsew")

    def start(self):
        self.bmeStatus.start()
        self.pump_control.start()

if __name__ == "__main__":
    app = App()
    app.start()
    app.mainloop()
