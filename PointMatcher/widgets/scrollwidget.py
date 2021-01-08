from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets


class ScrollWidget(QtWidgets.QScrollArea):

    def __init__(self, parent):
        super(ScrollWidget, self).__init__()

        self.parent = parent

        self.setWidget(self.parent.canvas)
        self.setWidgetResizable(True)
        self.scrollBars = {
            QtCore.Qt.Vertical: self.verticalScrollBar(),
            QtCore.Qt.Horizontal: self.horizontalScrollBar()}

    def scrollRequest(self, delta, orientation):
        units = - delta / (8 * 15)
        bar = self.scrollBars[orientation]
        bar.setValue(bar.value() + bar.singleStep() * units)
