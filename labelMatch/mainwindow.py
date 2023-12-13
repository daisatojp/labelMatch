import json
import os
import os.path as osp
from loguru import logger
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from labelMatch.__init__ import __appname__
from labelMatch.widgets import *
from labelMatch.actions import *
from labelMatch.matching import Matching
from labelMatch.settings import Settings
from labelMatch.utils import *


QMB = QMessageBox


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.settings = Settings()
        self.settings.load()

        self.matching = None
        self.annot_dir = self.settings.get('annot_dir', None)
        self.image_dir = self.settings.get('image_dir', None)

        self.view_i_widget = ViewIWidget(parent=self)
        self.view_i_widget.itemClicked_connect(self.viewitem_clicked)
        self.view_j_widget = ViewJWidget(parent=self)
        self.view_j_widget.itemClicked_connect(self.viewitem_clicked)

        self.canvas = Canvas(self)
        self.zoom_widget = ZoomWidget(self)
        self.scroll_widget = ScrollWidget(self)
        self.canvas.zoom_request.connect(self.zoom_widget.zoom_request)
        self.canvas.scroll_request.connect(self.scroll_widget.scroll_request)

        self.setCentralWidget(self.scroll_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.view_i_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.view_j_widget)

        self.save_action = SaveAction(self)
        self.export_action = ExportAction(self)
        self.close_workspace_action = CloseWorkspaceAction(self)
        self.quit_app_action = QuitAppAction(self)
        self.open_workspace_action = OpenWorkspaceAction(self)
        self.open_next_view_action = OpenNextViewAction(self)
        self.open_prev_view_action = OpenPrevViewAction(self)
        self.edit_keypoint_mode_action = EditKeypointModeAction(self)
        self.edit_match_mode_action = EditMatchModeAction(self)
        self.auto_save_action = AutoSaveAction(self)
        self.show_info_action = ShowInfoAction(self)

        self.menus = struct(
            file=self.menuBar().addMenu('&File'),
            edit=self.menuBar().addMenu('&Edit'),
            view=self.menuBar().addMenu('&View'),
            help=self.menuBar().addMenu('&Help'))

        self.menus.file.addAction(self.open_workspace_action)
        self.menus.file.addAction(self.save_action)
        self.menus.file.addAction(self.export_action)
        self.menus.file.addAction(self.close_workspace_action)
        self.menus.file.addAction(self.quit_app_action)
        self.menus.edit.addAction(self.edit_keypoint_mode_action)
        self.menus.edit.addAction(self.edit_match_mode_action)
        self.menus.view.addAction(self.auto_save_action)
        self.menus.view.addSeparator()
        self.menus.view.addAction(self.zoom_widget.zoom_in_action)
        self.menus.view.addAction(self.zoom_widget.zoom_out_action)
        self.menus.view.addAction(self.zoom_widget.zoom_org_action)
        self.menus.view.addAction(self.zoom_widget.zoom_fit_window_action)
        self.menus.help.addAction(self.show_info_action)

        self.toolbar = ToolBar('Tools')
        self.toolbar.setObjectName('ToolBar')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.addAction(self.open_workspace_action)
        self.toolbar.addAction(self.save_action)
        self.toolbar.addAction(self.export_action)
        self.toolbar.addAction(self.close_workspace_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.open_next_view_action)
        self.toolbar.addAction(self.open_prev_view_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.zoom_widget.zoom_in_action)
        self.toolbar.addAction(self.zoom_widget.zoom_action)
        self.toolbar.addAction(self.zoom_widget.zoom_out_action)
        self.toolbar.addAction(self.zoom_widget.zoom_org_action)
        self.toolbar.addAction(self.zoom_widget.zoom_fit_window_action)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        self.statusBar().showMessage('{} started.'.format(__appname__))
        self.statusBar().show()

        size = QSize(600, 500)
        position = QPoint(0, 0)
        saved_position = QPoint(0, 0)
        # Fix the multiple monitors issue
        for i in range(QApplication.desktop().screenCount()):
            if QApplication.desktop() \
                           .availableGeometry(i) \
                           .contains(saved_position):
                position = saved_position
                break
        self.resize(size)
        self.move(position)

        self.labelCoordinates = QLabel('')
        self.statusBar().addPermanentWidget(self.labelCoordinates)

        self.update_title()

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)

    def paintCanvas(self):
        self.canvas.scale = 0.01 * self.zoom_widget.spinbox.value()
        self.canvas.adjustSize()
        self.canvas.update()

    def closeEvent(self, event):
        if not self.may_continue():
            event.ignore()
        self.settings['annot_dir'] = self.annot_dir
        self.settings['image_dir'] = self.image_dir
        self.settings.save()

    def open_workspace(self):
        if not osp.exists(self.annot_dir):
            logger.error('{} does not exist.'
                         .format(self.annot_dir))
            return
        if not osp.exists(self.image_dir):
            logger.error('{} does not exist.'
                         .format(self.image_dir))
            return
        self.matching = Matching(self.annot_dir, self.image_dir)
        self.matching.set_update_callback(self.get_matching_update_event)
        self.matching.set_dirty_callback(self.get_matching_dirty_event)
        self.view_i_widget.initialize()
        self.view_j_widget.initialize()
        view_id_i = self.matching.get_list_of_view_id()[0]
        view_id_j = self.matching.get_list_of_view_id()[1]
        self.change_pair(view_id_i, view_id_j)
        self.export_action.setEnabled(True)
        self.zoom_widget.enable_actions()
        self.update_title()

    def close_workspace(self):
        self.matching = None
        self.view_i_widget.clear()
        self.view_j_widget.clear()
        self.canvas.clear_pixmap()
        self.canvas.repaint()
        self.export_action.setEnabled(False)
        self.zoom_widget.disable_actions()
        self.update_title()

    def viewitem_clicked(self, item=None):
        view_id_i = self.matching.get_list_of_view_id()[self.view_i_widget.get_current_idx()]
        view_id_j = self.matching.get_list_of_view_id()[self.view_j_widget.get_current_idx()]
        self.change_pair(view_id_i, view_id_j)

    def change_pair(self, view_id_i, view_id_j):
        self.matching.clear_decoration()
        view_idx_i = self.matching.find_view_idx(view_id_i)
        view_idx_j = self.matching.find_view_idx(view_id_j)
        self.matching.set_view(view_id_i, view_id_j)
        self.view_i_widget.set_current_idx(view_idx_i)
        self.view_j_widget.set_current_idx(view_idx_j)
        self.view_j_widget.update_text()
        self.canvas.update_pixmap()
        self.canvas.repaint()
        if self.auto_save_action.isChecked():
            if self.matching.dirty():
                self.matching.save()
                self.save_action.setEnabled(False)

    def get_matching_update_event(self):
        self.view_i_widget.update_text()
        self.view_j_widget.update_text()

    def get_matching_dirty_event(self):
        self.save_action.setEnabled(True)

    def update_title(self):
        if (self.matching is not None) and \
           (self.annot_dir is not None) and \
           (self.image_dir is not None):
            title = '{} (wrk={}, img={})'.format(
                __appname__, self.annot_dir, self.image_dir)
        else:
            title = '{}'.format(
                __appname__)
        self.setWindowTitle(title)

    def update_status_message(self):
        if self.matching is None:
            self.statusBar().showMessage('')
            return
        vid = None
        kid = None
        if self.matching.highlighted_id_i is not None:
            vid = self.matching.get_view_id_i()
            kid = self.matching.highlighted_id_i
        elif self.matching.highlighted_id_j is not None:
            vid = self.matching.get_view_id_j()
            kid = self.matching.highlighted_id_j
        elif self.matching.selected_id_i is not None:
            vid = self.matching.get_view_id_i()
            kid = self.matching.selected_id_i
        elif self.matching.selected_id_j is not None:
            vid = self.matching.get_view_id_j()
            kid = self.matching.selected_id_j
        if (vid is not None) and (kid is not None):
            keypoint = self.matching.get_keypoint(vid, kid)
            self.statusBar().showMessage(
                '[{}] view_id={}, keypoint_id={}, group_id={}, x={:0.1f}, y={:0.1f}'
                .format(self.canvas.edit_mode_to_str(),
                        vid, kid,
                        keypoint['group_id'],
                        keypoint['pos'][0],
                        keypoint['pos'][1]))
        else:
            self.statusBar().showMessage(
                '[{}]'
                .format(self.canvas.edit_mode_to_str()))

    def may_continue(self):
        msg = 'You have unsaved changes, would you like to save them and proceed?'
        if self.matching is not None:
            if self.matching.dirty():
                save_changes = QMB.warning(self, 'Attention', msg, QMB.Yes | QMB.No | QMB.Cancel)
                if save_changes == QMB.Yes:
                    self.matching.save()
                    return True
                elif save_changes == QMB.No:
                    return True
                else:
                    return False
        return True
