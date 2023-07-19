import os
from youtube_func import get_video_urls_from_playlist, get_playlist_info, get_video_info

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.uic import loadUi


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
        loadUi("ui/mainScreen.ui", self)

        # Hide stuff
        self.progressBar.setVisible(False)
        self.stopDownloadButton.setVisible(False)
        self.titleLabel.setVisible(False)
        self.viewsLabel.setVisible(False)
        self.playlistIdLabel.setVisible(False)

        # Buttons and Signals
        self.processButton.clicked.connect(self.process_link)
        self.downloadButton.clicked.connect(self.download)

    def display_data_in_table(self, data: list[tuple], columns: list):
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(columns))
        self.tableWidget.setHorizontalHeaderLabels(columns)

        for row, items in enumerate(data):
            if items:
                for col, col_item in enumerate(items):
                    widget_item = QtWidgets.QTableWidgetItem(str(col_item))
                    self.tableWidget.setItem(row, col, widget_item)
                    self.tableWidget.horizontalHeader()\
                        .setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

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
            info: dict = get_playlist_info(link)
            if info:
                self.titleLabel.setVisible(True)
                self.titleLabel.setText(f"Playlist Title: {info.get('playlist_title')}")

                self.viewsLabel.setVisible(True)
                self.viewsLabel.setText(f"Views: {info.get('views'):,}")

                self.playlistIdLabel.setVisible(True)
                self.playlistIdLabel.setText(f"Playlist ID: {info.get('playlist_id')}")
            else:
                showMsgBox(
                    "Invalid URL",
                    "URL is not supported or is invalid",
                    "Error",
                    QtWidgets.QMessageBox.Icon.Critical
                )
                return None

            table_data_list = []
            for video_url in get_video_urls_from_playlist(link):
                status, video_dict = get_video_info(video_url)
                if status:
                    tuple_data = (video_dict.get("title"), video_dict.get("author"), video_dict.get("duration_sec"))
                    table_data_list.append(tuple_data)

            print(table_data_list)
            self.display_data_in_table(table_data_list, ["Title", "Channel", "Length"])


        else:
            # video
            print("video")
            status, video_dict = get_video_info(link)
            if status:
                pass
            else:
                if video_dict:
                    showMsgBox(
                        video_dict.get("err_title"),
                        video_dict.get("error"),
                        "Error",
                        QtWidgets.QMessageBox.Icon.Critical
                    )

    def download(self):
        pass


def create_window():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    create_window()
