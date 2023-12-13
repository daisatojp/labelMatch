import os.path as osp
from PyQt5.QtWidgets import *
from labelMatch.utils import *


class EditMatchModeAction(QAction):

    def __init__(self, parent):
        super(EditMatchModeAction, self).__init__('Edit Match', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.triggered.connect(self.edit_match_mode)
        self.setEnabled(True)
        self.setCheckable(True)
        self.setChecked(False)
        self.setShortcut('e')

    def edit_match_mode(self):
        self.mw.edit_keypoint_mode_action.setChecked(False)
        self.mw.edit_match_mode_action.setChecked(True)
        self.mw.canvas.set_edit_match_mode()
        self.mw.update_status_message()
