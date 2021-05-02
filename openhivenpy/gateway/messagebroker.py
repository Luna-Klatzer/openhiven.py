# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import asyncio
import logging
from typing import Optional, List, NoReturn, Coroutine, Tuple
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from .. import utils, Object

if TYPE_CHECKING:
    from .. import HivenClient
    from ..exceptions import EventConsumerLoopError
    from ..events import DispatchEventListener

__all__ = ['DynamicEventBuffer', 'MessageBroker']

logger = logging.getLogger(__name__)


class DynamicEventBuffer(list, Object):
    """
    The DynamicEventBuffer is a list containing all not-executed events that were received over the websocket.
    Workers will fetch from the Buffer events and then execute them if event_listeners are assigned to them.
    """

    def __init__(self, event: str, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def __repr__(self):
        info = [
            ('event', self.event)
        ]
        return '<{} {}>'.format(self.__class__.__name__, ' '.join('%s=%s' % t for t in info))

    def add(self, data: dict, args: Optional[tuple] = None, kwargs: Optional[dict] = None):
        """Adds a new event to the Buffer which will trigger the listeners assigned to the event

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
        """ Fetches the oldest event at index 0. Raises an exception if the buffer is empty! """
        return self.pop(0)


class MessageBroker(Object):
    """ Message Broker that will store the messages in queues """

    def __init__(self, client: HivenClient):
        self.event_buffers = {}
        self.client = client
        self.event_consumer = EventConsumer(self)
        self.worker_loop: Optional[asyncio.Task] = None

    @property
    def running(self) -> bool:
        if self.worker_loop:
            return not getattr(self.worker_loop, 'done')()
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

    def get_buffer(self, event: str,
                   args: Optional[tuple] = None,
                   kwargs: Optional[dict] = None) -> DynamicEventBuffer:
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
        """ Runs the event_consumer instance which stores the workers for all event_listeners """
        self.worker_loop = asyncio.create_task(self.event_consumer.run_all_workers())
        try:
            await self.worker_loop
        except asyncio.CancelledError:
            logger.debug("Event Consumer stopped! All workers are cancelled!")
        except Exception as e:
            raise EventConsumerLoopError("The event_consumer process loop failed to be kept alive") from e


class Worker(Object):
    """ Worker class targeted at running event_listeners that were fetched from the assigned event_buffer """

    def __init__(self, event: str, message_broker):
        self.assigned_event = event
        self.message_broker: MessageBroker = message_broker
        self.client: HivenClient = message_broker.client
        self._task: Optional[asyncio.Task] = None

    def __repr__(self):
        info = [
            ('event', self.assigned_event),
        ]
        return '<{} {}>'.format(self.__class__.__name__, ' '.join('%s=%s' % t for t in info))

    @property
    def assigned_event_buffer(self) -> DynamicEventBuffer:
        return self.message_broker.event_buffers.get(self.assigned_event)

    @property
    def _closing(self) -> bool:
        return getattr(self.client.connection, '_closing', False)

    async def _gather_tasks(self, tasks: List[Coroutine]) -> NoReturn:
        """ Executes all passed event_listener tasks parallel """
        await asyncio.gather(*tasks)

    async def _wait_for_closing(self) -> NoReturn:
        """ Loops until the closing call is received which will destroy the currently running loop """
        while True:
            if self._closing:
                if not self._task.cancelled():
                    self._task.cancel()
                return
            await asyncio.sleep(1)

    async def _loop_sequence(self) -> NoReturn:
        # Unless the closing signal is received inside the client it will run forever
        while self._closing is not True:
            # If the event_buffer is not empty
            if self.assigned_event_buffer:
                await self.run_one_sequence()
            await asyncio.sleep(.50)

    @utils.wrap_with_logging
    async def run_forever(self) -> Tuple:
        """
        Runs a while loop where the worker will wait for events and call the listeners when received
        Does not return until the client received the close call!
        """
        # Unless the closing signal is received inside the client it will run forever
        self._task = asyncio.create_task(self._loop_sequence())
        return await asyncio.gather(self._wait_for_closing(), self._loop_sequence())

    @utils.wrap_with_logging
    async def run_one_sequence(self):
        """ Fetches an event from the buffer and runs all assigned event listeners """
        if self.assigned_event_buffer:
            # Fetching the even data for the next event
            event: dict = self.assigned_event_buffer.get_next_event()

            listeners: List[DispatchEventListener] = self.client.active_listeners.get(self.assigned_event)

            # If no listeners exists it will just return
            if not listeners:
                return

            args = event['args']  # args to pass to the coro
            kwargs = event['kwargs']  # kwargs to pass to the coro

            try:
                # Creating a new task for every active listener
                tasks: List[Coroutine] = [listener(*args, **kwargs) for listener in listeners]

                # if queue_events is active running a sequence will not return until all event_listeners were dispatched
                if self.client.queue_events:
                    await self._gather_tasks(tasks)
                else:
                    # without queuing all tasks will be assigned to the asyncio event_loop and run parallel
                    asyncio.create_task(self._gather_tasks(tasks))

            except asyncio.CancelledError:
                logger.debug(f"Worker {repr(self)} was cancelled and did not finish its tasks!")
            except Exception as e:
                self.assigned_event_buffer.add(**event)
                raise RuntimeError(f"Failed to run listener tasks assigned to {repr(self)}") from e


class EventConsumer(Object):
    """ EventConsumer class which will simply manage the workers on runtime """

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

    async def run_all_workers(self) -> tuple:
        """
        Creates workers for all available events and runs them parallel
        *non_buffer_events* in this case are ignored since they are non-websocket events and need to be called using
        call_listeners. Those tasks will not be running parallel but will be called in the websocket task and delay
        the websocket receiving process, so that startup can be easier managed (on_init, on_ready)
        """
        workers = [
            self.get_worker(_) for _ in self.client.available_events if _ not in self.client.non_buffer_events
        ]
        tasks = [worker.run_forever() for worker in workers]
        return await asyncio.gather(*tasks)
