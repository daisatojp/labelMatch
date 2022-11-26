import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PointMatcher.utils import *


class SaveAction(QAction):

    def __init__(self, parent):
        super(SaveAction, self).__init__('Save', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('save')))
        self.setShortcut('Ctrl+S')
        self.triggered.connect(self.save)
        self.setEnabled(False)

    def save(self, _value=False):
        self.mw.matching.save()
        self.mw.actions.save.setEnabled(False)
