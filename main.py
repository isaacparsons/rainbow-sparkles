# import sys
# import random
# from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         # Set the main window properties
#         self.setWindowTitle("PyQt5 Line Graph with Button")
#         self.setGeometry(100, 100, 800, 600)

#         # Create a QWidget to hold the layout
#         main_widget = QWidget()
#         self.setCentralWidget(main_widget)

#         # Create a layout and add it to the main widget
#         self.layout = QVBoxLayout(main_widget)

#         # Create a Matplotlib figure and canvas
#         self.figure = Figure()
#         self.canvas = FigureCanvas(self.figure)

#         # Add the canvas to the layout
#         self.layout.addWidget(self.canvas)

#         # Create a button
#         self.button = QPushButton("Update Graph")
#         self.button.clicked.connect(self.update_graph)
#         self.layout.addWidget(self.button)

#         # Initial graph plot
#         self.plot_line_graph()

#     def plot_line_graph(self):
#         # Clear the figure to avoid overlaying plots
#         self.figure.clear()

#         # Get the figure's axes
#         ax = self.figure.add_subplot(111)

#         # Example data for the line graph
#         self.x = [1, 2, 3, 4, 5]
#         self.y = [10, 20, 15, 25, 30]

#         # Plot the data
#         ax.plot(self.x, self.y, marker='o', label='Line 1')

#         # Set the title and labels
#         ax.set_title("Simple Line Graph")
#         ax.set_xlabel("X-axis")
#         ax.set_ylabel("Y-axis")

#         # Add a legend
#         ax.legend()

#         # Refresh the canvas to display the graph
#         self.canvas.draw()

#     def update_graph(self):
#         # Generate random data for the graph
#         self.y = [random.randint(10, 50) for _ in self.x]

#         # Replot the graph with updated data
#         self.plot_line_graph()

# # PyQt5 application setup
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())


import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize the main application window
root = tk.Tk()
root.title("Basic Tkinter App")

# Set the dimensions of the main window
root.geometry("400x300")

# Add a label
label = tk.Label(root, text="Welcome to Tkinter!", font=("Arial", 16))
label.pack(pady=10)

# Add an entry box
entry = tk.Entry(root, width=30)
entry.pack(pady=10)

# Add a button with a click action
def on_button_click():
    user_text = entry.get()
    if user_text:
        label.config(text=f"Hello, {user_text}!")
    else:
        label.config(text="Please enter your name!")

button = tk.Button(root, text="Greet", command=on_button_click)
button.pack(pady=10)


# Create a figure for the graph
fig = Figure(figsize=(5, 4), dpi=100)
plot = fig.add_subplot(1, 1, 1)

# Example data points
x = [1, 2, 3, 4, 5]
y = [10, 20, 15, 30, 25]
plot.plot(x, y, marker='o')

# Embed the figure into a Tkinter Canvas
canvas = FigureCanvasTkAgg(fig, root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(pady=20)

# Run the main event loop
root.mainloop()
