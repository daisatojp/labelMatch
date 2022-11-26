import os.path as osp
from PyQt5.QtWidgets import *


class AutoSaveAction(QAction):

    def __init__(self, parent):
        super(AutoSaveAction, self).__init__('Auto Save Mode', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setCheckable(True)
        self.setChecked(False)
        self.setEnabled(True)
