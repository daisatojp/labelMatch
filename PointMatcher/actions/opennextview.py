import os.path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PointMatcher.utils.filesystem import icon_path


class OpenNextViewAction(QAction):

    def __init__(self, parent):
        super(OpenNextViewAction, self).__init__('Open Next View', parent)

        self.p = parent
        self.setIcon(QIcon(icon_path('next')))
        self.setShortcut('d')
        self.triggered.connect(self.openNextView)
        self.setEnabled(False)

    def openNextView(self, _value=False):
        if self.p.actions.autoSaving.isChecked():
            self.p.matching.save()
        view_id_i = self.p.matching.get_view_id_i()
        view_id_j = self.p.matching.get_view_id_j()
        view_id_j = self.p.matching.get_next_view(view_id_j)
        self.p.changePair(view_id_i, view_id_j)
