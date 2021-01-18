import os
import os.path as osp
import argparse
import json
from PointMatcher.data.matching import Matching


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src')
    parser.add_argument('annot_dir')
    args = parser.parse_args()

    with open(args.src, 'r') as f:
        src_data = json.load(f)
    src_view_id_to_idx = {}
    for idx, view in enumerate(src_data['views']):
        src_view_id_to_idx[view['id_view']] = idx

    matching = Matching(args.annot_dir)

    for src_pair in src_data['pairs']:
        src_view_id_i = src_pair['id_view_i']
        src_view_id_j = src_pair['id_view_j']
        src_view_idx_i = src_view_id_to_idx[src_view_id_i]
        src_view_idx_j = src_view_id_to_idx[src_view_id_j]
        src_view_i = src_data['views'][src_view_idx_i]
        src_view_j = src_data['views'][src_view_idx_j]
        matching.set_view(src_view_id_i, src_view_id_j)
        assert osp.join(*src_view_i['filename']) == matching.get_filename(src_view_id_i)
        assert osp.join(*src_view_j['filename']) == matching.get_filename(src_view_id_j)
        for src_match in src_pair['matches']:
            keypoint_idx_i = src_match[0]
            keypoint_idx_j = src_match[1]
            keypoint_pos_i = src_view_i['keypoints'][keypoint_idx_i]
            keypoint_pos_j = src_view_j['keypoints'][keypoint_idx_j]
            ret_i = matching.min_distance_in_view_i(keypoint_pos_i[0], keypoint_pos_i[1])
            ret_j = matching.min_distance_in_view_j(keypoint_pos_j[0], keypoint_pos_j[1])
            if (ret_i is not None) and (ret_j is not None):
                if ret_i[0] < 3.0 and ret_j[0] < 3.0:
                    try:
                        matching.append_match(ret_i[1], ret_j[1])
                        print('vid_i={}, vid_j={}, kid_i={}, kid_j={}, ok'.format(
                            src_view_id_i, src_view_id_j, ret_i[1], ret_j[1]))
                    except RuntimeWarning as e:
                        print('vid_i={}, vid_j={}, kid_i={}, kid_j={}, what={}'.format(
                            src_view_id_i, src_view_id_j, ret_i[1], ret_j[1], e))

    matching.save()


if __name__ == '__main__':
    main()
