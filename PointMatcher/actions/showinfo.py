import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PointMatcher import __appname__, __version__
from PointMatcher.utils import *


QMB = QMessageBox


class ShowInfoAction(QAction):

    def __init__(self, parent):
        super(ShowInfoAction, self).__init__('Show Info', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('help')))
        self.triggered.connect(self.show_info_dialog)
        self.setEnabled(True)

    def show_info_dialog(self):
        msg = '{0}\nversion : {1}'.format(__appname__, __version__)
        QMB.information(self.p, 'Information', msg)
