import urequests as requests
import btree
import ujson as json
from utils import get_data



class Db(object):
    def __init__(self, url, db_name="default_db"):
        self.url = url

        self.f = self.db_init(db_name)
        self.db = btree.open(self.f)
        self.db_delete()

    def __del__(self):
        self.f.close()
        self.db.close()

    def __call__(self, *args, **kwargs):
        return self.process_data_get()

    @staticmethod
    def db_init(dbname):
        try:
            f = open(dbname, "r+b")
            print("db opened")
        except OSError:
            f = open(dbname, "w+b")
            print("db created")
        return f

    def db_print(self):
        for key in self.db.keys():
            print(key)

    def db_delete(self):
        for key in self.db.keys():
            del self.db[key]

    def db_save(self, data):
        for key in data.keys():
            self.db[key] = json.dumps(data[key])
        self.db.flush()

    def db_load(self):
        ret_dict = {}
        for key in self.db.keys():
            ret_dict[key] = json.loads(self.db[key])
        return ret_dict

    def process_data_get(self):
        data = get_data(self.url)
        if data is not None:
            self.db_save(data)
            return True
        return False