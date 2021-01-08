import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class OpenPrevPairAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(OpenPrevPairAction, self).__init__('Open Prev Pair', parent)

        self.p = parent
        self.setIcon(QtGui.QIcon(icon_path('prev')))
        self.setShortcut('a')
        self.triggered.connect(self.openPrevPair)
        self.setEnabled(False)

    def openPrevPair(self, _value=False):
        if self.p.actions.autoSaving.isChecked():
            self.matching.save(self.p.savePath)
        view_id_i, view_id_j = self.p.matching.get_prev_view_pair()
        self.p.changePair(view_id_i, view_id_j)
