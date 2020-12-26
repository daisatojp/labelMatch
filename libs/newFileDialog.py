from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from libs.utils import newIcon

BB = QDialogButtonBox


class NewFileDialog(QDialog):

    def __init__(self, parent=None):
        super(NewFileDialog, self).__init__(parent)

        self.editMatchingFile = QLineEdit()

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.editMatchingFile)
        layout.addWidget(bb)

        self.setLayout(layout)

    def popUp(self, text='', move=True):
        self.editMatchingFile.setText('')
        return self.editMatchingFile.text() if self.exec_() else None
