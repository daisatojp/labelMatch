import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class CloseFileAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(CloseFileAction, self).__init__('Close File', parent)

        self.parent = parent
        self.setIcon(QtGui.QIcon(icon_path('close')))
        self.setShortcut('Ctrl+W')
        self.triggered.connect(self.closeFile)
        self.setEnabled(True)

    def closeFile(self, _value=False):
        if not self.parent.mayContinue():
            return
