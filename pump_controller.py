import tkinter as tk
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

class PumpController(tk.Frame):
    def __init__(self, parent,  pin, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.pin = pin
        self.duty_cycle = 0
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
            if self.duty_cycle == 100:
                self.increment_btn.config(state=tk.DISABLED)
            elif self.duty_cycle == 0:
                self.decrement_btn.config(state=tk.DISABLED)
            else:
                self.increment_btn.config(state=tk.NORMAL)
                self.decrement_btn.config(state=tk.NORMAL)

    def increment(self):
        self.updatePowerLevel(self.duty_cycle + 10)

    def decrement(self):
        self.updatePowerLevel(self.duty_cycle - 10)
