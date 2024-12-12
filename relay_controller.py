import tkinter as tk
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

class RelayController(tk.Frame):
    def __init__(self, parent, title, pin, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.pin = pin        
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH)
        self.label = tk.Label(self, text=title)
        self.label.pack()
        self.open_button = tk.Button(self, text="Open", command=self.open_relay)
        self.open_button.pack(side=tk.LEFT)

        self.close_button = tk.Button(self, text="Close", command=self.close_relay, state=tk.DISABLED)
        self.close_button.pack(side=tk.LEFT)

    def open_relay(self):
        self.open_button.config(state=tk.DISABLED)
        self.close_button.config(state=tk.NORMAL)
        GPIO.output(self.pin, GPIO.LOW)

    def close_relay(self):
        self.open_button.config(state=tk.NORMAL)
        self.close_button.config(state=tk.DISABLED)
        GPIO.output(self.pin, GPIO.HIGH)
