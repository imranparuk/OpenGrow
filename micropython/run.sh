#!/usr/bin/env bash

esptool.py --port /dev/ttyUSB1 erase_flash
esptool.py --port /dev/ttyUSB1 --baud 460800 write_flash --flash_size=detect 0 old/firmware/esp8266-20190125-v1.10.bin


#esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
#esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 old/firmware/esp32-20190125-v1.10.bin