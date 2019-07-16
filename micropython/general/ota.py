import os
import gc
import machine
import urequests as requests

from utils import read_json_file, write_json_file, get_device_id_list

SRC_FILENAME = 'main.py'
VERSION_FILENAME = 'config.json'
NEW_SRC = 'new'

class OTA(object):
    def __init__(self, url, _type):
        """
        https://gist.github.com/hiway/b3686a7839acca7d62e3a7234fdbb438
        """
        self.url = url
        self.type = _type
        self.device = get_device_id_list()

        self.lv = self.get_version_local()

        online, self.ov, self.files, self.files_url = self.get_data_online()

        if online:
            self.download_files(self.files, self.files_url)

    def __call__(self, *args, **kwargs):
        self.update_files(self.files)

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

    def get_data_online(self):
        print('getting versions and comparing')
        ov, data, url = self.get_online_data(self.url)
        return self.compare_versions(ov, self.lv), ov, data, url

    def get_online_data(self, url):
        json_payload = {
            "deviceId": self.device,
            "type": self.type,
            "version":  self.lv,
            "$OPTION": ["$GET_VERSION", "$GET_FILES"]
        }
        try:
            response = requests.post(url, json=json_payload)
            data = response.json()
            version = data['version']
            files = data['files']
            files_url = data['filesUrl']
            response.close()
            return self.version_string_to_list(version), files, files_url
        except OSError:
            print("OS")
            return None

    def download_file(self, url, path):
        print('Downloading (path, url): {} , {}'.format(path, url))
        with open(path, 'w') as outfile:
            json_payload = {
                "deviceId": self.device,
                "type": self.type,
                "version": self.lv,
                "$OPTION": {
                    "$DOWNLOAD_FILE": url
                }
            }
            try:
                response = requests.post(url, json=json_payload)
                outfile.write(response.text)
            finally:
                response.close()
                outfile.close()
                gc.collect()

    def download_files(self, file_list, files_url):
        self.ensure_dirs('/{}/'.format(NEW_SRC))
        print(file_list)
        for file in file_list:
            self.download_file("{}/{}".format(files_url, file), '/{}/{}'.format(NEW_SRC, file))

    def update_file(self, file):
        os.rename('/{}/{}'.format(NEW_SRC, file), '/{}'.format(file))

    def update_files(self, files):
        for file in files:
            self.update_file(file)

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

