
# -*- coding: utf-8 -*-

import logging
import threading
from functools import partial

import storj.exception as sjexc

from PyQt4 import QtCore, QtGui

from .qt_interfaces.dashboard_ui import Ui_MainMenu
from .bucket_edition import BucketEditingUI
from .client_config import ClientConfigurationUI
from .engine import StorjEngine
from .file_download import SingleFileDownloadUI
from .file_mirror import FileMirrorsListUI
from .file_upload import SingleFileUploadUI
from .utilities.tools import Tools
from .sync_menu import SyncMenuUI
from .account_dash import AccountDashUI
from .crypto_keys_manager import CryptoKeysManagerUI

from .resources.constants import DISPLAY_FILE_CREATION_DATE_IN_MAIN,\
    FILE_LIST_SORTING_MAIN_ENABLED, BUCKETS_LIST_SORTING_ENABLED,\
    DATA_TABLE_EDIT_ENABLED
from .resources.custom_qt_interfaces import TableModel


class ExtendedQLabel(QtGui.QLabel):
    """"""

    def __init(self, parent):
        QtGui.QLabel.__init__(self, parent)

    def mouseReleaseEvent(self, ev):
        self.emit(QtCore.SIGNAL('clicked()'))


class MainUI(QtGui.QMainWindow):
    """Main UI section."""

    __logger = logging.getLogger('%s.MainUI' % __name__)

    def __init__(self, parent=None, bucketid=None, encryption_key_seed=None):
        QtGui.QWidget.__init__(self, parent)
        self.file_manager_ui = Ui_MainMenu()
        self.file_manager_ui.setupUi(self)

        self.file_manager_ui.files_list_tableview.setSelectionMode(
            QtGui.QTableView.SingleSelection)
        self.file_manager_ui.files_list_tableview.setDragDropMode(
            QtGui.QTableView.InternalMove)
        self.file_manager_ui.files_list_tableview.setDragEnabled(True)
        self.file_manager_ui.files_list_tableview.setSelectionBehavior(
            QtGui.QTableView.SelectRows)
        self.file_manager_ui.files_list_tableview.setAcceptDrops(True)
        self.setAcceptDrops(True)

        # self.change_loading_gif()
        # connect ComboBox change listener
        QtCore.QObject.connect(self.file_manager_ui.bucket_select_combo_box,
                               QtCore.SIGNAL('currentIndexChanged(const QString&)'),
                               self.createNewFileListUpdateThread)
        # open mirrors list window
        QtCore.QObject.connect(self.file_manager_ui.file_mirrors_bt,
                               QtCore.SIGNAL('clicked()'),
                               self.open_mirrors_list_window)

        # create bucket action
        QtCore.QObject.connect(self.file_manager_ui.file_download_bt,
                               QtCore.SIGNAL('clicked()'),
                               self.open_single_file_download_window)
        # delete selected file
        QtCore.QObject.connect(self.file_manager_ui.file_delete_bt,
                               QtCore.SIGNAL('clicked()'),
                               self.delete_selected_file)

        self.connect(self, QtCore.SIGNAL('changeLoadingGif'),
                     self.change_loading_gif)
        self.connect(self, QtCore.SIGNAL('applyFilesToTable'),
                     self.apply_data_to_file_table)

        self.file_manager_ui.files_list_tableview.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                              QtGui.QSizePolicy.Expanding))
        # self.adjustSize()
        # self.setFixedSize(self.size())

        appStyle = """
        QTableView
        {
            alternate-background-color: #1F1F1F;
            background-color: gray;
            gridline-color: gray;
            color: gray;
        }
        QTableView::item
        {
            color: white;
        }

        QTableView::item:focus
        {
            color: gray;
            background: #0063cd;
        }
        QTableView::item:selected
        {
            color: gray;
            background: #0063cd;
        }

        QCheckBox::indicator:checked, QCheckBox::indicator:unchecked{
            color: #b1b1b1;
            background-color: #323232;
            border: 1px solid #b1b1b1;
            border-radius: 1px;
            width: 7px;
            height: 7px;
            margin: 0px 5px 0 5px;
        }
        """

        # self.file_manager_ui.files_list_tableview.setStyleSheet(appStyle)

        if DATA_TABLE_EDIT_ENABLED is False:
            self.file_manager_ui.files_list_tableview.setEditTriggers(
                QtGui.QAbstractItemView.NoEditTriggers)

        self.file_manager_ui.sync_menu_bt.mousePressEvent = self.open_sync_menu
        self.file_manager_ui.account_dash_bt.mousePressEvent =\
            self.open_account_dash_window
        self.file_manager_ui.settings_bt.mousePressEvent =\
            self.open_settings_window
        self.file_manager_ui.refresh_bt.mousePressEvent =\
            self.createNewFileListUpdateThread
        self.file_manager_ui.crypto_keys_manager_bt.mousePressEvent =\
            self.open_crypto_keys_manager_window

        # delete selected file
        QtCore.QObject.connect(self.file_manager_ui.new_file_upload_bt,
                               QtCore.SIGNAL('clicked()'),
                               self.open_single_file_upload_window)

        # open bucket edit window
        QtCore.QObject.connect(self.file_manager_ui.edit_bucket_bt,
                               QtCore.SIGNAL('clicked()'),
                               lambda: self.open_bucket_editing_window(
                                   action='edit'))

        # open bucket edit window
        QtCore.QObject.connect(self.file_manager_ui.create_bucket_bt,
                               QtCore.SIGNAL('clicked()'),
                               lambda: self.open_bucket_editing_window(
                                   action='add'))

        self.storj_engine = StorjEngine()  # init StorjEngine

        user_email = self.storj_engine.account_manager.get_user_email()
        self.file_manager_ui.account_label.setText(str(user_email))

        self.createNewBucketResolveThread()

        # Context menu policy

        self.file_manager_ui.files_list_tableview.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)

        self.file_manager_ui.files_list_tableview. \
            customContextMenuRequested.connect(
                partial(self.display_files_list_context_menu))

    def display_files_list_context_menu(self, position):
        tablemodel = self.file_manager_ui.files_list_tableview.model()
        rows = sorted(set(index.row() for index in
                          self.file_manager_ui.files_list_tableview.
                          selectedIndexes()))
        i = 0
        selected_row = 0
        any_row_selected = False
        for row in rows:
            any_row_selected = True
            fileid_index = tablemodel.index(row, 2)  # get fileid Index
            filename_index = tablemodel.index(row, 0)  # get filename Index
            # We suppose data are strings
            selected_file_name = str(tablemodel.data(
                filename_index).toString())
            selected_file_id = str(tablemodel.data(
                fileid_index).toString())
            selected_row = row
            i += 1

        if any_row_selected:
            menu = QtGui.QMenu()
            fileDeleteFromTableAction = menu.addAction('Delete file')
            action = menu.exec_(self.file_manager_ui.files_list_tableview.
                                mapToGlobal(position))

            if action == fileDeleteFromTableAction:
                # ask user and delete if sure
                msgBox = QtGui.QMessageBox(
                    QtGui.QMessageBox.Question,
                    'Question',
                    'Are you sure that you want to permanently remove file '
                    '"%s" ?' %
                    str(selected_file_name),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

                result = msgBox.exec_()

                if result == QtGui.QMessageBox.Yes:
                    try:
                        self.storj_engine.storj_client.file_remove(
                            str(self.current_selected_bucket_id),
                            str(selected_file_id))
                        # update files list
                        self.createNewFileListUpdateThread()
                        QtGui.QMessageBox.about(
                            self,
                            'Success',
                            'File "%s" has been deleted successfully' % selected_file_name)
                    except sjexc.StorjBridgeApiError as e:
                        self.__logger.error(e)
                        QtGui.QMessageBox.about(
                            self,
                            'Error',
                            'Bridge exception occured while trying to delete file: %s' % e)

                    except Exception as e:
                        self.__logger.error(e)
                        QtGui.QMessageBox.about(
                            self,
                            'Error',
                            'Unhandled exception occured while trying to delete file: %s' % e)

                    self.__logger.debug('Delete action')

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()
        for path in event.mimeData().urls():
            row_data = {}
            row_data["file_path"] = str(event.mimeData().text()).replace("file://", "").replace('\n', "").replace('\r', "")
            self.single_file_upload_window = SingleFileUploadUI(self, dashboard_instance=self, start=True, row_data=row_data)

            self.single_file_upload_window.show()

        self.__logger.debug(event.mimeData().text())

    def open_crypto_keys_manager_window(self, x):
        self.crypto_keys_manager_window = CryptoKeysManagerUI(self)
        self.crypto_keys_manager_window.show()

    def open_account_dash_window(self, x):
        self.account_dash_window = AccountDashUI(self)
        self.account_dash_window.show()

    def open_sync_menu(self, x):
        self.open_sync_menu_window = SyncMenuUI(self)
        self.open_sync_menu_window.show()

    def change_loading_gif(self, is_visible):
        if is_visible:
            movie = QtGui.QMovie(':/resources/loading.gif')
            self.file_manager_ui.refresh_bt.setMovie(movie)
            movie.start()
        else:
            self.file_manager_ui.refresh_bt.setPixmap(QtGui.QPixmap((
                ':/resources/refresh.png')))

    def open_bucket_editing_window(self, action):
        if action == 'edit':
            self.bucket_editing_window = BucketEditingUI(
                self, action=action,
                bucketid=str(self.current_selected_bucket_id),
                dashboard_instance=self)

        else:
            self.bucket_editing_window = BucketEditingUI(
                self, action=action, dashboard_instance=self)
        self.bucket_editing_window.show()

    def open_single_file_upload_window(self):
        self.single_file_upload_window = SingleFileUploadUI(
            self, dashboard_instance=self)
        self.single_file_upload_window.show()

    def open_settings_window(self, b):
        self.open_settings_window = ClientConfigurationUI(self)
        self.open_settings_window.show()

    def delete_selected_file(self):
        self.current_bucket_index = self.file_manager_ui.\
            bucket_select_combo_box.currentIndex()
        self.current_selected_bucket_id = self.bucket_id_list[
            self.current_bucket_index]

        tablemodel = self.file_manager_ui.files_list_tableview.model()
        rows = sorted(set(index.row() for index in
                          self.file_manager_ui.files_list_tableview.
                          selectedIndexes()))

        selected = False
        for row in rows:
            selected = True
            index = tablemodel.index(row, 2)  # get file ID index
            index_filename = tablemodel.index(row, 0)  # get file name index

            # We suppose data are strings
            selected_file_id = str(tablemodel.data(index).toString())
            selected_file_name = str(tablemodel.data(index_filename).toString())
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Question,
                'Question',
                'Are you sure you want to delete this file? File name: %s' %
                str(selected_file_name).decode('utf-8'),
                (QtGui.QMessageBox.Yes | QtGui.QMessageBox.No))

            result = msgBox.exec_()
            self.__logger.debug(result)

            if result == QtGui.QMessageBox.Yes:
                try:
                    self.storj_engine.storj_client.file_remove(
                        str(self.current_selected_bucket_id),
                        str(selected_file_id))
                    # update files list
                    self.createNewFileListUpdateThread()
                    QtGui.QMessageBox.about(
                        self,
                        'Success',
                        'File "%s" has been deleted successfully' %
                        selected_file_name)
                except sjexc.StorjBridgeApiError as e:
                    self.__logger.error(e)
                    QtGui.QMessageBox.about(
                        self,
                        'Error',
                        'Bridge exception occured while trying to delete file: %s' % e)

                except Exception as e:
                    self.__logger.error(e)
                    QtGui.QMessageBox.about(
                        self,
                        'Error',
                        'Unhandled exception occured while trying to delete file: %s' % e)

        if not selected:
            QtGui.QMessageBox.about(
                self, 'Information', 'Please select file which you want to delete')

        return True

    def open_mirrors_list_window(self):
        self.current_bucket_index = self.file_manager_ui.\
            bucket_select_combo_box.currentIndex()
        self.current_selected_bucket_id = self.bucket_id_list[
            self.current_bucket_index]

        tablemodel = self.file_manager_ui.files_list_tableview.model()
        rows = sorted(set(index.row() for index in
                          self.file_manager_ui.files_list_tableview.selectedIndexes()))
        i = 0
        for row in rows:
            self.__logger.info('Row %d is selected' % row)
            index = tablemodel.index(row, 2)  # get file ID
            index_filename = tablemodel.index(row, 0)  # get file ID
            # We suppose data are strings
            selected_file_id = str(tablemodel.data(index).toString())
            selected_file_name = str(tablemodel.data(index_filename).toString())
            self.file_mirrors_list_window = FileMirrorsListUI(
                self, str(self.current_selected_bucket_id),
                selected_file_id, filename=selected_file_name)
            self.file_mirrors_list_window.show()
            i += 1

        if i == 0:
            QtGui.QMessageBox.about(self, 'Warning!', 'Please select file from file list!')

        self.__logger.debug(1)

    def createNewFileListUpdateThread(self, a=None):
        download_thread = threading.Thread(target=self.update_files_list,
                                           args=())
        download_thread.start()

    def update_files_list(self):
        self.tools = Tools()

        self.current_bucket_index = self.file_manager_ui.\
            bucket_select_combo_box.currentIndex()
        self.current_selected_bucket_id = self.bucket_id_list[
            self.current_bucket_index]

        try:
            self.emit(QtCore.SIGNAL('changeLoadingGif'), True)
            files_data = self.storj_engine.storj_client.bucket_files(
                str(self.current_selected_bucket_id))
            self.emit(QtCore.SIGNAL('applyFilesToTable'), files_data)
        except sjexc.StorjBridgeApiError as e:
            self.__logger.error(e)

    def apply_data_to_file_table(self, files_data):

        model = TableModel(1, 1)
        file_list_header_labels = ['File name', 'File size', 'File ID']

        if DISPLAY_FILE_CREATION_DATE_IN_MAIN:
            file_list_header_labels.append('Creation date')

        model.setHorizontalHeaderLabels(file_list_header_labels)

        i = 0

        for self.file_details in files_data:
            item = QtGui.QStandardItem(
                str(self.file_details['filename'].replace('[DECRYPTED]', ''))
                .decode('utf8'))
            model.setItem(i, 0, item)  # row, column, item (StandardItem)

            # get human readable file size
            file_size_str =\
                self.tools.human_size(int(self.file_details['size']))

            item = QtGui.QStandardItem(str(file_size_str))
            model.setItem(i, 1, item)  # row, column, item (QQtGui.StandardItem)

            item = QtGui.QStandardItem(str(self.file_details['id']))
            model.setItem(i, 2, item)  # row, column, item (QStandardItem)

            if DISPLAY_FILE_CREATION_DATE_IN_MAIN:
                item = QtGui.QStandardItem(str(self.file_details[
                    'created']).replace('Z', '').replace('T', ' '))
                model.setItem(i, 3, item)  # row, column, item (QStandardItem)

            i = i + 1

            self.__logger.debug(self.file_details['filename'].
                                replace('[DECRYPTED]', '').decode('utf8'))

        self.file_manager_ui.files_list_tableview.clearFocus()
        self.file_manager_ui.files_list_tableview.setModel(model)
        self.file_manager_ui.files_list_tableview.horizontalHeader().\
            setResizeMode(QtGui.QHeaderView.Stretch)
        if FILE_LIST_SORTING_MAIN_ENABLED:
            self.file_manager_ui.files_list_tableview.setSortingEnabled(True)
            self.file_manager_ui.files_list_tableview.horizontalHeader().sortIndicatorChanged.connect(
                self.handleSortIndicatorChanged)
            self.file_manager_ui.files_list_tableview.sortByColumn(
                0, QtCore.Qt.AscendingOrder)
        self.emit(QtCore.SIGNAL('changeLoadingGif'), False)
        return True

    def handleSortIndicatorChanged(self, index, order):
        if index != 0:
            self.file_manager_ui.files_list_tableview.horizontalHeader().\
                setSortIndicator(
                0, self.file_manager_ui.files_list_tableview.model().
                    sortOrder())

    def createNewBucketResolveThread(self):
        download_thread = threading.Thread(
            target=self.initialize_bucket_select_combobox, args=())
        download_thread.start()

    def initialize_bucket_select_combobox(self):
        self.file_manager_ui.bucket_select_combo_box.clear()
        self.buckets_list = []
        self.bucket_id_list = []
        self.bucket_id_name_2D_list = []
        self.storj_engine = StorjEngine()  # init StorjEngine
        i = 0
        self.emit(QtCore.SIGNAL('changeLoadingGif'), True)
        try:
            for bucket in self.storj_engine.storj_client.bucket_list():
                # append buckets to list
                self.bucket_id_name_2D_list.append(
                    [str(bucket.id), str(bucket.name).decode('utf8')])

                i += 1

            if BUCKETS_LIST_SORTING_ENABLED:
                self.bucket_id_name_2D_list = sorted(self.bucket_id_name_2D_list, key=lambda x: x[1], reverse=False)

            for arr_data in self.bucket_id_name_2D_list:
                self.buckets_list.append(arr_data[1])
                self.bucket_id_list.append(arr_data[0])

        except sjexc.StorjBridgeApiError as e:
            self.__logger.error(e)
            QtGui.QMessageBox.about(self,
                                    'Unhandled bucket resolving exception',
                                    'Exception: ' % e)

        self.file_manager_ui.bucket_select_combo_box.addItems(self.buckets_list)
        self.emit(QtCore.SIGNAL('changeLoadingGif'), False)

    def open_single_file_download_window(self):
        self.current_bucket_index = self.file_manager_ui.\
            bucket_select_combo_box.currentIndex()
        self.current_selected_bucket_id = self.bucket_id_list[
            self.current_bucket_index]

        tablemodel = self.file_manager_ui.files_list_tableview.model()
        rows = sorted(set(index.row() for index in
                          self.file_manager_ui.files_list_tableview.
                          selectedIndexes()))
        i = 0
        for row in rows:
            self.__logger.info('Row %d is selected' % row)
            index = tablemodel.index(row, 2)  # get file ID
            # We suppose data are strings
            selected_file_id = str(tablemodel.data(index).toString())
            self.file_mirrors_list_window = SingleFileDownloadUI(
                self, str(self.current_selected_bucket_id), selected_file_id)
            self.file_mirrors_list_window.show()
            i += 1

        if i == 0:
            QtGui.QMessageBox.about(self, 'Warning!',
                                    'Please select file from file list!')

        self.__logger.debug(1)
