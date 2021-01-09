import os.path as osp
from PyQt5.QtWidgets import QAction


class AutoSavingAction(QAction):

    def __init__(self, parent):
        super(AutoSavingAction, self).__init__('Auto Save Mode', parent)
        self.p = parent

        self.setCheckable(True)
        self.setChecked(False)
        self.setEnabled(True)
