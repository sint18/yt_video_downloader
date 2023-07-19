from pytube import Playlist, YouTube, Stream
from pytube import exceptions


def get_playlist_info(playlist_link: str) -> dict:
    if not playlist_link:
        return {}

    try:
        playlist = Playlist(playlist_link)
    except exceptions.PytubeError as err:
        print(err)
        return {}

    return {
        "playlist_title": playlist.title,
        "views": playlist.views
    }


def get_video_urls_from_playlist(playlist_link: str):
    # Return empty list if link is empty
    if not playlist_link:
        return None

    try:
        # Create playlist object
        playlist = Playlist(playlist_link)
    except exceptions.PytubeError as err:
        print(err)
        return None

    return playlist.url_generator()


# TODO: Provide resolution options
def get_video_info(video_link: str) -> tuple:
    if not video_link:
        return 0, {}

    try:
        yt = YouTube(video_link)
    except exceptions.VideoPrivate:
        return 0, {"error": f"Video with link: {video_link} is private"}
    except exceptions.AgeRestrictedError:
        return 0, {"error": f"Age restricted for video: {video_link}"}
    except exceptions.VideoUnavailable:
        return 0, {"error": f"Video unavailable: {video_link}"}
    else:
        title: str = yt.title
        author: str = yt.author
        duration_sec: int = yt.length  # Converting to minutes

        # Get the best quality video
        video: Stream = yt.streams.filter(adaptive=True, type="video").asc().first()

        # Get the best quality audio
        audio: Stream = yt.streams.filter(adaptive=True, type="audio").asc().first()
        return 1, {"title": title, "author": author}


def download(stream: Stream):
    pass
# TODO: post-process streams with FFmpeg
