import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.uic import loadUi

colors = [("Red", "#FF0000"),
          ("Green", "#00FF00"),
          ("Blue", "#0000FF"),
          ("Black", "#000000"),
          ("White", "#FFFFFF"),
          ("Electric Green", "#41CD52"),
          ("Dark Blue", "#222840"),
          ("Yellow", "#F9E56d")]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("ui/mainScreen.ui", self)

        self.test_table()
        # Hide progress bar
        self.progressBar.setVisible(False)

        # Buttons and Signals
        self.processButton.clicked.connect(self.process_link)
        self.downloadButton.clicked.connect(self.download)

    def test_table(self):
        self.tableWidget.setRowCount(len(colors))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Name", "Hex Code"])

        for i, (name, code) in enumerate(colors):
            name_item = QtWidgets.QTableWidgetItem(name)
            code_item = QtWidgets.QTableWidgetItem(code)
            self.tableWidget.setItem(i, 0, name_item)
            self.tableWidget.setItem(i, 1, code_item)

    def process_link(self):
        link: str = self.linkLineEdit.text()

        if not link:
            print("cannot be empty")

        if "playlist" in link:
            # playlist
            pass



        else:
            # video
            print("video")

    def download(self):
        pass


def create_window():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    create_window()
