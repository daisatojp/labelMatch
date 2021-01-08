import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class EditMatchModeAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(EditMatchModeAction, self).__init__('Edit Match', parent)

        self.p = parent
        self.triggered.connect(self.editMatchMode)
        self.setEnabled(True)
        self.setCheckable(True)
        self.setChecked(False)
        self.setShortcut('e')

    def editMatchMode(self):
        self.p.actions.editKeypointMode.setChecked(False)
        self.p.actions.editMatchMode.setChecked(True)
        self.p.canvas.setEditMatchMode()
