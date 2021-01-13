import os.path as osp
from PyQt5.QtWidgets import QAction
from PointMatcher.utils.filesystem import icon_path


class SortPairAction(QAction):

    def __init__(self, parent):
        super(SortPairAction, self).__init__('Sort Pair', parent)
        self.p = parent

        self.triggered.connect(self.sortPair)
        self.setEnabled(True)

    def sortPair(self, _value=False):
        if self.p.matching is None:
            return
        view_id_i = self.p.matching.get_view_id_i()
        view_id_j = self.p.matching.get_view_id_j()
        self.p.matching.sort_pairs()
        self.p.matching.set_view(view_id_i, view_id_j)
        self.p.pairWidget.update_all()
        self.p.viewIWidget.set_current_idx(self.p.matching.get_view_idx_i())
        self.p.viewJWidget.set_current_idx(self.p.matching.get_view_idx_j())
        self.p.pairWidget.set_current_idx(self.p.matching.get_pair_idx())
