#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import codecs
import distutils.spawn
import os
import os.path as osp
import json
import numpy as np
import cv2
from functools import partial
from collections import defaultdict
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
# from libs.resources import *
from libs.constants import *
from libs.utils import *
from libs.settings import Settings
from libs.matching import Matching
from libs.stringBundle import StringBundle
from libs.canvas import Canvas
from libs.zoomWidget import ZoomWidget
from libs.newFileDialog import NewFileDialog
from libs.toolBar import ToolBar
from libs.ustr import ustr
from libs.hashableQListWidgetItem import HashableQListWidgetItem

__appname__ = 'PointMatcher'


class WindowMixin(object):

    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        return toolbar


class MainWindow(QMainWindow, WindowMixin):
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = list(range(3))

    def __init__(self, defaultFilename=None, defaultPrefdefClassFile=None, defaultSaveDir=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle(__appname__)

        self.settings = Settings()
        self.settings.load()

        self.matching = None

        self.stringBundle = StringBundle.getBundle()
        getStr = lambda strId: self.stringBundle.getString(strId)

        self.imageDir = None
        self.savePath = None
        self.img_i_w, self.img_i_h = None, None
        self.img_j_w, self.img_j_h = None, None

        # Whether we need to save or not.
        self.dirty = False

        listLayout = QVBoxLayout()
        listLayout.setContentsMargins(0, 0, 0, 0)

        self.pairListWidget = QListWidget()
        self.pairListWidget.itemDoubleClicked.connect(self.pairitemDoubleClicked)
        pairlistLayout = QVBoxLayout()
        pairlistLayout.setContentsMargins(0, 0, 0, 0)
        pairlistLayout.addWidget(self.pairListWidget)
        pairListContainer = QWidget()
        pairListContainer.setLayout(pairlistLayout)
        self.pairdock = QDockWidget(getStr('pairList'), self)
        self.pairdock.setObjectName(getStr('pairs'))
        self.pairdock.setWidget(pairListContainer)

        self.fileListWidgetI = QListWidget()
        self.fileListWidgetI.itemDoubleClicked.connect(self.fileitemDoubleClickedI)
        filelistLayoutI = QVBoxLayout()
        filelistLayoutI.setContentsMargins(0, 0, 0, 0)
        filelistLayoutI.addWidget(self.fileListWidgetI)
        fileListContainerI = QWidget()
        fileListContainerI.setLayout(filelistLayoutI)
        self.filedockI = QDockWidget(getStr('fileListI'), self)
        self.filedockI.setObjectName(getStr('files'))
        self.filedockI.setWidget(fileListContainerI)

        self.fileListWidgetJ = QListWidget()
        self.fileListWidgetJ.itemDoubleClicked.connect(self.fileitemDoubleClickedJ)
        filelistLayoutJ = QVBoxLayout()
        filelistLayoutJ.setContentsMargins(0, 0, 0, 0)
        filelistLayoutJ.addWidget(self.fileListWidgetJ)
        fileListContainerJ = QWidget()
        fileListContainerJ.setLayout(filelistLayoutJ)
        self.filedockJ = QDockWidget(getStr('fileListJ'), self)
        self.filedockJ.setObjectName(getStr('files'))
        self.filedockJ.setWidget(fileListContainerJ)

        self.canvas = Canvas(parent=self)
        self.canvas.zoomRequest.connect(self.zoomRequest)
        self.canvas.setDrawingShapeToSquare(self.settings.get(SETTING_DRAW_SQUARE, False))

        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: scroll.verticalScrollBar(),
            Qt.Horizontal: scroll.horizontalScrollBar()
        }
        self.scrollArea = scroll
        self.canvas.scrollRequest.connect(self.scrollRequest)

        self.canvas.newShape.connect(self.newShape)
        self.canvas.shapeMoved.connect(self.setDirty)
        self.canvas.drawingPolygon.connect(self.toggleDrawingSensitive)

        self.setCentralWidget(scroll)
        self.addDockWidget(Qt.RightDockWidgetArea, self.pairdock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filedockI)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filedockJ)
        self.filedockI.setFeatures(QDockWidget.DockWidgetFloatable)
        self.filedockJ.setFeatures(QDockWidget.DockWidgetFloatable)

        # Actions
        action = partial(newAction, self)

        # File menu
        openDir = action(
            getStr('openDir'), self.openImageDir,
            'Ctrl+u', 'open', getStr('openDirDetail'))
        newFile = action(
            getStr('newFile'), self.newFile,
            'Ctrl+N', 'open', getStr('newFileDetail'))
        openFile = action(
            getStr('openFile'), self.openFile,
            'Ctrl+O', 'open', getStr('openFileDetail'))
        saveFile = action(
            getStr('saveFile'), self.saveFile,
            'Ctrl+S', 'save', getStr('saveFileDetail'), enabled=False)
        closeFile = action(
            getStr('closeFile'), self.closeFile,
            'Ctrl+W', 'close', getStr('closeFileDetail'))
        quitApp = action(
            getStr('quitApp'), self.close,
            'Ctrl+Q', 'quit', getStr('quitApp'))
        openNextPair = action(
            getStr('openNextPair'), self.openNextPair,
            'd', 'next', getStr('openNextPairDetail'))
        openPrevPair = action(
            getStr('openPrevPair'), self.openPrevPair,
            'a', 'prev', getStr('openPrevPairDetail'))

        # View menu
        self.autoSaving = QAction(getStr('autoSaveMode'), self)
        self.autoSaving.setCheckable(True)
        self.autoSaving.setChecked(self.settings.get(SETTING_AUTO_SAVE, False))
        zoomIn = action(
            getStr('zoomIn'), partial(self.addZoom, 10),
            'Ctrl++', 'zoom-in', getStr('zoomInDetail'), enabled=False)
        zoomOut = action(
            getStr('zoomOut'), partial(self.addZoom, -10),
            'Ctrl+-', 'zoom-out', getStr('zoomOutDetail'), enabled=False)
        zoomOrg = action(
            getStr('zoomOrgSize'), partial(self.setZoom, 100),
            'Ctrl+=', 'zoom', getStr('zoomOrgSizeDetail'), enabled=False)
        fitWindow = action(
            getStr('fitWindow'), self.setFitWindow,
            'Ctrl+F', 'fit-window', getStr('fitWindowDetail'),
            checkable=True, enabled=False)
        fitWidth = action(
            getStr('fitWidth'), self.setFitWidth,
            'Ctrl+Shift+F', 'fit-width', getStr('fitWidthDetail'),
            checkable=True, enabled=False)

        # Edit menu
        editKeypointMode = action(
            getStr('editKeypoint'), self.setEditKeypointMode,
            'v', 'new', getStr('editKeypointDetail'), enabled=True)
        editMatchMode = action(
            getStr('editMatch'), self.setEditMatchMode,
            'e', 'edit', u'Move and edit Boxs', enabled=False)

        # Help Menu
        showInfo = action(
            getStr('showInfo'), self.showInfoDialog,
            None, 'help', getStr('showInfoDetail'))

        self.zoomWidget = ZoomWidget()
        zoom = QWidgetAction(self)
        zoom.setDefaultWidget(self.zoomWidget)
        self.zoomWidget.setWhatsThis(
            'Zoom in or out of the image. Also accessible with {} and {} from the canvas.'.format(
                fmtShortcut('Ctrl+[-+]'), fmtShortcut('Ctrl+Wheel')))
        self.zoomWidget.setEnabled(False)
        self.zoomMode = self.MANUAL_ZOOM
        self.scalers = {
            self.FIT_WINDOW: self.scaleFitWindow,
            self.FIT_WIDTH: self.scaleFitWidth,
            # Set to one to scale to 100% when loading files.
            self.MANUAL_ZOOM: lambda: 1}

        self.newFileDialog = NewFileDialog(self)

        # Store actions for further handling.
        self.actions = struct(
            openDir=openDir,
            newFile=newFile,
            openFile=openFile,
            saveFile=saveFile,
            closeFile=closeFile,
            editKeypointMode=editKeypointMode,
            editMatchMode=editMatchMode,
            zoom=zoom,
            zoomIn=zoomIn,
            zoomOut=zoomOut,
            zoomOrg=zoomOrg,
            fitWindow=fitWindow,
            fitWidth=fitWidth,
            fileMenuActions=(openDir, newFile, openFile, saveFile, closeFile, quitApp),
            editMenu=tuple(),
            onLoadActive=tuple())

        self.menus = struct(
            file=self.menu('&File'),
            edit=self.menu('&Edit'),
            view=self.menu('&View'),
            help=self.menu('&Help'))

        # setup menus
        addActions(
            self.menus.file,
            (openDir, newFile, openFile, saveFile, closeFile, quitApp))
        addActions(
            self.menus.edit,
            (editKeypointMode, editMatchMode))
        addActions(
            self.menus.view,
            (self.autoSaving, None,
             zoomIn, zoomOut, zoomOrg, None,
             fitWindow, fitWidth))
        addActions(
            self.menus.help,
            (showInfo,))

        # setup tools
        self.tools = self.toolbar('Tools')
        addActions(
            self.tools,
            (openDir, openFile, openNextPair, openPrevPair,
             zoomIn, zoom, zoomOut, fitWindow, fitWidth))

        self.statusBar().showMessage('%s started.' % __appname__)
        self.statusBar().show()

        # Application state.
        self.image = QImage()
        self.recentFiles = []
        self.maxRecent = 7
        self.zoom_level = 100
        self.fit_window = False

        size = self.settings.get(SETTING_WIN_SIZE, QSize(600, 500))
        position = QPoint(0, 0)
        saved_position = self.settings.get(SETTING_WIN_POSE, position)
        # Fix the multiple monitors issue
        for i in range(QApplication.desktop().screenCount()):
            if QApplication.desktop().availableGeometry(i).contains(saved_position):
                position = saved_position
                break
        self.resize(size)
        self.move(position)
        saveDir = ustr(self.settings.get(SETTING_SAVE_DIR, None))
        self.lastOpenDir = ustr(self.settings.get(SETTING_LAST_OPEN_DIR, None))

        self.restoreState(self.settings.get(SETTING_WIN_STATE, QByteArray()))

        def xbool(x):
            if isinstance(x, QVariant):
                return x.toBool()
            return bool(x)

        if xbool(self.settings.get(SETTING_ADVANCE_MODE, False)):
            self.actions.advancedMode.setChecked(True)
            self.toggleAdvancedMode()

        # Callbacks:
        self.zoomWidget.valueChanged.connect(self.paintCanvas)

        # Display cursor coordinates at the right of status bar
        self.labelCoordinates = QLabel('')
        self.statusBar().addPermanentWidget(self.labelCoordinates)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.canvas.setDrawingShapeToSquare(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            # Draw rectangle if Ctrl is pressed
            self.canvas.setDrawingShapeToSquare(True)

    def setDirty(self):
        self.dirty = True

    def setClean(self):
        self.dirty = False

    def resetState(self):
        self.itemsToShapes.clear()
        self.shapesToItems.clear()
        self.labelList.clear()
        self.imageDir = None
        self.savePath = None
        self.canvas.resetState()
        self.labelCoordinates.clear()
        self.comboBox.cb.clear()

    def showInfoDialog(self):
        from libs.__init__ import __version__
        msg = u'Name:{0} \nApp Version:{1} \n{2} '.format(__appname__, __version__, sys.version_info)
        QMessageBox.information(self, u'Information', msg)

    def createShape(self):
        assert self.beginner()
        self.canvas.setEditing(False)
        self.actions.create.setEnabled(False)

    def toggleDrawingSensitive(self, drawing=True):
        """In the middle of drawing, toggling between modes should be disabled."""
        self.actions.editMode.setEnabled(not drawing)
        if not drawing and self.beginner():
            # Cancel creation.
            print('Cancel creation.')
            self.canvas.setEditing(True)
            self.canvas.restoreCursor()
            self.actions.create.setEnabled(True)

    def setEditKeypointMode(self):
        self.actions.editKeypointMode.setEnabled(False)
        self.actions.editMatchMode.setEnabled(True)
        self.canvas.setEditKeypointMode()

    def setEditMatchMode(self):
        self.actions.editKeypointMode.setEnabled(True)
        self.actions.editMatchMode.setEnabled(False)
        self.canvas.setEditMatchMode()

    def pairitemDoubleClicked(self, item=None):
        idx = self.pairListWidget.currentIndex().row()
        if idx < len(self.matching.get_matches()):
            id_view_i = self.matching.get_matches()[idx]['id_view_i']
            id_view_j = self.matching.get_matches()[idx]['id_view_j']
            self.changePair(id_view_i, id_view_j)

    def fileitemDoubleClickedI(self, item=None):
        id_view_i = self.matching.get_views()[self.fileListWidgetI.currentIndex().row()]['id_view']
        id_view_j = self.matching.get_views()[self.fileListWidgetJ.currentIndex().row()]['id_view']
        self.changePair(id_view_i, id_view_j)

    def fileitemDoubleClickedJ(self, item=None):
        id_view_i = self.matching.get_views()[self.fileListWidgetI.currentIndex().row()]['id_view']
        id_view_j = self.matching.get_views()[self.fileListWidgetJ.currentIndex().row()]['id_view']
        self.changePair(id_view_i, id_view_j)

    def changePair(self, id_view_i, id_view_j):
        if len(self.matching.get_matches()) < self.pairListWidget.count():
            self.pairListWidget.takeItem(self.pairListWidget.count()-1)
        m = [[x['id_view_i'], x['id_view_j']] == [id_view_i, id_view_j] for x in self.matching.get_matches()]
        if any(m):
            idx = m.index(True)
            self.pairListWidget.setCurrentRow(idx)
        else:
            self.pairListWidget.addItem('None ({}, {})'.format(id_view_i, id_view_j))
            self.pairListWidget.setCurrentRow(self.pairListWidget.count()-1)
        self.matching.set_view(id_view_i, id_view_j)
        self.fileListWidgetI.setCurrentRow(self.matching.get_view_idx_i())
        self.fileListWidgetJ.setCurrentRow(self.matching.get_view_idx_j())
        self.canvas.updatePixmap()
        self.canvas.repaint()

    # Callback functions:
    def newShape(self):
        """Pop-up and give focus to the label editor.

        position MUST be in global coordinates.
        """
        if not self.useDefaultLabelCheckbox.isChecked() or not self.defaultLabelTextLine.text():
            if len(self.labelHist) > 0:
                self.labelDialog = LabelDialog(
                    parent=self, listItem=self.labelHist)

            # Sync single class mode from PR#106
            if self.singleClassMode.isChecked() and self.lastLabel:
                text = self.lastLabel
            else:
                text = self.labelDialog.popUp(text=self.prevLabelText)
                self.lastLabel = text
        else:
            text = self.defaultLabelTextLine.text()

        # Add Chris
        self.diffcButton.setChecked(False)
        if text is not None:
            self.prevLabelText = text
            generate_color = generateColorByText(text)
            shape = self.canvas.setLastLabel(text, generate_color, generate_color)
            self.addLabel(shape)
            if self.beginner():  # Switch to edit mode.
                self.canvas.setEditing(True)
                self.actions.create.setEnabled(True)
            else:
                self.actions.editMode.setEnabled(True)
            self.setDirty()

            if text not in self.labelHist:
                self.labelHist.append(text)
        else:
            # self.canvas.undoLastLine()
            self.canvas.resetAllLines()

    def scrollRequest(self, delta, orientation):
        units = - delta / (8 * 15)
        bar = self.scrollBars[orientation]
        bar.setValue(bar.value() + bar.singleStep() * units)

    def setZoom(self, value):
        self.actions.fitWidth.setChecked(False)
        self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.MANUAL_ZOOM
        self.zoomWidget.setValue(value)

    def addZoom(self, increment=10):
        self.setZoom(self.zoomWidget.value() + increment)

    def zoomRequest(self, delta):
        # get the current scrollbar positions
        # calculate the percentages ~ coordinates
        h_bar = self.scrollBars[Qt.Horizontal]
        v_bar = self.scrollBars[Qt.Vertical]

        # get the current maximum, to know the difference after zooming
        h_bar_max = h_bar.maximum()
        v_bar_max = v_bar.maximum()

        # get the cursor position and canvas size
        # calculate the desired movement from 0 to 1
        # where 0 = move left
        #       1 = move right
        # up and down analogous
        cursor = QCursor()
        pos = cursor.pos()
        relative_pos = QWidget.mapFromGlobal(self, pos)

        cursor_x = relative_pos.x()
        cursor_y = relative_pos.y()

        w = self.scrollArea.width()
        h = self.scrollArea.height()

        # the scaling from 0 to 1 has some padding
        # you don't have to hit the very leftmost pixel for a maximum-left movement
        margin = 0.1
        move_x = (cursor_x - margin * w) / (w - 2 * margin * w)
        move_y = (cursor_y - margin * h) / (h - 2 * margin * h)

        # clamp the values from 0 to 1
        move_x = min(max(move_x, 0), 1)
        move_y = min(max(move_y, 0), 1)

        # zoom in
        units = delta / (8 * 15)
        scale = 10
        self.addZoom(scale * units)

        # get the difference in scrollbar values
        # this is how far we can move
        d_h_bar_max = h_bar.maximum() - h_bar_max
        d_v_bar_max = v_bar.maximum() - v_bar_max

        # get the new scrollbar values
        new_h_bar_value = h_bar.value() + move_x * d_h_bar_max
        new_v_bar_value = v_bar.value() + move_y * d_v_bar_max

        h_bar.setValue(new_h_bar_value)
        v_bar.setValue(new_v_bar_value)

    def setFitWindow(self, value=True):
        if value:
            self.actions.fitWidth.setChecked(False)
        self.zoomMode = self.FIT_WINDOW if value else self.MANUAL_ZOOM
        self.adjustScale()

    def setFitWidth(self, value=True):
        if value:
            self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.FIT_WIDTH if value else self.MANUAL_ZOOM
        self.adjustScale()

    def loadFile(self, filePath):
        self.matching = Matching(filePath, self.imageDir)
        self.canvas.setMatching(self.matching)
        self.pairListWidget.clear()
        self.fileListWidgetI.clear()
        self.fileListWidgetJ.clear()
        for match in self.matching.get_matches():
            self.pairListWidget.addItem('({}, {})'.format(match['id_view_i'], match['id_view_j']))
        for view in self.matching.get_views():
            self.fileListWidgetI.addItem('{} | {}'.format(view['id_view'], view['filename']))
            self.fileListWidgetJ.addItem('{} | {}'.format(view['id_view'], view['filename']))
        id_view_i = self.matching.get_matches()[0]['id_view_i']
        id_view_j = self.matching.get_matches()[0]['id_view_j']
        self.changePair(id_view_i, id_view_j)

    def resizeEvent(self, event):
        if self.canvas and not self.image.isNull()\
           and self.zoomMode != self.MANUAL_ZOOM:
            self.adjustScale()
        super(MainWindow, self).resizeEvent(event)

    def paintCanvas(self):
        # assert not self.image.isNull(), "cannot paint null image"
        self.canvas.scale = 0.01 * self.zoomWidget.value()
        self.canvas.adjustSize()
        self.canvas.update()

    def adjustScale(self, initial=False):
        value = self.scalers[self.FIT_WINDOW if initial else self.zoomMode]()
        self.zoomWidget.setValue(int(100 * value))

    def scaleFitWindow(self):
        """Figure out the size of the pixmap in order to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.centralWidget().width() - e
        h1 = self.centralWidget().height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def scaleFitWidth(self):
        # The epsilon does not seem to work too well here.
        w = self.centralWidget().width() - 2.0
        return w / self.canvas.pixmap.width()

    def closeEvent(self, event):
        if not self.mayContinue():
            event.ignore()
        self.settings[SETTING_WIN_SIZE] = self.size()
        self.settings[SETTING_WIN_POSE] = self.pos()
        self.settings[SETTING_WIN_STATE] = self.saveState()
        self.settings[SETTING_RECENT_FILES] = self.recentFiles
        if self.defaultSaveDir and os.path.exists(self.defaultSaveDir):
            self.settings[SETTING_SAVE_DIR] = ustr(self.defaultSaveDir)
        else:
            self.settings[SETTING_SAVE_DIR] = ''
        if self.lastOpenDir and os.path.exists(self.lastOpenDir):
            self.settings[SETTING_LAST_OPEN_DIR] = self.lastOpenDir
        else:
            self.settings[SETTING_LAST_OPEN_DIR] = ''
        self.settings[SETTING_AUTO_SAVE] = self.autoSaving.isChecked()
        self.settings[SETTING_SINGLE_CLASS] = self.singleClassMode.isChecked()
        self.settings[SETTING_PAINT_LABEL] = self.displayLabelOption.isChecked()
        self.settings[SETTING_DRAW_SQUARE] = self.drawSquaresOption.isChecked()
        self.settings[SETTING_LABEL_FILE_FORMAT] = self.labelFileFormat
        self.settings.save()

    def openImageDir(self, _value=False):
        if self.imageDir and os.path.exists(self.imageDir):
            defaultDir = self.imageDir
        else:
            defaultDir = '.'
        self.imageDir = ustr(
            QFileDialog.getExistingDirectory(
                self, '%s - Open Directory' % __appname__, defaultDir,
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

    def newFile(self, _value=False):
        if not self.imageDir:
            QMessageBox.warning(self, 'Attention', 'First of all, you need to select image directory', QMessageBox.Ok)
            return
        if not self.mayContinue():
            return
        filePath = self.newFileDialog.popUp()
        x = {'matches': [], 'views': []}
        image_paths = self._scan_all_images(self.imageDir)
        for i in range(len(image_paths)):
            for j in range(i + 1, len(image_paths)):
                x['matches'].append({'id_view_i': i, 'id_view_j': j, 'match': []})
        for i, image_path in enumerate(image_paths):
            x['views'].append({
                'id_view': i,
                'filename': image_path[len(self.imageDir) + len(os.sep):].split(os.sep),
                'keypoints': []})
        self._save_file(x, filePath)

    def openFile(self, _value=False):
        if not self.mayContinue():
            return
        path = osp.dirname(ustr(self.savePath)) if self.savePath else '.'
        filters = 'matching file (*.json)'
        filename = QFileDialog.getOpenFileName(
            self, 'choose matching file', path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            if osp.exists(filename):
                self.loadFile(filename)
            else:
                QMessageBox.warning(self, 'Attention', 'File Not Found', QMessageBox.Ok)
                return

    def saveFile(self, _value=False):
        if self.savePath:
            self._saveFile(self.savePath)

    def closeFile(self, _value=False):
        if not self.mayContinue():
            return

    def openNextPair(self, _value=False):
        if self.autoSaving.isChecked():
            if self.dirty is True:
                if self.savePath:
                    self._save_file(obj, self.savePath)
        if not self.mayContinue():
            return

    def openPrevPair(self, _value=False):
        if self.autoSaving.isChecked():
            if self.dirty is True:
                if self.savePath:
                    self._save_file(obj, self.savePath)
        if not self.mayContinue():
            return

    @staticmethod
    def _save_file(obj, path):
        with open(path, 'w') as f:
            json.dump(obj, f)

    @staticmethod
    def _scan_all_images(root_dir):
        extensions = ['.jpg', '.JPG']
        image_paths = []
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relativePath = os.path.join(root, file)
                    path = ustr(os.path.abspath(relativePath))
                    image_paths.append(path)
        natural_sort(image_paths, key=lambda x: x.lower())
        return image_paths

    def mayContinue(self):
        if not self.dirty:
            return True
        else:
            discardChanges = self.discardChangesDialog()
            if discardChanges == QMessageBox.No:
                return True
            elif discardChanges == QMessageBox.Yes:
                self.saveFile()
                return True
            else:
                return False

    def discardChangesDialog(self):
        yes, no, cancel = QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel
        msg = u'You have unsaved changes, would you like to save them and proceed?'
        return QMessageBox.warning(self, u'Attention', msg, yes | no | cancel)


def get_main_app(argv=[]):
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    app = QApplication(argv)
    app.setApplicationName(__appname__)
    app.setWindowIcon(newIcon("app"))
    # Tzutalin 201705+: Accept extra agruments to change predefined class file
    argparser = argparse.ArgumentParser()
    argparser.add_argument("image_dir", nargs="?")
    argparser.add_argument("predefined_classes_file",
                           default=os.path.join(os.path.dirname(__file__), "data", "predefined_classes.txt"),
                           nargs="?")
    argparser.add_argument("save_dir", nargs="?")
    args = argparser.parse_args(argv[1:])
    # Usage : labelImg.py image predefClassFile saveDir
    win = MainWindow(args.image_dir,
                     args.predefined_classes_file,
                     args.save_dir)
    win.show()
    return app, win


def main():
    '''construct main app and run it'''
    app, _win = get_main_app(sys.argv)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
