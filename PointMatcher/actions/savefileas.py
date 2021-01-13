import os.path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QFileDialog
from PointMatcher.utils.filesystem import icon_path


class SaveFileAsAction(QAction):

    def __init__(self, parent):
        super(SaveFileAsAction, self).__init__('Save File As', parent)
        self.p = parent

        self.setIcon(QIcon(icon_path('save')))
        self.setShortcut('Ctrl+Alt+S')
        self.triggered.connect(self.saveFileAs)
        self.setEnabled(False)

    def saveFileAs(self, _value=False):
        if (self.p.savePath is not None) and osp.exists(osp.dirname(self.p.savePath)):
            path = osp.dirname(self.p.savePath)
        elif (self.p.imageDir is not None) and osp.exists(self.p.imageDir):
            path = self.p.imageDir
        else:
            path = '.'
        filters = 'matching file (*.json *.pkl)'
        filename = QFileDialog.getSaveFileName(
            self.p, 'choose file name to be saved', path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.p.savePath = filename
            self.p.matching.save(self.p.savePath)
            self.p.updateTitle()
