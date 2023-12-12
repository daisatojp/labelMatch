import os
import os.path as osp
import json
from PyQt5.QtWidgets import QMessageBox as QMB
from labelMatch.defines import *


class Settings(object):

    def __init__(self):
        self.data = None
        if not osp.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'w') as f:
                json.dump({
                    'annot_dir': None,
                    'image_dir': None
                }, f, indent=4)
        self.load()

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def save(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def load(self):
        with open(SETTINGS_FILE, 'r') as f:
            self.data = json.load(f)

    def get(self, keys, default=None):
        if type(keys) is str:
            keys = [keys]
        v = self.data
        for key in keys:
            if key not in v:
                v = None
                break
            v = v[key]
        if v is None:
            return default
        else:
            return v

    def set(self, keys, value):
        if type(keys) is str:
            keys = [keys]
        v = self.data
        for key in keys[:-1]:
            if key not in v:
                v[key] = {}
            v = v[key]
        v[keys[-1]] = value
