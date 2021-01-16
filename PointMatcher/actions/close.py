import os.path as osp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PointMatcher.utils.filesystem import icon_path


class CloseAction(QAction):

    def __init__(self, parent):
        super(CloseAction, self).__init__('Close', parent)
        self.p = parent

        self.setIcon(QIcon(icon_path('close')))
        self.setShortcut('Ctrl+W')
        self.triggered.connect(self._close)
        self.setEnabled(True)

    def _close(self, _value=False):
        if not self.parent.mayContinue():
            return
