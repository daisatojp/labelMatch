import collections


def count_all_keypoints(matching):
    n = 0
    for view in matching.get_views():
        n += len(view['keypoints'])
    return n


def list_pairs(matching):
    x = {}
    for pair in matching.get_pairs():
        view_id_i = pair['id_view_i']
        view_id_j = pair['id_view_j']
        if view_id_i not in x:
            x[view_id_i] = []
        if view_id_j not in x:
            x[view_id_j] = []
        x[view_id_i].append(view_id_j)
        x[view_id_j].append(view_id_i)
    return x


def grouping(matching):
    ma = matching
    ma_data = ma.data
    for v in ma_data['views']:
        v['picked'] = [False for _ in range(len(v['keypoints']))]

    current_idx = 0
    groups = {current_idx: []}

    def f(view_idx, keypoint_idx):
        if ma_data['views'][view_idx]['picked'][keypoint_idx]:
            return
        else:
            ma_data['views'][view_idx]['picked'][keypoint_idx] = True
            groups[current_idx].append((view_idx, keypoint_idx))
            view_id = ma_data['views'][view_idx]['id_view']
            for p in ma_data['pairs']:
                if p['id_view_i'] == view_id:
                    for m in p['matches']:
                        if m[0] == keypoint_idx:
                            view_idx_next = ma.find_view_idx(p['id_view_j'])
                            keypoint_idx_next = m[1]
                            f(view_idx_next, keypoint_idx_next)
                elif p['id_view_j'] == view_id:
                    for m in p['matches']:
                        if m[1] == keypoint_idx:
                            view_idx_next = ma.find_view_idx(p['id_view_i'])
                            keypoint_idx_next = m[0]
                            f(view_idx_next, keypoint_idx_next)

    for view_idx_ in range(len(ma_data['views'])):
        for keypoint_idx_ in range(len(ma_data['views'][view_idx_]['keypoints'])):
            if 0 < len(groups[current_idx]):
                current_idx += 1
                groups[current_idx] = []
            f(view_idx_, keypoint_idx_)

    # check
    count_all_1 = count_all_keypoints(ma)
    count_all_2 = 0
    for x in groups:
        count_all_2 += len(groups[x])
    assert count_all_1 == count_all_2

    return groups


def sanity_check(matching):
    groups = grouping(matching)
    bad_keypoints = []
    for key in groups:
        view_indices = [x[0] for x in groups[key]]
        bad_view_indices = [item for item, count in collections.Counter(view_indices).items() if count > 1]
        if 0 < len(bad_view_indices):
            for x in groups[key]:
                if x[0] in bad_view_indices:
                    bad_keypoints.append(x)
    return bad_keypoints
