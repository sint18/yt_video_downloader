import os
import pathlib
import yt_dlp
from PyQt5.QtCore import QObject, pyqtSignal

from module import get_playlist_info, get_video_urls_from_playlist, get_video_info
from main import download_path


class Worker(QObject):
    finished = pyqtSignal()  # Finished signal
    progress = pyqtSignal(int, tuple)  # Download Progress signal
    playlist_info_signal = pyqtSignal(dict)  # Playlist information signal
    video_info_signal = pyqtSignal(list)  # Video information signal

    def __init__(self, url=""):
        super().__init__()
        self.url = url
        self.videos = []
        self.playlist_title = ""

    def run_playlist(self):
        """
        Runs a get_playlist_info function and emits signals
        """
        playlist_info_dict: dict = get_playlist_info(self.url)
        self.playlist_info_signal.emit(playlist_info_dict)

        video_list = []
        for video_url in get_video_urls_from_playlist(self.url):
            video_dict = get_video_info(video_url)
            video_list.append(video_dict)

        self.video_info_signal.emit(video_list)
        self.finished.emit()

    def run_video(self):
        """
        Runs a get_video_info function and emits signals
        """
        self.video_info_signal.emit([get_video_info(self.url)])
        self.finished.emit()

    def download_videos(self):
        """
        Downloads videos and emits signals
        """
        index: int = 1

        def progress_hook(info):
            if info["status"] == "downloading":
                # print(info["filename"])
                # print(info["total_bytes"])
                # print(info["eta"])
                self.progress.emit(index, (info.get("downloaded_bytes"), info.get('total_bytes')))
            elif info["status"] == "finished":
                self.finished.emit()

        __download_path = pathlib.Path(download_path)
        if len(self.videos) > 1 and self.playlist_title:
            __download_path = pathlib.Path(download_path) / self.playlist_title
            os.mkdir(__download_path)

        ydl_options = {
            "outtmpl": str(__download_path) + "/%(title)s.%(ext)s",
            "progress_hooks": [progress_hook]
        }
        for item in self.videos:
            with yt_dlp.YoutubeDL(ydl_options) as ytdlp:
                ytdlp.download(item.get("url"))
            if len(self.videos) > 1:
                index = index + 1

        # self.finished.emit()
