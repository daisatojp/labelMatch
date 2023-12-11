import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from labelMatch import __appname__
from labelMatch.matching import Matching
from labelMatch.utils import *


QFD = QFileDialog
QMB = QMessageBox


class OpenAnnotDirAction(QAction):

    def __init__(self, parent):
        super(OpenAnnotDirAction, self).__init__('Open Annot Dir', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('open')))
        self.setShortcut('Ctrl+O')
        self.triggered.connect(self.open_annot_dir)
        self.setEnabled(False)

    def open_annot_dir(self, _value=False):
        if not self.mw.may_continue():
            return
        if (self.mw.annot_dir is not None) and osp.exists(self.mw.annot_dir):
            default_dir = self.mw.annot_dir
        elif (self.mw.image_dir is not None) and osp.exists(self.mw.image_dir):
            default_dir = self.mw.image_dir
        else:
            default_dir = '.'
        annot_dir = QFD.getExistingDirectory(
            self.mw, '{} - Open Annotation Directory'.format(__appname__), default_dir,
            QFD.DontUseNativeDialog | QFD.ShowDirsOnly | QFD.DontResolveSymlinks)
        if osp.isdir(annot_dir):
            views_dir = osp.join(annot_dir, 'views')
            groups_path = osp.join(annot_dir, 'groups.json')
            if not osp.isdir(views_dir):
                QMB.warning(self.p, 'Error', '{} not found'.format(views_dir), QMB.Ok)
                return
            if not osp.isfile(groups_path):
                QMB.warning(self.p, 'Error', '{} not found'.format(groups_path), QMB.Ok)
                return
            self.mw.annot_dir = annot_dir
            self.mw.load_matching()
            self.mw.update_title()
