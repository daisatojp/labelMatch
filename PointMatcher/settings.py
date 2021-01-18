import os
import os.path as osp
import pickle


class Settings(object):
    def __init__(self):
        home = osp.expanduser('~')
        self.data = {}
        self.path = osp.join(home, '.PointMatcherSettings.pkl')

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        return default

    def save(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)

    def load(self):
        if osp.exists(self.path):
            with open(self.path, 'rb') as f:
                self.data = pickle.load(f)
                return True
