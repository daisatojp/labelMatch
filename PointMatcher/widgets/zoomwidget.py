from functools import partial
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.struct import struct
from PointMatcher.utils.qt import newAction


class ZoomWidget:
    ZOOM_MANUAL = 1
    ZOOM_FIT_WINDOW = 2
    ZOOM_FIT_WIDTH = 3

    def __init__(self, parent, value=100):
        super(ZoomWidget, self).__init__()

        self.parent = parent
        getStr = self.parent.stringBundle.getString

        self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinbox.setRange(1, 500)
        self.spinbox.setSuffix(' %')
        self.spinbox.setValue(value)
        self.spinbox.setToolTip(u'Zoom Level')
        self.spinbox.setStatusTip(self.spinbox.toolTip())
        self.spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.spinbox.setEnabled(False)

        zoom = QtWidgets.QWidgetAction(parent)
        zoom.setDefaultWidget(self.spinbox)
        zoomIn = newAction(
            parent, getStr('zoomIn'), partial(self.addZoom, 10),
            'Ctrl++', 'zoom-in', getStr('zoomInDetail'), enabled=False)
        zoomOut = newAction(
            parent, getStr('zoomOut'), partial(self.addZoom, -10),
            'Ctrl+-', 'zoom-out', getStr('zoomOutDetail'), enabled=False)
        zoomOrg = newAction(
            parent, getStr('zoomOrgSize'), partial(self.setZoom, 100),
            'Ctrl+=', 'zoom', getStr('zoomOrgSizeDetail'), enabled=False)
        zoomFitWindow = newAction(
            parent, getStr('zoomFitWindow'), self.setFitWindow,
            'Ctrl+F', 'fit-window', getStr('zoomFitWindowDetail'),
            checkable=True, enabled=False)
        zoomFitWidth = newAction(
            parent, getStr('zoomFitWidth'), self.setFitWidth,
            'Ctrl+Shift+F', 'fit-width', getStr('zoomFitWidthDetail'),
            checkable=True, enabled=False)

        self.actions = struct(
            zoom=zoom,
            zoomIn=zoomIn,
            zoomOut=zoomOut,
            zoomOrg=zoomOrg,
            zoomFitWindow=zoomFitWindow,
            zoomFitWidth=zoomFitWidth)

        self.zoomMode = self.ZOOM_MANUAL
        self.scalers = {
            self.ZOOM_MANUAL: lambda: 1,
            self.ZOOM_FIT_WINDOW: self.scaleFitWindow,
            self.ZOOM_FIT_WIDTH: self.scaleFitWidth}

    def minimumSizeHint(self):
        height = self.spinbox.minimumSizeHint().height()
        fm = QtGui.QFontMetrics(self.spinbox.font())
        width = fm.width(str(self.spinbox.maximum()))
        return QtCore.QSize(width, height)

    def setZoom(self, value):
        self.actions.zoomFitWindow.setChecked(False)
        self.actions.zoomFitWidth.setChecked(False)
        self.zoomMode = self.ZOOM_MANUAL
        self.spinbox.setValue(value)

    def addZoom(self, increment=10):
        self.setZoom(self.spinbox.value() + increment)

    def setFitWindow(self, value=True):
        if value:
            self.actions.fitWidth.setChecked(False)
        self.zoomMode = self.FIT_WINDOW if value else self.MANUAL_ZOOM
        self.adjustScale()

    def setFitWidth(self, value=True):
        if value:
            self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.FIT_WIDTH if value else self.MANUAL_ZOOM
        self.adjustScale()

    def adjustScale(self, initial=False):
        value = self.scalers[self.ZOOM_FIT_WINDOW if initial else self.zoomMode]()
        self.spinbox.setValue(int(100 * value))

    def scaleFitWindow(self):
        """Figure out the size of the pixmap in order to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.parent.centralWidget().width() - e
        h1 = self.parent.centralWidget().height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.parent.canvas.pixmap.width() - 0.0
        h2 = self.parent.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def scaleFitWidth(self):
        # The epsilon does not seem to work too well here.
        w = self.parent.centralWidget().width() - 2.0
        return w / self.parent.canvas.pixmap.width()

    def zoomRequest(self, delta):
        # get the current scrollbar positions
        # calculate the percentages ~ coordinates
        h_bar = self.parent.scrollWidget.scrollBars[QtCore.Qt.Horizontal]
        v_bar = self.parent.scrollWidget.scrollBars[QtCore.Qt.Vertical]
        # get the current maximum, to know the difference after zooming
        h_bar_max = h_bar.maximum()
        v_bar_max = v_bar.maximum()
        # get the cursor position and canvas size
        # calculate the desired movement from 0 to 1
        # where 0 = move left
        #       1 = move right
        # up and down analogous
        cursor = QtGui.QCursor()
        pos = cursor.pos()
        relative_pos = QtWidgets.QWidget.mapFromGlobal(self.parent, pos)
        cursor_x = relative_pos.x()
        cursor_y = relative_pos.y()
        w = self.parent.scrollWidget.width()
        h = self.parent.scrollWidget.height()
        # the scaling from 0 to 1 has some padding
        # you don't have to hit the very leftmost pixel for a maximum-left movement
        margin = 0.1
        move_x = (cursor_x - margin * w) / (w - 2 * margin * w)
        move_y = (cursor_y - margin * h) / (h - 2 * margin * h)
        # clamp the values from 0 to 1
        move_x = min(max(move_x, 0), 1)
        move_y = min(max(move_y, 0), 1)
        # zoom in
        units = delta / (8 * 15)
        scale = 10
        self.addZoom(scale * units)
        # get the difference in scrollbar values
        # this is how far we can move
        d_h_bar_max = h_bar.maximum() - h_bar_max
        d_v_bar_max = v_bar.maximum() - v_bar_max
        # get the new scrollbar values
        new_h_bar_value = h_bar.value() + move_x * d_h_bar_max
        new_v_bar_value = v_bar.value() + move_y * d_v_bar_max
        h_bar.setValue(new_h_bar_value)
        v_bar.setValue(new_v_bar_value)
