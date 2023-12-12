import os
import os.path as osp
import numpy as np
import cv2
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from labelMatch.matching_painter import MatchingPainter


QMB = QMessageBox

CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT = Qt.PointingHandCursor
CURSOR_DRAW = Qt.CrossCursor
CURSOR_MOVE = Qt.ClosedHandCursor
CURSOR_GRAB = Qt.OpenHandCursor


class Canvas(QWidget):

    zoom_request = pyqtSignal(int)
    scroll_request = pyqtSignal(int, int)

    MODE_EDIT_KEYPOINT = 1
    MODE_EDIT_MATCH = 2

    epsilon = 32.0

    def __init__(self, parent):
        super(Canvas, self).__init__(parent=parent)
        self.p = parent  # MainWindow
        self.mw = self.p  # MainWindow

        self.mode = self.MODE_EDIT_KEYPOINT
        self.img_i_w = None
        self.img_i_h = None
        self.img_j_w = None
        self.img_j_h = None
        self.scale = 1.0
        self.pixmap = QPixmap()
        self._painter = QPainter()
        self._cursor = CURSOR_DEFAULT
        self.mp = MatchingPainter()

        # set widget options
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)

    def mouseMoveEvent(self, ev):
        if self.pixmap is None:
            return

        pos = self.transform_pos(ev.pos())
        pos_in_view_i = self.get_pos_in_view_i(pos.x(), pos.y())
        pos_in_view_j = self.get_pos_in_view_j(pos.x(), pos.y())

        if pos_in_view_i is not None:
            self.parent().window().labelCoordinates.setText(
                f'(View I) X: {pos_in_view_i[0]:0.1f}; Y: {pos_in_view_i[1]:0.1f}')
        if pos_in_view_j is not None:
            self.parent().window().labelCoordinates.setText(
                f'(View J) X: {pos_in_view_j[0]:0.1f}; Y: {pos_in_view_j[1]:0.1f}')

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if Qt.LeftButton & ev.buttons():
                if (pos_in_view_i is not None) and (self.mw.matching.selected_id_i is not None):
                    self.mw.matching.set_keypoint_pos_in_view_i(
                        self.mw.matching.selected_id_i, pos_in_view_i[0], pos_in_view_i[1])
                if (pos_in_view_j is not None) and (self.mw.matching.selected_id_j is not None):
                    self.mw.matching.set_keypoint_pos_in_view_j(
                        self.mw.matching.selected_id_j, pos_in_view_j[0], pos_in_view_j[1])
            else:
                if pos_in_view_i is not None:
                    self.mw.matching.highlighted_id_j = None
                    if not self.mw.matching.empty_i():
                        val, kid = self.mw.matching.min_distance_in_view_i(pos_in_view_i[0], pos_in_view_i[1])
                        if val < self.epsilon / self.scale:
                            self.mw.matching.highlighted_id_i = kid
                        else:
                            self.mw.matching.highlighted_id_i = None
                if pos_in_view_j is not None:
                    self.mw.matching.highlighted_id_i = None
                    if not self.mw.matching.empty_j():
                        val, kid = self.mw.matching.min_distance_in_view_j(pos_in_view_j[0], pos_in_view_j[1])
                        if val < self.epsilon / self.scale:
                            self.mw.matching.highlighted_id_j = kid
                        else:
                            self.mw.matching.highlighted_id_j = None

        if self.mode == self.MODE_EDIT_MATCH:
            if pos_in_view_i is not None:
                self.mw.matching.highlighted_id_j = None
                if not self.mw.matching.empty_i():
                    val, kid = self.mw.matching.min_distance_in_view_i(pos_in_view_i[0], pos_in_view_i[1])
                    if val < self.epsilon / self.scale and self.mw.matching.selected_id_i != kid:
                        self.mw.matching.highlighted_id_i = kid
                    else:
                        self.mw.matching.highlighted_id_i = None
            if pos_in_view_j is not None:
                self.mw.matching.highlighted_id_j = None
                if not self.mw.matching.empty_j():
                    val, kid = self.mw.matching.min_distance_in_view_j(pos_in_view_j[0], pos_in_view_j[1])
                    if val < self.epsilon / self.scale and self.mw.matching.selected_id_j != kid:
                        self.mw.matching.highlighted_id_j = kid
                    else:
                        self.mw.matching.highlighted_id_i = None

        self.mw.update_status_message()
        self.update()

    def mousePressEvent(self, ev):
        if self.pixmap is None:
            return

        pos = self.transform_pos(ev.pos())
        pos_in_view_i = self.get_pos_in_view_i(pos.x(), pos.y())
        pos_in_view_j = self.get_pos_in_view_j(pos.x(), pos.y())

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if ev.button() == Qt.LeftButton:
                if pos_in_view_i is not None:
                    ret = self.mw.matching.min_distance_in_view_i(pos_in_view_i[0], pos_in_view_i[1])
                    if ((ret is not None) and
                            (ret[0] < self.epsilon / self.scale and self.mw.matching.selected_id_i != ret[1])):
                        self.mw.matching.selected_id_i = ret[1]
                        self.mw.matching.highlighted_id_i = None
                    else:
                        self.mw.matching.append_keypoint_in_view_i(pos_in_view_i[0], pos_in_view_i[1])
                if pos_in_view_j is not None:
                    ret = self.mw.matching.min_distance_in_view_j(pos_in_view_j[0], pos_in_view_j[1])
                    if ((ret is not None) and
                            (ret[0] < self.epsilon / self.scale and self.mw.matching.selected_id_j != ret[1])):
                        self.mw.matching.selected_id_j = ret[1]
                        self.mw.matching.highlighted_id_j = None
                    else:
                        self.mw.matching.append_keypoint_in_view_j(pos_in_view_j[0], pos_in_view_j[1])

        if self.mode == self.MODE_EDIT_MATCH:
            if ev.button() == Qt.LeftButton:
                if pos_in_view_i and (not self.mw.matching.empty_i()):
                    val, kid = self.mw.matching.min_distance_in_view_i(pos_in_view_i[0], pos_in_view_i[1])
                    nearby = val < self.epsilon / self.scale
                    if nearby and (self.mw.matching.selected_id_j is not None):
                        try:
                            self.mw.matching.append_match(kid, self.mw.matching.selected_id_j)
                            self.mw.matching.clear_decoration()
                        except RuntimeWarning as e:
                            QMB.warning(self, 'Attention', '{}'.format(e), QMB.Ok)
                    elif (nearby and
                            (self.mw.matching.selected_id_j is None) and
                            (self.mw.matching.selected_id_i != kid)):
                        self.mw.matching.selected_id_i = kid
                        self.mw.matching.highlighted_id_i = None
                    elif (nearby and
                            (self.mw.matching.selected_id_j is None) and
                            (self.mw.matching.selected_id_i == kid)):
                        self.mw.matching.clear_decoration()
                if pos_in_view_j and (not self.mw.matching.empty_j()):
                    val, kid = self.mw.matching.min_distance_in_view_j(pos_in_view_j[0], pos_in_view_j[1])
                    nearby = val < self.epsilon / self.scale
                    if nearby and (self.mw.matching.selected_id_i is not None):
                        try:
                            self.mw.matching.append_match(self.mw.matching.selected_id_i, kid)
                            self.mw.matching.clear_decoration()
                        except RuntimeWarning as e:
                            QMB.warning(self, 'Attention', '{}'.format(e), QMB.Ok)
                    elif (nearby and
                            (self.mw.matching.selected_id_i is None) and
                            (self.mw.matching.selected_id_j != kid)):
                        self.mw.matching.selected_id_j = kid
                        self.mw.matching.highlighted_id_j = None
                    elif (nearby and
                            (self.mw.matching.selected_id_i is None) and
                            (self.mw.matching.selected_id_j == kid)):
                        self.mw.matching.clear_decoration()

        self.mw.update_status_message()
        self.update()

    def mouseReleaseEvent(self, ev):
        if self.pixmap is None:
            return
        if self.mw.matching is None:
            return

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if ev.button() == Qt.LeftButton:
                self.mw.matching.selected_id_i = None
                self.mw.matching.selected_id_j = None

        self.mw.update_status_message()
        self.update()

    def mouseDoubleClickEvent(self, ev):
        if self.pixmap is None:
            return
        
        pos = self.transform_pos(ev.pos())
        pos_in_view_i = self.get_pos_in_view_i(pos.x(), pos.y())
        pos_in_view_j = self.get_pos_in_view_j(pos.x(), pos.y())

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if pos_in_view_i and not self.mw.matching.empty_i():
                val, kid = self.mw.matching.min_distance_in_view_i(pos_in_view_i[0], pos_in_view_i[1])
                if val < self.epsilon / self.scale:
                    self.mw.matching.remove_keypoint_in_view_i(kid)
            if pos_in_view_j and not self.mw.matching.empty_j():
                val, kid = self.mw.matching.min_distance_in_view_j(pos_in_view_j[0], pos_in_view_j[1])
                if val < self.epsilon / self.scale:
                    self.mw.matching.remove_keypoint_in_view_j(kid)
            self.mw.matching.clear_decoration()

        if self.mode == self.MODE_EDIT_MATCH:
            if pos_in_view_i:
                val, kid = self.mw.matching.min_distance_in_view_i(pos_in_view_i[0], pos_in_view_i[1])
                if val < self.epsilon / self.scale:
                    self.mw.matching.remove_match_in_view_i(kid)
            if pos_in_view_j:
                val, kid = self.mw.matching.min_distance_in_view_j(pos_in_view_j[0], pos_in_view_j[1])
                if val < self.epsilon / self.scale:
                    self.mw.matching.remove_match_in_view_j(kid)

        self.mw.update_status_message()
        self.update()

    def paintEvent(self, event):
        if self.pixmap is None:
            return super(Canvas, self).paintEvent(event)

        p = self._painter
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offset_to_center())

        p.drawPixmap(0, 0, self.pixmap)

        if self.mw.matching is not None:
            self.mp.paint(p, self.mw.matching, self.scale)

        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(self.backgroundRole(), QColor(232, 232, 232, 255))
        self.setPalette(pal)

        p.end()

    def wheelEvent(self, ev):
        if self.pixmap is None:
            return

        qt_version = 4 if hasattr(ev, 'delta') else 5
        if qt_version == 4:
            if ev.orientation() == Qt.Vertical:
                v_delta = ev.delta()
                h_delta = 0
            else:
                h_delta = ev.delta()
                v_delta = 0
        else:
            delta = ev.angleDelta()
            h_delta = delta.x()
            v_delta = delta.y()

        mods = ev.modifiers()
        if Qt.ControlModifier == int(mods) and v_delta:
            self.zoom_request.emit(v_delta)
        else:
            v_delta and self.scroll_request.emit(v_delta, Qt.Vertical)
            h_delta and self.scroll_request.emit(h_delta, Qt.Horizontal)
        ev.accept()

    # These two, along with a call to adjustSize are required for the
    # scroll area.
    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super(Canvas, self).minimumSizeHint()

    def set_edit_keypoint_mode(self):
        self.mode = self.MODE_EDIT_KEYPOINT
        if self.mw.matching:
            self.mw.matching.clear_decoration()

    def set_edit_match_mode(self):
        self.mode = self.MODE_EDIT_MATCH
        if self.mw.matching:
            self.mw.matching.clear_decoration()

    def get_pos_in_view_i(self, x, y):
        if all([self.img_i_w, self.img_i_h, self.img_j_w, self.img_j_h]):
            if 0 <= x <= self.img_i_w and 0 <= y < self.img_i_h:
                return x, y
        return None

    def get_pos_in_view_j(self, x, y):
        if all([self.img_i_w, self.img_i_h, self.img_j_w, self.img_j_h]):
            if 0 <= x <= self.img_j_w and self.img_i_h <= y < self.img_i_h + self.img_j_h:
                return x, y - self.img_i_h
        return None

    def clear_pixmap(self):
        self.pixmap = None

    def update_pixmap(self):
        img_i = cv2.imread(osp.join(self.mw.image_dir, self.mw.matching.get_filename(self.mw.matching.get_view_id_i())))
        img_j = cv2.imread(osp.join(self.mw.image_dir, self.mw.matching.get_filename(self.mw.matching.get_view_id_j())))
        self.img_i_h, self.img_i_w, _ = img_i.shape
        self.img_j_h, self.img_j_w, _ = img_j.shape
        img_h = self.img_i_h + self.img_j_h
        img_w = max(self.img_i_w, self.img_j_w)
        img = np.zeros(shape=(img_h, img_w, 3), dtype=np.uint8)
        img[:self.img_i_h, :self.img_i_w, :] = img_i
        img[self.img_i_h:, :self.img_j_w, :] = img_j
        qimg = QImage(img.flatten(), img_w, img_h, QImage.Format_BGR888)
        self.pixmap = QPixmap.fromImage(qimg)
        self.mp.draw_offset_i_x = 0
        self.mp.draw_offset_i_y = 0
        self.mp.draw_offset_j_x = 0
        self.mp.draw_offset_j_y = self.img_i_h

    def transform_pos(self, point):
        """Convert from widget-logical coordinates to painter-logical coordinates."""
        return point / self.scale - self.offset_to_center()

    def offset_to_center(self):
        s = self.scale
        area = super(Canvas, self).size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QPointF(x, y)

    def finalise(self):
        self.update()
