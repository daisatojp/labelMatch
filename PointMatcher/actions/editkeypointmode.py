import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class EditKeypointModeAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(EditKeypointModeAction, self).__init__('Edit Keypoint', parent)

        self.p = parent
        self.triggered.connect(self.editKeypointMode)
        self.setEnabled(True)
        self.setCheckable(True)
        self.setChecked(True)
        self.setShortcut('v')

    def editKeypointMode(self):
        self.p.actions.editKeypointMode.setChecked(True)
        self.p.actions.editMatchMode.setChecked(False)
        self.p.canvas.setEditKeypointMode()
