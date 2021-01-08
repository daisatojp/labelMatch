from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class PairWidget(QDockWidget):

    ITEM_COLOR_OK = QBrush(QColor(255, 255, 255))
    ITEM_COLOR_NG = QBrush(QColor(255, 255, 0))

    def __init__(self, parent, title=''):
        super(PairWidget, self).__init__(title, parent)

        self.p = parent

        self.pairListWidget = QListWidget()
        self.pairlistLayout = QVBoxLayout()
        self.pairlistLayout.setContentsMargins(0, 0, 0, 0)
        self.pairlistLayout.addWidget(self.pairListWidget)
        self.pairListContainer = QWidget()
        self.pairListContainer.setLayout(self.pairlistLayout)
        self.setObjectName('Pair')
        self.setWidget(self.pairListContainer)
        self.setFeatures(QDockWidget.DockWidgetFloatable)

    def itemClicked_connect(self, f):
        self.pairListWidget.itemClicked.connect(f)

    def initialize_item(self, matching):
        pairs = matching.get_pairs()
        self.pairListWidget.clear()
        for pair in pairs:
            self.add_item(pair)

    def count(self):
        return self.pairListWidget.count()

    def get_current_idx(self):
        return self.pairListWidget.currentIndex().row()

    def set_current_idx(self, idx):
        self.pairListWidget.setCurrentRow(idx)

    def add_item(self, pair):
        if type(pair) is str:
            self.pairListWidget.addItem(pair)
        else:
            self.pairListWidget.addItem(self.item_text(pair))

    def remove_item_by_idx(self, idx):
        self.pairListWidget.takeItem(idx)

    def remove_last_item(self):
        self.remove_item_by_idx(self.count() - 1)

    def update_item_by_idx(self, matching, idx):
        pairs = matching.get_pairs()
        if type(idx) in (list, tuple):
            for i in idx:
                self.pairListWidget.item(i).setText(self.item_text(pairs[i]))
        else:
            self.pairListWidget.item(idx).setText(self.item_text(pairs[idx]))

    def apply_bad_keypoints(self, bad_keypoints):
        views = self.p.matching.get_views()
        pairs = self.p.matching.get_pairs()
        bad_view_ids = [views[x[0]]['id_view'] for x in bad_keypoints]
        for idx in range(len(pairs)):
            if (pairs[idx]['id_view_i'] in bad_view_ids) or (pairs[idx]['id_view_j'] in bad_view_ids):
                self.pairListWidget.item(idx).setBackground(self.ITEM_COLOR_NG)
            else:
                self.pairListWidget.item(idx).setBackground(self.ITEM_COLOR_OK)

    @staticmethod
    def item_text(pair):
        return '[({}, {}) [M={}]'.format(
            pair['id_view_i'],
            pair['id_view_j'],
            len(pair['matches']))
