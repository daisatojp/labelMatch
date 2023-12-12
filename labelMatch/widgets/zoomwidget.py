from functools import partial
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from labelMatch.utils import *


class ZoomWidget:

    ZOOM_MANUAL = 1
    ZOOM_FIT_WINDOW = 2
    ZOOM_FIT_WIDTH = 3

    def __init__(self, parent, value=100):
        super(ZoomWidget, self).__init__()
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.spinbox = QSpinBox()
        self.spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spinbox.setRange(1, 500)
        self.spinbox.setSuffix(' %')
        self.spinbox.setValue(value)
        self.spinbox.setToolTip(u'Zoom Level')
        self.spinbox.setStatusTip(self.spinbox.toolTip())
        self.spinbox.setAlignment(Qt.AlignCenter)
        self.spinbox.setEnabled(False)

        self.zoom_action = QWidgetAction(self.p)
        self.zoom_action.setDefaultWidget(self.spinbox)
        self.zoom_in_action = new_action(
            self.p, 'Zoom In', partial(self.add_zoom, 10),
            'Ctrl++', 'zoom-in',
            'Increase zoom level',
            enabled=False)
        self.zoom_out_action = new_action(
            self.p, 'Zoom Out', partial(self.add_zoom, -10),
            'Ctrl+-', 'zoom-out',
            'Decrease zoom level',
            enabled=False)
        self.zoom_org_action = new_action(
            self.p, 'Original size', partial(self.set_zoom, 100),
            'Ctrl+=', 'zoom',
            'Zoom to original size',
            enabled=False)
        self.zoom_fit_window_action = new_action(
            self.p, 'Fit Window', self.set_fit_window,
            'Ctrl+F', 'fit-window',
            'Zoom follows window size',
            enabled=False)

        self.spinbox.valueChanged.connect(self.p.paintCanvas)

    def enable_actions(self):
        self.zoom_in_action.setEnabled(True)
        self.zoom_out_action.setEnabled(True)
        self.zoom_org_action.setEnabled(True)
        self.zoom_fit_window_action.setEnabled(True)

    def disable_actions(self):
        self.zoom_in_action.setEnabled(False)
        self.zoom_out_action.setEnabled(False)
        self.zoom_org_action.setEnabled(False)
        self.zoom_fit_window_action.setEnabled(False)

    def minimumSizeHint(self):
        height = self.spinbox.minimumSizeHint().height()
        fm = QFontMetrics(self.spinbox.font())
        width = fm.width(str(self.spinbox.maximum()))
        return QSize(width, height)

    def set_zoom(self, value):
        self.spinbox.setValue(value)

    def add_zoom(self, increment=10):
        self.set_zoom(self.spinbox.value() + increment)

    def set_fit_window(self, value=True):
        value = self.scale_fit_window()
        self.spinbox.setValue(int(100 * value))

    def scale_fit_window(self):
        """Figure out the size of the pixmap in order to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.mw.centralWidget().width() - e
        h1 = self.mw.centralWidget().height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.mw.canvas.pixmap.width() - 0.0
        h2 = self.mw.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def zoom_request(self, delta):
        # get the current scrollbar positions
        # calculate the percentages ~ coordinates
        h_bar = self.mw.scroll_widget.scrollbars[Qt.Horizontal]
        v_bar = self.mw.scroll_widget.scrollbars[Qt.Vertical]
        # get the current maximum, to know the difference after zooming
        h_bar_max = h_bar.maximum()
        v_bar_max = v_bar.maximum()
        # get the cursor position and canvas size
        # calculate the desired movement from 0 to 1
        # where 0 = move left
        #       1 = move right
        # up and down analogous
        cursor = QCursor()
        pos = cursor.pos()
        relative_pos = QWidget.mapFromGlobal(self.mw, pos)
        cursor_x = relative_pos.x()
        cursor_y = relative_pos.y()
        w = self.mw.scroll_widget.width()
        h = self.mw.scroll_widget.height()
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
        self.add_zoom(scale * units)
        # get the difference in scrollbar values
        # this is how far we can move
        d_h_bar_max = h_bar.maximum() - h_bar_max
        d_v_bar_max = v_bar.maximum() - v_bar_max
        # get the new scrollbar values
        new_h_bar_value = h_bar.value() + move_x * d_h_bar_max
        new_v_bar_value = v_bar.value() + move_y * d_v_bar_max
        h_bar.setValue(new_h_bar_value)
        v_bar.setValue(new_v_bar_value)
