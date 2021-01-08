import os.path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PointMatcher.utils.filesystem import icon_path
from PointMatcher.data import Matching


class OpenFileAction(QAction):

    def __init__(self, parent):
        super(OpenFileAction, self).__init__('Open File', parent)

        self.p = parent

        self.setIcon(QIcon(icon_path('open')))
        self.setShortcut('Ctrl+O')
        self.triggered.connect(self.openFile)
        self.setEnabled(False)

    def openFile(self, _value=False):
        if not self.p.mayContinue():
            return
        if (self.p.savePath is not None) and osp.exists(osp.dirname(self.p.savePath)):
            path = osp.dirname(self.p.savePath)
        elif (self.p.imageDir is not None) and osp.exists(self.p.imageDir):
            path = self.p.imageDir
        else:
            path = '.'
        filters = 'matching file (*.json *.pkl)'
        filename = QFileDialog.getOpenFileName(
            self.p, 'choose matching file', path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            if osp.exists(filename):
                matching = Matching(filename)
                for view in matching.get_views():
                    img_path = osp.join(self.p.imageDir, osp.join(*view['filename']))
                    if not osp.exists(img_path):
                        QMessageBox.warning(self.p, 'Error', '{} not found.'.format(img_path), QMessageBox.Ok)
                        return
                self.p.loadMatching(matching)
                self.p.savePath = filename
                self.p.updateTitle()
            else:
                QMessageBox.warning(self.p, 'Attention', 'File Not Found', QMessageBox.Ok)
