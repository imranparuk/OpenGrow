from ota import OTA
import network

def do_connect_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('HUAWEI-B618-D500', 'J7M12T3RMNR')  # connect to an AP
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

do_connect_network()

ota_url = 'http://192.168.8.130:5000/download/'
v_url = 'http://192.168.8.130:5000/version/'

o = OTA(ota_url, v_url)

import main
