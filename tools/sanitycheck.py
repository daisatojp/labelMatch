import os
import os.path as osp
import argparse
import json
from glob import glob
from collections import Counter
from PointMatcher.matching import Matching


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('annot_dir')
    args = parser.parse_args()

    matching = Matching(args.annot_dir)

    with open(osp.join(args.annot_dir, 'groups.json'), 'r') as f:
        groups = json.load(f)

    num_1 = 0
    keys_1 = []
    for group in groups['groups']:
        num_1 += len(group['keypoints'])
        keys_1 += group['keypoints']

    num_2 = 0
    keys_2 = []
    key_num_total = 0
    view_paths = glob(osp.join(args.annot_dir, 'views', '*.json'))
    for view_path in view_paths:
        with open(view_path, 'r') as f:
            view = json.load(f)
        key_num_total += len(view['keypoints'])
        for keypoint in view['keypoints']:
            if keypoint['group_id'] is not None:
                num_2 += 1
                keys_2 += [[view['id'], keypoint['id']]]

    print('key_num_total', key_num_total)
    print('num_1', num_1)
    print('num_2', num_2)
    print('len(keys_1)', len(keys_1))
    print('len(keys_2)', len(keys_2))
    print('keys_1 duplicates', [item for item, count in Counter(map(tuple, keys_1)).items() if count > 1])
    print('keys_2 duplicates', [item for item, count in Counter(map(tuple, keys_2)).items() if count > 1])

    for group in groups['groups']:
        gid = group['id']
        for gk in group['keypoints']:
            keypoint = matching.get_keypoint(gk[0], gk[1])
            if keypoint['group_id'] != gid:
                print('wrong vid={}, kid={}, gid={}'.format(gk[0], gk[1], gid))

    for group in groups['groups']:
        if 0 < len([item for item, count in Counter(map(tuple, group['keypoints'])).items() if count > 1]):
            print('wrong gid={}'.format(group['id']))

    print('sanity check finish.')


if __name__ == '__main__':
    main()
