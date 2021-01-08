import os.path as osp
import time
import threading
from PyQt5.QtWidgets import QAction
from PointMatcher.utils.filesystem import icon_path
from PointMatcher.data.op import sanity_check


class SanityCheckAction(QAction):

    def __init__(self, parent):
        super(SanityCheckAction, self).__init__('Sanity Check', parent)

        self.p = parent

        self.setCheckable(True)
        self.setChecked(True)
        self.setEnabled(True)
        self.sanity_checked = False
        self.thread_executing_flag = True
        self.thread = threading.Thread(target=self.sanityCheck)
        self.thread.start()

    def requireSanityCheck(self):
        self.sanity_checked = False

    def sanityCheck(self):
        while self.thread_executing_flag:
            if self.isChecked() and (self.p.matching is not None) and (not self.sanity_checked):
                matching = self.p.matching.copy()
                self.sanity_checked = True
                bad_keypoints = sanity_check(matching)
                self.p.viewIWidget.apply_bad_keypoints(bad_keypoints)
                self.p.viewJWidget.apply_bad_keypoints(bad_keypoints)
                self.p.pairWidget.apply_bad_keypoints(bad_keypoints, matching)
                self.p.canvas.mp.set_bad_keypoints(bad_keypoints, matching)
            time.sleep(0.1)

    def terminate_thread(self):
        self.thread_executing_flag = False
        if self.thread:
            self.thread.join(1.0)
