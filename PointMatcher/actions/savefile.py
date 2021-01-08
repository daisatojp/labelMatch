import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class SaveFileAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(SaveFileAction, self).__init__('Save File', parent)

        self.parent = parent
        self.setIcon(QtGui.QIcon(icon_path('save')))
        self.setShortcut('Ctrl+S')
        self.triggered.connect(self.saveFile)
        self.setEnabled(False)

    def saveFile(self, _value=False):
        if self.parent.savePath:
            self.parent.matching.save(self.parent.savePath)
            self.parent.actions.saveFile.setEnabled(False)
