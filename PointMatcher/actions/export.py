import os.path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QFileDialog
from PointMatcher.utils.filesystem import icon_path


class ExportAction(QAction):

    def __init__(self, parent):
        super(ExportAction, self).__init__('Export', parent)
        self.p = parent

        self.setIcon(QIcon(icon_path('save')))
        self.setShortcut('Ctrl+Alt+S')
        self.triggered.connect(self.export)
        self.setEnabled(False)

    def export(self, _value=False):
        if (self.p.annotDir is not None) and osp.exists(self.p.annotDir):
            path = self.p.annotDir
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
            raise NotImplementedError()
