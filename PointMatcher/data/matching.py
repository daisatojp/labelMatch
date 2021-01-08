import os
import os.path as osp
import json
import pickle
import cv2


class Matching:

    def __init__(self, data=None, image_dir=None):

        if type(data) is dict:
            self.data = data
        elif type(data) is Matching:
            self.data = data.data.copy()
        elif type(data) is str:
            ext = osp.splitext(data)[1]
            if ext == '.json':
                with open(data, 'r') as f:
                    self.data = json.load(f)
            elif ext == '.pkl':
                with open(data, 'rb') as f:
                    self.data = pickle.load(f)
            else:
                raise RuntimeError('invalid filename ({})'.format(data))
        else:
            self.data = None
        self.image_dir = image_dir

        self.highlighted_idx_i = None
        self.highlighted_idx_j = None
        self.selected_idx_i = None
        self.selected_idx_j = None

        self._view_id_i = None
        self._view_id_j = None
        self._view_idx_i = None
        self._view_idx_j = None
        self._pair_idx = None

        self._update_callback = None

        self._dirty = False
        self._dirty_callback = None

    def get_views(self):
        return self.data['views']

    def get_pairs(self):
        return self.data['pairs']

    def get_view_i(self):
        return self.data['views'][self._view_idx_i]

    def get_view_j(self):
        return self.data['views'][self._view_idx_j]

    def get_pair(self):
        return self.data['pairs'][self._pair_idx]

    def get_view_id_i(self):
        return self._view_id_i

    def get_view_id_j(self):
        return self._view_id_j

    def get_view_idx_i(self):
        return self._view_idx_i

    def get_view_idx_j(self):
        return self._view_idx_j

    def get_pair_idx(self):
        return self._pair_idx

    def get_view_id_by_view_idx(self, idx):
        return self.data['views'][idx]['id_view']

    def get_view_id_i_by_pair_idx(self, idx):
        return self.data['pairs'][idx]['id_view_i']

    def get_view_id_j_by_pair_idx(self, idx):
        return self.data['pairs'][idx]['id_view_j']

    def get_keypoints_count(self, view_id):
        view_idx = self.find_view_idx(view_id)
        if view_idx is None:
            return len(self.data['views'][view_idx]['keypoints'])
        else:
            return None

    def get_matches_count(self, view_id_i, view_id_j):
        pair_idx = self.find_pair_idx(view_id_i, view_id_j)
        if pair_idx is not None:
            return len(self.data['pairs'][pair_idx]['matches'])
        else:
            return None

    def get_img_i(self):
        return cv2.imread(osp.join(self.image_dir, osp.join(*self.data['views'][self._view_idx_i]['filename'])))

    def get_img_j(self):
        return cv2.imread(osp.join(self.image_dir, osp.join(*self.data['views'][self._view_idx_j]['filename'])))

    def get_next_view_pair(self):
        if self._pair_idx is None:
            raise RuntimeError('view pair is not set.')
        match_idx = min(len(self.data['pairs']) - 1, self._pair_idx + 1)
        view_id_i = self.data['pairs'][match_idx]['id_view_i']
        view_id_j = self.data['pairs'][match_idx]['id_view_j']
        return view_id_i, view_id_j

    def get_prev_view_pair(self):
        if self._pair_idx is None:
            raise RuntimeError('view pair is not set.')
        match_idx = max(0, self._pair_idx - 1)
        view_id_i = self.data['pairs'][match_idx]['id_view_i']
        view_id_j = self.data['pairs'][match_idx]['id_view_j']
        return view_id_i, view_id_j

    def set_view(self, view_id_i, view_id_j):
        self._view_id_i = view_id_i
        self._view_id_j = view_id_j
        self._view_idx_i = self.find_view_idx(view_id_i)
        self._view_idx_j = self.find_view_idx(view_id_j)
        self._pair_idx = self.find_pair_idx(view_id_i, view_id_j)

    def set_keypoint_pos_in_view_i(self, idx, x, y):
        self.data['views'][self._view_idx_i]['keypoints'][idx] = [x, y]
        self.set_update()
        self.set_dirty()

    def set_keypoint_pos_in_view_j(self, idx, x, y):
        self.data['views'][self._view_idx_j]['keypoints'][idx] = [x, y]
        self.set_update()
        self.set_dirty()

    def append_keypoint_in_view_i(self, x, y):
        self.data['views'][self._view_idx_i]['keypoints'].append([x, y])
        self.set_update()
        self.set_dirty()

    def append_keypoint_in_view_j(self, x, y):
        self.data['views'][self._view_idx_j]['keypoints'].append([x, y])
        self.set_update()
        self.set_dirty()

    def append_pair(self, view_id_i, view_id_j, update=True):
        if self.find_pair_idx(view_id_i, view_id_j) is None:
            self.data['pairs'].append({
                'id_view_i': view_id_i,
                'id_view_j': view_id_j,
                'matches': []})
            if update:
                self.set_update()
            self.set_dirty()
            return True
        else:
            return False

    def append_match(self, keypoint_idx_i, keypoint_idx_j):
        if self._pair_idx is not None:
            arr = [match[0] == keypoint_idx_i or match[1] == keypoint_idx_j
                   for match in self.data['pairs'][self._pair_idx]['matches']]
            if any(arr):
                raise RuntimeWarning('this keypoints are assined as a match')
            self.data['pairs'][self._pair_idx]['matches'].append([keypoint_idx_i, keypoint_idx_j])
        else:
            raise RuntimeWarning('This view pair is not registered.')
        self.set_update()
        self.set_dirty()

    def remove_keypoint_in_view_i(self, idx):
        self.remove_keypoint(self._view_id_i, idx)
        # update and dirty is called in remove_keypoint

    def remove_keypoint_in_view_j(self, idx):
        self.remove_keypoint(self._view_id_j, idx)
        # update and dirty is called in remove_keypoint

    def remove_keypoint(self, view_id, idx):
        view_idx = self.find_view_idx(view_id)
        keypoints = self.data['views'][view_idx]['keypoints']
        self.data['views'][view_idx]['keypoints'] = keypoints[:idx] + keypoints[idx+1:]
        for i in range(len(self.data['pairs'])):
            if self.data['pairs'][i]['id_view_i'] == view_id:
                j = 0
                while j < len(self.data['pairs'][i]['matches']):
                    if self.data['pairs'][i]['matches'][j][0] == idx:
                        self.data['pairs'][i]['matches'].pop(j)
                        continue
                    if self.data['pairs'][i]['matches'][j][0] > idx:
                        self.data['pairs'][i]['matches'][j][0] -= 1
                    j += 1
            if self.data['pairs'][i]['id_view_j'] == view_id:
                j = 0
                while j < len(self.data['pairs'][i]['matches']):
                    if self.data['pairs'][i]['matches'][j][1] == idx:
                        self.data['pairs'][i]['matches'].pop(j)
                        continue
                    if self.data['pairs'][i]['matches'][j][1] > idx:
                        self.data['pairs'][i]['matches'][j][1] -= 1
                    j += 1

        self.set_update()
        self.set_dirty()

    def remove_pair(self, view_id_i, view_id_j):
        if (view_id_i, view_id_j) == (self._view_id_i, self._view_id_j):
            raise RuntimeError('invelid view_id_i and view_id_j')
        idx = self.find_pair_idx(view_id_i, view_id_j)
        if idx is not None:
            self.data['pairs'].pop(idx)
            self.set_view(self._view_id_i, self._view_id_j)
            self.set_update()
            self.set_dirty()

    def remove_match(self, match_idx):
        if self._pair_idx is None:
            raise RuntimeError('runtime error at remove_match')
        self.data['pairs'][self._pair_idx]['matches'].pop(match_idx)
        self.set_update()
        self.set_dirty()

    def empty_i(self):
        return len(self.data['views'][self._view_idx_i]['keypoints']) == 0

    def empty_j(self):
        return len(self.data['views'][self._view_idx_j]['keypoints']) == 0

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

    def find_pair_idx(self, view_id_i, view_id_j):
        arr = [m['id_view_i'] == view_id_i and m['id_view_j'] == view_id_j for m in self.data['pairs']]
        if any(arr):
            return arr.index(True)
        else:
            return None

    def find_match_idx_in_view_i(self, keypoint_idx):
        if self._pair_idx is None:
            return None
        arr = [m[0] == keypoint_idx for m in self.data['pairs'][self._pair_idx]['matches']]
        if any(arr):
            return arr.index(True)
        else:
            return None

    def find_match_idx_in_view_j(self, keypoint_idx):
        if self._pair_idx is None:
            return None
        arr = [m[1] == keypoint_idx for m in self.data['pairs'][self._pair_idx]['matches']]
        if any(arr):
            return arr.index(True)
        else:
            return None

    def clear_decoration(self):
        self.highlighted_idx_i = None
        self.highlighted_idx_j = None
        self.selected_idx_i = None
        self.selected_idx_j = None

    def save(self, file_path):
        ext = osp.splitext(file_path)[1]
        if ext == '.json':
            with open(file_path, 'w') as f:
                json.dump(self.data, f)
        elif ext == '.pkl':
            with open(file_path, 'wb') as f:
                pickle.dump(self.data, f)
        else:
            raise RuntimeError('invalid file_path ({})'.format(file_path))
        self._dirty = False

    def set_update(self):
        if self._update_callback:
            self._update_callback()

    def set_update_callback(self, f):
        self._update_callback = f

    def dirty(self):
        return self._dirty

    def set_dirty(self):
        if not self._dirty:
            self._dirty = True
            if self._dirty_callback:
                self._dirty_callback()

    def set_dirty_callback(self, f):
        self._dirty_callback = f

    # def sanity_check(self):
    #     x = dict()
        # group_id = 0
        # for p in self.data['pairs']:
        #     for m in p['matches']:

    @staticmethod
    def min_distance(x, y, keypoints):
        if len(keypoints) == 0:
            return None
        distances = [((keypoint[0] - x)**2 + (keypoint[1] - y)**2)**(1/2) for keypoint in keypoints]
        val = min(distances)
        idx = distances.index(val)
        return val, idx
