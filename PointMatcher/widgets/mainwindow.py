import os
import os.path as osp
from functools import partial
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PointMatcher.__init__ import __appname__, __version__
from PointMatcher.data.matching import Matching
from PointMatcher.widgets.viewwidget import ViewWidget
from PointMatcher.widgets.settings import Settings
from PointMatcher.widgets.stringbundle import StringBundle
from PointMatcher.widgets.canvas import Canvas
from PointMatcher.widgets.zoomwidget import ZoomWidget
from PointMatcher.widgets.newfiledialog import NewFileDialog
from PointMatcher.widgets.toolbar import ToolBar
from PointMatcher.widgets.utils import newAction, addActions, fmtShortcut, struct, icon_path, string_path


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

        self.viewIWidget = ViewWidget()
        self.viewIWidget.itemClicked_connect(self.viewIitemClicked)
        self.viewIdock = QDockWidget(getStr('viewIList'), self)
        self.viewIdock.setObjectName(getStr('views'))
        self.viewIdock.setWidget(self.viewIWidget)

        self.viewJWidget = ViewWidget()
        self.viewJWidget.itemClicked_connect(self.viewJitemClicked)
        self.viewJdock = QDockWidget(getStr('viewJList'), self)
        self.viewJdock.setObjectName(getStr('views'))
        self.viewJdock.setWidget(self.viewJWidget)

        self.pairListWidget = QListWidget()
        self.pairListWidget.itemClicked.connect(self.pairitemClicked)
        pairlistLayout = QVBoxLayout()
        pairlistLayout.setContentsMargins(0, 0, 0, 0)
        pairlistLayout.addWidget(self.pairListWidget)
        pairListContainer = QWidget()
        pairListContainer.setLayout(pairlistLayout)
        self.pairdock = QDockWidget(getStr('pairList'), self)
        self.pairdock.setObjectName(getStr('pairs'))
        self.pairdock.setWidget(pairListContainer)

        self.zoomWidget = ZoomWidget(self, self.stringBundle)
        za = self.zoomWidget.actions
        zoom = QWidgetAction(self)
        zoom.setDefaultWidget(self.zoomWidget.spinbox)

        self.canvas = Canvas(parent=self)
        self.canvas.zoomRequest.connect(self.zoomWidget.zoomRequest)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.canvas)
        self.scrollArea.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: self.scrollArea.verticalScrollBar(),
            Qt.Horizontal: self.scrollArea.horizontalScrollBar()}
        self.canvas.scrollRequest.connect(self.scrollRequest)

        self.setCentralWidget(self.scrollArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.pairdock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.viewIdock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.viewJdock)
        self.viewIdock.setFeatures(QDockWidget.DockWidgetFloatable)
        self.viewJdock.setFeatures(QDockWidget.DockWidgetFloatable)

        # File menu
        openDir = newAction(
            self, getStr('openDir'), self.openDir,
            'Ctrl+u', 'open', getStr('openDirDetail'))
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
             None, za.zoomIn, zoom, za.zoomOut, za.zoomFitWindow, za.zoomFitWidth))

        self.statusBar().showMessage('{} started.'.format(__appname__))
        self.statusBar().show()

        self.zoom_level = 100
        self.fit_window = False

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

    def keyReleaseEvent(self, ev):
        pass

    def keyPressEvent(self, ev):
        pass

    def viewIitemClicked(self, item=None):
        view_id_i = self.matching.get_view_id_by_idx(self.viewIWidget.get_current_idx())
        view_id_j = self.matching.get_view_id_by_idx(self.viewJWidget.get_current_idx())
        self.changePair(view_id_i, view_id_j)

    def viewJitemClicked(self, item=None):
        id_view_i = self.matching.get_view_id_by_idx(self.viewIWidget.get_current_idx())
        id_view_j = self.matching.get_view_id_by_idx(self.viewJWidget.get_current_idx())
        self.changePair(id_view_i, id_view_j)

    def pairitemClicked(self, item=None):
        idx = self.pairListWidget.currentIndex().row()
        if idx < len(self.matching.get_pairs()):
            view_id_i = self.matching.get_pairs()[idx]['id_view_i']
            view_id_j = self.matching.get_pairs()[idx]['id_view_j']
            self.changePair(view_id_i, view_id_j)

    def changePair(self, view_id_i, view_id_j):
        if len(self.matching.get_pairs()) < self.pairListWidget.count():
            self.pairListWidget.takeItem(self.pairListWidget.count()-1)
        pair_idx = self.matching.find_pair_idx(view_id_i, view_id_j)
        if pair_idx is not None:
            self.pairListWidget.setCurrentRow(pair_idx)
            self.actions.addPair.setEnabled(False)
            self.actions.removePair.setEnabled(True)
            self.actions.openNextPair.setEnabled(True)
            self.actions.openPrevPair.setEnabled(True)
        else:
            self.pairListWidget.addItem('None ({}, {})'.format(view_id_i, view_id_j))
            self.pairListWidget.setCurrentRow(self.pairListWidget.count()-1)
            self.actions.addPair.setEnabled(True)
            self.actions.removePair.setEnabled(False)
            self.actions.openNextPair.setEnabled(False)
            self.actions.openPrevPair.setEnabled(False)
        self.matching.set_view(view_id_i, view_id_j)
        self.viewIWidget.set_current_idx(self.matching.get_view_idx_i())
        self.viewJWidget.set_current_idx(self.matching.get_view_idx_j())
        self.canvas.updatePixmap()
        self.canvas.repaint()

    def scrollRequest(self, delta, orientation):
        units = - delta / (8 * 15)
        bar = self.scrollBars[orientation]
        bar.setValue(bar.value() + bar.singleStep() * units)

    def loadMatching(self, data):
        self.matching = Matching(data, self.imageDir)
        self.matching.set_update_callback(self.getMatchingUpdateEvent)
        self.matching.set_dirty_callback(self.getMatchingDirtyEvent)
        self.canvas.setMatching(self.matching)
        self.viewIWidget.initialize_item(self.matching)
        self.viewJWidget.initialize_item(self.matching)
        self.pairListWidget.clear()
        for pair in self.matching.get_pairs():
            self.pairListWidget.addItem(self.getPairItemText(
                pair['id_view_i'], pair['id_view_j']))
        if 0 < len(self.matching.get_pairs()):
            view_id_i = self.matching.get_pairs()[0]['id_view_i']
            view_id_j = self.matching.get_pairs()[0]['id_view_j']
        else:
            view_id_i = self.matching.get_views()[0]['id_view']
            view_id_j = self.matching.get_views()[1]['id_view']
        self.changePair(view_id_i, view_id_j)
        self.actions.saveFileAs.setEnabled(True)

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

    def openDir(self, _value=False):
        if self.imageDir and os.path.exists(self.imageDir):
            defaultDir = self.imageDir
        else:
            defaultDir = '.'
        self.imageDir = QFileDialog.getExistingDirectory(
            self, '{} - Open Directory'.format(__appname__), defaultDir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

    def newFile(self, _value=False):
        if not self.mayContinue():
            return
        ret = self.newFileDialog.popUp()
        if ret is None:
            return
        self.imageDir, self.savePath = ret
        x = {'views': [], 'pairs': []}
        image_paths = self._scan_all_images(self.imageDir)
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
        view_id_i = self.matching.get_views()[self.viewListWidgetI.currentIndex().row()]['id_view']
        view_id_j = self.matching.get_views()[self.viewListWidgetJ.currentIndex().row()]['id_view']
        self.matching.append_pair(view_id_i, view_id_j, update=False)
        self.pairListWidget.item(self.pairListWidget.count() - 1).setText(
            self.getPairItemText(view_id_i, view_id_j))
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
        self.pairListWidget.takeItem(self.matching.get_pair_idx())
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

    def getPairItemText(self, view_id_i, view_id_j):
        idx = self.matching.find_pair_idx(view_id_i, view_id_j)
        if idx is not None:
            p = self.matching.get_pairs()[idx]
            return '({}, {}) [matches={}]'.format(
                view_id_i, view_id_j, len(p['matches']))
        raise RuntimeError('invalid view_id_i and view_id_j')

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

    @staticmethod
    def _scan_all_images(root_dir):
        extensions = ['.jpg', '.JPG']
        image_paths = []
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relativePath = os.path.join(root, file)
                    path = os.path.abspath(relativePath)
                    image_paths.append(path)
        natural_sort(image_paths, key=lambda x: x.lower())
        return image_paths
