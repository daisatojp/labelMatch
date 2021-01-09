import os.path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PointMatcher.utils.filesystem import icon_path


class SaveFileAction(QAction):

    def __init__(self, parent):
        super(SaveFileAction, self).__init__('Save File', parent)
        self.p = parent

        self.setIcon(QIcon(icon_path('save')))
        self.setShortcut('Ctrl+S')
        self.triggered.connect(self.saveFile)
        self.setEnabled(False)

    def saveFile(self, _value=False):
        if self.p.savePath:
            self.p.matching.save(self.p.savePath)
            self.p.actions.saveFile.setEnabled(False)
