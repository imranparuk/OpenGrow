#!/usr/bin/env bash

ampy -p /dev/ttyUSB0 put light-controller/ota.py
ampy -p /dev/ttyUSB0 put light-controller/boot.py
ampy -p /dev/ttyUSB0 put light-controller/version.json

# ampy -p /dev/ttyUSB0 put main.py
ampy -p /dev/ttyUSB0 run light-controller/main.py
