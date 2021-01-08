import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class SaveFileAsAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(SaveFileAsAction, self).__init__('Save File As', parent)

        self.parent = parent
        self.setIcon(QtGui.QIcon(icon_path('save')))
        self.setShortcut('Ctrl+Alt+S')
        self.triggered.connect(self.saveFileAs)
        self.setEnabled(False)

    def saveFileAs(self, _value=False):
        if (self.parent.savePath is not None) and osp.exists(osp.dirname(self.parent.savePath)):
            path = osp.dirname(self.savePath)
        elif (self.parent.imageDir is not None) and osp.exists(self.parent.imageDir):
            path = self.parent.imageDir
        else:
            path = '.'
        filters = 'matching file (*.json *.pkl)'
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self.parent, 'choose file name to be saved', path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.parent.savePath = filename
            self.parent.matching.save(self.parent.savePath)

