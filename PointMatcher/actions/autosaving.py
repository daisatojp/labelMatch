import os.path as osp
import time
import threading
from PyQt5.QtWidgets import QAction
from PointMatcher.utils.filesystem import icon_path


class AutoSavingAction(QAction):

    def __init__(self, parent):
        super(AutoSavingAction, self).__init__('Auto Save Mode', parent)

        self.p = parent
        self.triggered.connect(self.clicked)
        self.setCheckable(True)
        self.setChecked(False)
        self.setEnabled(True)
        self.thread_executing_flag = True
        self.thread = threading.Thread(target=self.autoSavingThread)
        self.thread.start()

    def clicked(self, _value=False):
        if self.isChecked():
            self.p.actions.saveFile.setEnabled(False)

    def autoSavingThread(self):
        while self.thread_executing_flag:
            if (self.p.matching is not None) and self.isChecked():
                if self.p.matching.dirty():
                    self.p.matching.save(self.p.savePath)
            time.sleep(0.1)

    def terminate_thread(self):
        self.thread_executing_flag = False
        if self.thread:
            self.thread.join(1.0)
