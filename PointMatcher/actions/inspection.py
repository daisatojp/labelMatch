import os.path as osp
import time
import threading
from PyQt5.QtWidgets import QAction
from PointMatcher.utils.filesystem import icon_path
from PointMatcher.data.op import sanity_check


class InspectionAction(QAction):

    def __init__(self, parent):
        super(InspectionAction, self).__init__('Inspection', parent)

        self.p = parent

        self.setCheckable(True)
        self.setChecked(True)
        self.setEnabled(True)
        self.inspected = False
        self.thread_executing_flag = True
        self.thread = threading.Thread(target=self.inspectionThread)
        self.thread.start()

    def requireInspection(self):
        self.inspected = False

    def inspectionThread(self):
        while self.thread_executing_flag:
            if self.isChecked() and (self.p.matching is not None) and (not self.inspected):
                matching = self.p.matching.copy()
                self.inspected = True
                bad_keypoints, _ = sanity_check(matching)
                self.p.viewIWidget.apply_bad_keypoints(bad_keypoints)
                self.p.viewJWidget.apply_bad_keypoints(bad_keypoints)
                self.p.pairWidget.apply_bad_keypoints(bad_keypoints, matching)
                self.p.canvas.mp.set_bad_keypoints(bad_keypoints, matching)
            time.sleep(0.1)

    def terminate_thread(self):
        self.thread_executing_flag = False
        if self.thread:
            self.thread.join(1.0)
