import os.path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QFileDialog
from PointMatcher import __appname__
from PointMatcher.utils.filesystem import icon_path


QFD = QFileDialog


class OpenImageDirAction(QAction):

    def __init__(self, parent):
        super(OpenImageDirAction, self).__init__('Open Image Dir', parent)
        self.p = parent

        self.setIcon(QIcon(icon_path('open')))
        self.setShortcut('Ctrl+u')
        self.triggered.connect(self.openImageDir)
        self.setEnabled(True)

    def openImageDir(self, _value=False):
        if (self.p.imageDir is not None) and osp.exists(self.p.imageDir):
            defaultDir = self.p.imageDir
        else:
            defaultDir = '.'
        imageDir = QFileDialog.getExistingDirectory(
            self.p, '{} - Open Image Directory'.format(__appname__), defaultDir,
            QFD.ShowDirsOnly | QFD.DontResolveSymlinks)
        if osp.isdir(imageDir):
            self.p.imageDir = imageDir
            self.p.actions.openAnnotDir.setEnabled(True)
