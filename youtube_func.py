from pytube import Playlist, YouTube, Stream
from pytube import exceptions


def get_playlist_info(playlist_link: str) -> dict:
    if not playlist_link:
        return {}

    try:
        playlist = Playlist(playlist_link)

        info_dict = {
            "playlist_title": playlist.title,
            "playlist_id": playlist.playlist_id,
            "views": playlist.views
        }
    except exceptions.PytubeError as err:
        print(err)
        return {}
    except KeyError:
        return {}

    return info_dict


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
    else:
        return playlist.url_generator()


# TODO: Provide resolution options
def get_video_info(video_link: str) -> tuple:
    if not video_link:
        return 0, {}

    try:
        yt = YouTube(video_link)

        # TODO: Get all video and audio streams and filter later
        # Get the best quality video
        video: Stream = yt.streams.filter(adaptive=True, type="video").asc().first()

        # Get the best quality audio
        audio: Stream = yt.streams.filter(adaptive=True, type="audio").asc().first()

        result_dict = {
            "title": yt.title,  # Title of Video
            "author": yt.author,  # Creator of video
            "duration_sec": yt.length,  # Length of video in seconds
            "video_stream": video,
            "audio_stream": audio
        }

    except exceptions.VideoPrivate:
        return 0, {"error": f"Video with link: {video_link} is private", "err_title": "Private Video"}
    except exceptions.AgeRestrictedError:
        return 0, {"error": f"Age restricted for video: {video_link}", "err_title": "Age Restricted"}
    except exceptions.VideoUnavailable:
        return 0, {"error": f"Video unavailable: {video_link}", "err_title": "Video Unavailable"}
    except exceptions.RegexMatchError:
        return 0, {"error": f"URL is invalid or not supported", "err_title": "Invalid URL"}
    else:

        return 1, result_dict


def download(stream: Stream):
    pass
# TODO: post-process streams with FFmpeg
