#!/usr/bin/python

import sys
from math import sqrt
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Keypoint(object):
    MOVE_VERTEX, NEAR_VERTEX = range(2)

    default_fill_color = QColor(255, 0, 0, 128)
    highlighted_fill_color = QColor(255, 0, 0, 255)
    selected_fill_color = QColor(0, 128, 255, 155)
    size = 8
    scale = 1.0

    def __init__(self, x, y):
        self.point = [x, y]

    def paint(self, painter, offset=0, highlighted=False, selected=False):
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
        elif highlighted:
            painter.fillPath(point_path, self.highlighted_fill_color)
        else:
            painter.fillPath(point_path, self.default_fill_color)

    def distance(self, p):
        return sqrt((p[0] - self.point[0])**2 + (p[1] - self.point[1])**2)
