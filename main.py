import os
from youtube_func import get_video_urls_from_playlist, get_playlist_info, get_video_info

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication
from PyQt5.uic import loadUi
from PyQt5.QtCore import QObject, QThread, pyqtSignal


class Worker(QObject):
    finished = pyqtSignal()
    playlist_info_signal = pyqtSignal(dict)
    video_info_signal = pyqtSignal(list)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        playlist_info_dict: dict = get_playlist_info(self.url)

        self.playlist_info_signal.emit(playlist_info_dict)

        video_list = []
        for video_url in get_video_urls_from_playlist(self.url):
            status, video_dict = get_video_info(video_url)

            if status:
                video_list.append(video_dict)

        self.video_info_signal.emit(video_list)
        self.finished.emit()


def showMsgBox(text: str, informative_text: str, window_title: str, icon):
    """
    Displays a message box with given messages
    Args:
        text: Title text
        informative_text: Message
        window_title: Title of the window
        icon: Icons inside Qt
    """
    msg = QtWidgets.QMessageBox()
    msg.setIcon(icon)
    msg.setText(text)
    msg.setInformativeText(informative_text)
    msg.setWindowTitle(window_title)
    msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Close)
    msg.exec()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker = None
        self.thread = None
        loadUi("ui/mainScreen.ui", self)

        # Hide stuff
        self.progressBar.setVisible(False)
        self.stopDownloadButton.setVisible(False)
        self.label1.setVisible(False)
        self.label2.setVisible(False)
        self.label3.setVisible(False)
        self.label4.setVisible(False)
        self.downloadStatusLabel.setVisible(False)

        # Buttons and Signals
        self.processButton.clicked.connect(self.process_link)
        self.downloadButton.clicked.connect(self.download)
        self.stopDownloadButton.clicked.connect(self.stop_loading_animation)

        # Loader
        self.movie = QMovie("assets/loader.gif")

        # Empty List
        self.video_list: list = []

    def start_loading_animation(self):
        size: int = 70  # Size of loader (Change this to alter the loader size)
        self.loaderLabel.setScaledContents(True)
        self.loaderLabel.setMinimumSize(QtCore.QSize(size, size))
        self.loaderLabel.setMaximumSize(QtCore.QSize(size, size))
        self.loaderLabel.setMovie(self.movie)
        self.movie.start()

    def stop_loading_animation(self):
        self.movie.stop()
        self.loaderLabel.clear()

    def display_data_in_table(self, data: list[tuple], columns: list):
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(columns))
        self.tableWidget.setHorizontalHeaderLabels(columns)

        for row, items in enumerate(data):
            if items:
                for col, col_item in enumerate(items):
                    widget_item = QtWidgets.QTableWidgetItem(str(col_item))
                    self.tableWidget.setItem(row, col, widget_item)
                    self.tableWidget.horizontalHeader() \
                        .setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def run_fetch_playlist_task(self, url: str):
        self.thread = QThread()
        self.worker = Worker(url)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Get Emitted signal
        self.worker.playlist_info_signal.connect(self.display_playlist_info)
        self.worker.video_info_signal.connect(self.display_video_info)

        self.thread.start()

    def display_video_info(self, video_list: list):
        total_size: list = []
        table_data_list: list = []
        for video_dict in video_list:
            vid_stream = video_dict.get("video_stream")
            audio_stream = video_dict.get("audio_stream")

            tuple_data = (
                video_dict.get("title"),
                video_dict.get("author"),
                vid_stream.resolution,
                video_dict.get("duration_sec"),
            )
            table_data_list.append(tuple_data)

            total_size.append(vid_stream.filesize_mb + audio_stream.filesize_mb)

        self.label4.setVisible(True)
        self.label4.setText(f"Total Size: {sum(total_size):.2f} MB")
        self.display_data_in_table(table_data_list, ["Title", "Channel", "Resolution", "Length"])

    def display_playlist_info(self, playlist_info: dict):
        if playlist_info:
            self.label1.setVisible(True)
            self.label1.setText(f"Playlist Title: {playlist_info.get('playlist_title')}")

            self.label2.setVisible(True)
            self.label2.setText(f"Views: {playlist_info.get('views'):,}")

            self.label3.setVisible(True)
            self.label3.setText(f"Playlist ID: {playlist_info.get('playlist_id')}")
        else:
            showMsgBox(
                "Invalid URL",
                "URL is not supported or is invalid",
                "Error",
                QtWidgets.QMessageBox.Icon.Critical
            )
            return None

    def process_link(self):
        link: str = self.linkLineEdit.text().strip()

        if not link:
            showMsgBox(
                "No Link",
                "Link cannot be empty",
                "Error",
                QtWidgets.QMessageBox.Icon.Critical
            )

        if "playlist" in link:
            # playlist

            self.run_fetch_playlist_task(link)

            # total_size: list = []
            # table_data_list: list = []
            # for video_url in get_video_urls_from_playlist(link):
            #     status, video_dict = get_video_info(video_url)
            #     if status:
            #         self.video_list.append(video_dict)
            #         vid_stream = video_dict.get("video_stream")
            #         audio_stream = video_dict.get("audio_stream")
            #
            #         tuple_data = (
            #             video_dict.get("title"),
            #             video_dict.get("author"),
            #             vid_stream.resolution,
            #             video_dict.get("duration_sec"),
            #         )
            #         table_data_list.append(tuple_data)
            #
            #         total_size.append(vid_stream.filesize_mb + audio_stream.filesize_mb)
            #
            # self.label4.setVisible(True)
            # self.label4.setText(f"Total Size: {sum(total_size):.2f} MB")
            # self.display_data_in_table(table_data_list, ["Title", "Channel", "Resolution", "Length"])
            # self.loaderLabel.setVisible(False)  # Hide loader

        else:
            # video
            print("video")
            status, video_dict = get_video_info(link)
            if status:
                vid_stream = video_dict.get("video_stream")
                audio_stream = video_dict.get("audio_stream")

                data = [(
                    video_dict.get("title"),
                    video_dict.get("author"),
                    vid_stream.resolution,
                    video_dict.get("duration_sec"))]
                self.display_data_in_table(data, ["Title", "Channel", "Resolution", "Length"])

                self.label1.setVisible(True)
                self.label1.setText(f"Size: {vid_stream.filesize_mb + audio_stream.filesize_mb:.2f} MB")

            else:
                if video_dict:
                    showMsgBox(
                        video_dict.get("err_title"),
                        video_dict.get("error"),
                        "Error",
                        QtWidgets.QMessageBox.Icon.Critical
                    )

    def download(self):
        self.downloadStatusLabel.setVisible(True)
        self.downloadStatusLabel.setText("Downloading...")
        # self.start_loading_animation()

    def update_progress(self):
        self.progressBar.setVisible(True)

    def cancel_download(self):
        pass
        # self.stop_loading_animation()


def create_window():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    create_window()
