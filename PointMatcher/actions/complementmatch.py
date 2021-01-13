import os.path as osp
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMessageBox
from PointMatcher.data.op import count_all_matches, sanity_check
from PointMatcher.utils.filesystem import icon_path


class ComplementMatchAction(QAction):

    def __init__(self, parent):
        super(ComplementMatchAction, self).__init__('Complement Match', parent)
        self.p = parent

        self.triggered.connect(self.complementMatch)
        self.setEnabled(True)

    def complementMatch(self):
        if self.p.matching is None:
            return
        matching = self.p.matching
        print('start complement, matches={}'.format(count_all_matches(matching)))
        bad_keypoints, groups = sanity_check(matching.copy())
        if 0 < len(bad_keypoints):
            QMessageBox.warning(self.p, 'Error', 'sanity check failed', QMessageBox.Ok)
            return
        for key in groups:
            group = groups[key]
            group.sort(key=lambda x: x[0])
            for i in range(0, len(group)):
                for j in range(i + 1, len(group)):
                    view_id_i = matching.get_views()[group[i][0]]['id_view']
                    view_id_j = matching.get_views()[group[j][0]]['id_view']
                    keypoint_idx_i = group[i][1]
                    keypoint_idx_j = group[j][1]
                    pair_idx = matching.append_pair(view_id_i, view_id_j, update=False)
                    matching.append_match(
                        keypoint_idx_i, keypoint_idx_j,
                        pair_idx=pair_idx, raise_exception=False, update=False)
        matching.update_adjacencies()
        self.p.pairWidget.update_all()
        print('finish complement, matches={}'.format(count_all_matches(matching)))
