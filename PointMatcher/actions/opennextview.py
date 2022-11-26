import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PointMatcher.utils import *


class OpenNextViewAction(QAction):

    def __init__(self, parent):
        super(OpenNextViewAction, self).__init__('Open Next View', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('next')))
        self.setShortcut('d')
        self.triggered.connect(self.open_next_view)
        self.setEnabled(True)

    def open_next_view(self, _value=False):
        view_id_i = self.mw.matching.get_view_id_i()
        view_id_j = self.mw.matching.get_view_id_j()
        view_id_j = self.mw.matching.get_next_view(view_id_j)
        self.mw.change_pair(view_id_i, view_id_j)
