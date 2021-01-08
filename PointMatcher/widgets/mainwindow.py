import os
import os.path as osp
from functools import partial
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PointMatcher.__init__ import __appname__, __version__
from PointMatcher.data.matching import Matching
from PointMatcher.actions import *
from PointMatcher.widgets.viewwidget import ViewWidget
from PointMatcher.widgets.pairwidget import PairWidget
from PointMatcher.widgets.settings import Settings
from PointMatcher.widgets.canvas import Canvas
from PointMatcher.widgets.zoomwidget import ZoomWidget
from PointMatcher.widgets.scrollwidget import ScrollWidget
from PointMatcher.widgets.toolbar import ToolBar
from PointMatcher.utils.filesystem import icon_path, string_path
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

        self.matching = None
        self.imageDir = None
        self.savePath = None

        self.settings = Settings()
        self.settings.load()

        self.viewIWidget = ViewWidget(parent=self, title='View List (First)')
        self.viewIWidget.itemClicked_connect(self.viewIitemClicked)
        self.viewJWidget = ViewWidget(parent=self, title='View List (Second)')
        self.viewJWidget.itemClicked_connect(self.viewJitemClicked)
        self.pairWidget = PairWidget(parent=self, title='Pair List')
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

        self.actions = struct(
            openDir=OpenDirAction(self),
            newFile=NewFileAction(self),
            openFile=OpenFileAction(self),
            saveFile=SaveFileAction(self),
            saveFileAs=SaveFileAsAction(self),
            closeFile=CloseFileAction(self),
            quitApp=QuitAppAction(self),
            openNextPair=OpenNextPairAction(self),
            openPrevPair=OpenPrevPairAction(self),
            addPair=AddPairAction(self),
            removePair=RemovePairAction(self),
            editKeypointMode=EditKeypointModeAction(self),
            editMatchMode=EditMatchModeAction(self),
            sanityCheck=SanityCheckAction(self),
            complementMatch=ComplementMatchAction(self),
            autoSaving=AutoSavingAction(self),
            showInfo = ShowInfoAction(self))

        self.menus = struct(
            file=self.menu('&File'),
            edit=self.menu('&Edit'),
            view=self.menu('&View'),
            help=self.menu('&Help'))

        # setup menus
        a = self.actions
        za = self.zoomWidget.actions
        addActions(
            self.menus.file,
            (a.openDir, a.newFile, a.openFile, a.saveFile, a.saveFileAs, a.closeFile, a.quitApp))
        addActions(
            self.menus.edit,
            (a.addPair, a.removePair,
             None, a.editKeypointMode, a.editMatchMode,
             None, a.sanityCheck, a.complementMatch))
        addActions(
            self.menus.view,
            (a.autoSaving,
             None, za.zoomIn, za.zoomOut, za.zoomOrg, za.zoomFitWindow, za.zoomFitWidth))
        addActions(
            self.menus.help,
            (a.showInfo,))

        # setup tools
        self.tools = self.toolbar('Tools')
        addActions(
            self.tools,
            (a.openDir, a.openFile, a.saveFile, a.saveFileAs,
             None, a.addPair, a.removePair, a.openNextPair, a.openPrevPair,
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
