#!/usr/bin/env python

import sys
import argparse
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from labelMatch.__init__ import __appname__
from labelMatch.mainwindow import MainWindow
from labelMatch.utils.filesystem import icon_path


def main():
    argparser = argparse.ArgumentParser()
    args = argparser.parse_args()

    app = QApplication([])
    app.setApplicationName(__appname__)
    app.setWindowIcon(QIcon(icon_path('app')))
    win = MainWindow()
    win.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
