""" Currently empty through the fact that feed is not available yet """
import openhivenpy

token_ = ""
client = openhivenpy.HivenClient()


def test_start(token):
    global token_
    token_ = token


class TestFeed:
    def test_preparation(self):
        pass

    def test_init(self):
        pass
