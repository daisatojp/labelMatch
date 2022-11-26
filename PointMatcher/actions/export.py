import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PointMatcher.utils import *


QFD = QFileDialog


class ExportAction(QAction):

    def __init__(self, parent):
        super(ExportAction, self).__init__('Export', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('save')))
        self.setShortcut('Ctrl+Alt+S')
        self.triggered.connect(self.export)
        self.setEnabled(False)

    def export(self, _value=False):
        if (self.mw.annot_dir is not None) and osp.exists(self.mw.annot_dir):
            default_dir = self.mw.annot_dir
        elif (self.mw.image_dir is not None) and osp.exists(self.mw.image_dir):
            default_dir = self.mw.image_dir
        else:
            default_dir = '.'
        default_dir = self.mw.settings.get('export_path', default_dir)
        filters = 'json file (*.json)'
        filename = QFD.getSaveFileName(
            self.p, 'choose file name to be exported', default_dir, filters,
            options=QFD.DontUseNativeDialog)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.mw.matching.export(filename)
            self.mw.settings['export_path'] = osp.dirname(filename)
