import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets


class ViewWidget(QtWidgets.QDockWidget):

    def __init__(self, parent=None, title=''):
        super(ViewWidget, self).__init__(title, parent)

        self.viewListWidget = QtWidgets.QListWidget()
        self.viewlistLayout = QtWidgets.QVBoxLayout()
        self.viewlistLayout.setContentsMargins(0, 0, 0, 0)
        self.viewlistLayout.addWidget(self.viewListWidget)
        self.viewWidgetContainer = QtWidgets.QWidget()
        self.viewWidgetContainer.setLayout(self.viewlistLayout)
        self.setObjectName('View')
        self.setWidget(self.viewWidgetContainer)
        self.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable)

    def itemClicked_connect(self, f):
        self.viewListWidget.itemClicked.connect(f)

    def initialize_item(self, matching):
        views = matching.get_views()
        self.viewListWidget.clear()
        for view in views:
            self.viewListWidget.addItem(self.item_text(view))

    def get_current_idx(self):
        return self.viewListWidget.currentIndex().row()

    def set_current_idx(self, idx):
        self.viewListWidget.setCurrentRow(idx)

    def update_item_by_idx(self, matching, idx):
        views = matching.get_views()
        if type(idx) in (list, tuple):
            for i in idx:
                self.viewListWidget.item(i).setText(self.item_text(views[i]))
        else:
            self.viewListWidget.item(idx).setText(self.item_text(views[idx]))

    @staticmethod
    def item_text(view):
        return '(ID={}, K={}) {}'.format(
            view['id_view'],
            len(view['keypoints']),
            osp.join(*view['filename']))
