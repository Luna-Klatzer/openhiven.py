import asyncio
import logging

from .. import utils

__all__ = ['DynamicEventBuffer', 'MessageBroker']

logger = logging.getLogger(__name__)


class DynamicEventBuffer(list):
    def __init__(self, event: str, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def add(self, data: dict, args: tuple = None, kwargs: dict = None):
        """
        Adds a new event to the Buffer which will trigger the listeners assigned to the event

        :param data: The raw WebSocket data containing the information of the event
        :param args: Args of the Event that should be passed to the event listeners
        :param kwargs:
        """
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = ()
        self.append(
            {
                'data': data,
                'args': args,
                'kwargs': kwargs
            }
        )

    def get_next_event(self) -> dict:
        """ Fetches the event at index 0. Raises an exception if the buffer is empty! """
        return self.pop(0)


class MessageBroker:
    """ Message Broker that will store the messages in queues """
    def __init__(self, client):
        self.event_buffers = {}
        self.client = client
        self.event_consumer = EventConsumer(self)
        self.running_loop = None

    @property
    def running(self):
        if self.running_loop:
            return not getattr(self.running_loop, 'done')()
        else:
            return False

    def create_buffer(self, event: str, args, kwargs) -> DynamicEventBuffer:
        """
        Creates a new EventBuffer which stores events that will trigger event_listener

        :param event: The event name
        :param args: Args that should be passed for the creation of the buffer
        :param kwargs: Kwargs that should be passed for the creation of the buffer
        :return: The newly created Buffer
        """
        new_buffer = DynamicEventBuffer(event, *args, **kwargs)
        self.event_buffers[event] = new_buffer
        return new_buffer

    def get_buffer(self, event: str, args: tuple = None, kwargs: dict = None) -> DynamicEventBuffer:
        """
        Tries to fetch a buffer from the cache. If the buffer is not found a new one will be created

        :param event: The event name
        :param args: Args that should be passed for the creation of the buffer if it's not found
        :param kwargs: Kwargs that should be passed for the creation of the buffer if it's not found
        :return: The fetched or newly created buffer instance
        """
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = ()

        buffer = self.event_buffers.get(event)
        if buffer is not None:
            return buffer
        else:
            return self.create_buffer(event, args, kwargs)

    async def run(self):
        """ Runs the Event Consumer instance which stores the workers for all event_listeners """
        self.running_loop = asyncio.create_task(self.event_consumer.process_loop())
        await self.running_loop


class Worker:
    """ Worker class that runs the Event Listeners"""
    def __init__(self, event: str, message_broker):
        self.event = event
        self.message_broker = message_broker
        self.client = message_broker.client

    @property
    def event_buffer(self):
        return self.message_broker.event_buffers.get(self.event)

    async def gather_tasks(self, tasks):
        """ Executes all passed event_listener tasks parallel """
        await asyncio.gather(*tasks)

    async def run_forever(self):
        """
        Runs a loop where the worker will wait for the next event that is received.
        Does not return until the client received the close call!
        """
        # Unless the closing signal is received inside the client it will run forever
        while self.client.connection_status not in ("CLOSING", "CLOSED"):
            # If the event_buffer is not empty => not False
            if self.event_buffer:
                await self.run_one_sequence()
            await asyncio.sleep(.075)

    @utils.wrap_with_logging
    async def run_one_sequence(self):
        """ Fetches an event from the buffer and runs all assigned Event Listeners """
        if self.event_buffer:
            # Fetching the even data for the next event
            event = self.event_buffer.get_next_event()

            listeners = self.client.active_listeners.get(self.event)
            # If listeners are present they will be called
            if listeners:
                data = event['data']  # raw received websocket data
                args = event['args']  # args to pass to the coro
                kwargs = event['kwargs']  # kwargs to pass to the coro

                # Creating a new task for every active listener
                tasks = [utils.wrap_with_logging(e)(data, *args, **kwargs) for e in listeners]

                # if queue_events is active running a sequence will not return until all event_listeners were dispatched
                if self.client.queue_events:
                    await self.gather_tasks(tasks)
                else:
                    # without queue_events all tasks will be assigned to the asyncio event_loop and the function will return
                    asyncio.create_task(self.gather_tasks(tasks))


class EventConsumer:
    """ Dispatcher which will fetch events and execute them in a loop """
    def __init__(self, message_broker):
        self.workers = {}
        self.message_broker = message_broker
        self.client = message_broker.client

    def get_worker(self, event) -> Worker:
        """ Creates a new worker that can execute event_listeners """
        worker = self.workers.get(event)
        if not worker:
            worker = Worker(event, self.message_broker)
            self.workers[event] = worker
        return worker

    async def process_loop(self):
        # Creating an worker for every available event that can be received
        workers = [
             asyncio.create_task(self.get_worker(_).run_forever()) for _ in self.client.available_events
        ]
        await asyncio.gather(*workers)
