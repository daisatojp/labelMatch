import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class SanityCheckAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(SanityCheckAction, self).__init__('Sanity Check', parent)

        self.p = parent
        self.triggered.connect(self.sanityCheck)
        self.setEnabled(True)

    def sanityCheck(self):
        pass
