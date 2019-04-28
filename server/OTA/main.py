import machine
import time

pin = machine.Pin(2, machine.Pin.OUT)

while True:
    pin.off()
    time.sleep(0.5)
    pin.on()
    time.sleep(0.5)

