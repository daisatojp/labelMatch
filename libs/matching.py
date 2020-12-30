import os
import os.path as osp
import json
import cv2
from PyQt5.QtGui import *


class Matching:

    default_fill_color = QColor(255, 0, 0, 128)
    highlighted_fill_color = QColor(255, 0, 0, 255)
    selected_fill_color = QColor(0, 128, 255, 155)
    size = 8

    def __init__(self, data=None, image_dir=None):

        if type(data) is dict:
            self.data = data
        elif type(data) is str:
            with open(data, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = None
        self.image_dir = image_dir

        self.highlighted_idx_i = None
        self.highlighted_idx_j = None
        self.selected_idx_i = None
        self.selected_idx_j = None
        self.draw_offset_i_x = 0
        self.draw_offset_i_y = 0
        self.draw_offset_j_x = 0
        self.draw_offset_j_y = 0

        self._view_id_i = None
        self._view_id_j = None
        self._view_idx_i = None
        self._view_idx_j = None
        self._match_idx = None

    def paint(self, painter, scale):
        color = self.default_fill_color
        pen = QPen(color)
        pen.setWidth(max(1, int(round(2.0 / scale))))
        painter.setPen(pen)
        for idx, keypoint in enumerate(self.data['views'][self._view_idx_i]['keypoints']):
            point_path = QPainterPath()
            point_path.addEllipse(
                keypoint[0] + self.draw_offset_i_x - (self.size / scale) / 2.0,
                keypoint[1] + self.draw_offset_i_y - (self.size / scale) / 2.0,
                (self.size / scale),
                (self.size / scale))
            painter.drawPath(point_path)
            if idx == self.selected_idx_i:
                painter.fillPath(point_path, self.selected_fill_color)
            elif idx == self.highlighted_idx_i:
                painter.fillPath(point_path, self.highlighted_fill_color)
            else:
                painter.fillPath(point_path, self.default_fill_color)
        for idx, keypoint in enumerate(self.data['views'][self._view_idx_j]['keypoints']):
            point_path = QPainterPath()
            point_path.addEllipse(
                keypoint[0] + self.draw_offset_j_x - (self.size / scale) / 2.0,
                keypoint[1] + self.draw_offset_j_y - (self.size / scale) / 2.0,
                (self.size / scale),
                (self.size / scale))
            painter.drawPath(point_path)
            if idx == self.selected_idx_j:
                painter.fillPath(point_path, self.selected_fill_color)
            elif idx == self.highlighted_idx_j:
                painter.fillPath(point_path, self.highlighted_fill_color)
            else:
                painter.fillPath(point_path, self.default_fill_color)

    def get_matches(self):
        return self.data['matches']

    def get_views(self):
        return self.data['views']

    def get_view_idx_i(self):
        return self._view_idx_i

    def get_view_idx_j(self):
        return self._view_idx_j

    def get_img_i(self):
        return cv2.imread(osp.join(self.image_dir, osp.join(*self.data['views'][self._view_idx_i]['filename'])))

    def get_img_j(self):
        return cv2.imread(osp.join(self.image_dir, osp.join(*self.data['views'][self._view_idx_j]['filename'])))

    def set_view(self, view_id_i, view_id_j):
        self._view_id_i = view_id_i
        self._view_id_j = view_id_j
        self._view_idx_i = self.find_view_idx(view_id_i)
        self._view_idx_j = self.find_view_idx(view_id_j)
        self._match_idx = self.find_match_idx(view_id_i, view_id_j)

    def append_keypoint_in_view_i(self, x, y):
        self.data['views'][self._view_idx_i]['keypoints'].append([x, y])

    def append_keypoint_in_view_j(self, x, y):
        self.data['views'][self._view_idx_j]['keypoints'].append([x, y])

    def set_keypoint_pos_in_view_i(self, idx, x, y):
        self.data['views'][self._view_idx_i]['keypoints'][idx] = [x, y]

    def set_keypoint_pos_in_view_j(self, idx, x, y):
        self.data['views'][self._view_idx_j]['keypoints'][idx] = [x, y]

    def remove_keypoint_in_view_i(self, idx):
        self.remove_keypoint(self._view_id_i, idx)

    def remove_keypoint_in_view_j(self, idx):
        self.remove_keypoint(self._view_id_j, idx)

    def remove_keypoint(self, view_id, idx):
        view_idx = Matching.find_view_idx(self.data, view_id)
        keypoints = self.data['views'][view_idx]['keypoints']
        self.data['views'][view_idx]['keypoints'] = keypoints[:idx] + keypoints[idx+1:]
        for i in range(len(self.data['matches'])):
            if self.data['matches'][i]['id_view_i'] == view_id:
                for j in range(len(self.data['matches'][i]['match'])):
                    if self.data['matches'][i]['match'][j][0] == idx:
                        self.data['matches'][i]['match'].pop(j)
                    if self.data['matches'][i]['match'][j][0] > idx:
                        self.data['matches'][i]['match'][j][0] -= 1
            if self.data['matches'][i]['view_j'] == view_id:
                for j in range(len(self.data['matches'][i]['match'])):
                    if self.data['matches'][i]['match'][j][1] == idx:
                        self.data['matches'][i]['match'].pop(j)
                    if self.data['matches'][i]['match'][j][1] > idx:
                        self.data['matches'][i]['match'][j][1] -= 1

    def empty_i(self):
        return Matching.empty(self.data['views'][self._view_idx_i]['keypoints'])

    def empty_j(self):
        return Matching.empty(self.data['views'][self._view_idx_j]['keypoints'])

    def min_distance_in_view_i(self, x, y):
        return Matching.min_distance(x, y, self.data['views'][self._view_idx_i]['keypoints'])

    def min_distance_in_view_j(self, x, y):
        return Matching.min_distance(x, y, self.data['views'][self._view_idx_j]['keypoints'])

    def find_view_idx(self, view_id):
        arr = [v['id_view'] == view_id for v in self.data['views']]
        if any(arr):
            return arr.index(True)
        else:
            return None

    def find_match_idx(self, view_id_i, view_id_j):
        arr = [m['id_view_i'] == view_id_i and m['id_view_j'] == view_id_j for m in self.data['matches']]
        if any(arr):
            return arr.index(True)
        else:
            return None

    @staticmethod
    def empty(keypoints):
        if 0 < len(keypoints):
            return False
        else:
            return True

    @staticmethod
    def min_distance(x, y, keypoints):
        if Matching.empty(keypoints):
            return None
        distances = [((keypoint[0] - x)**2 + (keypoint[1] - y)**2)**(1/2) for keypoint in keypoints]
        val = min(distances)
        idx = distances.index(val)
        return val, idx
