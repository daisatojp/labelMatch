import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from labelMatch import __appname__
from labelMatch.utils.filesystem import icon_path


QFD = QFileDialog


class OpenImageDirAction(QAction):

    def __init__(self, parent):
        super(OpenImageDirAction, self).__init__('Open Image Dir', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('open')))
        self.setShortcut('Ctrl+u')
        self.triggered.connect(self.open_image_dir)
        self.setEnabled(True)

    def open_image_dir(self, _value=False):
        if (self.mw.image_dir is not None) and osp.exists(self.mw.image_dir):
            default_dir = self.p.image_dir
        else:
            default_dir = '.'
        image_dir = QFD.getExistingDirectory(
            self.mw, '{} - Open Image Directory'.format(__appname__), default_dir,
            QFD.DontUseNativeDialog | QFD.ShowDirsOnly | QFD.DontResolveSymlinks)
        if osp.isdir(image_dir):
            self.mw.image_dir = image_dir
            self.mw.open_annot_dir_action.setEnabled(True)
