from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets


class PairWidget(QtWidgets.QDockWidget):

    def __init__(self, parent=None, title=''):
        super(PairWidget, self).__init__(title, parent)

        self.pairListWidget = QtWidgets.QListWidget()
        self.pairlistLayout = QtWidgets.QVBoxLayout()
        self.pairlistLayout.setContentsMargins(0, 0, 0, 0)
        self.pairlistLayout.addWidget(self.pairListWidget)
        self.pairListContainer = QtWidgets.QWidget()
        self.pairListContainer.setLayout(self.pairlistLayout)
        self.setObjectName('Pair')
        self.setWidget(self.pairListContainer)
        self.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable)

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

    @staticmethod
    def item_text(pair):
        return '[({}, {}) [M={}]'.format(
            pair['id_view_i'],
            pair['id_view_j'],
            len(pair['matches']))
