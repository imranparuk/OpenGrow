import btree
import network
try:
    import urequests as requests
except ImportError:
    import requests

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('HUAWEI-B618-D500', 'J7M12T3RMNR')  # connect to an AP
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

url = 'http://192.168.8.130:5000/'

def get_data():
    r = requests.get(url)
    json_ret = r.json()
    r.close()
    return json_ret

def set_db():
    # First, we need to open a stream which holds a database
    # This is usually a file, but can be in-memory database
    # using uio.BytesIO, a raw flash partition, etc.
    # Oftentimes, you want to create a database file if it doesn't
    # exist and open if it exists. Idiom below takes care of this.
    # DO NOT open database with "a+b" access mode.

    try:
        f = open("mydb", "r+b")
    except OSError:
        f = open("mydb", "w+b")

    # Now open a database itself
    db = btree.open(f)

    data = get_data()

    for _key in data.keys():
        db[str(_key)] = data[_key]

    db.flush()

    print("data")
    for key in db:
        print(db[key])

    print("keys")
    for key in db:
        print(key)

    db.close()
    f.close()

do_connect()
set_db()