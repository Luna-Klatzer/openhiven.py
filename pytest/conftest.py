import logging
import sys

import pytest

logging.basicConfig(level=logging.DEBUG)


def pytest_addoption(parser):
    parser.addoption(
        "--token", action="store", default="", help="Token used for authentication"
    )


def pytest_sessionstart(session):
    logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def token(request):
    return request.config.getoption("--token")


@pytest.fixture(autouse=True)
def capture_wrap():
    """
    Workaround for pytest, where after finishing the testing (ValueError: I/O operation on closed file.) is raised since
    the integrated logging module interferes with it

    REF: https://github.com/pytest-dev/pytest/issues/5502#issuecomment-678368525
    """
    sys.stderr.close = lambda *args: None
    sys.stdout.close = lambda *args: None
    yield


@pytest.fixture(scope="module", autouse=True)
def logging_init():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("openhivenpy")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(
        filename='openhiven.log',
        encoding='utf-8',
        mode='w'
    )
    handler.setFormatter(
        logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    )
    logger.addHandler(handler)
