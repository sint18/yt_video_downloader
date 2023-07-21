import pytest
from pytube import exceptions

import youtube_func

url = "https://www.youtube.com/playlist?list=PLCC34OHNcOtpmCA8s_dpPMvQLyHbvxocY"
vid_url = "https://www.youtube.com/watch?v=BaW_jenozKc"
invalid_url = "https://www.python.org/"


class TestGetVideoUrlsFromPlaylist:
    def test_no_url(self):
        with pytest.raises(KeyError):
            youtube_func.get_video_urls_from_playlist("")

    def test_get_items(self):
        assert youtube_func.get_video_urls_from_playlist(url) is not None

    def test_invalid_url(self):
        with pytest.raises(KeyError):
            youtube_func.get_video_urls_from_playlist(invalid_url)


class TestGetPlaylistInfo:
    def test_playlist_info(self):
        assert len(youtube_func.get_playlist_info(url).keys()) == 3

    def test_empty_playlist_info(self):
        with pytest.raises(KeyError):
            youtube_func.get_playlist_info("")

    def test_gibberish_string(self):
        with pytest.raises(KeyError):
            youtube_func.get_playlist_info("aosdjfoasejf")

    def test_invalid_link(self):
        with pytest.raises(KeyError):
            youtube_func.get_playlist_info(invalid_url)


class TestGetVideoInfo:
    def test_is_tuple(self):
        assert isinstance(youtube_func.get_video_info(vid_url), dict) is True

    def test_empty_video_info(self):
        with pytest.raises(TypeError):
            youtube_func.get_video_info("")

    def test_valid_video_info(self):
        assert bool(youtube_func.get_video_info(vid_url)) is True

    def test_invalid_video_url(self):
        with pytest.raises(TypeError):
            youtube_func.get_video_info(invalid_url)


class TestConversion:
    def test_convert_true(self):
        assert youtube_func.convert_min(3600) == "1:00:00"

    def test_convert_true1(self):
        assert youtube_func.convert_min(12345) == "3:25:45"

    def test_convert_type(self):
        assert isinstance(youtube_func.convert_min(12345), str)

    def test_convert_false(self):
        assert youtube_func.convert_min(0) == "0:00:00"
