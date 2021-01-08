import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher import __appname__
from PointMatcher.utils.filesystem import icon_path


class OpenDirAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(OpenDirAction, self).__init__('Open Dir', parent)

        self.parent = parent
        self.setIcon(QtGui.QIcon(icon_path('open')))
        self.setShortcut('Ctrl+u')
        self.triggered.connect(self.openDir)
        self.setEnabled(True)

    def openDir(self, _value=False):
        if self.parent.imageDir and osp.exists(self.parent.imageDir):
            defaultDir = self.imageDir
        else:
            defaultDir = '.'
        self.parent.imageDir = QtWidgets.QFileDialog.getExistingDirectory(
            self.parent, '{} - Open Directory'.format(__appname__), defaultDir,
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
