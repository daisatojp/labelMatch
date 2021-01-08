import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher import __appname__, __version__
from PointMatcher.utils.filesystem import icon_path


class ShowInfoAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(ShowInfoAction, self).__init__('Show Info', parent)

        self.p = parent
        self.setIcon(QtGui.QIcon(icon_path('help')))
        self.triggered.connect(self.showInfoDialog)
        self.setEnabled(True)

    def showInfoDialog(self):
        msg = '{0}\nversion : {1}'.format(__appname__, __version__)
        QtWidgets.QMessageBox.information(self.p, 'Information', msg)
