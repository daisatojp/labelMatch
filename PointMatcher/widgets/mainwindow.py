import os
import os.path as osp
from functools import partial
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PointMatcher.__init__ import __appname__, __version__
from PointMatcher.data.matching import Matching
from PointMatcher.actions import OpenDirAction
from PointMatcher.widgets.viewwidget import ViewWidget
from PointMatcher.widgets.pairwidget import PairWidget
from PointMatcher.widgets.settings import Settings
from PointMatcher.widgets.stringbundle import StringBundle
from PointMatcher.widgets.canvas import Canvas
from PointMatcher.widgets.zoomwidget import ZoomWidget
from PointMatcher.widgets.scrollwidget import ScrollWidget
from PointMatcher.widgets.newfiledialog import NewFileDialog
from PointMatcher.widgets.toolbar import ToolBar
from PointMatcher.utils.filesystem import icon_path, string_path, scan_all_images
from PointMatcher.utils.struct import struct
from PointMatcher.utils.qt import newAction, addActions


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

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(__appname__)

        self.settings = Settings()
        self.settings.load()

        self.matching = None

        self.stringBundle = StringBundle.getBundle()
        getStr = self.stringBundle.getString

        self.imageDir = None
        self.savePath = None

        self.viewIWidget = ViewWidget(parent=self, title=getStr('viewIList'))
        self.viewIWidget.itemClicked_connect(self.viewIitemClicked)
        self.viewJWidget = ViewWidget(parent=self, title=getStr('viewJList'))
        self.viewJWidget.itemClicked_connect(self.viewJitemClicked)
        self.pairWidget = PairWidget(parent=self, title=getStr('pairList'))
        self.pairWidget.itemClicked_connect(self.pairitemClicked)

        self.canvas = Canvas(parent=self)
        self.zoomWidget = ZoomWidget(self)
        self.scrollWidget = ScrollWidget(self)
        self.canvas.zoomRequest.connect(self.zoomWidget.zoomRequest)
        self.canvas.scrollRequest.connect(self.scrollWidget.scrollRequest)

        self.setCentralWidget(self.scrollWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.pairWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.viewIWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.viewJWidget)

        # File menu
        openDir = OpenDirAction(self)
        newFile = newAction(
            self, getStr('newFile'), self.newFile,
            'Ctrl+N', 'open', getStr('newFileDetail'))
        openFile = newAction(
            self, getStr('openFile'), self.openFile,
            'Ctrl+O', 'open', getStr('openFileDetail'))
        saveFile = newAction(
            self, getStr('saveFile'), self.saveFile,
            'Ctrl+S', 'save', getStr('saveFileDetail'), enabled=False)
        saveFileAs = newAction(
            self, getStr('saveFileAs'), self.saveFileAs,
            'Ctrl+Alt+S', 'save', getStr('saveFileAsDetail'), enabled=False)
        closeFile = newAction(
            self, getStr('closeFile'), self.closeFile,
            'Ctrl+W', 'close', getStr('closeFileDetail'))
        quitApp = newAction(
            self, getStr('quitApp'), self.close,
            'Ctrl+Q', 'quit', getStr('quitApp'))
        openNextPair = newAction(
            self, getStr('openNextPair'), self.openNextPair,
            'd', 'next', getStr('openNextPairDetail'), enabled=False)
        openPrevPair = newAction(
            self, getStr('openPrevPair'), self.openPrevPair,
            'a', 'prev', getStr('openPrevPairDetail'), enabled=False)

        # View menu
        autoSaving = QAction(getStr('autoSaveMode'), self)
        autoSaving.setCheckable(True)
        autoSaving.setChecked(False)

        # Edit menu
        addPair = newAction(
            self, getStr('addPair'), self.addPair,
            'Ctrl+X', 'save', getStr('addPairDetail'), enabled=False)
        removePair = newAction(
            self, getStr('removePair'), self.removePair,
            'Ctrl+C', 'delete', getStr('removePairDetail'), enabled=False)
        editKeypointMode = QAction(getStr('editKeypoint'), self)
        editKeypointMode.triggered.connect(self.editKeypointMode)
        editKeypointMode.setEnabled(True)
        editKeypointMode.setCheckable(True)
        editKeypointMode.setChecked(True)
        editKeypointMode.setShortcut('v')
        editMatchMode = QAction(getStr('editMatch'), self)
        editMatchMode.triggered.connect(self.editMatchMode)
        editMatchMode.setEnabled(True)
        editMatchMode.setCheckable(True)
        editMatchMode.setChecked(False)
        editMatchMode.setShortcut('e')
        sanityCheck = newAction(
            self, getStr('sanityCheck'), self.sanityCheck,
            None, None, getStr('sanityCheckDetail'))
        complementMatch = newAction(
            self, getStr('complementMatch'), self.complementMatch,
            None, None, getStr('complementMatchDetail'))

        # Help Menu
        showInfo = newAction(
            self, getStr('showInfo'), self.showInfoDialog,
            None, 'help', getStr('showInfoDetail'))

        self.newFileDialog = NewFileDialog(self)

        self.actions = struct(
            openDir=openDir,
            newFile=newFile,
            openFile=openFile,
            saveFile=saveFile,
            saveFileAs=saveFileAs,
            closeFile=closeFile,
            openNextPair=openNextPair,
            openPrevPair=openPrevPair,
            addPair=addPair,
            removePair=removePair,
            editKeypointMode=editKeypointMode,
            editMatchMode=editMatchMode,
            sanityCheck=sanityCheck,
            complementMatch=complementMatch,
            autoSaving=autoSaving)

        self.menus = struct(
            file=self.menu('&File'),
            edit=self.menu('&Edit'),
            view=self.menu('&View'),
            help=self.menu('&Help'))

        # setup menus
        za = self.zoomWidget.actions
        addActions(
            self.menus.file,
            (openDir, newFile, openFile, saveFile, saveFileAs, closeFile, quitApp))
        addActions(
            self.menus.edit,
            (addPair, removePair,
             None, editKeypointMode, editMatchMode,
             None, sanityCheck, complementMatch))
        addActions(
            self.menus.view,
            (autoSaving,
             None, za.zoomIn, za.zoomOut, za.zoomOrg, za.zoomFitWindow, za.zoomFitWidth))
        addActions(
            self.menus.help,
            (showInfo,))

        # setup tools
        self.tools = self.toolbar('Tools')
        addActions(
            self.tools,
            (openDir, openFile, saveFile, saveFileAs,
             None, addPair, removePair, openNextPair, openPrevPair,
             None, za.zoomIn, za.zoom, za.zoomOut, za.zoomFitWindow, za.zoomFitWidth))

        self.statusBar().showMessage('{} started.'.format(__appname__))
        self.statusBar().show()

        size = QSize(600, 500)
        position = QPoint(0, 0)
        saved_position = QPoint(0, 0)
        # Fix the multiple monitors issue
        for i in range(QApplication.desktop().screenCount()):
            if QApplication.desktop().availableGeometry(i).contains(saved_position):
                position = saved_position
                break
        self.resize(size)
        self.move(position)

        # Callbacks:
        self.zoomWidget.spinbox.valueChanged.connect(self.paintCanvas)

        # Display cursor coordinates at the right of status bar
        self.labelCoordinates = QLabel('')
        self.statusBar().addPermanentWidget(self.labelCoordinates)

    def loadMatching(self, data):
        self.matching = Matching(data, self.imageDir)
        self.matching.set_update_callback(self.getMatchingUpdateEvent)
        self.matching.set_dirty_callback(self.getMatchingDirtyEvent)
        self.canvas.setMatching(self.matching)
        self.viewIWidget.initialize_item(self.matching)
        self.viewJWidget.initialize_item(self.matching)
        self.pairWidget.initialize_item(self.matching)
        if 0 < len(self.matching.get_pairs()):
            view_id_i = self.matching.get_pairs()[0]['id_view_i']
            view_id_j = self.matching.get_pairs()[0]['id_view_j']
        else:
            view_id_i = self.matching.get_views()[0]['id_view']
            view_id_j = self.matching.get_views()[1]['id_view']
        self.changePair(view_id_i, view_id_j)
        self.actions.saveFileAs.setEnabled(True)

    def viewIitemClicked(self, item=None):
        view_id_i = self.matching.get_view_id_by_view_idx(self.viewIWidget.get_current_idx())
        view_id_j = self.matching.get_view_id_by_view_idx(self.viewJWidget.get_current_idx())
        self.changePair(view_id_i, view_id_j)

    def viewJitemClicked(self, item=None):
        id_view_i = self.matching.get_view_id_by_view_idx(self.viewIWidget.get_current_idx())
        id_view_j = self.matching.get_view_id_by_view_idx(self.viewJWidget.get_current_idx())
        self.changePair(id_view_i, id_view_j)

    def pairitemClicked(self, item=None):
        idx = self.pairWidget.get_current_idx()
        if idx < len(self.matching.get_pairs()):
            view_id_i = self.matching.get_pairs()[idx]['id_view_i']
            view_id_j = self.matching.get_pairs()[idx]['id_view_j']
            self.changePair(view_id_i, view_id_j)

    def changePair(self, view_id_i, view_id_j):
        if len(self.matching.get_pairs()) < self.pairWidget.count():
            self.pairWidget.remove_last_item()
        pair_idx = self.matching.find_pair_idx(view_id_i, view_id_j)
        if pair_idx is not None:
            self.pairWidget.set_current_idx(pair_idx)
            self.actions.addPair.setEnabled(False)
            self.actions.removePair.setEnabled(True)
            self.actions.openNextPair.setEnabled(True)
            self.actions.openPrevPair.setEnabled(True)
        else:
            self.pairWidget.add_item('None ({}, {})'.format(view_id_i, view_id_j))
            self.pairWidget.set_current_idx(self.pairWidget.count()-1)
            self.actions.addPair.setEnabled(True)
            self.actions.removePair.setEnabled(False)
            self.actions.openNextPair.setEnabled(False)
            self.actions.openPrevPair.setEnabled(False)
        self.matching.set_view(view_id_i, view_id_j)
        self.viewIWidget.set_current_idx(self.matching.get_view_idx_i())
        self.viewJWidget.set_current_idx(self.matching.get_view_idx_j())
        self.canvas.updatePixmap()
        self.canvas.repaint()

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)

    def paintCanvas(self):
        self.canvas.scale = 0.01 * self.zoomWidget.spinbox.value()
        self.canvas.adjustSize()
        self.canvas.update()

    def closeEvent(self, event):
        # if not self.mayContinue():
        #     event.ignore()
        self.settings.save()

    def newFile(self, _value=False):
        if not self.mayContinue():
            return
        ret = self.newFileDialog.popUp()
        if ret is None:
            return
        self.imageDir, self.savePath = ret
        x = {'views': [], 'pairs': []}
        image_paths = scan_all_images(self.imageDir)
        for i in range(len(image_paths)):
            for j in range(i + 1, len(image_paths)):
                x['pairs'].append({'id_view_i': i, 'id_view_j': j, 'matches': []})
        for i, image_path in enumerate(image_paths):
            x['views'].append({
                'id_view': i,
                'filename': image_path[len(self.imageDir) + len(os.sep):].split(os.sep),
                'keypoints': []})
        self.loadMatching(x)
        self.matching.save(self.savePath)

    def openFile(self, _value=False):
        if not self.mayContinue():
            return
        if (self.savePath is not None) and osp.exists(osp.dirname(self.savePath)):
            path = osp.dirname(self.savePath)
        elif (self.imageDir is not None) and osp.exists(self.imageDir):
            path = self.imageDir
        else:
            path = '.'
        filters = 'matching file (*.json *.pkl)'
        filename = QFileDialog.getOpenFileName(
            self, 'choose matching file', path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            if osp.exists(filename):
                self.savePath = filename
                self.loadMatching(filename)
            else:
                QMessageBox.warning(self, 'Attention', 'File Not Found', QMessageBox.Ok)
                return

    def saveFile(self, _value=False):
        if self.savePath:
            self.matching.save(self.savePath)
            self.actions.saveFile.setEnabled(False)

    def saveFileAs(self, _value=False):
        if (self.savePath is not None) and osp.exists(osp.dirname(self.savePath)):
            path = osp.dirname(self.savePath)
        elif (self.imageDir is not None) and osp.exists(self.imageDir):
            path = self.imageDir
        else:
            path = '.'
        filters = 'matching file (*.json *.pkl)'
        filename = QFileDialog.getSaveFileName(
            self, 'choose file name to be saved', path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.savePath = filename
            self.matching.save(self.savePath)

    def closeFile(self, _value=False):
        if not self.mayContinue():
            return

    def openNextPair(self, _value=False):
        if self.actions.autoSaving.isChecked():
            self.matching.save(self.savePath)
        view_id_i, view_id_j = self.matching.get_next_view_pair()
        self.changePair(view_id_i, view_id_j)

    def openPrevPair(self, _value=False):
        if self.actions.autoSaving.isChecked():
            self.matching.save(self.savePath)
        view_id_i, view_id_j = self.matching.get_prev_view_pair()
        self.changePair(view_id_i, view_id_j)

    def addPair(self):
        view_id_i = self.matching.get_view_id_by_view_idx(self.viewIWidget.get_current_idx())
        view_id_j = self.matching.get_view_id_by_view_idx(self.viewJWidget.get_current_idx())
        self.matching.append_pair(view_id_i, view_id_j, update=False)
        self.pairWidget.remove_last_item()
        self.pairWidget.add_item(self.matching.get_pairs()[-1])
        self.changePair(view_id_i, view_id_j)

    def removePair(self):
        view_id_i = self.matching.get_view_id_i()
        view_id_j = self.matching.get_view_id_j()
        trans_view_id_i, trans_view_id_j = self.matching.get_prev_view_pair()
        if (trans_view_id_i, trans_view_id_j) == (view_id_i, view_id_j):
            trans_view_id_i, trans_view_id_j = self.matching.get_next_view_pair()
        if (trans_view_id_i, trans_view_id_j) == (view_id_i, view_id_j):
            trans_view_id_i = self.matching.get_views()[0]['id_view']
            trans_view_id_j = self.matching.get_views()[1]['id_view']
        self.pairWidget.remove_item_by_idx(self.matching.get_pair_idx())
        self.changePair(trans_view_id_i, trans_view_id_j)
        self.matching.remove_pair(view_id_i, view_id_j)

    def editKeypointMode(self):
        self.actions.editKeypointMode.setChecked(True)
        self.actions.editMatchMode.setChecked(False)
        self.canvas.setEditKeypointMode()

    def editMatchMode(self):
        self.actions.editKeypointMode.setChecked(False)
        self.actions.editMatchMode.setChecked(True)
        self.canvas.setEditMatchMode()

    def sanityCheck(self):
        pass

    def complementMatch(self):
        pass

    def showInfoDialog(self):
        msg = '{0}\nversion : {1}'.format(__appname__, __version__)
        QMessageBox.information(self, 'Information', msg)

    def getMatchingUpdateEvent(self):
        view_id_i = self.matching.get_view_id_i()
        view_id_j = self.matching.get_view_id_j()
        view_idx_i = self.matching.get_view_idx_i()
        view_idx_j = self.matching.get_view_idx_j()
        self.viewIWidget.update_item_by_idx(self.matching, [view_idx_i, view_idx_j])
        self.viewJWidget.update_item_by_idx(self.matching, [view_idx_i, view_idx_j])
        pair_idx = self.matching.find_pair_idx(view_id_i, view_id_j)
        if pair_idx is not None:
            self.pairListWidget.item(pair_idx).setText(self.getPairItemText(view_id_i, view_id_j))

    def getMatchingDirtyEvent(self):
        self.actions.saveFile.setEnabled(True)

    def mayContinue(self):
        if self.matching is not None:
            if self.matching.dirty():
                saveChanges = self.saveChangesDialog()
                if saveChanges == QMessageBox.Yes:
                    self.matching.save(self.savePath)
                    return True
                elif saveChanges == QMessageBox.No:
                    return True
                else:
                    return False
        return True

    def saveChangesDialog(self):
        yes, no, cancel = QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel
        msg = u'You have unsaved changes, would you like to save them and proceed?'
        return QMessageBox.warning(self, u'Attention', msg, yes | no | cancel)
