import os
import os.path as osp
import json
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PointMatcher.utils.filesystem import icon_path, scan_all_images


QDBB = QDialogButtonBox


class NewProjectDialog(QDialog):

    def __init__(self, parent=None):
        super(NewProjectDialog, self).__init__(parent)

        labelOpenImageDir = QLabel('Image Directory')
        self.editOpenImageDir = QLineEdit()
        buttonOpenImageDir = QPushButton(QIcon(icon_path('open')), 'open', self)
        buttonOpenImageDir.clicked.connect(self.popOpenImageDir)

        labelOpenAnnotDir = QLabel('Annotation Directory')
        self.editOpenAnnotDir = QLineEdit()
        buttonOpenAnnotDir = QPushButton(QIcon(icon_path('open')), 'open', self)
        buttonOpenAnnotDir.clicked.connect(self.popOpenAnnotDir)

        self.buttonBox = bb = QDBB(QDBB.Ok | QDBB.Cancel, Qt.Horizontal, self)
        bb.button(QDBB.Ok).setIcon(QIcon(osp.join('resources', 'icons', 'done.png')))
        bb.button(QDBB.Cancel).setIcon(QIcon(osp.join('recources', 'icons', 'undo.png')))
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        layoutH1 = QHBoxLayout()
        layoutH1.addWidget(labelOpenImageDir)
        layoutH1.addWidget(self.editOpenImageDir)
        layoutH1.addWidget(buttonOpenImageDir)
        layoutH2 = QHBoxLayout()
        layoutH2.addWidget(labelOpenAnnotDir)
        layoutH2.addWidget(self.editOpenAnnotDir)
        layoutH2.addWidget(buttonOpenAnnotDir)

        layout = QVBoxLayout()
        layout.addLayout(layoutH1)
        layout.addLayout(layoutH2)
        layout.addWidget(bb)

        self.setLayout(layout)

    def popOpenImageDir(self):
        defaultImageDir = '.'
        if osp.exists(self.editOpenImageDir.text()):
            defaultImageDir = self.editOpenImageDir.text()
        openImageDir = QFileDialog.getExistingDirectory(
            self, 'Open Image Directory', defaultImageDir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.editOpenImageDir.setText(openImageDir)

    def popOpenAnnotDir(self):
        defaultAnnotDir = '.'
        if osp.exists(self.editOpenAnnotDir.text()):
            defaultAnnotDir = self.editOpenAnnotDir.text()
        openAnnotDir = QFileDialog.getExistingDirectory(
            self, 'Open Annotation Directory', defaultAnnotDir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.editOpenAnnotDir.setText(openAnnotDir)

    def popUp(self, openImageDir='', openAnnotDir=''):
        self.editOpenImageDir.setText(openImageDir)
        self.editOpenAnnotDir.setText(openAnnotDir)
        if self.exec_():
            return self.editOpenImageDir.text(), self.editOpenAnnotDir.text()
        else:
            return None


class NewProjectAction(QAction):

    def __init__(self, parent):
        super(NewProjectAction, self).__init__('New Project', parent)
        self.p = parent

        self.setIcon(QIcon(icon_path('open')))
        self.setShortcut('Ctrl+N')
        self.triggered.connect(self.newProject)
        self.setEnabled(True)

        self.newProjectDialog = NewProjectDialog(self.p)

    def newProject(self, _value=False):
        if not self.p.mayContinue():
            return

        ret = self.newProjectDialog.popUp()
        if ret is None:
            return
        assert osp.isdir(ret[0])

        self.p.imageDir, self.p.annotDir = ret

        views_dir = osp.join(self.p.annotDir, 'views')
        if not osp.exists(views_dir):
            os.makedirs(views_dir)
        image_paths = scan_all_images(self.p.imageDir)
        for i, image_path in enumerate(image_paths):
            with open(osp.join(views_dir, 'view_{}.json'.format(i)), 'w') as f:
                json.dump({
                    'id': i,
                    'filename': image_path[len(self.p.imageDir) + len(os.sep):].split(os.sep),
                    'keypoints': []},
                    f, indent=4)
        with open(osp.join(self.p.annotDir, 'groups.json'), 'w') as f:
            json.dump({'groups': []}, f, indent=4)
