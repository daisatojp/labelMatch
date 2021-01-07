import os
import os.path as osp
import re
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


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


def newButton(text, icon=None, slot=None):
    b = QPushButton(text)
    if icon is not None:
        b.setIcon(QIcon(icon_path(icon)))
    if slot is not None:
        b.clicked.connect(slot)
    return b


def newAction(
        parent, text,
        slot=None, shortcut=None, icon=None,
        tip=None, checkable=False, enabled=True):
    """Create a new action and assign callbacks, shortcuts, etc."""
    a = QAction(text, parent)
    if icon is not None:
        a.setIcon(QIcon(icon_path(icon)))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    return a


def addActions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)


class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def fmtShortcut(text):
    mod, key = text.split('+', 1)
    return '<b>%s</b>+<b>%s</b>' % (mod, key)


def natural_sort(list, key=lambda s:s):
    """
    Sort the list into natural alphanumeric order.
    """
    def get_alphanum_key_func(key):
        convert = lambda text: int(text) if text.isdigit() else text
        return lambda s: [convert(c) for c in re.split('([0-9]+)', key(s))]
    sort_key = get_alphanum_key_func(key)
    list.sort(key=sort_key)
