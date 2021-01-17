from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPainterPath
from PyQt5.QtGui import QPen


class MatchingPainter:

    keypoint_fill_color = QColor(255, 0, 0, 128)
    keypoint_highlighted_fill_color = QColor(255, 0, 0, 255)
    keypoint_selected_fill_color = QColor(0, 128, 255, 155)
    keypoint_size = 8
    match_line_colors = [
        (255, 0, 0, 128),
        (0, 255, 0, 128),
        (0, 0, 255, 128),
        (255, 255, 0, 128),
        (255, 0, 255, 128),
        (0, 255, 255, 128),
        (255, 255, 255, 128)]
    match_line_width = 2
    match_highlighted_line_width = 3
    match_selected_line_width = 3
    match_line_alpha = 128
    match_highlighted_line_alpha = 255
    match_selected_line_alpha = 255

    def __init__(self):
        self.draw_offset_i_x = 0
        self.draw_offset_i_y = 0
        self.draw_offset_j_x = 0
        self.draw_offset_j_y = 0

    def paint(self, painter, matching, scale):
        keypoints_i = matching.get_keypoints_i()
        keypoints_j = matching.get_keypoints_j()
        matches = matching.get_matches()

        pen = QPen(self.keypoint_fill_color)
        pen.setWidth(max(1, int(round(2.0 / scale))))
        painter.setPen(pen)
        for keypoint in keypoints_i:
            kid = keypoint['id']
            pos = keypoint['pos']
            point_path = QPainterPath()
            point_path.addEllipse(
                pos[0] + self.draw_offset_i_x - (self.keypoint_size / scale) / 2.0,
                pos[1] + self.draw_offset_i_y - (self.keypoint_size / scale) / 2.0,
                (self.keypoint_size / scale),
                (self.keypoint_size / scale))
            painter.drawPath(point_path)
            if kid == matching.selected_id_i:
                painter.fillPath(point_path, self.keypoint_selected_fill_color)
            elif kid == matching.highlighted_id_i:
                painter.fillPath(point_path, self.keypoint_highlighted_fill_color)
            else:
                painter.fillPath(point_path, self.keypoint_fill_color)
        for keypoint in keypoints_j:
            kid = keypoint['id']
            pos = keypoint['pos']
            point_path = QPainterPath()
            point_path.addEllipse(
                pos[0] + self.draw_offset_j_x - (self.keypoint_size / scale) / 2.0,
                pos[1] + self.draw_offset_j_y - (self.keypoint_size / scale) / 2.0,
                (self.keypoint_size / scale),
                (self.keypoint_size / scale))
            painter.drawPath(point_path)
            if kid == matching.selected_id_j:
                painter.fillPath(point_path, self.keypoint_selected_fill_color)
            elif kid == matching.highlighted_id_j:
                painter.fillPath(point_path, self.keypoint_highlighted_fill_color)
            else:
                painter.fillPath(point_path, self.keypoint_fill_color)

        for idx, key in enumerate(matches.keys()):
            match = matches[key]
            if (match[0] is None) or (match[1] is None):
                continue
            kid_i = match[0]
            kid_j = match[1]
            kidx_i = matching.find_keypoint_idx(keypoints_i, kid_i)
            kidx_j = matching.find_keypoint_idx(keypoints_j, kid_j)
            pos_i = keypoints_i[kidx_i]['pos']
            pos_j = keypoints_j[kidx_j]['pos']
            match_path = QPainterPath()
            match_path.moveTo(pos_i[0] + self.draw_offset_i_x, pos_i[1] + self.draw_offset_i_y)
            match_path.lineTo(pos_j[0] + self.draw_offset_j_x, pos_j[1] + self.draw_offset_j_y)
            color = self.match_line_colors[idx % len(self.match_line_colors)]
            if kid_i == matching.selected_id_i or kid_j == matching.selected_id_j:
                pen = QPen(QColor(color[0], color[1], color[2], self.match_selected_line_alpha))
                pen.setWidth(self.match_highlighted_line_width / scale)
            elif kid_i == matching.highlighted_id_i or kid_j == matching.highlighted_id_j:
                pen = QPen(QColor(color[0], color[1], color[2], self.match_highlighted_line_alpha))
                pen.setWidth(self.match_selected_line_width / scale)
            else:
                pen = QPen(QColor(color[0], color[1], color[2], self.match_line_alpha))
                pen.setWidth(self.match_line_width / scale)
            painter.setPen(pen)
            painter.drawPath(match_path)
