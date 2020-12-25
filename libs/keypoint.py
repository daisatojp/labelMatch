#!/usr/bin/python

import sys
from math import sqrt
from PyQt5.QtGui import *
from PyQt5.QtCore import *

DEFAULT_FILL_COLOR = QColor(255, 0, 0, 128)
DEFAULT_SELECT_FILL_COLOR = QColor(0, 128, 255, 155)


class Keypoint(object):
    MOVE_VERTEX, NEAR_VERTEX = range(2)

    fill_color = DEFAULT_FILL_COLOR
    selected_fill_color = DEFAULT_SELECT_FILL_COLOR
    size = 8
    scale = 1.0

    def __init__(self, x, y):
        self.point = [x, y]

    def paint(self, painter, offset=0, selected=False):
        color = self.fill_color
        pen = QPen(color)
        pen.setWidth(max(1, int(round(2.0 / self.scale))))
        painter.setPen(pen)
        point_path = QPainterPath()
        point_path.addEllipse(
            self.point[0] - (self.size / self.scale) / 2.0,
            self.point[1] + offset - (self.size / self.scale) / 2.0,
            (self.size / self.scale),
            (self.size / self.scale))
        painter.drawPath(point_path)
        if selected:
            painter.fillPath(point_path, self.selected_fill_color)
        else:
            painter.fillPath(point_path, self.fill_color)

    def distance(self, p):
        return sqrt((p[0] - self.point[0])**2 + (p[1] - self.point[1])**2)

    def moveBy(self, offset):
        self.points = [p + offset for p in self.points]

    def moveVertexBy(self, i, offset):
        self.points[i] = self.points[i] + offset

    def copy(self):
        shape = Shape("%s" % self.label)
        shape.points = [p for p in self.points]
        shape.fill = self.fill
        shape.selected = self.selected
        shape._closed = self._closed
        if self.line_color != Shape.line_color:
            shape.line_color = self.line_color
        if self.fill_color != Shape.fill_color:
            shape.fill_color = self.fill_color
        shape.difficult = self.difficult
        return shape

    def __len__(self):
        return len(self.points)

    def __getitem__(self, key):
        return self.points[key]

    def __setitem__(self, key, value):
        self.points[key] = value
