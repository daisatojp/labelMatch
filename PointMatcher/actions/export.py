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
            defaultDir = self.p.annotDir
        elif (self.p.imageDir is not None) and osp.exists(self.p.imageDir):
            defaultDir = self.p.imageDir
        else:
            defaultDir = '.'
        defaultDir = self.p.settings.get('exportPath', defaultDir)
        filters = 'json file (*.json)'
        filename = QFileDialog.getSaveFileName(
            self.p, 'choose file name to be exported', defaultDir, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.p.matching.export(filename)
            self.p.settings['exportPath'] = osp.dirname(filename)
