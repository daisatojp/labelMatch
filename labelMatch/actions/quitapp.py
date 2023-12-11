import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from labelMatch.utils import *


class QuitAppAction(QAction):

    def __init__(self, parent):
        super(QuitAppAction, self).__init__('Quit App', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('quit')))
        self.setShortcut('Ctrl+Q')
        self.triggered.connect(self.mw.close)
        self.setEnabled(True)
