import os
import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

BB = QDialogButtonBox


class NewFileDialog(QDialog):

    def __init__(self, parent=None):
        super(NewFileDialog, self).__init__(parent)

        labelOpenImageDir = QLabel('Image Directory')
        self.editOpenImageDir = QLineEdit()
        buttonOpenImageDir = QPushButton(QIcon(osp.join('resources', 'icons', 'open.png')), 'open', self)
        buttonOpenImageDir.clicked.connect(self.popOpenImageDir)

        labelSaveMatchingFile = QLabel('Matching File')
        self.editSaveMatchingFile = QLineEdit()
        buttonSaveMatchingFile = QPushButton(QIcon(osp.join('resources', 'icons', 'open.png')), 'open', self)
        buttonSaveMatchingFile.clicked.connect(self.popOpenSaveMatchingFile)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(QIcon(osp.join('resources', 'icons', 'done.png')))
        bb.button(BB.Cancel).setIcon(QIcon(osp.join('recources', 'icons', 'undo.png')))
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        layoutH1 = QHBoxLayout()
        layoutH1.addWidget(labelOpenImageDir)
        layoutH1.addWidget(self.editOpenImageDir)
        layoutH1.addWidget(buttonOpenImageDir)
        layoutH2 = QHBoxLayout()
        layoutH2.addWidget(labelSaveMatchingFile)
        layoutH2.addWidget(self.editSaveMatchingFile)
        layoutH2.addWidget(buttonSaveMatchingFile)

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

    def popOpenSaveMatchingFile(self):
        filters = 'matching file (*.json)'
        filename = QFileDialog.getOpenFileName(
            self, 'matching file to be saved', '.', filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.editSaveMatchingFile.setText(filename)

    def popUp(self, openDir=''):
        self.editOpenImageDir.setText(openDir)
        if self.exec_():
            return self.editOpenImageDir.text(), self.editSaveMatchingFile.text()
        else:
            return None
