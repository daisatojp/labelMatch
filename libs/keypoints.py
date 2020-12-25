from libs.keypoint import Keypoint


class Keypoints(object):

    def __init__(self):
        self.keypoints = []
        self.selected_idx = None

    def paint(self, painter, offset=0):
        for idx, keypoint in enumerate(self.keypoints):
            keypoint.paint(
                painter=painter,
                offset=offset,
                selected=(idx == self.selected_idx))

    def append(self, x, y):
        self.keypoints.append(Keypoint(x, y))

    def min_distance(self, x, y):
        distances = [keypoint.distance([x, y]) for keypoint in self.keypoints]
        val = min(distances)
        idx = distances.index(val)
        return val, idx

    def select(self, idx):
        self.selected_idx = idx
