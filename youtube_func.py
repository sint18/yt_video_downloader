from pytube import Playlist, YouTube, Stream
from pytube import exceptions
import os


def get_playlist_info(playlist_link: str) -> dict:
    if not playlist_link:
        raise KeyError("URL cannot be empty")

    try:
        playlist = Playlist(playlist_link)

        info_dict = {
            "playlist_title": playlist.title,
            "playlist_id": playlist.playlist_id,
            "views": playlist.views
        }
    except KeyError:
        raise KeyError("Invalid Link")

    return info_dict


def get_video_urls_from_playlist(playlist_link: str):
    # Return empty list if link is empty
    if not playlist_link:
        raise KeyError("No url")
    elif "youtube" in playlist_link or "youtu.be" in playlist_link:
        playlist = Playlist(playlist_link)
        return playlist.url_generator()
    else:
        raise KeyError("Invalid Link (Only YouTube is supported)")

# TODO: Provide resolution options
def get_video_info(video_link: str) -> dict:
    if not video_link:
        raise exceptions.RegexMatchError

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
        raise exceptions.VideoPrivate(f"Video with link: {video_link} is private")
    except exceptions.AgeRestrictedError:
        raise exceptions.AgeRestrictedError(f"Age restricted for video: {video_link}")
    except exceptions.VideoUnavailable:
        raise exceptions.VideoUnavailable(f"Video unavailable: {video_link}")
    except exceptions.RegexMatchError:
        raise exceptions.RegexMatchError(f"URL is invalid or not supported")
    else:

        return result_dict


def download(stream: Stream):
    pass
# TODO: post-process streams with FFmpeg

