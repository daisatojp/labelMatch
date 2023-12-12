import os.path as osp
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ViewJWidget(QDockWidget):

    ITEM_COLOR_OK = QBrush(QColor(255, 255, 255))
    ITEM_COLOR_NG = QBrush(QColor(255, 255, 0))

    def __init__(self, parent):
        super(ViewJWidget, self).__init__('View J List', parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.viewlist_widget = QListWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.viewlist_widget)
        widget = QWidget()
        widget.setLayout(layout)
        self.setObjectName('View')
        self.setWidget(widget)
        self.setFeatures(QDockWidget.DockWidgetFloatable)

    def itemClicked_connect(self, f):
        self.viewlist_widget.itemClicked.connect(f)

    def count(self):
        return self.viewlist_widget.count()

    def get_current_idx(self):
        return self.viewlist_widget.currentIndex().row()

    def set_current_idx(self, idx):
        self.viewlist_widget.setCurrentRow(idx)

    def clear(self):
        self.viewlist_widget.clear()

    def initialize(self):
        self.clear()
        list_of_view_id = self.mw.matching.get_list_of_view_id()
        for view_id in list_of_view_id:
            self.viewlist_widget.addItem(self.item_text(view_id))

    def update_text(self):
        list_of_view_id = self.mw.matching.get_list_of_view_id()
        assert self.count() == len(list_of_view_id)
        for i in range(self.count()):
            self.viewlist_widget.item(i).setText(self.item_text(list_of_view_id[i]))

    def item_text(self, view_id):
        view_id_i = self.mw.matching.get_view_id_i()
        return '(ID={}, K={}, M={}) {}'.format(
            view_id,
            self.mw.matching.get_keypoint_count(view_id),
            self.mw.matching.get_match_count(view_id_i, view_id),
            self.mw.matching.get_filename(view_id))
