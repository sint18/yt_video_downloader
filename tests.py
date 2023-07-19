import youtube_func

url = "https://www.youtube.com/playlist?list=PLCC34OHNcOtpmCA8s_dpPMvQLyHbvxocY"
vid_url = "https://www.youtube.com/watch?v=BaW_jenozKc"
invalid_url = "https://www.python.org/"

class TestGetVideoUrlsFromPlaylist:
    def test_get_items_from_playlist(self):
        assert youtube_func.get_video_urls_from_playlist("") is None

    def test_get_items(self):
        assert youtube_func.get_video_urls_from_playlist(url) is not None


class TestGetPlaylistInfo:
    def test_playlist_info(self):
        assert len(youtube_func.get_playlist_info(url).keys()) == 3

    def test_empty_playlist_info(self):
        assert youtube_func.get_playlist_info("") == {}

    def test_gibberish_string(self):
        assert youtube_func.get_playlist_info("aoeijfoasdje") == {}

    def test_invalid_link(self):
        assert youtube_func.get_playlist_info(invalid_url) == {}


class TestGetVideoInfo:
    def test_empty_video_info(self):
        assert youtube_func.get_video_info("") == (0, {})

    def test_valid_video_info(self):
        assert youtube_func.get_video_info(vid_url)[0] == 1

    def test_invalid_video_url(self):
        assert youtube_func.get_video_info(invalid_url)[0] == 0

