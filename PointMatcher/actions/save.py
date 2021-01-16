import os.path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PointMatcher.utils.filesystem import icon_path


class SaveAction(QAction):

    def __init__(self, parent):
        super(SaveAction, self).__init__('Save', parent)
        self.p = parent

        self.setIcon(QIcon(icon_path('save')))
        self.setShortcut('Ctrl+S')
        self.triggered.connect(self.save)
        self.setEnabled(False)

    def save(self, _value=False):
        self.p.matching.save()
        self.p.actions.save.setEnabled(False)
