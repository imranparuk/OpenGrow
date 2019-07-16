from machine import Pin, I2C

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

print(i2c.scan())                      # scan for slaves, returning a list of 7-bit addresses
#
# print(lists)
# # while True:
#
# ret = b'G\1'
# i2c.writeto(0x04, ret)         # write 3 bytes to slave with 7-bit address 42
# sleep(1)
# ret = b'G\0'
# i2c.writeto(0x04, ret)         # write 3 bytes to slave with 7-bit address 42
# sleep(1)
