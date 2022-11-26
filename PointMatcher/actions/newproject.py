import os
import os.path as osp
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PointMatcher.utils import *


QDBB = QDialogButtonBox
QFD = QFileDialog


class NewProjectDialog(QDialog):

    def __init__(self, parent=None):
        super(NewProjectDialog, self).__init__(parent)

        label_open_image_dir = QLabel('Image Directory')
        self.ledit_open_image_dir = QLineEdit()
        button_open_image_dir = QPushButton(QIcon(icon_path('open')), 'open', self)
        button_open_image_dir.clicked.connect(self.pop_open_image_dir)

        label_open_annot_dir = QLabel('Annotation Directory')
        self.ledit_open_annot_dir = QLineEdit()
        button_open_annot_dir = QPushButton(QIcon(icon_path('open')), 'open', self)
        button_open_annot_dir.clicked.connect(self.pop_open_annot_dir)

        self.bb = QDBB(QDBB.Ok | QDBB.Cancel, Qt.Horizontal, self)
        self.bb.button(QDBB.Ok).setIcon(QIcon(osp.join('resources', 'icons', 'done.png')))
        self.bb.button(QDBB.Cancel).setIcon(QIcon(osp.join('recources', 'icons', 'undo.png')))
        self.bb.accepted.connect(self.accept)
        self.bb.rejected.connect(self.reject)

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(label_open_image_dir)
        hlayout1.addWidget(self.ledit_open_image_dir)
        hlayout1.addWidget(button_open_image_dir)
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(label_open_annot_dir)
        hlayout2.addWidget(self.ledit_open_annot_dir)
        hlayout2.addWidget(button_open_annot_dir)

        layout = QVBoxLayout()
        layout.addLayout(hlayout1)
        layout.addLayout(hlayout2)
        layout.addWidget(self.bb)

        self.setLayout(layout)

    def pop_open_image_dir(self):
        default_image_dir = '.'
        if osp.exists(self.ledit_open_image_dir.text()):
            default_image_dir = self.ledit_open_image_dir.text()
        open_image_dir = QFD.getExistingDirectory(
            self, 'Open Image Directory', default_image_dir,
            QFD.DontUseNativeDialog | QFD.ShowDirsOnly | QFD.DontResolveSymlinks)
        self.ledit_open_image_dir.setText(open_image_dir)

    def pop_open_annot_dir(self):
        default_annot_dir = '.'
        if osp.exists(self.ledit_open_annot_dir.text()):
            default_annot_dir = self.ledit_open_annot_dir.text()
        open_annot_dir = QFD.getExistingDirectory(
            self, 'Open Annotation Directory', default_annot_dir,
            QFD.DontUseNativeDialog | QFD.ShowDirsOnly | QFD.DontResolveSymlinks)
        self.ledit_open_annot_dir.setText(open_annot_dir)

    def popup(self, open_image_dir='', open_annot_dir=''):
        self.ledit_open_image_dir.setText(open_image_dir)
        self.ledit_open_annot_dir.setText(open_annot_dir)
        if self.exec_():
            return self.ledit_open_image_dir.text(), self.ledit_open_annot_dir.text()
        else:
            return None


class NewProjectAction(QAction):

    def __init__(self, parent):
        super(NewProjectAction, self).__init__('New Project', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setIcon(QIcon(icon_path('open')))
        self.setShortcut('Ctrl+N')
        self.triggered.connect(self.new_project)
        self.setEnabled(True)

        self.new_project_dialog = NewProjectDialog(self.p)

    def new_project(self, _value=False):
        if not self.mw.may_continue():
            return

        ret = self.new_project_dialog.popup()
        if ret is None:
            return
        assert osp.isdir(ret[0])

        self.mw.image_dir, self.mw.annot_dir = ret

        views_dir = osp.join(self.mw.annot_dir, 'views')
        if not osp.exists(views_dir):
            os.makedirs(views_dir)
        image_paths = scan_all_images(self.mw.image_dir)
        for i, image_path in enumerate(image_paths):
            with open(osp.join(views_dir, 'view_{}.json'.format(i)), 'w') as f:
                json.dump({
                    'id': i,
                    'filename': image_path[len(self.mw.image_dir) + len(os.sep):].split(os.sep),
                    'keypoints': []},
                    f, indent=4)
        with open(osp.join(self.mw.annot_dir, 'groups.json'), 'w') as f:
            json.dump({'groups': []}, f, indent=4)
