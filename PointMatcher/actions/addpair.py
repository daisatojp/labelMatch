import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path


class AddPairAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(AddPairAction, self).__init__('Add Pair', parent)

        self.p = parent
        self.setIcon(QtGui.QIcon(icon_path('save')))
        self.triggered.connect(self.addPair)
        self.setEnabled(False)

    def addPair(self):
        view_id_i = self.p.matching.get_view_id_by_view_idx(self.p.viewIWidget.get_current_idx())
        view_id_j = self.p.matching.get_view_id_by_view_idx(self.p.viewJWidget.get_current_idx())
        self.p.matching.append_pair(view_id_i, view_id_j, update=False)
        self.p.pairWidget.remove_last_item()
        self.p.pairWidget.add_item(self.p.matching.get_pairs()[-1])
        self.p.changePair(view_id_i, view_id_j)
