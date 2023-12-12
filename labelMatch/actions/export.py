import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from labelMatch.utils import *


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
        default_dir = '.'
        export_file = self.mw.settings.get('export_file', default_dir)
        if export_file is not None:
            export_dir = osp.dirname(export_file)
            if osp.exists(export_dir):
                default_dir = export_dir
        filters = 'json file (*.json)'
        filename = QFD.getSaveFileName(
            self.p,
            'choose file name to be exported',
            default_dir, filters,
            options=QFD.DontUseNativeDialog)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.mw.matching.export(filename)
            self.mw.settings['export_file'] = filename
