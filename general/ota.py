import os
import gc
import machine
import urequests as requests

from utils import read_json_file, write_json_file, get_device_json

SRC_FILENAME = 'main.py'
VERSION_FILENAME = 'config.json'

class OTA(object):
    def __init__(self, url, v_url, _type):
        """
        https://gist.github.com/hiway/b3686a7839acca7d62e3a7234fdbb438
        """
        self.url = url
        self.v_url = v_url
        self.type = _type

        online, lv, ov = self.get_versions()
        if online:
            self.ensure_dirs('/new/')
            self.download_file("{}{}".format(self.url, SRC_FILENAME), '/new/{}'.format(SRC_FILENAME))
            self.update_file()
            self.update_version(ov)
            self.delete_files()

    def get_versions(self):
        print('getting versions and comparing')
        ov = self.get_version_online(self.v_url)
        lv = self.get_version_local()
        return self.compare_versions(ov, lv), lv, ov

    def get_version_online(self, url):
        try:
            response = requests.post(url, json=get_device_json(self.type))
            data = response.json()
            version = data['version']
            response.close()
            return self.version_string_to_list(version)
        except OSError:
            print("OS")
            return None

    def get_version_local(self):
        data = read_json_file("/{}".format(VERSION_FILENAME))
        version = data['version']
        return self.version_string_to_list(version)

    def update_version(self, ov):
        data = read_json_file("/{}".format(VERSION_FILENAME))
        ov = [str(i) for i in ov]
        data['version'] = '.'.join(ov)
        write_json_file("/{}".format(VERSION_FILENAME), data)

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
                response = requests.post(url, json=get_device_json(self.type))
                outfile.write(response.text)
            finally:
                response.close()
                outfile.close()
                gc.collect()

    def update_file(self):
        print("moving paths from {} to {}".format('/new/main.py', '/main.py'))
        os.rename('/new/{}'.format(SRC_FILENAME), '/main.py')

    def delete_files(self):
        pass

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

