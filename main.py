import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import max6675

from queue import Queue
import threading
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) 
coil_relay_pin = 13
GPIO.setup(coil_relay_pin, GPIO.OUT, initial = GPIO.LOW)    

# set the pin for communicate with MAX6675
cs = 38
sck = 40
so = 36

# max6675.set_pin(CS, SCK, SO, unit)   [unit : 0 - raw, 1 - Celsius, 2 - Fahrenheit]
max6675.set_pin(cs, sck, so, 1)

class RealTimePlotApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.title("Real-Time Data Plotting")

        # Initialize data queue for thread communication
        self.data_queue = Queue()

        # Set up Matplotlib figure
        self.figure = Figure(figsize=(2, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.line, = self.ax.plot([], [], marker='o')
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 100)
        self.ax.set_title("Real-Time Plot")
        self.ax.set_xlabel("Time Step")
        self.ax.set_ylabel("Value")

        # Embed the Matplotlib figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
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
        self.root.after(100, self.update_plot) # Schedule the next update


class RelayController:
    def __init__(self, root):
        self.root = root
        self.root.title("Relay controller")
        self.root.attributes('-fullscreen', True)

        self.open_button = tk.Button(self.root, text="Open", command=self.open_relay)
        self.open_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.close_button = tk.Button(self.root, text="Close", command=self.close_relay)
        self.close_button.pack(side=tk.LEFT, padx=10, pady=10)

    def open_relay(self):
        GPIO.output(coil_relay_pin, GPIO.HIGH)

    def close_relay(self):
        GPIO.output(coil_relay_pin, GPIO.LOW)

# Create and run the Tkinter app
if __name__ == "__main__":
    root = tk.Tk()
    RealTimePlotApp(root)
    RelayController(root)
    root.mainloop()