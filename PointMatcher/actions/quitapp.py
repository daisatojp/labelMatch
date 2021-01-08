import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class QuitAppAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(QuitAppAction, self).__init__('Quit App', parent)

        self.parent = parent
        self.setIcon(QtGui.QIcon(icon_path('quit')))
        self.setShortcut('Ctrl+Q')
        self.triggered.connect(self.parent.close)
        self.setEnabled(True)
