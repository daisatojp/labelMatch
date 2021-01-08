import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class OpenFileAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(OpenFileAction, self).__init__('Open File', parent)

        self.parent = parent
        self.setIcon(QtGui.QIcon(icon_path('open')))
        self.setShortcut('Ctrl+O')
        self.triggered.connect(self.openFile)
        self.setEnabled(True)

    def openFile(self, _value=False):
        if not self.parent.mayContinue():
            return
        if (self.parent.savePath is not None) and osp.exists(osp.dirname(self.parent.savePath)):
            path = osp.dirname(self.parent.savePath)
        elif (self.parent.imageDir is not None) and osp.exists(self.parent.imageDir):
            path = self.parent.imageDir
        else:
            path = '.'
        filters = 'matching file (*.json *.pkl)'
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self.parent, 'choose matching file', path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            if osp.exists(filename):
                self.parent.savePath = filename
                self.parent.loadMatching(filename)
            else:
                QtWidgets.QMessageBox.warning(self.parent, 'Attention', 'File Not Found', QtWidgets.QMessageBox.Ok)
