import os
import os.path as osp
import copy
from functools import cmp_to_key
from collections import Counter
from collections import OrderedDict
import json
from glob import glob


class Matching:

    def __init__(self, annot_dir):
        self.annot_dir = annot_dir
        self._groups = None
        self._group_id_to_idx = None
        self._viewlist = None
        self._matchcounter = None
        self._view_i = None
        self._view_j = None
        self._matches = None

        self.load_groups()
        self.load_viewlist()
        self.initialize_matchcounter()
        self.set_view(self.get_list_of_view_id()[0], self.get_list_of_view_id()[1])

        self.highlighted_id_i = None
        self.highlighted_id_j = None
        self.selected_id_i = None
        self.selected_id_j = None

        self._update_callback = None

        self._dirty = False
        self._dirty_groups = False
        self._dirty_views = {}
        self._dirty_callback = None

    def load_groups(self):
        with open(self.get_groups_path(), 'r') as f:
            self._groups = json.load(f)
        self.update_group_id_to_idx()

    def load_viewlist(self):
        view_paths = glob(osp.join(self.get_views_dir(), '*.json'))
        self._viewlist = OrderedDict()
        for view_path in view_paths:
            with open(view_path, 'r') as f:
                v = json.load(f)
            self._viewlist[v['id']] = {
                'view_path': view_path,
                'filename': osp.join(*v['filename']),
                'keypoint_count': len(v['keypoints'])}
        self._viewlist = OrderedDict(sorted(self._viewlist.items(), key=lambda x: x[0]))

    def load_view(self, view_id):
        with open(self._viewlist[view_id]['view_path'], 'r') as f:
            x = json.load(f)
        return x

    def update_group_id_to_idx(self):
        self._group_id_to_idx = {}
        for idx, group in enumerate(self._groups['groups']):
            self._group_id_to_idx[group['id']] = idx

    def initialize_matchcounter(self):
        self._matchcounter = {}
        for group in self._groups['groups']:
            for i in range(0, len(group['keypoints'])):
                for j in range(i + 1, len(group['keypoints'])):
                    view_id_i = group['keypoints'][i][0]
                    view_id_j = group['keypoints'][j][0]
                    self.increment_matchcounter(view_id_i, view_id_j)
                    self.increment_matchcounter(view_id_j, view_id_i)

    def increment_matchcounter(self, view_id_i, view_id_j):
        if view_id_i not in self._matchcounter:
            self._matchcounter[view_id_i] = {view_id_j: 1}
        elif view_id_j not in self._matchcounter[view_id_i]:
            self._matchcounter[view_id_i][view_id_j] = 1
        else:
            self._matchcounter[view_id_i][view_id_j] += 1

    def decrement_matchcounter(self, view_id_i, view_id_j):
        self._matchcounter[view_id_i][view_id_j] -= 1

    def set_view(self, view_id_i, view_id_j):
        self._view_i = self.load_view(view_id_i)
        self._view_j = self.load_view(view_id_j)
        self._matches = OrderedDict()
        for keypoint in self._view_i['keypoints']:
            kid = keypoint['id']
            gid = keypoint['group_id']
            if gid is not None:
                self._matches[gid] = [kid, None]
        for keypoint in self._view_j['keypoints']:
            kid = keypoint['id']
            gid = keypoint['group_id']
            if gid is not None:
                if gid in self._matches:
                    self._matches[gid][1] = kid
                else:
                    self._matches[gid] = [None, kid]

    def get_views_dir(self):
        return osp.join(self.annot_dir, 'views')

    def get_groups_path(self):
        return osp.join(self.annot_dir, 'groups.json')

    def get_view_id_i(self):
        return self._view_i['id']

    def get_view_id_j(self):
        return self._view_j['id']

    def get_keypoints_i(self):
        return self._view_i['keypoints']

    def get_keypoints_j(self):
        return self._view_j['keypoints']

    def get_matches(self):
        return self._matches

    def get_filename(self, view_id):
        return self._viewlist[view_id]['filename']

    def get_keypoint_count(self, view_id):
        return self._viewlist[view_id]['keypoint_count']

    def get_match_count(self, view_id_i, view_id_j):
        if (view_id_i in self._matchcounter) and (view_id_j in self._matchcounter[view_id_i]):
            return self._matchcounter[view_id_i][view_id_j]
        else:
            return 0

    def get_pair_count(self, view_id):
        if view_id in self._matchcounter:
            return len(self._matchcounter[view_id])
        else:
            return 0

    def get_view_count(self):
        return len(self._viewlist)

    def get_list_of_view_id(self):
        return list(self._viewlist.keys())

    def get_next_view(self, view_id):
        view_idx = self.find_view_idx(view_id)
        view_idx = min(view_idx + 1, self.get_view_count() - 1)
        return self.get_list_of_view_id()[view_idx]

    def get_prev_view(self, view_id):
        view_idx = self.find_view_idx(view_id)
        view_idx = max(view_idx - 1, 0)
        return self.get_list_of_view_id()[view_idx]

    def set_keypoint_pos_in_view_i(self, keypoint_id, x, y):
        kidx = self.find_keypoint_idx(self.get_keypoints_i(), keypoint_id)
        self._view_i['keypoints'][kidx]['pos'] = [x, y]
        self._dirty_views[self._view_i['id']] = self._view_i
        self.set_update()
        self.set_dirty()

    def set_keypoint_pos_in_view_j(self, keypoint_id, x, y):
        kidx = self.find_keypoint_idx(self.get_keypoints_j(), keypoint_id)
        self._view_j['keypoints'][kidx]['pos'] = [x, y]
        self._dirty_views[self._view_i['id']] = self._view_j
        self.set_update()
        self.set_dirty()

    def append_keypoint_in_view_i(self, x, y):
        if self.empty_i():
            new_id = 0
        else:
            new_id = self._view_i['keypoints'][-1]['id'] + 1
        self._view_i['keypoints'].append({
            'id': new_id,
            'pos': [x, y],
            'group_id': None})
        self.set_update()
        self.set_dirty()

    def append_keypoint_in_view_j(self, x, y):
        if self.empty_j():
            new_id = 0
        else:
            new_id = self._view_j['keypoints'][-1]['id'] + 1
        self._view_j['keypoints'].append({
            'id': new_id,
            'pos': [x, y],
            'group_id': None})
        self.set_update()
        self.set_dirty()

    def append_match(self, keypoint_id_i, keypoint_id_j, update=True):
        kid_i = keypoint_id_i
        kid_j = keypoint_id_j
        kidx_i = self.find_keypoint_idx(self.get_keypoints_i(), kid_i)
        kidx_j = self.find_keypoint_idx(self.get_keypoints_j(), kid_j)
        gid_i = self._view_i['keypoints'][kidx_i]['group_id']
        gid_j = self._view_j['keypoints'][kidx_j]['group_id']
        vid_i = self.get_view_id_i()
        vid_j = self.get_view_id_j()
        if vid_i == vid_j:
            raise RuntimeWarning('same views')
        if len(self._groups['groups']) == 0:
            new_group_id = 0
        else:
            new_group_id = self._groups['groups'][-1]['id'] + 1
        if (gid_i is None) and (gid_j is None):
            self._groups['groups'].append({
                'id': new_group_id,
                'keypoints': [(vid_i, kid_i), (vid_j, kid_j)]})
            self.update_group_id_to_idx()
            self._view_i['keypoints'][kidx_i]['group_id'] = new_group_id
            self._view_j['keypoints'][kidx_j]['group_id'] = new_group_id
            self._matches[new_group_id] = [kid_i, kid_j]
            self._dirty_groups = True
            self._dirty_views[vid_i] = self._view_i
            self._dirty_views[vid_j] = self._view_j
            self.increment_matchcounter(vid_i, vid_j)
            self.increment_matchcounter(vid_j, vid_i)
            if update:
                self.set_update()
            self.set_dirty()
            return
        if (gid_i is not None) and (gid_j is None):
            gks_i = self._groups['groups'][self._group_id_to_idx[gid_i]]['keypoints']
            if vid_j in [gk[0] for gk in gks_i]:
                raise RuntimeWarning('conflict')
            self._groups['groups'][self._group_id_to_idx[gid_i]]['keypoints'].append((vid_j, kid_j))
            self._view_j['keypoints'][kidx_j]['group_id'] = gid_i
            self._matches[gid_i][1] = kid_j
            self._dirty_groups = True
            self._dirty_views[vid_j] = self._view_j
            for gk in gks_i:
                self.increment_matchcounter(gk[0], vid_j)
                self.increment_matchcounter(vid_j, gk[0])
            if update:
                self.set_update()
            self.set_dirty()
            return
        if (gid_i is None) and (gid_j is not None):
            gks_j = self._groups['groups'][self._group_id_to_idx[gid_j]]['keypoints']
            if vid_i in [gk[0] for gk in gks_j]:
                raise RuntimeWarning('conflict')
            self._groups['groups'][self._group_id_to_idx[gid_j]]['keypoints'].append((vid_i, kid_i))
            self._view_i['keypoints'][kidx_i]['group_id'] = gid_j
            self._matches[gid_j][0] = kid_i
            self._dirty_groups = True
            self._dirty_views[vid_i] = self._view_i
            for gk in gks_j:
                self.increment_matchcounter(vid_i, gk[0])
                self.increment_matchcounter(gk[0], vid_i)
            if update:
                self.set_update()
            self.set_dirty()
            return
        if (gid_i is not None) and (gid_j is not None):
            gks_i = self._groups['groups'][self._group_id_to_idx[gid_i]]['keypoints']
            gks_j = self._groups['groups'][self._group_id_to_idx[gid_j]]['keypoints']
            gks = gks_i + gks_j
            all_vids = [gk[0] for gk in gks]
            if any([count > 1 for item, count in Counter(all_vids).items()]):
                raise RuntimeWarning('conflict')
            del self._groups['groups'][self._group_id_to_idx[gid_i]]
            self.update_group_id_to_idx()
            del self._groups['groups'][self._group_id_to_idx[gid_j]]
            self.update_group_id_to_idx()
            self._groups['groups'].append({
                'id': new_group_id,
                'keypoints': gks})
            self.update_group_id_to_idx()
            del self._matches[gid_i]
            del self._matches[gid_j]
            self._view_i['keypoints'][kidx_i]['group_id'] = new_group_id
            self._view_j['keypoints'][kidx_j]['group_id'] = new_group_id
            self._matches[new_group_id] = [kid_i, kid_j]
            self._dirty_groups = True
            self._dirty_views[vid_i] = self._view_i
            self._dirty_views[vid_j] = self._view_j
            for gk in gks:
                vid = gk[0]
                kid = gk[1]
                if vid in (vid_i, vid_j):
                    continue
                if vid in self._dirty_views:
                    view = self._dirty_views[vid]
                else:
                    view = self.load_view(vid)
                kidx = self.find_keypoint_idx(view['keypoints'], kid)
                view['keypoints'][kidx]['group_id'] = new_group_id
                self._dirty_views[vid] = view
            for gk_i in gks_i:
                for gk_j in gks_j:
                    self.increment_matchcounter(gk_i[0], gk_j[0])
                    self.increment_matchcounter(gk_j[0], gk_i[0])
            if update:
                self.set_update()
            self.set_dirty()
            return True
        return False

    def remove_keypoint_in_view_i(self, keypoint_id):
        vid = self.get_view_id_i()
        kid = keypoint_id
        kidx = self.find_keypoint_idx(self.get_keypoints_i(), kid)
        gid = self._view_i['keypoints'][kidx]['group_id']
        if gid is not None:
            self.remove_keypoint_from_group(gid, vid, kid)
            self._dirty_groups = True
            if self._matches[gid][1] is None:
                del self._matches[gid]
            else:
                self._matches[gid][0] = None
            gks = self._groups['groups'][self._group_id_to_idx[gid]]
            for gk in gks:
                self.decrement_matchcounter(gk[0], vid)
                self.decrement_matchcounter(vid, gk[0])
        del self._view_i['keypoints'][kidx]
        self._dirty_views[vid] = self._view_i
        self.set_update()
        self.set_dirty()

    def remove_keypoint_in_view_j(self, keypoint_id):
        vid = self.get_view_id_j()
        kid = keypoint_id
        kidx = self.find_keypoint_idx(self.get_keypoints_j(), kid)
        gid = self._view_j['keypoints'][kidx]['group_id']
        if gid is not None:
            self.remove_keypoint_from_group(gid, vid, kid)
            self._dirty_groups = True
            if self._matches[gid][0] is None:
                del self._matches[gid]
            else:
                self._matches[gid][1] = None
            gks = self._groups['groups'][self._group_id_to_idx[gid]]
            for gk in gks:
                self.decrement_matchcounter(gk[0], vid)
                self.decrement_matchcounter(vid, gk[0])
        del self._view_j['keypoints'][kidx]
        self._dirty_views[vid] = self._view_j
        self.set_update()
        self.set_dirty()

    def remove_match_in_view_i(self, keypoint_id):
        vid = self.get_view_id_i()
        kid = keypoint_id
        kidx = self.find_keypoint_idx(self.get_keypoints_i(), kid)
        gid = self._view_i['keypoints'][kidx]['group_id']
        if gid is not None:
            self.remove_keypoint_from_group(gid, vid, kid)
            self._dirty_groups = True
            if self._matches[gid][1] is None:
                del self._matches[gid]
            else:
                self._matches[gid][0] = None
            self._view_i['keypoints'][kidx]['group_id'] = None
            self._dirty_views[vid] = self._view_i
            self.set_update()
            self.set_dirty()

    def remove_match_in_view_j(self, keypoint_id):
        vid = self.get_view_id_j()
        kid = keypoint_id
        kidx = self.find_keypoint_idx(self.get_keypoints_j(), kid)
        gid = self._view_j['keypoints'][kidx]['group_id']
        if gid is not None:
            self.remove_keypoint_from_group(gid, vid, kid)
            self._dirty_groups = True
            if self._matches[gid][0] is None:
                del self._matches[gid]
            else:
                self._matches[gid][1] = None
            self._view_j['keypoints'][kidx]['group_id'] = None
            self._dirty_views[vid] = self._view_j
            self.set_update()
            self.set_dirty()

    def remove_keypoint_from_group(self, gid, vid, kid):
        self._groups['groups'][self._group_id_to_idx[gid]]['keypoints'].remove((vid, kid))
        if len(self._groups['groups'][self._group_id_to_idx[gid]]) == 0:
            del self._groups['groups'][self._group_id_to_idx[gid]]
            self.update_group_id_to_idx()

    def empty_i(self):
        return len(self._view_i['keypoints']) == 0

    def empty_j(self):
        return len(self._view_j['keypoints']) == 0

    def min_distance_in_view_i(self, x, y):
        return Matching.min_distance(x, y, self._view_i['keypoints'])

    def min_distance_in_view_j(self, x, y):
        return Matching.min_distance(x, y, self._view_j['keypoints'])

    @staticmethod
    def min_distance(x, y, keypoints):
        if len(keypoints) == 0:
            return None
        distances = [((keypoint['pos'][0] - x)**2 + (keypoint['pos'][1] - y)**2)**(1/2) for keypoint in keypoints]
        val = min(distances)
        idx = distances.index(val)
        return val, keypoints[idx]['id']

    def find_view_idx(self, view_id):
        arr = [key == view_id for key in self._viewlist.keys()]
        if any(arr):
            return arr.index(True)
        else:
            return None

    def find_keypoint_idx(self, keypoints, keypoint_id):
        arr = [keypoint['id'] == keypoint_id for keypoint in keypoints]
        if any(arr):
            return arr.index(True)
        else:
            return None

    def clear_decoration(self):
        self.highlighted_id_i = None
        self.highlighted_id_j = None
        self.selected_id_i = None
        self.selected_id_j = None

    def copy(self):
        raise NotImplementedError()

    def save(self):
        self._dirty = False
        if self._dirty_groups:
            with open(self.get_groups_path(), 'w') as f:
                json.dump(self._groups, f, indent=4)
            self._dirty_groups = True
        for key, val in self._dirty_views.items():
            with open(self._viewlist[val['id']]['view_path'], 'w') as f:
                json.dump(val, f, indent=4)
            self._dirty_views = {}

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
