import os.path as osp
from PyQt5.QtWidgets import *
from labelMatch.utils import *


class EditKeypointModeAction(QAction):

    def __init__(self, parent):
        super(EditKeypointModeAction, self).__init__('Edit Keypoint', parent)
        self.p = parent
        self.mw = self.p

        self.triggered.connect(self.edit_keypoint_mode)
        self.setEnabled(True)
        self.setCheckable(True)
        self.setChecked(True)
        self.setShortcut('v')

    def edit_keypoint_mode(self):
        self.mw.edit_keypoint_mode_action.setChecked(True)
        self.mw.edit_match_mode_action.setChecked(False)
        self.mw.canvas.set_edit_keypoint_mode()
        self.mw.update_status_message()
