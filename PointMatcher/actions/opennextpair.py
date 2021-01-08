import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class OpenNextPairAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(OpenNextPairAction, self).__init__('Open Next Pair', parent)

        self.p = parent
        self.setIcon(QtGui.QIcon(icon_path('next')))
        self.setShortcut('d')
        self.triggered.connect(self.openNextPair)
        self.setEnabled(False)

    def openNextPair(self, _value=False):
        if self.p.actions.autoSaving.isChecked():
            self.p.matching.save(self.p.savePath)
        view_id_i, view_id_j = self.p.matching.get_next_view_pair()
        self.p.changePair(view_id_i, view_id_j)
