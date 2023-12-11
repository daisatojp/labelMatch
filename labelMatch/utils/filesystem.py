import sys
import os
import os.path as osp
from labelMatch.utils.sort import natural_sort


here = osp.dirname(osp.abspath(__file__))


def icon_path(icon):
    if hasattr(sys, '_MEIPASS'):
        return osp.join(sys._MEIPASS,
                        'PointMatcher',
                        'package_data',
                        'icons',
                        '{}.png'.format(icon))
    icons_dir = osp.join(here, '..', 'package_data', 'icons')
    return osp.join(icons_dir, '{}.png'.format(icon))


def scan_all_images(root_dir):
    extensions = ['.bmp', '.dib',
                  '.jpeg', '.jpg', '.jpe',
                  '.jp2',
                  '.png',
                  '.webp',
                  '.avif',
                  '.pbm', '.pgm', '.ppm', '.pxm', '.pnm',
                  '.pfm',
                  '.sr', '.ras',
                  '.tiff', '.tif',
                  '.exr',
                  '.hdr', '.pic']
    image_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(tuple(extensions)):
                relativePath = osp.join(root, file)
                path = osp.abspath(relativePath)
                image_files.append(path)
    natural_sort(image_files, key=lambda x: x.lower())
    return image_files
