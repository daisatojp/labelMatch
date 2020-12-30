import os
import os.path as osp
import numpy as np
import cv2
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT = Qt.PointingHandCursor
CURSOR_DRAW = Qt.CrossCursor
CURSOR_MOVE = Qt.ClosedHandCursor
CURSOR_GRAB = Qt.OpenHandCursor


class Canvas(QWidget):
    zoomRequest = pyqtSignal(int)
    scrollRequest = pyqtSignal(int, int)
    newShape = pyqtSignal()
    selectionChanged = pyqtSignal(bool)
    shapeMoved = pyqtSignal()
    drawingPolygon = pyqtSignal(bool)

    MODE_EDIT_KEYPOINT = 1
    MODE_EDIT_MATCH = 2

    epsilon = 32.0

    def __init__(self, *args, **kwargs):
        super(Canvas, self).__init__(*args, **kwargs)
        self.mode = self.MODE_EDIT_KEYPOINT
        self.matching = None
        self.img_i_w = None
        self.img_i_h = None
        self.img_j_w = None
        self.img_j_h = None
        self.current = None
        self.selectedShape = None  # save the selected shape here
        self.selectedShapeCopy = None
        self.drawingLineColor = QColor(0, 0, 255)
        self.drawingRectColor = QColor(0, 0, 255)
        self.prevPoint = QPointF()
        self.offsets = QPointF(), QPointF()
        self.scale = 1.0
        self.pixmap = QPixmap()
        self.visible = {}
        self._painter = QPainter()
        self._cursor = CURSOR_DEFAULT
        # Menus:
        self.menus = (QMenu(), QMenu())
        # Set widget options.
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)
        self.verified = False
        self.drawSquare = False

        #initialisation for panning
        self.pan_initial_pos = QPoint()

    def enterEvent(self, ev):
        self.overrideCursor(self._cursor)

    def leaveEvent(self, ev):
        self.restoreCursor()

    def focusOutEvent(self, ev):
        self.restoreCursor()

    def isVisible(self, shape):
        return self.visible.get(shape, True)

    def editing(self):
        return self.mode == self.EDIT

    def setEditing(self, value=True):
        self.mode = self.EDIT if value else self.CREATE
        if not value:  # Create
            self.unHighlight()
            self.deSelectShape()
        self.prevPoint = QPointF()
        self.repaint()

    def mouseMoveEvent(self, ev):
        pos = self.transformPos(ev.pos())
        posInViewI = self.GetPosInViewI(pos.x(), pos.y())
        posInViewJ = self.GetPosInViewJ(pos.x(), pos.y())

        if posInViewI:
            self.parent().window().labelCoordinates.setText(
                '(View I) X: {:0.1f}; Y: {:0.1f}'.format(posInViewI[0], posInViewI[1]))
        if posInViewJ:
            self.parent().window().labelCoordinates.setText(
                '(View J) X: {:0.1f}; Y: {:0.1f}'.format(posInViewJ[0], posInViewJ[1]))

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if Qt.LeftButton & ev.buttons():
                if posInViewI and self.matching.selected_idx_i is not None:
                    self.matching.set_keypoint_pos_in_view_i(
                        self.matching.selected_idx_i, posInViewI[0], posInViewI[1])
            else:
                if posInViewI and not self.matching.empty_i():
                    val, idx = self.matching.min_distance_in_view_i(posInViewI[0], posInViewI[1])
                    if val < self.epsilon / self.scale:
                        self.matching.highlighted_idx_i = idx
                    else:
                        self.matching.highlighted_idx_i = None
        self.update()

    def mousePressEvent(self, ev):
        pos = self.transformPos(ev.pos())
        posInViewI = self.GetPosInViewI(pos.x(), pos.y())
        posInViewJ = self.GetPosInViewJ(pos.x(), pos.y())

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if ev.button() == Qt.LeftButton:
                if posInViewI:
                    if self.matching.highlighted_idx_i is not None:
                        self.matching.selected_idx_i = self.matching.highlighted_idx_i
                        self.matching.highlighted_idx_i = None
                    else:
                        self.matching.append_keypoint_in_view_i(posInViewI[0], posInViewI[1])
        self.update()

    def mouseReleaseEvent(self, ev):
        if self.matching is None:
            return

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if ev.button() == Qt.LeftButton:
                self.matching.selected_idx_i = None
                self.matching.selected_idx_j = None

        self.update()

    def mouseDoubleClickEvent(self, ev):
        pos = self.transformPos(ev.pos())
        posInViewI = self.GetPosInViewI(pos.x(), pos.y())
        posInViewJ = self.GetPosInViewJ(pos.x(), pos.y())

        if self.mode == self.MODE_EDIT_KEYPOINT:
            if posInViewI and not self.matching.empty_i():
                val, idx = self.matching.min_distance_in_view_i(posInViewI[0], posInViewI[1])
                if val < self.epsilon / self.scale:
                    self.matching.remove_keypoint_in_view_i(idx)

    def setMatching(self, matching):
        self.matching = matching

    def setEditKeypointMode(self):
        self.mode = self.MODE_EDIT_KEYPOINT

    def setEditMatchMode(self):
        self.mode = self.MODE_EDIT_MATCH

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
        img_i = self.matching.get_img_i()
        img_j = self.matching.get_img_j()
        self.img_i_h, self.img_i_w, _ = img_i.shape
        self.img_j_h, self.img_j_w, _ = img_j.shape
        img_h = self.img_i_h + self.img_j_h
        img_w = max(self.img_i_w, self.img_j_w)
        img = np.zeros(shape=(img_h, img_w, 3), dtype=np.uint8)
        img[:self.img_i_h, :self.img_i_w, :] = img_i
        img[self.img_i_h:, :self.img_j_w, :] = img_j
        qimg = QImage(img.flatten(), img_w, img_h, QImage.Format_BGR888)
        self.pixmap = QPixmap.fromImage(qimg)
        self.matching.draw_offset_i_x = 0
        self.matching.draw_offset_i_y = 0
        self.matching.draw_offset_j_x = 0
        self.matching.draw_offset_j_y = self.img_i_h

    def endMove(self, copy=False):
        assert self.selectedShape and self.selectedShapeCopy
        shape = self.selectedShapeCopy
        #del shape.fill_color
        #del shape.line_color
        if copy:
            self.shapes.append(shape)
            self.selectedShape.selected = False
            self.selectedShape = shape
            self.repaint()
        else:
            self.selectedShape.points = [p for p in shape.points]
        self.selectedShapeCopy = None

    def hideBackroundShapes(self, value):
        self.hideBackround = value
        if self.selectedShape:
            # Only hide other shapes if there is a current selection.
            # Otherwise the user will not be able to select a shape.
            self.setHiding(True)
            self.repaint()

    def handleDrawing(self, pos):
        if self.current and self.current.reachMaxPoints() is False:
            initPos = self.current[0]
            minX = initPos.x()
            minY = initPos.y()
            targetPos = self.line[1]
            maxX = targetPos.x()
            maxY = targetPos.y()
            self.current.addPoint(QPointF(maxX, minY))
            self.current.addPoint(targetPos)
            self.current.addPoint(QPointF(minX, maxY))
            self.finalise()
        elif not self.outOfPixmap(pos):
            self.current = Shape()
            self.current.addPoint(pos)
            self.line.points = [pos, pos]
            self.setHiding()
            self.drawingPolygon.emit(True)
            self.update()

    def boundedMoveVertex(self, pos):
        index, shape = self.hVertex, self.hShape
        point = shape[index]
        if self.outOfPixmap(pos):
            size = self.pixmap.size()
            clipped_x = min(max(0, pos.x()), size.width())
            clipped_y = min(max(0, pos.y()), size.height())
            pos = QPointF(clipped_x, clipped_y)

        if self.drawSquare:
            opposite_point_index = (index + 2) % 4
            opposite_point = shape[opposite_point_index]

            min_size = min(abs(pos.x() - opposite_point.x()), abs(pos.y() - opposite_point.y()))
            directionX = -1 if pos.x() - opposite_point.x() < 0 else 1
            directionY = -1 if pos.y() - opposite_point.y() < 0 else 1
            shiftPos = QPointF(opposite_point.x() + directionX * min_size - point.x(),
                               opposite_point.y() + directionY * min_size - point.y())
        else:
            shiftPos = pos - point

        shape.moveVertexBy(index, shiftPos)

        lindex = (index + 1) % 4
        rindex = (index + 3) % 4
        lshift = None
        rshift = None
        if index % 2 == 0:
            rshift = QPointF(shiftPos.x(), 0)
            lshift = QPointF(0, shiftPos.y())
        else:
            lshift = QPointF(shiftPos.x(), 0)
            rshift = QPointF(0, shiftPos.y())
        shape.moveVertexBy(rindex, rshift)
        shape.moveVertexBy(lindex, lshift)

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

        if self.matching:
            self.matching.paint(p, self.scale)

        if self.current:
            self.current.paint(p)
            self.line.paint(p)
        if self.selectedShapeCopy:
            self.selectedShapeCopy.paint(p)

        # Paint rect
        if self.current is not None and len(self.line) == 2:
            leftTop = self.line[0]
            rightBottom = self.line[1]
            rectWidth = rightBottom.x() - leftTop.x()
            rectHeight = rightBottom.y() - leftTop.y()
            p.setPen(self.drawingRectColor)
            brush = QBrush(Qt.BDiagPattern)
            p.setBrush(brush)
            p.drawRect(leftTop.x(), leftTop.y(), rectWidth, rectHeight)

        # if self.drawing() and not self.prevPoint.isNull() and not self.outOfPixmap(self.prevPoint):
        #     p.setPen(QColor(0, 0, 0))
        #     p.drawLine(self.prevPoint.x(), 0, self.prevPoint.x(), self.pixmap.height())
        #     p.drawLine(0, self.prevPoint.y(), self.pixmap.width(), self.prevPoint.y())

        self.setAutoFillBackground(True)
        if self.verified:
            pal = self.palette()
            pal.setColor(self.backgroundRole(), QColor(184, 239, 38, 128))
            self.setPalette(pal)
        else:
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
        assert self.current
        if self.current.points[0] == self.current.points[-1]:
            self.current = None
            self.drawingPolygon.emit(False)
            self.update()
            return

        self.current.close()
        self.shapes.append(self.current)
        self.current = None
        self.setHiding(False)
        self.newShape.emit()
        self.update()

    def closeEnough(self, p1, p2):
        #d = distance(p1 - p2)
        #m = (p1-p2).manhattanLength()
        # print "d %.2f, m %d, %.2f" % (d, m, d - m)
        return distance(p1 - p2) < self.epsilon

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

    def keyPressEvent(self, ev):
        key = ev.key()
        if key == Qt.Key_Escape and self.current:
            print('ESC press')
            self.current = None
            self.drawingPolygon.emit(False)
            self.update()
        elif key == Qt.Key_Return and self.canCloseShape():
            self.finalise()
        elif key == Qt.Key_Left and self.selectedShape:
            self.moveOnePixel('Left')
        elif key == Qt.Key_Right and self.selectedShape:
            self.moveOnePixel('Right')
        elif key == Qt.Key_Up and self.selectedShape:
            self.moveOnePixel('Up')
        elif key == Qt.Key_Down and self.selectedShape:
            self.moveOnePixel('Down')

    def moveOutOfBound(self, step):
        points = [p1+p2 for p1, p2 in zip(self.selectedShape.points, [step]*4)]
        return True in map(self.outOfPixmap, points)

    def setLastLabel(self, text, line_color  = None, fill_color = None):
        assert text
        self.shapes[-1].label = text
        if line_color:
            self.shapes[-1].line_color = line_color

        if fill_color:
            self.shapes[-1].fill_color = fill_color

        return self.shapes[-1]

    def resetAllLines(self):
        assert self.shapes
        self.current = self.shapes.pop()
        self.current.setOpen()
        self.line.points = [self.current[-1], self.current[0]]
        self.drawingPolygon.emit(True)
        self.current = None
        self.drawingPolygon.emit(False)
        self.update()

    def setShapeVisible(self, shape, value):
        self.visible[shape] = value
        self.repaint()

    def currentCursor(self):
        cursor = QApplication.overrideCursor()
        if cursor is not None:
            cursor = cursor.shape()
        return cursor

    def overrideCursor(self, cursor):
        self._cursor = cursor
        if self.currentCursor() is None:
            QApplication.setOverrideCursor(cursor)
        else:
            QApplication.changeOverrideCursor(cursor)

    def restoreCursor(self):
        QApplication.restoreOverrideCursor()

    def resetState(self):
        self.restoreCursor()
        self.pixmap = None
        self.update()

    def setDrawingShapeToSquare(self, status):
        self.drawSquare = status
