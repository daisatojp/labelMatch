import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PointMatcher.utils import *


class OpenPrevViewAction(QAction):

    def __init__(self, parent):
        super(OpenPrevViewAction, self).__init__('Open Prev View', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('prev')))
        self.setShortcut('a')
        self.triggered.connect(self.open_prev_view)
        self.setEnabled(True)

    def open_prev_view(self, _value=False):
        view_id_i = self.mw.matching.get_view_id_i()
        view_id_j = self.mw.matching.get_view_id_j()
        view_id_j = self.mw.matching.get_prev_view(view_id_j)
        self.mw.change_pair(view_id_i, view_id_j)
