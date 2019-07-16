#!/usr/bin/env bash

ampy -p /dev/ttyUSB4 put general/boot.py
ampy -p /dev/ttyUSB4 put general/ota.py
ampy -p /dev/ttyUSB4 put general/utils.py
ampy -p /dev/ttyUSB4 put general/rtc.py
ampy -p /dev/ttyUSB4 put general/config.json
ampy -p /dev/ttyUSB4 put general/db.py

ampy -p /dev/ttyUSB4 put light-controller/main.py
