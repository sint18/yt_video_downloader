import os
from youtube_func import get_video_urls_from_playlist, get_playlist_info, get_video_info
from os import path
import pathlib
import ffmpeg
import tempfile
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication
from PyQt5.uic import loadUi
from PyQt5.QtCore import QObject, QThread, pyqtSignal

download_path = path.join(path.expanduser("~"), "Downloads")


class Worker(QObject):
    finished = pyqtSignal()
    playlist_info_signal = pyqtSignal(dict)
    video_info_signal = pyqtSignal(list)

    def __init__(self, url=""):
        super().__init__()
        self.url = url
        self.videos = []

    def run_playlist(self):
        playlist_info_dict: dict = get_playlist_info(self.url)
        self.playlist_info_signal.emit(playlist_info_dict)

        video_list = []
        for video_url in get_video_urls_from_playlist(self.url):
            video_dict = get_video_info(video_url)
            video_list.append(video_dict)

        self.video_info_signal.emit(video_list)
        self.finished.emit()

    def run_video(self):
        self.video_info_signal.emit([get_video_info(self.url)])
        self.finished.emit()

    def download_videos(self):
        temp_dir = tempfile.gettempdir()
        for item in self.videos:
            audio_file = item.get("audio_stream").download(output_path=temp_dir, filename_prefix="audio_")
            print(f"Audio file Downloaded :{audio_file}")
            video_file = item.get("video_stream").download(output_path=temp_dir)
            print(f"Video file Downloaded :{video_file}")

            filename = pathlib.Path(download_path) / item.get("video_stream").default_filename
            audio_stream = ffmpeg.input(audio_file)
            video_stream = ffmpeg.input(video_file)
            print(f"Location :{filename}")
            ffmpeg.output(audio_stream, video_stream, str(filename)).run()
            print(f"Downloaded :{filename}")

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
        self.downloadLocationLabel.setVisible(False)

        # Buttons and Signals
        self.processButton.clicked.connect(self.process_link)
        self.downloadButton.clicked.connect(self.download)
        self.stopDownloadButton.clicked.connect(self.stop_loading_animation)
        self.resetButton.clicked.connect(self.reset_button)

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
        if self.downloadStatusLabel.isVisible():
            self.downloadLocationLabel.setVisible(True)
            self.downloadStatusLabel.setText("Done!")
            self.downloadLocationLabel.setText(f"Saved :{download_path}")
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

        # Started
        self.thread.started.connect(self.start_loading_animation)  # Show loading animation
        self.thread.started.connect(self.worker.run_playlist)
        # Finished
        self.worker.finished.connect(self.stop_loading_animation)  # Hide loading animation when finished
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Get Custom signal
        self.worker.playlist_info_signal.connect(self.display_playlist_info)
        self.worker.video_info_signal.connect(self.display_video_info)

        self.thread.start()

    def run_fetch_video_only(self, url: str):
        self.thread = QThread()
        self.worker = Worker(url)
        self.worker.moveToThread(self.thread)

        # Started
        self.thread.started.connect(self.start_loading_animation)  # Show loading animation
        self.thread.started.connect(self.worker.run_video)

        # Finished
        self.worker.finished.connect(self.stop_loading_animation)  # Hide loading animation when finished
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Get Custom signal
        self.worker.video_info_signal.connect(self.display_video_info)

        self.thread.start()

    def run_download_videos(self):
        self.thread = QThread()
        self.worker = Worker()
        self.worker.videos = self.video_list
        self.worker.moveToThread(self.thread)

        # Started
        self.thread.started.connect(self.start_loading_animation)  # Show loading animation
        self.thread.started.connect(self.worker.download_videos)

        # Finished
        self.worker.finished.connect(self.stop_loading_animation)  # Hide loading animation when finished
        # TODO: Add progress bar
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def display_video_info(self, videos: list):
        total_size: list = []
        table_data_list: list = []
        self.video_list.extend(videos)
        for video_dict in videos:
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
            return None

        if "playlist" in link:
            self.run_fetch_playlist_task(link)
        else:
            self.run_fetch_video_only(link)

    def download(self):
        if not self.video_list:
            showMsgBox(
                "No Video",
                "Get videos first before downloading",
                "Error",
                QtWidgets.QMessageBox.Icon.Critical
            )
            return None

        self.downloadStatusLabel.setVisible(True)
        self.downloadStatusLabel.setText("Downloading...")
        self.run_download_videos()

    def update_progress(self):
        self.progressBar.setVisible(True)

    def cancel_download(self):
        pass
        # self.stop_loading_animation()

    def reset_button(self):
        self.video_list.clear()
        self.linkLineEdit.clear()
        self.label1.clear()
        self.label2.clear()
        self.label3.clear()
        self.label4.clear()
        self.downloadLocationLabel.clear()
        self.downloadStatusLabel.clear()
        self.tableWidget.setRowCount(0)


def create_window():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    create_window()
