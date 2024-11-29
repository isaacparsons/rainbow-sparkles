import tkinter as tk

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
