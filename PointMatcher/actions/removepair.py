import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class RemovePairAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(RemovePairAction, self).__init__('Remove Pair', parent)

        self.p = parent
        self.setIcon(QtGui.QIcon(icon_path('delete')))
        self.triggered.connect(self.removePair)
        self.setEnabled(False)

    def removePair(self):
        view_id_i = self.matching.get_view_id_i()
        view_id_j = self.matching.get_view_id_j()
        trans_view_id_i, trans_view_id_j = self.matching.get_prev_view_pair()
        if (trans_view_id_i, trans_view_id_j) == (view_id_i, view_id_j):
            trans_view_id_i, trans_view_id_j = self.matching.get_next_view_pair()
        if (trans_view_id_i, trans_view_id_j) == (view_id_i, view_id_j):
            trans_view_id_i = self.matching.get_views()[0]['id_view']
            trans_view_id_j = self.matching.get_views()[1]['id_view']
        self.pairWidget.remove_item_by_idx(self.matching.get_pair_idx())
        self.changePair(trans_view_id_i, trans_view_id_j)
        self.matching.remove_pair(view_id_i, view_id_j)
