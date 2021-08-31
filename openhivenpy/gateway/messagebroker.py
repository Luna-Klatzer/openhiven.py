"""
Message-Broker module which manages events, buffers and executes events using
workers. Simple workflow of such handling:

Web-Socket event --> Event Parser --> Adding to Buffer (waiting list) -->
Worker fetching from Buffer --> Calling all listeners

---

Under MIT License

Copyright © 2020 - 2021 Luna Klatzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import asyncio
import logging
from typing import Optional, List, Coroutine, Tuple, Dict
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from .. import utils
from ..base_types import HivenObject

if TYPE_CHECKING:
    from .. import HivenClient
    from ..exceptions import EventConsumerLoopError, WorkerTaskError
    from ..events import DispatchEventListener

__all__ = ['DynamicEventBuffer', 'MessageBroker']

logger = logging.getLogger(__name__)


async def _wait_until_done(task: asyncio.Task) -> None:
    """ Waits until the passed task is done and then returns """
    while not task.done():
        await asyncio.sleep(.05)


class DynamicEventBuffer(list, HivenObject):
    """
    The DynamicEventBuffer is a list containing all not-executed events that
    were received over the websocket.

    Workers will fetch from the Buffer events and then execute them if
    event_listeners are assigned to them.
    """

    def __init__(self, event: str, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def __repr__(self):
        info = [
            ('event', self.event)
        ]
        return '<{} {}>'.format(self.__class__.__name__,
                                ' '.join('%s=%s' % t for t in info))

    def add_new_event(
            self,
            data: dict,
            args: Optional[tuple] = None,
            kwargs: Optional[dict] = None
    ):
        """
        Adds a new event to the Buffer which will trigger the listeners
        assigned to the event

        :param data: The raw WebSocket data containing the information of the
         event
        :param args: Args of the Event that should be passed to the event
         listeners
        :param kwargs: Kwargs / named args of the Event that should be passed
         to the event listeners
        """
        if kwargs is None:
            kwargs: Dict = {}
        if args is None:
            args: Tuple = ()
        self.append(
            {
                'data': data,
                'args': args,
                'kwargs': kwargs
            }
        )

    def get_next_event(self) -> dict:
        """
        Fetches the oldest event at index 0. Raises an exception if the buffer
        is empty!
        """
        return self.pop(0)


class MessageBroker(HivenObject):
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

    @property
    def _force_closing(self) -> bool:
        return getattr(self.client.connection, '_force_closing', False)

    def create_buffer(self, event: str, args, kwargs) -> DynamicEventBuffer:
        """
        Creates a new EventBuffer which stores events that will trigger
        event_listener

        :param event: The event name
        :param args: Args that should be passed for the creation of the buffer
        :param kwargs: Kwargs that should be passed for the creation of the
         buffer
        :return: The newly created Buffer
        """
        new_buffer = DynamicEventBuffer(event, *args, **kwargs)
        self.event_buffers[event] = new_buffer
        return new_buffer

    def get_buffer(self, event: str,
                   args: Optional[tuple] = None,
                   kwargs: Optional[dict] = None) -> DynamicEventBuffer:
        """
        Tries to fetch a buffer from the cache. If the buffer is not found a
        new one will be created

        :param event: The event name
        :param args: Args that should be passed for the creation of the buffer
         if it's not found
        :param kwargs: Kwargs that should be passed for the creation of the
         buffer if it's not found
        :return: The fetched or newly created buffer instance
        """
        if kwargs is None:
            kwargs: Dict = {}
        if args is None:
            args: Tuple = ()

        buffer = self.event_buffers.get(event)
        if buffer is not None:
            return buffer
        else:
            return self.create_buffer(event, args, kwargs)

    def _cleanup_buffers(self) -> None:
        """ Removes all buffers and their content to """
        del self.event_buffers
        self.event_buffers = {}

    async def close_loop(self) -> None:
        """ Closes the worker_loop and its tasks """
        if self._force_closing:
            await self.event_consumer.close()

            if self.worker_loop.cancelled():
                return
            self.worker_loop.cancel()
            await _wait_until_done(self.worker_loop)

        else:
            await _wait_until_done(self.worker_loop)
            # Despite not being force_closed all tasks and workers will still be removed and a cleanup started, but
            # only after all workers have finished to avoid destroying event_listeners in their execution
            await self.event_consumer.close()

        self._cleanup_buffers()

    async def run(self) -> None:
        """
        Runs the event_consumer instance which stores the workers for all
        event_listeners
        """
        self.worker_loop = asyncio.create_task(
            self.event_consumer.run_all_workers()
        )
        try:
            await self.worker_loop
        except asyncio.CancelledError:
            logger.debug("Event Consumer stopped! All workers are cancelled!")
        except Exception as e:
            raise EventConsumerLoopError(
                "The event_consumer process loop failed to be kept alive"
            ) from e


class Worker(HivenObject):
    """
    Worker class targeted at running event_listeners that were fetched from
    the assigned event_buffer
    """

    def __init__(self, event: str, message_broker):
        self.assigned_event = event
        self.message_broker: MessageBroker = message_broker
        self.client: HivenClient = message_broker.client
        self._sequence_loop: Optional[asyncio.Task] = None
        self._listener_tasks: List[asyncio.Task] = []
        self._cancel_called = False

    def __repr__(self):
        info = [
            ('event', self.assigned_event),
            ('done', self.done())
        ]
        return '<{} {}>'.format(
            self.__class__.__name__, ' '.join('%s=%s' % t for t in info)
        )

    @property
    def assigned_event_buffer(self) -> DynamicEventBuffer:
        """ The assigned event buffer to the worker """
        return self.message_broker.event_buffers.get(self.assigned_event)

    @property
    def closing(self) -> bool:
        """ Returns whether the client connection is currently closing """
        return getattr(self.client.connection, '_closing', False)

    @property
    def force_closing(self) -> bool:
        """ Returns whether force_closing is enabled in the message_broker """
        return getattr(self.message_broker, '_force_closing', False)

    async def _gather_tasks(self, tasks: List[Coroutine]) -> None:
        """ Executes all passed event_listener tasks parallel """
        await asyncio.gather(*tasks)

    def done(self) -> bool:
        """
        Returns whether the process is finished and all tasks finished
        correctly. If it hasn't started yet it will also return False
        """
        return all([
            self._tasks_done,
            self._sequence_loop.done() if self._sequence_loop else False,
            self._cancel_called
        ])

    async def cancel(self) -> None:
        """
        Cancels all tasks in the current worker and the main loop that was
        started using run_forever()
        """
        for task in self._listener_tasks:
            if task.done():  # already done or cancelled
                continue

            task.cancel()
            await _wait_until_done(task)

        if not self._sequence_loop.cancelled():
            self._sequence_loop.cancel()
            await _wait_until_done(self._sequence_loop)

        self._cancel_called = True
        logger.debug(f"{repr(self)} cancelled")

    def _tasks_done(self) -> bool:
        return all(t.done() for t in self._listener_tasks)

    async def _wait_until_finished(self) -> None:
        """ Waits until all tasks have finished """
        while True:
            if self._tasks_done():
                return

            await asyncio.sleep(.05)

    async def _loop_sequence(self) -> None:
        """
        Worker Loop sequence. Only stops when connection.close() was called
        """
        while not self.closing:
            # If the event_buffer is not empty
            if self.assigned_event_buffer:
                await self.run_one_sequence()
            await asyncio.sleep(.50)

        if self.force_closing:
            await self.cancel()  # destroys itself
        else:
            await self._wait_until_finished()

    @utils.wrap_with_logging
    async def run_forever(self) -> Tuple:
        """
        Runs a while loop where the worker will wait for events and call the
        listeners when received.
        Does not return until the client received the close call!
        """
        # Unless the closing signal is received inside the client it will run
        # forever
        self._sequence_loop = asyncio.create_task(self._loop_sequence())
        try:
            return await self._sequence_loop
        except asyncio.CancelledError:
            pass
        except Exception as e:
            raise WorkerTaskError(f"{repr(self)} failed to run") from e

    @utils.wrap_with_logging
    async def run_one_sequence(self):
        """
        Fetches an event from the buffer and runs all assigned event listeners
        """
        if self.assigned_event_buffer:
            # Fetching the even data for the next event
            event: dict = self.assigned_event_buffer.get_next_event()

            listeners: List[
                DispatchEventListener] = self.client.active_listeners.get(
                self.assigned_event)

            # If no listeners exists it will just return
            if not listeners:
                return

            args: Tuple = event['args']  # args to pass to the coro
            kwargs = event['kwargs']  # kwargs to pass to the coro

            try:
                # Creating a new task for every active listener
                tasks: List[Coroutine] = [
                    listener(*args, **kwargs) for listener in listeners
                ]

                # if queue_events is active running a sequence will not return
                # until all event_listeners were dispatched
                if self.client.queue_events:
                    task = asyncio.create_task(self._gather_tasks(tasks))
                    self._listener_tasks.append(task)
                    await task
                else:
                    # without queuing all tasks will be assigned to the asyncio
                    # event_loop and run parallel
                    task = asyncio.create_task(self._gather_tasks(tasks))
                    self._listener_tasks.append(task)

            except asyncio.CancelledError:
                logger.debug(
                    f"Worker {repr(self)} was cancelled and "
                    f"did not finish its tasks!"
                )
            except Exception as e:
                self.assigned_event_buffer.add_new_event(**event)
                raise RuntimeError(
                    f"Failed to run listener tasks assigned to {repr(self)}"
                ) from e


class EventConsumer(HivenObject):
    """ EventConsumer class which will simply manage the workers on runtime """

    def __init__(self, message_broker: MessageBroker):
        self.workers: Dict[Worker] = {}
        self.message_broker = message_broker
        self.client = message_broker.client
        self._tasks: Optional[Dict[Worker, asyncio.Task]] = {}

    def get_worker(self, event) -> Worker:
        """ Creates a new worker that can execute event_listeners """
        worker = self.workers.get(event)

        # Avoids cancelled workers that cannot be reused
        if not worker or getattr(worker, '_cancel_called', False) is True:
            worker = Worker(event, self.message_broker)
            self.workers[event] = worker
        return worker

    def tasks_done(self) -> bool:
        """
        Returns whether all workers and tasks are done
        (cancelled, raised an exception or finished)
        """
        return all([
            *(t.done() for t in self._tasks.values()),
            *(w.done() for w in self.workers.values())
        ])

    async def close(self) -> None:
        """
        Closes all worker tasks that are currently running. Waits until
        everything was cleaned up and finished
        """
        for w in self.workers.values():
            w: Worker
            if w.done():
                continue

            await w.cancel()

        for t in self._tasks.values():
            t: asyncio.Task
            if t.done():
                continue

            t.cancel()

        # Waiting until all workers and tasks were really finished and
        # everything is cleaned up
        while not self.tasks_done():
            await asyncio.sleep(.05)

        logger.debug(f"All workers and tasks of {repr(self)} were cancelled")

        self._cleanup()

    def _cleanup(self) -> None:
        """ Removes all workers and removes the data that still exists """
        del self.workers
        self.workers = {}

        del self._tasks
        self._tasks = {}

    async def run_all_workers(self) -> tuple:
        """
        Creates workers for all available events and runs them parallel
        *non_buffer_events* in this case are ignored since they are
        non-websocket events and need to be called using call_listeners. Those
        tasks will not be running parallel but will be called in the websocket
        task and delay the websocket receiving process, so that startup can be
         easier managed (on_init, on_ready)
        """
        workers = [
            self.get_worker(_) for _ in self.client.available_events if _ not in self.client.non_buffer_events
        ]
        self._tasks: Optional[Dict[Worker, asyncio.Task]] = {
            worker: asyncio.create_task(worker.run_forever()) for worker in workers
        }
        return await asyncio.gather(*self._tasks.values())
