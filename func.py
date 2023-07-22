from pytube import Playlist, YouTube, Stream
from pytube import exceptions
import datetime
import os
import urllib


def convert_min(seconds: int) -> str:
    """
    Converts seconds to beautiful string
    :param seconds: int
    :return: str
    """
    return str(datetime.timedelta(seconds=seconds))


def is_valid_url(url: str) -> object | None:
    """
    Checks if a url is valid or supported.
    Returns a ParserObject if it's supported
    :return: None or object
    """
    res = urllib.parse.urlparse(url)
    if res.scheme and res.netloc:
        if "youtube" not in res.netloc:
            return None
        if res.path and res.query:
            return res

    return None


def get_playlist_info(playlist_link: str) -> dict:
    """
    Extract information of a playlist
    :return: dict keys - playlist_title, playlist_owner, last_updated
    """
    if not playlist_link:
        raise KeyError("URL cannot be empty")

    try:
        playlist = Playlist(playlist_link)

        info_dict = {
            "playlist_title": playlist.title,
            "playlist_owner": playlist.owner,
            "last_updated": playlist.last_updated
        }
    except KeyError:
        raise KeyError("Invalid Link")

    return info_dict


def get_video_urls_from_playlist(playlist_link: str):
    """
    Extract a list of video URLs from a given playlist link
    :param playlist_link: Link of a playlist
    :return: Generator
    """
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
    """
    Extract information of a video
    :param video_link: Link of a video
    :return: dict keys - title, author, duration, filesize, resolution, url, views
    """
    if not video_link:
        raise exceptions.RegexMatchError

    try:
        yt = YouTube(video_link)

        # Get the best quality video
        video: Stream = yt.streams.filter(adaptive=True, type="video").asc().first()

        # Get the best quality audio
        audio: Stream = yt.streams.filter(adaptive=True, type="audio").asc().first()

        result_dict = {
            "title": yt.title,  # Title of Video
            "author": yt.author,  # Creator of video
            "duration": convert_min(yt.length),  # Length of video in seconds
            "filesize": video.filesize_mb + audio.filesize_mb,
            "resolution": video.resolution,
            "url": video_link,
            "views": yt.views
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

