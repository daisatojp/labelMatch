import os
import os.path as osp
import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src', type=str)
    parser.add_argument('out_dir', type=str)
    args = parser.parse_args()

    views_dir = osp.join(args.out_dir, 'views')

    if not osp.exists(views_dir):
        os.makedirs(views_dir)

    with open(args.src, 'r') as f:
        x = json.load(f)

    for v in x['views']:
        view_path = osp.join(views_dir, 'view_{}.json'.format(v['id_view']))
        with open(view_path, 'w') as f:
            json.dump({
                'id': v['id_view'],
                'filename': v['filename'],
                'keypoints': [{
                    'id': i,
                    'pos': keypoint,
                    'group_id': None
                } for i, keypoint in enumerate(v['keypoints'])]}, f, indent=4)

    groups_path = osp.join(args.out_dir, 'groups.json')
    with open(groups_path, 'w') as f:
        json.dump({'groups': []}, f)


if __name__ == '__main__':
    main()
