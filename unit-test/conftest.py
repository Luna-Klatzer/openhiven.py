import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--token", action="store", default="", help="Token used for authentication"
    )


@pytest.fixture
def token(request):
    return request.config.getoption("--token")
