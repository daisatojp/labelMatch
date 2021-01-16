import os.path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PointMatcher.utils.filesystem import icon_path


class OpenPrevViewAction(QAction):

    def __init__(self, parent):
        super(OpenPrevViewAction, self).__init__('Open Prev View', parent)
        self.p = parent

        self.setIcon(QIcon(icon_path('prev')))
        self.setShortcut('a')
        self.triggered.connect(self.openPrevView)
        self.setEnabled(False)

    def openPrevView(self, _value=False):
        if self.p.actions.autoSaving.isChecked():
            self.matching.save()
        view_id_i = self.p.matching.get_view_id_i()
        view_id_j = self.p.matching.get_view_id_j()
        view_id_j = self.p.matching.get_prev_view(view_id_j)
        self.p.changePair(view_id_i, view_id_j)
