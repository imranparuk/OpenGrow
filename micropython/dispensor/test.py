import machine
import utime as time

_in = machine.Pin(4, machine.Pin.IN)
# _out = machine.Pin(2 ,machine.Pin.OUT)

# _out.value(_in.value())
print(_in.value())