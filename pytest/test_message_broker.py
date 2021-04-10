import asyncio

import openhivenpy

token_ = ""


def test_start(token):
    global token_
    token_ = token


class TestDynamicEventBuffer:
    def test_init(self):
        buffer = openhivenpy.gateway.DynamicEventBuffer("ready")
        assert buffer.event == "ready"

    def test_add(self):
        buffer = openhivenpy.gateway.DynamicEventBuffer("ready")
        buffer.add({})
        assert buffer[0]['data'] == {}
        assert buffer[0]['args'] == ()
        assert buffer[0]['kwargs'] == {}

    def test_get_next_event(self):
        buffer = openhivenpy.gateway.DynamicEventBuffer("ready")
        buffer.add({})
        assert buffer[0]['data'] == {}
        assert buffer[0]['args'] == ()
        assert buffer[0]['kwargs'] == {}

        data = buffer.get_next_event()
        assert data['data'] == {}
        assert data['args'] == ()
        assert data['kwargs'] == {}


class TestMessageBroker:
    async def call(self, *args, **kwargs):
        pass

    async def run(self):
        client = openhivenpy.HivenClient()
        client.add_multi_listener("ready", self.call)  # <== only for testing
        message_broker = openhivenpy.gateway.MessageBroker(client)
        buffer = message_broker.get_buffer("ready")
        buffer.add({})
        
        async def test():
            await asyncio.sleep(.5)
            client.connection._connection_status = "CLOSING"

        client.connection._connection_status = "OPEN"
        await asyncio.gather(message_broker.run(), asyncio.wait_for(test(), 3))

    def test_init(self):
        client = openhivenpy.HivenClient()
        message_broker = openhivenpy.gateway.MessageBroker(client)
        assert message_broker.running is False

        dynamic_buffer = message_broker.get_buffer("ready")
        fetched_buffer = message_broker.get_buffer("ready")
        assert dynamic_buffer == fetched_buffer
        assert isinstance(dynamic_buffer, openhivenpy.gateway.DynamicEventBuffer)
        assert dynamic_buffer == message_broker.get_buffer("ready")

    def test_run(self):
        asyncio.run(self.run())


class TestWorker:
    def test_init(self):
        client = openhivenpy.HivenClient()
        message_broker = openhivenpy.gateway.MessageBroker(client)
        message_broker.get_buffer("ready")

        worker = message_broker.event_consumer.get_worker("ready")
        assert worker.event == "ready"
        assert worker.message_broker == message_broker
        assert worker.client == message_broker.client
        assert worker.assigned_event_buffer == message_broker.event_buffers['ready']

    def test_exec(self):
        pass

    def test_run_one_sequence(self):
        pass
