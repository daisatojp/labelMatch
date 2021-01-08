import os.path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog
from PointMatcher import __appname__
from PointMatcher.utils.filesystem import icon_path


QFD = QFileDialog


class OpenDirAction(QAction):

    def __init__(self, parent):
        super(OpenDirAction, self).__init__('Open Dir', parent)

        self.p = parent
        self.setIcon(QIcon(icon_path('open')))
        self.setShortcut('Ctrl+u')
        self.triggered.connect(self.openDir)
        self.setEnabled(True)

    def openDir(self, _value=False):
        if self.p.imageDir and osp.exists(self.p.imageDir):
            defaultDir = self.p.imageDir
        else:
            defaultDir = '.'
        self.p.imageDir = QFileDialog.getExistingDirectory(
            self.p, '{} - Open Directory'.format(__appname__), defaultDir,
            QFD.ShowDirsOnly | QFD.DontResolveSymlinks)
