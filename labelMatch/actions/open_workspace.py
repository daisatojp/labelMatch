import os
import os.path as osp
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox as QMB
from labelMatch import __appname__
from labelMatch.defines import *
from labelMatch.utils import *


QDBB = QDialogButtonBox
QFD = QFileDialog


class OpenWorkspaceDialog(QDialog):

    def __init__(self, parent=None):
        super(OpenWorkspaceDialog, self).__init__(parent)
        self.mw = parent  # MainWindow

        label_annot_dir = QLabel('Annotation directory')
        self.ledit_annot_dir = QLineEdit()
        button_annot_dir = QPushButton(QIcon(icon_path('open')), 'open', self)
        button_annot_dir.clicked.connect(self.pop_open_annot_dir)

        label_new_annot_dir = QLabel('Create new annotation directory')
        self.checkbox_new_annot_dir = QCheckBox()

        label_image_dir = QLabel('Image directory')
        self.ledit_image_dir = QLineEdit()
        button_image_dir = QPushButton(QIcon(icon_path('open')), 'open', self)
        button_image_dir.clicked.connect(self.pop_open_image_dir)

        self.bb = QDBB(QDBB.Ok | QDBB.Cancel, Qt.Horizontal, self)
        self.bb.button(QDBB.Ok).setIcon(QIcon(osp.join('resources', 'icons', 'done.png')))
        self.bb.button(QDBB.Cancel).setIcon(QIcon(osp.join('recources', 'icons', 'undo.png')))
        self.bb.accepted.connect(self.accept)
        self.bb.rejected.connect(self.reject)

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(label_annot_dir)
        hlayout1.addWidget(self.ledit_annot_dir)
        hlayout1.addWidget(button_annot_dir)

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(label_new_annot_dir)
        hlayout2.addWidget(self.checkbox_new_annot_dir)

        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(label_image_dir)
        hlayout3.addWidget(self.ledit_image_dir)
        hlayout3.addWidget(button_image_dir)

        vlayout = QVBoxLayout()
        vlayout.addLayout(hlayout1)
        vlayout.addLayout(hlayout2)
        vlayout.addLayout(hlayout3)
        vlayout.addWidget(self.bb)

        self.setLayout(vlayout)
        self.setWindowTitle('{} - Open Workspace'.format(__appname__))

    def pop_open_annot_dir(self):
        default_annot_dir = '.'
        if osp.exists(self.ledit_annot_dir.text()):
            default_annot_dir = self.ledit_annot_dir.text()
        new_annot_dir = \
            QFD.getExistingDirectory(
                self, 'New Annotation Directory',
                directory=default_annot_dir,
                options=QFD.DontUseNativeDialog | QFD.ShowDirsOnly | QFD.DontResolveSymlinks)
        self.ledit_annot_dir.setText(new_annot_dir)

    def pop_open_image_dir(self):
        default_image_dir = '.'
        if osp.exists(self.ledit_image_dir.text()):
            default_image_dir = self.ledit_image_dir.text()
        new_image_dir = \
            QFD.getExistingDirectory(
                self, 'New Image Directory',
                directory=default_image_dir,
                options=QFD.DontUseNativeDialog | QFD.ShowDirsOnly | QFD.DontResolveSymlinks)
        self.ledit_image_dir.setText(new_image_dir)

    def popup(self):
        if (self.mw.annot_dir is not None) and \
             osp.exists(self.mw.annot_dir):
            self.ledit_annot_dir.setText(self.mw.annot_dir)
        if (self.mw.image_dir is not None) and \
             osp.exists(self.mw.image_dir):
            self.ledit_image_dir.setText(self.mw.image_dir)        
        if not self.exec_():
            return False
        if self.checkbox_new_annot_dir.isChecked():
            new_annot_dir = self.ledit_annot_dir.text()
            if osp.exists(new_annot_dir):
                QMB.warning(None, 'Warning',
                            '{} have already existed.'
                            .format(new_annot_dir),
                            QMB.Ok)
                return False
            views_dir = osp.join(new_annot_dir, 'views')
            mkdir_if_not_exists(views_dir)
            with open(osp.join(new_annot_dir, 'groups.json'), 'w') as f:
                json.dump({'groups': []}, f, indent=4)
        if not osp.exists(self.ledit_annot_dir.text()):
            QMB.warning(None, 'Warning',
                        '{} does not exist.'
                        .format(self.ledit_annot_dir.text()))
            return False
        if not osp.exists(self.ledit_image_dir.text()):
            QMB.warning(None, 'Warning',
                        '{} does not exist.'
                        .format(self.ledit_image_dir.text()))
            return False
        return True


class OpenWorkspaceAction(QAction):

    def __init__(self, parent):
        super(OpenWorkspaceAction, self).__init__('Open Workspace', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('open')))
        self.setShortcut('Ctrl+N')
        self.triggered.connect(self.open_workspace)
        self.setEnabled(True)

        self.open_workspace_dialog = OpenWorkspaceDialog(self.mw)

    def open_workspace(self, _value=False):
        if not self.mw.may_continue():
            return

        if not self.open_workspace_dialog.popup():
            return

        self.mw.annot_dir = self.open_workspace_dialog.ledit_annot_dir.text()
        self.mw.image_dir = self.open_workspace_dialog.ledit_image_dir.text()

        self.mw.open_workspace()
