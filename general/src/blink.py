import machine
import time

pin = machine.Pin(2, machine.Pin.OUT)

while True:
    pin.low()
    time.sleep(0.5)
    pin.high()
    time.sleep(0.5)