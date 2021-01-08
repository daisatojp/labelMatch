import os.path as osp
from PyQt5.QtWidgets import QAction
from PointMatcher.utils.filesystem import icon_path
from PointMatcher.data.op import sanity_check


class SanityCheckAction(QAction):

    def __init__(self, parent):
        super(SanityCheckAction, self).__init__('Sanity Check', parent)

        self.p = parent

        self.triggered.connect(self.sanityCheck)
        self.setEnabled(True)

    def sanityCheck(self):
        bad_keypoints = sanity_check(self.p.matching)
        self.p.viewIWidget.apply_bad_keypoints(bad_keypoints)
        self.p.viewJWidget.apply_bad_keypoints(bad_keypoints)
        self.p.pairWidget.apply_bad_keypoints(bad_keypoints)
        self.p.canvas.mp.set_bad_keypoints(bad_keypoints, self.p.matching)
