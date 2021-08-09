import asyncio
import logging

from openhivenpy import utils


class ExampleClass:
    def __init__(self):
        self.name = "test"

    def example_func(self, *args, **kwargs):
        assert args == ("test", "test")
        assert kwargs == {"test": "test"}
        return "func"

    async def example_coro(self, *args, **kwargs):
        assert args == ("test", "test")
        assert kwargs == {"test": "test"}
        return "coro"


class TestUtils:
    def test_fetch_func(self):
        obj = ExampleClass()
        assert obj.example_func.__name__ == utils.fetch_func(obj, "example_func").__name__

    def test_dispatch_func_if_exists(self):
        obj = ExampleClass()

        assert "func" == utils.dispatch_func_if_exists(
            obj, "example_func", ("test", "test"), {"test": "test"}
        )

        assert "coro" == asyncio.run(utils.dispatch_coro_if_exists(
            obj, "example_coro", ("test", "test"), {"test": "test"}
        ))

    def test_log_traceback(self):
        logging.basicConfig(level=logging.DEBUG)
        try:
            raise ValueError("test")
        except ValueError as e:
            utils.log_traceback()

        try:
            raise ValueError("test")
        except ValueError as e:
            try:
                utils.log_traceback(level=None)
            except TypeError as e:
                pass
            else:
                assert False

    def test_get(self):
        obj_list = [ExampleClass()]
        assert obj_list[0] == utils.get(obj_list, name="test")

    def test_safe_convert(self):
        assert 2 == utils.safe_convert(int, "2")
        assert "12" == utils.safe_convert(str, 12)
        assert "test" == utils.safe_convert(int, "x", "test")

        try:
            utils.safe_convert(int, "x")
        except ValueError as e:
            pass
        else:
            assert False

    def test_convertible(self):
        assert utils.convertible(int, "1")
        assert not utils.convertible(int, "x")
        assert not utils.convertible(int, None)

    def test_update_and_return(self):
        data = {
            "x": {
                "y"
            },
            "y": "x"
        }
        assert {"x": "y", "y": "x"} == utils.update_and_return(data, x="y")
