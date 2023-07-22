from module.func import is_valid_url
from module.worker import Worker
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread


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
        self.download_finished = False
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
        self.stopDownloadButton.clicked.connect(self.cancel_download)
        self.resetButton.clicked.connect(self.reset_button)

        # Loader
        self.movie = QMovie("assets/loader.gif")

        # Empty variables
        self.video_list: list = []
        self.playlist_title: str = ""

    def start_loading_animation(self):
        size: int = 70  # Size of loader (Change this to alter the loader size)
        self.loaderLabel.setScaledContents(True)
        self.loaderLabel.setMinimumSize(QtCore.QSize(size, size))
        self.loaderLabel.setMaximumSize(QtCore.QSize(size, size))
        self.loaderLabel.setMovie(self.movie)
        self.movie.start()

    def stop_loading_animation(self):
        if self.downloadStatusLabel.isVisible() and self.download_finished:
            self.downloadLocationLabel.setVisible(True)
            self.downloadStatusLabel.setText("Done!")
            self.downloadLocationLabel.setText(f"Saved to {download_path}")
        else:
            self.downloadStatusLabel.setText("Download Stopped!, Click 'Reset'")
        self.movie.stop()
        self.loaderLabel.clear()

    def display_data_in_table(self, data: list[tuple], column_headers: list):
        """
        Displays information in a table widget
        :param data: Actual data in list[tuple] format
        :param column_headers: Column headers
        """
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(column_headers))
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

        for row, items in enumerate(data):
            if items:
                for col, col_item in enumerate(items):
                    widget_item = QtWidgets.QTableWidgetItem(str(col_item))
                    self.tableWidget.setItem(row, col, widget_item)
                    self.tableWidget.horizontalHeader() \
                        .setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def flag_downloaded(self):
        """
        Flags when the download has finished.
        """
        self.download_finished = True
        self.video_list.clear()
        self.stopDownloadButton.setVisible(False)

    def run_fetch_playlist_task(self, url: str):
        """
        Performs tasks for playlist in a new QThread.
        :param url: playlist url
        """
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
        """
        Performs task to fetch only videos
        :param url: Video url
        """
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
        """
        Performs tasks to download videos
        """
        self.thread = QThread()
        self.worker = Worker()
        self.worker.videos = self.video_list
        self.worker.playlist_title = self.playlist_title
        self.worker.moveToThread(self.thread)

        # Started
        self.thread.started.connect(self.start_loading_animation)  # Show loading animation
        self.thread.started.connect(self.worker.download_videos)

        self.worker.progress.connect(self.update_progress)  # Show progress

        # Finished
        self.worker.finished.connect(self.flag_downloaded)
        self.worker.finished.connect(self.stop_loading_animation)  # Hide loading animation when finished
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def display_video_info(self, videos: list):
        """
        Display video information in a table
        :param videos: a list of videos
        """
        total_size: list = []
        table_data_list: list = []
        self.video_list.extend(videos)
        self.progressBar.setMaximum(len(videos))
        for video_dict in videos:
            tuple_data = (
                video_dict.get("title"),
                video_dict.get("author"),
                f"{video_dict.get('views'):,}",
                video_dict.get("duration"),
                video_dict.get("resolution")
            )
            table_data_list.append(tuple_data)

            total_size.append(video_dict.get("filesize"))

        self.label4.setVisible(True)
        self.label4.setText(f"Total Size: {sum(total_size):.2f} MB")
        self.display_data_in_table(table_data_list, ["Title", "Channel", "Views", "Length", "Resolution"])

    def display_playlist_info(self, playlist_info: dict):
        """
        Display a playlist information
        :param playlist_info: A dict of playlist info
        :return:
        """
        if playlist_info:
            self.label1.setVisible(True)
            self.label1.setText(f"Playlist Title: {playlist_info.get('playlist_title')}")
            self.playlist_title = playlist_info.get('playlist_title')

            self.label2.setVisible(True)
            self.label2.setText(f"Playlist Owner: {playlist_info.get('playlist_owner')}")

            self.label3.setVisible(True)
            self.label3.setText(f"Last Updated: {playlist_info.get('last_updated')}")
        else:
            showMsgBox(
                "Invalid URL",
                "URL is not supported or is invalid",
                "Error",
                QtWidgets.QMessageBox.Icon.Critical
            )
            return None

    def process_link(self):
        """
        For Get button
        :return: None
        """
        link: str = self.linkLineEdit.text().strip()

        if not link:
            showMsgBox(
                "No Link",
                "Link cannot be empty",
                "Error",
                QtWidgets.QMessageBox.Icon.Critical
            )
            return None
        url_check_result = is_valid_url(link)
        if url_check_result is None:
            showMsgBox(
                "Invalid URL",
                f"The give URL '{link}' is invalid or not supported",
                "Try Again!",
                QtWidgets.QMessageBox.Icon.Critical
            )
            return None
        if url_check_result.path == "/playlist":  # For playlists
            self.run_fetch_playlist_task(link)
        elif url_check_result.path == "/watch":  # For videos
            self.run_fetch_video_only(link)
        else:
            pass

    def download(self):
        """
        For Download button
        :return: None
        """
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
        self.stopDownloadButton.setVisible(True)
        self.progressBar.setVisible(True)
        self.run_download_videos()

    def update_progress(self, index: int, bytes: tuple):
        """
        Update progress hook for progress bar
        :param bytes: (downloaded_bytes, total_bytes)
        :param index: value
        """
        self.downloadStatusLabel.setText(f"Downloading... {index}/{len(self.video_list)}")
        if bytes:
            self.progressBar.setMaximum(bytes[1])  # Total Bytes
            self.progressBar.setValue(bytes[0])  # Downloaded Bytes

    def cancel_download(self):
        """
        For Stop download button
        """
        self.thread.quit()
        self.worker.deleteLater()
        self.thread.deleteLater()
        self.stop_loading_animation()

    def reset_button(self):
        """
        For reset button
        """
        self.video_list.clear()
        self.linkLineEdit.clear()
        self.label1.clear()
        self.label2.clear()
        self.label3.clear()
        self.label4.clear()
        self.downloadLocationLabel.clear()
        self.downloadStatusLabel.clear()
        self.progressBar.reset()
        self.progressBar.setVisible(False)
        self.tableWidget.setRowCount(0)
        self.stopDownloadButton.setVisible(False)


def create_window():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    create_window()
