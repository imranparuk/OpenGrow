try:
    import urequests as requests
except ImportError:
    import requests

url = 'http://192.168.8.130:5000/'

r = requests.get(url)
print(r)
print(r.content)
print(r.text)
print(r.content)
print(r.json())

# It's mandatory to close response objects as soon as you finished
# working with them. On MicroPython platforms without full-fledged
# OS, not doing so may lead to resource leaks and malfunction.
r.close()