import asyncio
import inspect

import pytest

import openhivenpy

token_ = ""
client = openhivenpy.HivenClient()


def test_start(token):
    global token_
    token_ = token


class TestSingleDispatchEventListener:
    example_args = ['test']
    example_kwargs = {'test': 'test'}

    async def example(self, *args, **kwargs):
        assert args[0] == 'test'
        assert kwargs.pop('test') == 'test'

    def test_dispatch_without_coro(self):
        try:
            openhivenpy.events.MultiDispatchEventListener(client, 'test', None)
        except Exception:
            pass
        else:
            assert False

    def test_dispatch_with_coro(self):
        listener = openhivenpy.events.SingleDispatchEventListener(client, 'test', self.example)
        asyncio.run(listener.dispatch(*self.example_args, **self.example_kwargs))

    def test_call(self):
        listener = openhivenpy.events.SingleDispatchEventListener(client, 'test', self.example)

        coro = listener(*self.example_args, **self.example_kwargs)
        assert inspect.iscoroutine(coro)
        asyncio.run(coro)

    def test_get_attribute(self):
        listener = openhivenpy.events.SingleDispatchEventListener(client, 'test', self.example)

        assert listener.awaitable == self.example
        assert listener.event_name == 'test'
        assert listener._client == client
        assert openhivenpy.utils.get(client._active_listeners['test'], awaitable=self.example) is not None

        asyncio.run(listener(*self.example_args, **self.example_kwargs))
        assert listener.dispatched
        assert list(listener.args) == self.example_args
        assert listener.kwargs == self.example_kwargs
        assert openhivenpy.utils.get(client._active_listeners['test'], awaitable=self.example) is None


class TestMultiDispatchEventListener:
    example_args = ['test']
    example_kwargs = {'test': 'test'}

    async def example(self, *args, **kwargs):
        assert args[0] == 'test'
        assert kwargs.pop('test') == 'test'

    def test_dispatch_without_coro(self):
        try:
            openhivenpy.events.MultiDispatchEventListener(client, 'test', None)
        except Exception:
            pass
        else:
            assert False

    def test_dispatch_with_coro(self):
        listener = openhivenpy.events.MultiDispatchEventListener(client, 'test', self.example)
        asyncio.run(listener.dispatch(*self.example_args, **self.example_kwargs))

    def test_call(self):
        listener = openhivenpy.events.MultiDispatchEventListener(client, 'test', self.example)

        coro = listener(*self.example_args, **self.example_kwargs)
        assert inspect.iscoroutine(coro)
        asyncio.run(coro)

    def test_get_attribute(self):
        listener = openhivenpy.events.MultiDispatchEventListener(client, 'test', self.example)

        assert listener.awaitable == self.example
        assert listener.event_name == 'test'
        assert listener._client == client
        assert openhivenpy.utils.get(client._active_listeners['test'], awaitable=self.example) is not None


class TestHivenEventHandler:
    def test_init(self):
        # Creating a new Client to avoid possible different results by using
        # older ones
        global client
        client = openhivenpy.UserClient()

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        assert len(client._active_listeners['ready']) == 1

        client.run(token_)

    @pytest.mark.parametrize(
        "args,kwargs", [
            (("1", "2"), {"1": "1", "2": "2"}),
            ((), {"1": "1", "2": "2"}),
            (("1", "2"), {})
        ]
    )
    def test_dispatch_event(self, args: tuple, kwargs: dict):
        global client
        client = openhivenpy.UserClient()

        @client.event()
        async def on_message_create(*args, **kwargs):
            assert args == args
            assert kwargs == kwargs
            await client.close()

        @client.event()
        async def on_ready():
            client.dispatch_event(
                'message_create', args, kwargs
            )
            assert client.message_broker.get_buffer("message_create")

        client.run(token_)

    def test_dispatch_event_wrong_event(self):
        global client
        client = openhivenpy.UserClient()

        @client.event()
        async def on_ready():
            try:
                client.dispatch_event(
                    'x', (), {}
                )
            except Exception:
                await client.close()
            else:
                assert False, "Expected exception"

        client.run(token_)

    def test_wait_for(self):
        async def on_ready():
            print("\non_ready was called!")
            return

        async def trigger_test_event():
            await asyncio.sleep(.5)
            await client.call_listeners('ready', (), {})

        async def run():
            await asyncio.gather(
                trigger_test_event(),
                client.wait_for('on_ready', awaitable=on_ready)
            )

        asyncio.run(run())

    def test_add_new_multi_event_listener(self):
        async def on_ready():
            print("\non_ready was called!")
            return

        async def trigger_test_event():
            await asyncio.sleep(.5)
            await client.call_listeners('ready', (), {})

        async def run():
            await asyncio.gather(
                trigger_test_event(),
                client.wait_for('on_ready', awaitable=on_ready)
            )

        asyncio.run(run())

    def test_add_new_single_event_listener(self):
        async def on_ready():
            print("\non_ready was called!")
            return

        async def trigger_test_event():
            await asyncio.sleep(.5)
            await client.call_listeners('ready', (), {})

        async def run():
            assert len(client.active_listeners['ready']) == 0

            client.add_single_listener(event_name='ready', awaitable=on_ready)
            # Checking if the listener was added correctly
            assert len(client.active_listeners['ready']) == 1

            await trigger_test_event()
            # Checking if the listener was removed correctly after being used
            assert len(client.active_listeners['ready']) == 0

        asyncio.run(run())
