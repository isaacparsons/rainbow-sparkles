import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import max6675

from queue import Queue
import threading
import time

# set the pin for communicate with MAX6675
cs = 38
sck = 40
so = 36

# max6675.set_pin(CS, SCK, SO, unit)   [unit : 0 - raw, 1 - Celsius, 2 - Fahrenheit]
max6675.set_pin(cs, sck, so, 1)



class RealTimePlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Data Plotting")

        # Initialize data queue for thread communication
        self.data_queue = Queue()

        # Set up Matplotlib figure
        self.figure = Figure(figsize=(5, 4), dpi=100)
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
        self.start_button = tk.Button(self.root, text="Start", command=self.start_collection)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_collection, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        # State variables
        self.is_running = False
        self.data_thread = None
        self.x_data = []
        self.y_data = []

    def start_collection(self):
        """Start the data collection and real-time plotting."""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Start the data collection thread
            self.data_thread = threading.Thread(target=self.collect_data, daemon=True)
            self.data_thread.start()

            # Start the real-time plot updater
            self.update_plot()

    def stop_collection(self):
        """Stop the data collection."""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

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

            # Limit data to the last 20 points
            self.x_data = self.x_data[-20:]
            self.y_data = self.y_data[-20:]

            # Update the line data
            self.line.set_xdata(self.x_data)
            self.line.set_ydata(self.y_data)
            self.ax.set_xlim(max(0, len(self.x_data) - 20), len(self.x_data))

        # Redraw the canvas
        self.canvas.draw()

        # Schedule the next update
        self.root.after(100, self.update_plot)

# Create and run the Tkinter app
if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimePlotApp(root)
    root.mainloop()




# try:
#     while 1:
#         # read temperature connected at CS 22
#         print(max6675.read_temp(cs))
#         max6675.time.sleep(2)
# except KeyboardInterrupt:
#     pass





# # Initialize the main application window
# root = tk.Tk()
# root.title("Basic Tkinter App")

# # Set the dimensions of the main window
# root.attributes('-fullscreen', True)
# # root.geometry("400x300")

# # Add a button with a click action
# # def on_button_click():
# #     user_text = entry.get()
# #     if user_text:
# #         label.config(text=f"Hello, {user_text}!")
# #     else:
# #         label.config(text="Please enter your name!")

# # button = tk.Button(root, text="Greet", command=on_button_click)
# # button.pack(pady=10)


# # Create a figure for the graph
# fig = Figure(figsize=(5, 4), dpi=100)
# plot = fig.add_subplot(1, 1, 1)

# # Example data points
# x = [1, 2, 3, 4, 5]
# y = [10, 20, 15, 30, 25]
# plot.plot(x, y, marker='o')

# # Embed the figure into a Tkinter Canvas
# canvas = FigureCanvasTkAgg(fig, root)
# canvas_widget = canvas.get_tk_widget()
# canvas_widget.pack(pady=20)

# # Run the main event loop
# root.mainloop()
