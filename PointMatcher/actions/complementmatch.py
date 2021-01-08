import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class ComplementMatchAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(ComplementMatchAction, self).__init__('Complement Match', parent)

        self.p = parent
        self.triggered.connect(self.complementMatch)
        self.setEnabled(True)

    def complementMatch(self):
        pass
