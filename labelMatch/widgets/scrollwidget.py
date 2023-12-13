from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class ScrollWidget(QScrollArea):

    def __init__(self, parent):
        super(ScrollWidget, self).__init__()
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.setWidget(self.p.canvas)
        self.setWidgetResizable(True)
        self.scrollbars = {
            Qt.Vertical: self.verticalScrollBar(),
            Qt.Horizontal: self.horizontalScrollBar()}

    def scroll_request(self, delta, orientation):
        units = - delta / (8 * 15)
        bar = self.scrollbars[orientation]
        bar.setValue(int(bar.value() + bar.singleStep() * units))
