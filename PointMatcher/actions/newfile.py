import os
import os.path as osp
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PointMatcher.utils.filesystem import icon_path, scan_all_images


BB = QtWidgets.QDialogButtonBox


class NewFileDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(NewFileDialog, self).__init__(parent)

        labelOpenImageDir = QtWidgets.QLabel('Image Directory')
        self.editOpenImageDir = QtWidgets.QLineEdit()
        buttonOpenImageDir = QtWidgets.QPushButton(QtGui.QIcon(icon_path('open')), 'open', self)
        buttonOpenImageDir.clicked.connect(self.popOpenImageDir)

        labelSaveMatchingFile = QtWidgets.QLabel('Matching File')
        self.editSaveMatchingFile = QtWidgets.QLineEdit()
        buttonSaveMatchingFile = QtWidgets.QPushButton(QtGui.QIcon(icon_path('open')), 'open', self)
        buttonSaveMatchingFile.clicked.connect(self.popOpenSaveMatchingFile)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, QtCore.Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(QtGui.QIcon(osp.join('resources', 'icons', 'done.png')))
        bb.button(BB.Cancel).setIcon(QtGui.QIcon(osp.join('recources', 'icons', 'undo.png')))
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        layoutH1 = QtWidgets.QHBoxLayout()
        layoutH1.addWidget(labelOpenImageDir)
        layoutH1.addWidget(self.editOpenImageDir)
        layoutH1.addWidget(buttonOpenImageDir)
        layoutH2 = QtWidgets.QHBoxLayout()
        layoutH2.addWidget(labelSaveMatchingFile)
        layoutH2.addWidget(self.editSaveMatchingFile)
        layoutH2.addWidget(buttonSaveMatchingFile)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layoutH1)
        layout.addLayout(layoutH2)
        layout.addWidget(bb)

        self.setLayout(layout)

    def popOpenImageDir(self):
        defaultImageDir = '.'
        if osp.exists(self.editOpenImageDir.text()):
            defaultImageDir = self.editOpenImageDir.text()
        openImageDir = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Open Image Directory', defaultImageDir,
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
        self.editOpenImageDir.setText(openImageDir)

    def popOpenSaveMatchingFile(self):
        filters = 'matching file (*.json *.pkl)'
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self, 'matching file to be saved', '.', filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.editSaveMatchingFile.setText(filename)

    def popUp(self, openDir=''):
        self.editOpenImageDir.setText(openDir)
        if self.exec_():
            return self.editOpenImageDir.text(), self.editSaveMatchingFile.text()
        else:
            return None


class NewFileAction(QtWidgets.QAction):

    def __init__(self, parent):
        super(NewFileAction, self).__init__('New File', parent)

        self.parent = parent
        self.setIcon(QtGui.QIcon(icon_path('open')))
        self.setShortcut('Ctrl+N')
        self.triggered.connect(self.newFile)
        self.setEnabled(True)

        self.newFileDialog = NewFileDialog(self.parent)

    def newFile(self, _value=False):
        if not self.parent.mayContinue():
            return
        ret = self.newFileDialog.popUp()
        if ret is None:
            return
        self.parent.imageDir, self.parent.savePath = ret
        x = {'views': [], 'pairs': []}
        image_paths = scan_all_images(self.parent.imageDir)
        for i in range(len(image_paths)):
            for j in range(i + 1, len(image_paths)):
                x['pairs'].append({'id_view_i': i, 'id_view_j': j, 'matches': []})
        for i, image_path in enumerate(image_paths):
            x['views'].append({
                'id_view': i,
                'filename': image_path[len(self.parent.imageDir) + len(os.sep):].split(os.sep),
                'keypoints': [],
                'adjacencies': []})
        self.parent.loadMatching(x)
        self.parent.matching.save(self.parent.savePath)
