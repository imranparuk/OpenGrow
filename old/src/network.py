import network

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('HUAWEI-B618-D500', 'J7M12T3RMNR')  # connect to an AP
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

do_connect()