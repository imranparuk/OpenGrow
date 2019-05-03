#!/usr/bin/env bash

esptool.py --port /dev/ttyUSB0 erase_flash
#
#esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 firmware/esp8266-20170108-v1.8.7.bin

esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 old/firmware/esp8266-20190125-v1.10.bin
##ampy --port /dev/ttyUSB0 put main.py

#ampy -p /dev/ttyUSB0 put main.py
#ampy -p /dev/ttyUSB0 get main.py
#ampy -p /dev/ttyUSB0 run light-controller/main.py


#
#esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
#esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 firmware/esp32-20190125-v1.10.bin