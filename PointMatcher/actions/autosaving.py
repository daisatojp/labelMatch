import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class AutoSavingAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(AutoSavingAction, self).__init__('Auto Save Mode', parent)

        self.parent = parent
        self.setCheckable(True)
        self.setChecked(False)
