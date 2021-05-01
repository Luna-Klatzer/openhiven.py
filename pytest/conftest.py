import logging
import sys

import pytest

logging.basicConfig(level=logging.DEBUG)


def pytest_addoption(parser):
    parser.addoption(
        "--token", action="store", default="", help="Token used for authentication"
    )


@pytest.fixture
def token(request):
    return request.config.getoption("--token")


@pytest.fixture(autouse=True)
def capture_wrap():
    """
    Workaround for pytest, where after finishing the testing (ValueError: I/O operation on closed file.) is raised since
    the integrated logging module inteferes with it

    REF: https://github.com/pytest-dev/pytest/issues/5502#issuecomment-678368525
    """
    sys.stderr.close = lambda *args: None
    sys.stdout.close = lambda *args: None
    yield
