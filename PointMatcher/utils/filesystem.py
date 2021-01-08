import sys
import os
import os.path as osp


here = osp.dirname(osp.abspath(__file__))


def icon_path(icon):
    if hasattr(sys, '_MEIPASS'):
        return osp.join(sys._MEIPASS, 'PointMatcher', 'package_data', 'icons', '{}.png'.format(icon))
    icons_dir = osp.join(here, '..', 'package_data', 'icons')
    return osp.join(icons_dir, '{}.png'.format(icon))


def string_path(string):
    if hasattr(sys, '_MEIPASS'):
        return osp.join(sys._MEIPASS, 'PointMatcher', 'package_data', 'strings', '{}.properties'.format(string))
    strings_dir = osp.join(here, '..', 'package_data', 'strings')
    return osp.join(strings_dir, '{}.properties'.format(string))


def scan_all_images(root_dir):
    extensions = ['.jpg', '.JPG']
    image_paths = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(tuple(extensions)):
                relativePath = osp.join(root, file)
                path = osp.abspath(relativePath)
                image_paths.append(path)
    natural_sort(image_paths, key=lambda x: x.lower())
    return image_paths
