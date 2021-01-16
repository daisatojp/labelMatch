from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PointMatcher.__init__ import __appname__
from PointMatcher.widgets import *
from PointMatcher.actions import *
from PointMatcher.data.matching import Matching
from PointMatcher.settings import Settings
from PointMatcher.utils.struct import struct
from PointMatcher.utils.qt import addActions


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

        self.matching = None
        self.imageDir = None
        self.annotDir = None

        self.settings = Settings()
        self.settings.load()

        self.viewIWidget = ViewIWidget(parent=self)
        self.viewIWidget.itemClicked_connect(self.viewitemClicked)
        self.viewJWidget = ViewJWidget(parent=self)
        self.viewJWidget.itemClicked_connect(self.viewitemClicked)

        self.canvas = Canvas(self)
        self.zoomWidget = ZoomWidget(self)
        self.scrollWidget = ScrollWidget(self)
        self.canvas.zoomRequest.connect(self.zoomWidget.zoomRequest)
        self.canvas.scrollRequest.connect(self.scrollWidget.scrollRequest)

        self.setCentralWidget(self.scrollWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.viewIWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.viewJWidget)

        self.actions = struct(
            newProject=NewProjectAction(self),
            openImageDir=OpenImageDirAction(self),
            openAnnotDir=OpenAnnotDirAction(self),
            save=SaveAction(self),
            export=ExportAction(self),
            close=CloseAction(self),
            quitApp=QuitAppAction(self),
            openNextView=OpenNextViewAction(self),
            openPrevView=OpenPrevViewAction(self),
            editKeypointMode=EditKeypointModeAction(self),
            editMatchMode=EditMatchModeAction(self),
            autoSaving=AutoSavingAction(self),
            showInfo=ShowInfoAction(self))

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
            (a.newProject, a.openImageDir, a.openAnnotDir, a.save, a.export, a.close, a.quitApp))
        addActions(
            self.menus.edit,
            (a.editKeypointMode, a.editMatchMode))
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
            (a.openImageDir, a.openAnnotDir, a.save, a.export,
             None, a.openNextView, a.openPrevView,
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

        self.updateTitle()
        self.labelCoordinates = QLabel('')
        self.statusBar().addPermanentWidget(self.labelCoordinates)

    def loadMatching(self):
        self.matching = Matching(self.annotDir)
        self.matching.set_update_callback(self.getMatchingUpdateEvent)
        self.matching.set_dirty_callback(self.getMatchingDirtyEvent)
        self.viewIWidget.initialize()
        self.viewJWidget.initialize()
        view_id_i = self.matching.get_list_of_view_id()[0]
        view_id_j = self.matching.get_list_of_view_id()[1]
        self.changePair(view_id_i, view_id_j)
        self.actions.export.setEnabled(True)

    def viewitemClicked(self, item=None):
        view_id_i = self.matching.get_list_of_view_id()[self.viewIWidget.get_current_idx()]
        view_id_j = self.matching.get_list_of_view_id()[self.viewJWidget.get_current_idx()]
        self.changePair(view_id_i, view_id_j)

    def changePair(self, view_id_i, view_id_j):
        view_idx_i = self.matching.find_view_idx(view_id_i)
        view_idx_j = self.matching.find_view_idx(view_id_j)
        self.matching.set_view(view_id_i, view_id_j)
        self.viewIWidget.set_current_idx(view_idx_i)
        self.viewJWidget.set_current_idx(view_idx_j)
        self.viewJWidget.update_text()
        self.canvas.updatePixmap()
        self.canvas.repaint()
        if self.actions.autoSaving.isChecked():
            if self.matching.dirty():
                self.matching.save(self.savePath)
                self.actions.save.setEnabled(False)

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)

    def paintCanvas(self):
        self.canvas.scale = 0.01 * self.zoomWidget.spinbox.value()
        self.canvas.adjustSize()
        self.canvas.update()

    def closeEvent(self, event):
        if not self.mayContinue():
            event.ignore()
        self.settings.save()
        self.actions.inspection.terminate_thread()

    def getMatchingUpdateEvent(self):
        self.viewIWidget.update_text()
        self.viewJWidget.update_text()

    def getMatchingDirtyEvent(self):
        if not self.actions.autoSaving.isChecked():
            self.actions.save.setEnabled(True)

    def updateTitle(self):
        if self.annotDir is None:
            self.setWindowTitle(__appname__)
        else:
            self.setWindowTitle('{} [{}]'.format(__appname__, self.annotDir))

    def mayContinue(self):
        Yes = QMessageBox.Yes
        No = QMessageBox.No
        Cancel = QMessageBox.Cancel
        msg = 'You have unsaved changes, would you like to save them and proceed?'
        if self.matching is not None:
            if self.matching.dirty():
                saveChanges = QMessageBox.warning(self, 'Attention', msg, Yes | No | Cancel)
                if saveChanges == Yes:
                    self.matching.save(self.savePath)
                    return True
                elif saveChanges == No:
                    return True
                else:
                    return False
        return True
