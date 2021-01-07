#!/usr/bin/env python

import sys
import argparse
import os
import os.path as osp
from functools import partial
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PointMatcher.__init__ import __appname__, __version__
from PointMatcher.mainwindow import MainWindow
from PointMatcher.libs.utils import icon_path


def main():
    argparser = argparse.ArgumentParser()
    args = argparser.parse_args()

    app = QApplication([])
    app.setApplicationName(__appname__)
    app.setWindowIcon(QIcon(icon_path('app.png')))
    win = MainWindow()
    win.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
