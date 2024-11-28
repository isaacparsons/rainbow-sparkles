import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import max6675

from queue import Queue
import threading
import time
import RPi.GPIO as GPIO
from smbus2 import SMBus
from bme280 import BME280

GPIO.setmode(GPIO.BOARD)
# bme 280
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

exhaust_relay_pin = 15 # exhaust control
coil_relay_pin = 13 # heating coil control
pump_pin = 12

# set the pin for communicate with MAX6675
cs = 38
sck = 40
so = 36

# max6675.set_pin(CS, SCK, SO, unit)   [unit : 0 - raw, 1 - Celsius, 2 - Fahrenheit]
max6675.set_pin(cs, sck, so, 1)


class PumpController(tk.Frame):
    def __init__(self, parent,  pin, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.pin = pin
        self.duty_cycle = 50
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 100)
        self.label = tk.Label(self, text="Extraction pump power: 50")

        self.label.pack()
        self.increment_btn = tk.Button(self, text="+", command=self.increment)
        self.decrement_btn = tk.Button(self, text="-", command=self.decrement)
        self.increment_btn.pack(side=tk.LEFT)
        self.decrement_btn.pack(side=tk.RIGHT)

    def start(self):
        self.pwm.start(self.duty_cycle)

    def stop(self):
        self.pwm.stop()

    def updatePowerLevel(self, dc):
        if dc <= 100 and dc >= 0:
            self.duty_cycle = dc
            self.pwm.ChangeDutyCycle(self.duty_cycle)
            self.label.config(text=f"Extraction pump power: {self.duty_cycle}")

    def increment(self):
        self.updatePowerLevel(self.duty_cycle + 10)

    def decrement(self):
        self.updatePowerLevel(self.duty_cycle - 10)

