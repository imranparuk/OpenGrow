import os
import gc
import machine
import network
import ujson as json
import usocket as socket

class OTA(object):
    def __init__(self, url, filename):
        """
        https://gist.github.com/hiway/b3686a7839acca7d62e3a7234fdbb438
        """
        self.do_connect_network()
        self.url = url
        self.filename = filename
        self.get_file(self.url, self.filename, 'main.py')

    def http_get_async(self, url):
        _, _, host, path = url.split('/', 3)
        if ':' in host:
            host, port = host.split(':')
        else:
            port = 80
        addr = socket.getaddrinfo(host, int(port))[0][-1]
        s = socket.socket()
        s.connect(addr)
        s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host),
                     'utf8'))
        started = False
        header_str = b''
        headers = {}
        while True:
            data = s.recv(1000)
            if data:
                body_bytes = data
                if not started and b'HTTP' in body_bytes:
                    started = True
                    continue
                buffer = header_str + body_bytes
                if not headers and not b'\r\n\r\n' in buffer:
                    header_str += body_bytes
                    continue
                if b'\r\n\r\n' in buffer:
                    headers, body_bytes = buffer.split(b'\r\n\r\n')
                if body_bytes:
                    yield body_bytes
            else:
                break

    def http_get(self, url):
        response = b''
        try:
            get = self.http_get_async(url)
            while True:
                file_bytes = get.send(None)
                response += file_bytes
        except StopIteration:
            pass

        response_str = str(response, 'utf-8')
        return response_str

    @staticmethod
    def ensure_dirs(path):
        split_path = path.split('/')
        if len(split_path) > 1:
            for i, fragment in enumerate(split_path):
                parent = '/'.join(split_path[:-i])
                try:
                    os.mkdir(parent)
                except OSError:
                    pass

    def http_get_to_file(self, url, path):
        self.ensure_dirs(path)
        with open(path, 'w') as outfile:
            try:
                get = self.http_get_async(url)
                while True:
                    file_bytes = get.send(None)
                    outfile.write(file_bytes)
            except StopIteration:
                outfile.close()

    @staticmethod
    def do_connect_network():
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect('HUAWEI-B618-D500', 'J7M12T3RMNR')  # connect to an AP
            while not wlan.isconnected():
                pass
        print('network config:', wlan.ifconfig())

    def get_file(self, url, filename, new_filename):
        self.http_get_to_file('{}{}'.format(url, filename), '/new/{}'.format(new_filename))

    def update_file(self):
        os.rename('/new/{}'.format('main.py'), 'main.py')


class Response:

    def __init__(self, f):
        self.raw = f
        self.encoding = 'utf-8'
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        return ujson.loads(self.content)


class HttpClient:
    def request(self, method, url, data=None, json=None, headers={}, stream=None):
        try:
            proto, dummy, host, path = url.split('/', 3)
        except ValueError:
            proto, dummy, host = url.split('/', 2)
            path = ''
        if proto == 'http:':
            port = 80
        elif proto == 'https:':
            import ussl
            port = 443
        else:
            raise ValueError('Unsupported protocol: ' + proto)

        if ':' in host:
            host, port = host.split(':', 1)
            port = int(port)

        ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
        ai = ai[0]

        s = usocket.socket(ai[0], ai[1], ai[2])
        try:
            s.connect(ai[-1])
            if proto == 'https:':
                s = ussl.wrap_socket(s, server_hostname=host)
            s.write(b'%s /%s HTTP/1.0\r\n' % (method, path))
            if not 'Host' in headers:
                s.write(b'Host: %s\r\n' % host)
            # Iterate over keys to avoid tuple alloc
            for k in headers:
                s.write(k)
                s.write(b': ')
                s.write(headers[k])
                s.write(b'\r\n')
            # add user agent
            s.write('User-Agent')
            s.write(b': ')
            s.write('MicroPython OTAUpdater')
            s.write(b'\r\n')
            if json is not None:
                assert data is None
                import ujson
                data = ujson.dumps(json)
                s.write(b'Content-Type: application/json\r\n')
            if data:
                s.write(b'Content-Length: %d\r\n' % len(data))
            s.write(b'\r\n')
            if data:
                s.write(data)

            l = s.readline()
            # print(l)
            l = l.split(None, 2)
            status = int(l[1])
            reason = ''
            if len(l) > 2:
                reason = l[2].rstrip()
            while True:
                l = s.readline()
                if not l or l == b'\r\n':
                    break
                # print(l)
                if l.startswith(b'Transfer-Encoding:'):
                    if b'chunked' in l:
                        raise ValueError('Unsupported ' + l)
                elif l.startswith(b'Location:') and not 200 <= status <= 299:
                    raise NotImplementedError('Redirects not yet supported')
        except OSError:
            s.close()
            raise

        resp = Response(s)
        resp.status_code = status
        resp.reason = reason
        return resp

    def head(self, url, **kw):
        return self.request('HEAD', url, **kw)

    def get(self, url, **kw):
        return self.request('GET', url, **kw)

    def post(self, url, **kw):
        return self.request('POST', url, **kw)

    def put(self, url, **kw):
        return self.request('PUT', url, **kw)

    def patch(self, url, **kw):
        return self.request('PATCH', url, **kw)

    def delete(self, url, **kw):
        return self.request('DELETE', url, **kw)
