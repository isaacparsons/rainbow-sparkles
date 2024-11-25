import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import max6675

# set the pin for communicate with MAX6675
cs = 8
sck = 11
so = 9

# max6675.set_pin(CS, SCK, SO, unit)   [unit : 0 - raw, 1 - Celsius, 2 - Fahrenheit]
max6675.set_pin(cs, sck, so, 1)


try:
    while 1:
        # read temperature connected at CS 22
        a = max6675.read_temp(cs)

        # print temperature
        print a

        # when there are some errors with sensor, it return "-" sign and CS pin number
        # in this case it returns "-22" 
        
        max6675.time.sleep(2)
        
except KeyboardInterrupt:
    pass


# Initialize the main application window
# root = tk.Tk()
# root.title("Basic Tkinter App")

# # Set the dimensions of the main window
# root.geometry("400x300")

# # Add a button with a click action
# def on_button_click():
#     user_text = entry.get()
#     if user_text:
#         label.config(text=f"Hello, {user_text}!")
#     else:
#         label.config(text="Please enter your name!")

# button = tk.Button(root, text="Greet", command=on_button_click)
# button.pack(pady=10)


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
