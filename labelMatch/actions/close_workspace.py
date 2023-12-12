import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from labelMatch.utils import *


class CloseWorkspaceAction(QAction):

    def __init__(self, parent):
        super(CloseWorkspaceAction, self).__init__('Close Workspace', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('close')))
        self.setShortcut('Ctrl+W')
        self.triggered.connect(self.close)
        self.setEnabled(True)

    def close(self, _value=False):
        if not self.mw.may_continue():
            return
        self.mw.close_workspace()
