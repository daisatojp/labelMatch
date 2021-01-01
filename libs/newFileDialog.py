import os
import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

BB = QDialogButtonBox


class NewFileDialog(QDialog):

    def __init__(self, parent=None):
        super(NewFileDialog, self).__init__(parent)

        self.editMatchingFile = QLineEdit()

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(QIcon(osp.join('resources', 'icons', 'done.png')))
        bb.button(BB.Cancel).setIcon(QIcon(osp.join('recources', 'icons', 'undo.png')))
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.editMatchingFile)
        layout.addWidget(bb)

        self.setLayout(layout)

    def popUp(self, text='', move=True):
        self.editMatchingFile.setText('')
        return self.editMatchingFile.text() if self.exec_() else None
