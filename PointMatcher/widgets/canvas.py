import os
import os.path as osp
import numpy as np
import cv2
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PointMatcher.data.painter import MatchingPainter


CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT = Qt.PointingHandCursor
CURSOR_DRAW = Qt.CrossCursor
CURSOR_MOVE = Qt.ClosedHandCursor
CURSOR_GRAB = Qt.OpenHandCursor


class Canvas(QWidget):
    zoomRequest = pyqtSignal(int)
    scrollRequest = pyqtSignal(int, int)

    MODE_EDIT_KEYPOINT = 1
    MODE_EDIT_MATCH = 2

    epsilon = 32.0

    def __init__(self, parent):
        super(Canvas, self).__init__(parent=parent)
        self.p = parent
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

    def enterEvent(self, ev):
        pass

    def leaveEvent(self, ev):
        pass

    def focusOutEvent(self, ev):
        pass

    def mouseMoveEvent(self, ev):
        pos = self.transformPos(ev.pos())
        posInViewI = self.GetPosInViewI(pos.x(), pos.y())
        posInViewJ = self.GetPosInViewJ(pos.x(), pos.y())

        if posInViewI is not None:
            self.parent().window().labelCoordinates.setText(
                '(View I) X: {:0.1f}; Y: {:0.1f}'.format(posInViewI[0], posInViewI[1]))
        if posInViewJ is not None:
            self.parent().window().labelCoordinates.setText(
                '(View J) X: {:0.1f}; Y: {:0.1f}'.format(posInViewJ[0], posInViewJ[1]))

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if Qt.LeftButton & ev.buttons():
                if (posInViewI is not None) and (self.p.matching.selected_id_i is not None):
                    self.p.matching.set_keypoint_pos_in_view_i(
                        self.p.matching.selected_id_i, posInViewI[0], posInViewI[1])
                if (posInViewJ is not None) and (self.p.matching.selected_id_j is not None):
                    self.p.matching.set_keypoint_pos_in_view_j(
                        self.p.matching.selected_id_j, posInViewJ[0], posInViewJ[1])
            else:
                if posInViewI is not None:
                    self.p.matching.highlighted_id_j = None
                    if not self.p.matching.empty_i():
                        val, kid = self.p.matching.min_distance_in_view_i(posInViewI[0], posInViewI[1])
                        if val < self.epsilon / self.scale:
                            self.p.matching.highlighted_id_i = kid
                        else:
                            self.p.matching.highlighted_id_i = None
                if posInViewJ is not None:
                    self.p.matching.highlighted_id_i = None
                    if not self.p.matching.empty_j():
                        val, kid = self.p.matching.min_distance_in_view_j(posInViewJ[0], posInViewJ[1])
                        if val < self.epsilon / self.scale:
                            self.p.matching.highlighted_id_j = kid
                        else:
                            self.p.matching.highlighted_id_j = None

        if self.mode == self.MODE_EDIT_MATCH:
            if posInViewI is not None:
                self.p.matching.highlighted_id_j = None
                if not self.p.matching.empty_i():
                    val, kid = self.p.matching.min_distance_in_view_i(posInViewI[0], posInViewI[1])
                    if val < self.epsilon / self.scale and self.p.matching.selected_id_i != kid:
                        self.p.matching.highlighted_id_i = kid
                    else:
                        self.p.matching.highlighted_id_i = None
            if posInViewJ is not None:
                self.p.matching.highlighted_id_j = None
                if not self.p.matching.empty_j():
                    val, kid = self.p.matching.min_distance_in_view_j(posInViewJ[0], posInViewJ[1])
                    if val < self.epsilon / self.scale and self.p.matching.selected_id_j != kid:
                        self.p.matching.highlighted_id_j = kid
                    else:
                        self.p.matching.highlighted_id_i = None

        self.p.updateStatusMessage()
        self.update()

    def mousePressEvent(self, ev):
        pos = self.transformPos(ev.pos())
        posInViewI = self.GetPosInViewI(pos.x(), pos.y())
        posInViewJ = self.GetPosInViewJ(pos.x(), pos.y())

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if ev.button() == Qt.LeftButton:
                if posInViewI is not None:
                    ret = self.p.matching.min_distance_in_view_i(posInViewI[0], posInViewI[1])
                    if (ret is not None) and \
                            (ret[0] < self.epsilon / self.scale and self.p.matching.selected_id_i != ret[1]):
                        self.p.matching.selected_id_i = ret[1]
                        self.p.matching.highlighted_id_i = None
                    else:
                        self.p.matching.append_keypoint_in_view_i(posInViewI[0], posInViewI[1])
                if posInViewJ is not None:
                    ret = self.p.matching.min_distance_in_view_j(posInViewJ[0], posInViewJ[1])
                    if (ret is not None) and \
                            (ret[0] < self.epsilon / self.scale and self.p.matching.selected_id_j != ret[1]):
                        self.p.matching.selected_id_j = ret[1]
                        self.p.matching.highlighted_id_j = None
                    else:
                        self.p.matching.append_keypoint_in_view_j(posInViewJ[0], posInViewJ[1])

        if self.mode == self.MODE_EDIT_MATCH:
            if ev.button() == Qt.LeftButton:
                if posInViewI and (not self.p.matching.empty_i()):
                    val, kid = self.p.matching.min_distance_in_view_i(posInViewI[0], posInViewI[1])
                    nearby = val < self.epsilon / self.scale
                    if nearby and (self.p.matching.selected_id_j is not None):
                        try:
                            self.p.matching.append_match(kid, self.p.matching.selected_id_j)
                            self.p.matching.clear_decoration()
                        except RuntimeWarning as e:
                            QMessageBox.warning(self, 'Attention', '{}'.format(e), QMessageBox.Ok)
                    elif nearby and (self.p.matching.selected_id_j is None) and (self.p.matching.selected_id_i != kid):
                        self.p.matching.selected_id_i = kid
                        self.p.matching.highlighted_id_i = None
                    elif nearby and (self.p.matching.selected_id_j is None) and (self.p.matching.selected_id_i == kid):
                        self.p.matching.clear_decoration()
                if posInViewJ and (not self.p.matching.empty_j()):
                    val, kid = self.p.matching.min_distance_in_view_j(posInViewJ[0], posInViewJ[1])
                    nearby = val < self.epsilon / self.scale
                    if nearby and (self.p.matching.selected_id_i is not None):
                        try:
                            self.p.matching.append_match(self.p.matching.selected_id_i, kid)
                            self.p.matching.clear_decoration()
                        except RuntimeWarning as e:
                            QMessageBox.warning(self, 'Attention', '{}'.format(e), QMessageBox.Ok)
                    elif nearby and (self.p.matching.selected_id_i is None) and (self.p.matching.selected_id_j != kid):
                        self.p.matching.selected_id_j = kid
                        self.p.matching.highlighted_id_j = None
                    elif nearby and (self.p.matching.selected_id_i is None) and (self.p.matching.selected_id_j == kid):
                        self.p.matching.clear_decoration()

        self.p.updateStatusMessage()
        self.update()

    def mouseReleaseEvent(self, ev):
        if self.p.matching is None:
            return

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if ev.button() == Qt.LeftButton:
                self.p.matching.selected_id_i = None
                self.p.matching.selected_id_j = None

        self.p.updateStatusMessage()
        self.update()

    def mouseDoubleClickEvent(self, ev):
        pos = self.transformPos(ev.pos())
        posInViewI = self.GetPosInViewI(pos.x(), pos.y())
        posInViewJ = self.GetPosInViewJ(pos.x(), pos.y())

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if posInViewI and not self.p.matching.empty_i():
                val, kid = self.p.matching.min_distance_in_view_i(posInViewI[0], posInViewI[1])
                if val < self.epsilon / self.scale:
                    self.p.matching.remove_keypoint_in_view_i(kid)
            if posInViewJ and not self.p.matching.empty_j():
                val, kid = self.p.matching.min_distance_in_view_j(posInViewJ[0], posInViewJ[1])
                if val < self.epsilon / self.scale:
                    self.p.matching.remove_keypoint_in_view_j(kid)
            self.p.matching.clear_decoration()

        if self.mode == self.MODE_EDIT_MATCH:
            if posInViewI:
                val, kid = self.p.matching.min_distance_in_view_i(posInViewI[0], posInViewI[1])
                if val < self.epsilon / self.scale:
                    self.p.matching.remove_match_in_view_i(kid)
            if posInViewJ:
                val, kid = self.p.matching.min_distance_in_view_j(posInViewJ[0], posInViewJ[1])
                if val < self.epsilon / self.scale:
                    self.p.matching.remove_match_in_view_j(kid)

        self.p.updateStatusMessage()
        self.update()

    def setEditKeypointMode(self):
        self.mode = self.MODE_EDIT_KEYPOINT
        if self.p.matching:
            self.p.matching.clear_decoration()

    def setEditMatchMode(self):
        self.mode = self.MODE_EDIT_MATCH
        if self.p.matching:
            self.p.matching.clear_decoration()

    def GetPosInViewI(self, x, y):
        if all([self.img_i_w, self.img_i_h, self.img_j_w, self.img_j_h]):
            if 0 <= x <= self.img_i_w and 0 <= y < self.img_i_h:
                return x, y
        return None

    def GetPosInViewJ(self, x, y):
        if all([self.img_i_w, self.img_i_h, self.img_j_w, self.img_j_h]):
            if 0 <= x <= self.img_j_w and self.img_i_h <= y < self.img_i_h + self.img_j_h:
                return x, y - self.img_i_h
        return None

    def updatePixmap(self):
        img_i = cv2.imread(osp.join(self.p.imageDir, self.p.matching.get_filename(self.p.matching.get_view_id_i())))
        img_j = cv2.imread(osp.join(self.p.imageDir, self.p.matching.get_filename(self.p.matching.get_view_id_j())))
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

    def paintEvent(self, event):
        if not self.pixmap:
            return super(Canvas, self).paintEvent(event)

        p = self._painter
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offsetToCenter())

        p.drawPixmap(0, 0, self.pixmap)

        if self.p.matching is not None:
            self.mp.paint(p, self.p.matching, self.scale)

        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(self.backgroundRole(), QColor(232, 232, 232, 255))
        self.setPalette(pal)

        p.end()

    def transformPos(self, point):
        """Convert from widget-logical coordinates to painter-logical coordinates."""
        return point / self.scale - self.offsetToCenter()

    def offsetToCenter(self):
        s = self.scale
        area = super(Canvas, self).size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QPointF(x, y)

    def finalise(self):
        self.update()

    # These two, along with a call to adjustSize are required for the
    # scroll area.
    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super(Canvas, self).minimumSizeHint()

    def wheelEvent(self, ev):
        qt_version = 4 if hasattr(ev, "delta") else 5
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
            self.zoomRequest.emit(v_delta)
        else:
            v_delta and self.scrollRequest.emit(v_delta, Qt.Vertical)
            h_delta and self.scrollRequest.emit(h_delta, Qt.Horizontal)
        ev.accept()
