import openhivenpy
from openhivenpy.types import Context

token_ = ""


def test_start(token):
    global token_
    token_ = token


class TestContext:
    pass
