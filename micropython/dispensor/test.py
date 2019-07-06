import btree
import network
import machine
import utime
import uos as os
import ujson as json
import urequests as requests
import ustruct as struct
import usocket as socket
import uasyncio as asyncio
#
# LED_PIN = 2
#
# def get_data(_url):
#     try:
#         r = requests.get(_url)
#         json_ret = r.json()
#         r.close()
#         return json_ret
#     except OSError:
#         print("OSError in request")
#         return None
#     except MemoryError:
#         pass
#
# async def pulse(pin, ms):
#     pin.off()
#     await asyncio.sleep_ms(ms)
#     pin.on()
#
# data = {
#     2: 10,
#     4: 15,
#     5: 20,
#     12: 25
# }
#
# time_const = 5
#
# pins = {}
# for pin, dispense_val in data.items():
#     _temp = machine.Pin(pin, machine.Pin.OUT)
#     pulse(_temp, 10000)
# print("done")
#
#
#
# print("test")
# print(machine.unique_id())
#
# ota_url = 'http://192.168.8.130:5000/download/'
# v_url = 'http://192.168.8.130:5000/version/'
#
# from utils import do_connect_network
#
#
# def get_version_online( url):
#
#     _data = {
#         "device_id": [i for i in machine.unique_id()],
#         "type": "abv"
#     }
#     print('getting version online')
#     try:
#         response = requests.post(url, json=_data)
#         data = response.json()
#         version = data['version']
#         print(version)
#     except OSError:
#         return None
#
# do_connect_network()
# get_version_online(v_url)

# import upip
#
# upip.install("micropython-datetime")

import datetime

a = datetime.datetime()