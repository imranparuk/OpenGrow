import os
import gc
import machine
import network
import ujson as json
import usocket as socket
import urequests as requests

SRC_FILENAME = 'main.py'
VERSION_FILENAME = 'version.json'

class OTA(object):
    def __init__(self, url, v_url):
        """
        https://gist.github.com/hiway/b3686a7839acca7d62e3a7234fdbb438
        """
        self.url = url
        self.v_url = v_url

        if self.get_online():
            self.ensure_dirs('/new/')
            self.download_file("{}{}".format(self.url, SRC_FILENAME), '/new/{}'.format(SRC_FILENAME))
            self.update_file()
            # machine.reset()

    def get_online(self):
        ov = self.get_version_online(self.v_url)
        lv = self.get_version_local()
        return self.compare_versions(ov, lv)

    def get_version_online(self, url):
        print('getting version online')
        try:
            response = requests.get(url)
            data = response.json()
            version = data['version']
            response.close()
            return self.version_string_to_list(version)
        except IOError:
            return None

    def get_version_local(self):
        print('getting version local')
        try:
            with open("/{}".format(VERSION_FILENAME)) as f:
                data = json.loads(f.read())
                version = data['version']
                return self.version_string_to_list(version)
        except IOError:
            return None

    @staticmethod
    def compare_versions(v1, v2):
        both = zip(v1, v2)
        for i in both:
            v_1, v_2 = i
            if v_1 > v_2:
                return True
        return False

    @staticmethod
    def version_string_to_list(v):
        data = v.split('.', 3)
        return [int(i) for i in data]

    def download_file(self, url, path):
        print('Downloading (path, url): {} , {}'.format(path, url))

        with open(path, 'w') as outfile:
            try:
                response = requests.get(url)
                outfile.write(response.text)
            finally:
                response.close()
                outfile.close()
                gc.collect()

    def update_file(self):
        print("moving paths from {} to {}".format('/new/main.py', '/main.py'))
        os.rename('/new/{}'.format(SRC_FILENAME), '/main.py')

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

