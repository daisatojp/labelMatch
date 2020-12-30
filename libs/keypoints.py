from libs.keypoint import Keypoint


class Keypoints(object):

    def __init__(self):
        self.keypoints = []
        self.selected_idx = None
        self.highlighted_idx = None

    def set_pos(self, idx, x, y):
        self.keypoints[idx].set_pos(x, y)

    def paint(self, painter, offset=0):
        for idx, keypoint in enumerate(self.keypoints):
            keypoint.paint(
                painter=painter,
                offset=offset,
                highlighted=(idx == self.highlighted_idx),
                selected=(idx == self.selected_idx))

    def append(self, x, y):
        self.keypoints.append(Keypoint(x, y))

    def min_distance(self, x, y):
        if self.empty():
            return None
        distances = [keypoint.distance([x, y]) for keypoint in self.keypoints]
        val = min(distances)
        idx = distances.index(val)
        return val, idx

    def empty(self):
        return not 0 < len(self.keypoints)
