from pytube import Stream


# TODO: Refactor code to work with classes instead of dictionaries
class Video:
    def __init__(self):
        self.title: str = ""
        self.author: str = ""
        self.duration_sec: int = 0
        self.video_stream = None
        self.audio_stream = None