class RelayController(tk.Frame):
    def __init__(self, parent, title, pin, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.pin = pin        
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
        self.label = tk.Label(self, text=title)
        self.label.pack()
        self.open_button = tk.Button(self, text="Open", command=self.open_relay)
        self.open_button.pack(side=tk.LEFT)

        self.close_button = tk.Button(self, text="Close", command=self.close_relay)
        self.close_button.pack(side=tk.LEFT)

    def open_relay(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def close_relay(self):
        GPIO.output(self.pin, GPIO.LOW)

class Status(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = tk.Label(self, text="Status")
        self.label.pack()

class TemperatureControls(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

class BME280Status(tk.Frame):
    def __init__(self, parent, bme280,*args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.bme = bme280

        self.is_running = False

        self.temperature = 0.0
        self.pressure = 0.0
        self.humidity = 0.0

        self.temp_label = tk.Label(self, text="Temperature: ")
        self.pressure_label = tk.Label(self, text="Pressure: ")
        self.humidity_label = tk.Label(self, text="Humidity: ") 

        self.temp_label.grid(row=0, column=0)
        self.pressure_label.grid(row=1, column=0)
        self.humidity_label.grid(row=2, column=0)
 
    def update(self):
        if self.is_running:
            self.temperature = self.bme.get_temperature()
            self.pressure = self.bme.get_pressure()
            self.humidity = self.bme.get_humidity()
            self.temp_label.config(text=f"Temperature: {self.temperature:05.2f}°C")
            self.pressure_label.config(text=f"Pressure: {self.pressure:05.2f}hPa")
            self.humidity_label.config(text=f"Humidity: {self.humidity:05.2f}%")
            self.after(1000, self.update)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.update()

    def stop(self):
        self.is_running = False

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

class TemperatureGraph(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Initialize data queue for thread communication
        self.data_queue = Queue()

        # Set up Matplotlib figure
        self.figure = Figure(figsize=(2, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.line, = self.ax.plot([], [], marker='o')
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (c)")

        # Embed the Matplotlib figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Start/Stop button
        # self.start_button = tk.Button(self.root, text="Start", command=self.start_collection)
        # self.start_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_collection, state=tk.DISABLED)
        # self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        # State variables
        self.is_running = False
        self.data_thread = None
        self.x_data = []
        self.y_data = []

        self.start_collection()

    def start_collection(self):
        """Start the data collection and real-time plotting."""
        if not self.is_running:
            self.is_running = True
            # self.start_button.config(state=tk.DISABLED)
            # self.stop_button.config(state=tk.NORMAL)

            # Start the data collection thread
            self.data_thread = threading.Thread(target=self.collect_data, daemon=True)
            self.data_thread.start()

            # Start the real-time plot updater
            self.update_plot()

    def stop_collection(self):
        """Stop the data collection."""
        self.is_running = False
        # self.start_button.config(state=tk.NORMAL)
        # self.stop_button.config(state=tk.DISABLED)

    def collect_data(self):
        """Simulate data collection in a separate thread."""
        while self.is_running:
            time.sleep(1)  # Simulate a delay in data collection
            new_value = max6675.read_temp(cs)
            self.data_queue.put(new_value)

    def update_plot(self):
        """Update the plot with new data from the queue."""
        if not self.is_running:
            return

        while not self.data_queue.empty():
            # Get new data from the queue
            new_value = self.data_queue.get()
            self.x_data.append(len(self.x_data))  # Time step
            self.y_data.append(new_value)

            # Limit data to the last 5000 points
            self.x_data = self.x_data[-5000:]
            self.y_data = self.y_data[-5000:]
            
            # Update the line data
            x = self.x_data[-50:]
            y = self.y_data[-50:]
            self.line.set_xdata(x)
            self.line.set_ydata(y)
            self.ax.set_xlim(min(x), max(x))

            min_y = min(y) - 5
            max_y = max(y) + 5
            self.ax.set_ylim(min_y, max_y)
        
        self.canvas.draw() # Redraw the canvas
        self.after(100, self.update_plot) # Schedule the next update


#class RelayController:
#    def __init__(self, root):
#        self.root = root
#        self.root.title("Relay controller")
#        self.root.attributes('-fullscreen', True)

#        self.open_button = tk.Button(self.root, text="Open", command=self.open_relay)
#        self.open_button.pack(side=tk.LEFT, padx=10, pady=10)
        
#        self.close_button = tk.Button(self.root, text="Close", command=self.close_relay)
#        self.close_button.pack(side=tk.LEFT, padx=10, pady=10)

#    def open_relay(self):
#        GPIO.output(coil_relay_pin, GPIO.HIGH)

#    def close_relay(self):
#        GPIO.output(coil_relay_pin, GPIO.LOW)

#class ExhaustController:
#    def __init__(self, root):
#        self.root = root
#        self.root.title("Exhaust controller")
#        self.root.attributes('-fullscreen', True)

#        self.open_button = tk.Button(self.root, text="Open", command=self.open_relay)
#        self.open_button.pack(side=tk.LEFT, padx=10, pady=10)

#        self.close_button = tk.Button(self.root, text="Close", command=self.close_relay)
#        self.close_button.pack(side=tk.LEFT, padx=10, pady=10)

#    def open_relay(self):
#        GPIO.output(exhaust_relay_pin, GPIO.HIGH)

#    def close_relay(self):
#        GPIO.output(exhaust_relay_pin, GPIO.LOW)
# Create and run the Tkinter app
if __name__ == "__main__":
    #root = tk.Tk()
    #ExhaustController(root)
    #RealTimePlotApp(root)
    #RelayController(root)
    #root.mainloop()
    #while True:
    #    temperature = bme280.get_temperature()
    #    pressure = bme280.get_pressure()
    #    humidity = bme280.get_humidity()
    #    print(f"{temperature:05.2f}°C {pressure:05.2f}hPa {humidity:05.2f}%")
    #    time.sleep(1)
    app = App()
    app.start()
    app.mainloop()
