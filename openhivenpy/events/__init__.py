"""
Module that stores the EventListeners Methods, Parsers and Classes for
listening and reacting to WebSocket Events

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
import inspect
import logging
import sys
import time
from typing import Coroutine, Callable, Union, Dict, List, Awaitable, Optional, \
    Tuple
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from .event_parsers import HivenParsers
from .. import utils
from ..base_types import HivenObject
from ..exceptions import UnknownEventError

if TYPE_CHECKING:
    from ..gateway import MessageBroker
    from .. import HivenClient

__all__ = [
    'DispatchEventListener',
    'SingleDispatchEventListener',
    'HivenEventHandler',
    'HivenParsers',
    'EVENTS',
    'NON_BUFFER_EVENTS'
]

logger = logging.getLogger(__name__)

EVENTS = [
    'init', 'ready', 'user_update',
    'house_join', 'house_leave', 'house_update', 'house_delete', 'house_down',
    'room_create', 'room_update', 'room_delete',
    'house_member_join', 'house_member_leave',
    'house_member_online',
    'house_member_offline',
    'house_member_update',
    'house_member_chunk', 'batch_house_member_update',
    'house_entity_update',
    'relationship_update',
    'presence_update',
    'message_create', 'message_update', 'message_delete',
    'typing_start'
]

NON_BUFFER_EVENTS = [
    'init', 'ready'
]


class DispatchEventListener(HivenObject):
    """ Base Class for all DispatchEventListeners"""

    def __init__(
            self,
            client: HivenClient,
            event_name: str,
            awaitable: Union[Awaitable, Callable]
    ):
        self._client = client
        self._event_name = event_name
        self._awaitable: Optional[Awaitable] = None
        self.set_awaitable(awaitable)
        self._client.add_listener(self)

    def __str__(self):
        return f"<{self.__class__.__name__} for event {self.event_name}>"

    @property
    def awaitable(self) -> Union[Awaitable, Callable]:
        return getattr(self, '_awaitable', None)

    @property
    def client(self) -> HivenClient:
        return getattr(self, '_client', None)

    @property
    def event_name(self) -> str:
        return getattr(self, '_event_name', None)

    def __repr__(self):
        info = [
            ('event_name', getattr(self, 'event_name', None)),
            ('awaitable', getattr(self, 'awaitable', None))
        ]
        return '<MultiDispatchEventListener {}>'.format(
            ' '.join('%s=%s' % t for t in info)
        )

    def __call__(self, *args, **kwargs) -> Union[Coroutine, Awaitable]:
        """
        Returns the dispatch function of the class itself

        :param event_data: Data of the received event
        :param args: Args that will be passed to the coroutine
        :param kwargs: Kwargs that will be passed to the coroutine
        :return: The coroutine instance which can be used in an await
         expression or asyncio functions
        """
        dispatch: Union[Callable, Union[Awaitable, Callable]] = getattr(
            self, 'dispatch'
        )
        return dispatch(*args, **kwargs)

    def set_awaitable(self, awaitable: Union[Awaitable, Callable]) -> None:
        """
        Sets the coroutine of the event_listener, which will be called when
        ws-events are received

        :param awaitable: Awaitable (Coroutine Function). Can NOT be a
         initialised coroutine, since parameters will be passed on Runtime and
         coroutines are limited to a one-time execution. Coroutine functions
         or standard asyncio awaitable functions are defined using the
         `async def` syntax
        """
        if inspect.iscoroutine(awaitable):
            raise RuntimeError(
                "Coroutine are not allowed as event_listener awaitable")
        elif inspect.isawaitable(awaitable) or inspect.iscoroutinefunction(
                awaitable):
            self._awaitable = awaitable
        else:
            raise RuntimeError(f"Expected awaitable, but got {type(awaitable)}")

    async def dispatch(self) -> None:
        ...


class SingleDispatchEventListener(DispatchEventListener):
    """
    EventListener Class that will be called only once and will store the
    events data, args and kwargs
    """

    def __init__(self, client: HivenClient, event_name: str,
                 awaitable: Union[Awaitable, Callable]):
        self._dispatched = False
        self._event_data = None
        self._args = None
        self._kwargs = None
        super().__init__(client, event_name, awaitable)

    def __repr__(self):
        info = [
            ('event_name', getattr(self, 'event_name', None)),
            ('dispatched', self.dispatched),
            ('awaitable', getattr(self, 'awaitable', None))
        ]
        return '<SingleDispatchEventListener {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def dispatched(self) -> bool:
        return getattr(self, '_dispatched', False)

    @property
    def args(self) -> tuple:
        return getattr(self, '_args')

    @property
    def kwargs(self) -> dict:
        return getattr(self, '_kwargs')

    async def dispatch(self, *args, **kwargs) -> None:
        """
        Dispatches the EventListener and calls a coroutine if one was passed

        :param args: Args that will be passed to the coroutine
        :param kwargs: Kwargs that will be passed to the coroutine
        :return: Returns the passed event_data
        """
        try:
            self._args = args
            self._kwargs = kwargs
            await self.awaitable(*args, **kwargs)

        except Exception as e:
            utils.log_traceback(
                brief=f"[EVENTS] Ignoring exception in {repr(self)}:",
                exc_info=sys.exc_info()
            )
            raise RuntimeError(f"Failed to execute assigned coroutine '{self.awaitable.__name__}'") from e
        self._dispatched = True
        self.client.remove_listener(self)


class MultiDispatchEventListener(DispatchEventListener):
    """
    EventListener Class that is used primarily for EventListeners that will
    be called multiple times
    """

    async def dispatch(self, *args, **kwargs) -> None:
        """
        Dispatches the EventListener and calls a coroutine if one was passed.
        Does not raise exceptions but silences them!

        :param args: Args that will be passed to the coroutine
        :param kwargs: Kwargs that will be passed to the coroutine
        """
        try:
            await self.awaitable(*args, **kwargs)
        except Exception as e:
            utils.log_traceback(
                brief=f"[EVENTS] Ignoring exception in {repr(self)}:",
                exc_info=sys.exc_info()
            )
            raise RuntimeError(
                f"Failed to execute assigned coroutine "
                f"'{self.awaitable.__name__}'"
            ) from e


class HivenEventHandler(HivenObject):
    """
    Events class used to register the main event listeners.
    Is inherited by the HivenClient for easier access.
    """

    def __init__(self, client: HivenClient, parsers: HivenParsers):
        self.parsers = parsers
        self._client = client
        self._active_listeners = {}
        self._available_events = EVENTS
        self._non_buffer_events = NON_BUFFER_EVENTS

        # Searching through the HivenClient to find all async functions that
        # were registered for event_listening Regular functions will NOT be
        # registered and only if they are async! This will avoid that errors
        # are thrown when trying to call the functions using 'await'
        for listener in inspect.getmembers(
                self, predicate=inspect.iscoroutinefunction
        ):
            func_name = listener[0].replace('on_', '')
            awaitable = listener[1]
            if func_name in self._available_events:
                self.add_multi_listener(func_name, awaitable)
                logger.debug(f"[EVENTS] Event {listener[0]} registered")

    @property
    def active_listeners(self) -> Dict[str, List[DispatchEventListener]]:
        return getattr(self, '_active_listeners', None)

    @property
    def available_events(self) -> List[str]:
        return getattr(self, '_available_events', None)

    @property
    def non_buffer_events(self) -> List[str]:
        return getattr(self, '_non_buffer_events', None)

    def _validate_existence_of_event(self, name: str):
        if name.replace('on_', '') not in self.available_events:
            raise UnknownEventError(
                "The passed event type is invalid/does not exist"
            )

    def cleanup_listeners(self) -> None:
        """ Cleanups the listeners and empties all active listeners """
        self._active_listeners = {}

    def dispatch_event(
            self, event_name: str, args: tuple, kwargs: dict
    ) -> None:
        """
        Manually adds an event to the event_buffer and triggers all listeners.
        Will return immediately and does not require asyncio unlike
        call_listeners which only calls the listeners;

        Note that this will NOT call the event parsers but manually directly
        pass the args and kwargs to the functions!

        :param event_name: The name of the event that should be triggered
        :param args: Args that will be passed to the coroutines
        :param kwargs: Kwargs that will be passed to the coroutines
        """
        self._validate_existence_of_event(event_name)

        _: MessageBroker = getattr(self, 'message_broker')
        buffer = _.get_buffer(event_name)
        buffer.add_new_event(
            {
                "callee": event_name,
                "caller": "client",
                "time": time.time()
            },
            args,
            kwargs
        )

    def add_listener(self, listener: DispatchEventListener) -> None:
        """
        Adds the listener to the client cache and will create a new list if
         the event_name does not exist yet!

        :param listener: The Listener that will be added
        """
        if self.active_listeners.get(listener.event_name):
            self.active_listeners[listener.event_name].append(listener)
        else:
            self.active_listeners[listener.event_name] = [listener]

    def remove_listener(self, listener: DispatchEventListener) -> None:
        """
        Removes the listener from the client cache

        :param listener: The Listener that will be removed
        :raises KeyError: If the listener does not exist in the cache
        """
        if self.active_listeners.get(listener.event_name):
            self.active_listeners[listener.event_name].remove(listener)
        else:
            raise KeyError("The listener does not exist in the cache")

    async def call_listeners(
            self, event_name: str, args: tuple, kwargs: dict
    ) -> None:
        """
        Dispatches all active EventListeners for the specified event.
        Does not call the parsers but the function directly and requires the
        args, kwargs passed

        Will run all tasks before returning! Only supposed to be called in
        cases of special events!

        :param event_name: The name of the event that should be triggered
        :param args: Args that will be passed to the coroutines
        :param kwargs: Kwargs that will be passed to the coroutines
        """
        listeners: List[DispatchEventListener] = self._active_listeners.get(
            event_name.lower().replace('on_', '')
        )
        if listeners:
            tasks = [listener(*args, **kwargs) for listener in listeners]
            await asyncio.gather(*tasks)

    async def wait_for(
            self,
            event_name: str,
            awaitable: Union[Callable, Coroutine, None] = None
    ) -> Tuple[tuple, dict]:
        """
        Waits for an event to be triggered and then returns the *args and
        **kwargs passed

        :param event_name: Name of the event to wait for
        :param awaitable: Coroutine that can be passed to be additionally
         triggered when received
        :raises UnknownEventError: If the event does not exist
        :return: A tuple of the args and kwargs => (args, kwargs)
        """
        event_name = event_name.replace('on_', '')
        if event_name not in self.available_events:
            raise UnknownEventError(
                "The passed event type is invalid/does not exist"
            )

        listener = self.add_single_listener(event_name, awaitable)
        while not listener.dispatched:
            await asyncio.sleep(.05)

        return listener.args, listener.kwargs

    def event(self, awaitable: Union[Callable, Coroutine] = None) -> Callable:
        """
        Decorator used for registering Client Events

        :param awaitable: Function that should be wrapped and registered
        """

        def decorator(awaitable: Union[Callable, Coroutine]) -> Callable:
            if not inspect.iscoroutinefunction(awaitable):
                raise TypeError(
                    f"A coroutine was expected, got {type(awaitable)}"
                )

            self._validate_existence_of_event(awaitable.__name__)

            func_name = awaitable.__name__.replace('on_', '')
            self.add_multi_listener(func_name, awaitable)
            logger.debug(f"[EVENTS] Event {func_name} registered")

            # func can still be used normally outside the event listening
            # process
            return awaitable

        if awaitable is None:
            return decorator
        else:
            return decorator(awaitable)

    def add_multi_listener(
            self,
            event_name: str,
            awaitable: Union[Callable, Awaitable]
    ) -> MultiDispatchEventListener:
        """
        Adds a new event listener to the list of active listeners

        :param event_name: The key/name of the event the EventListener should
          be listening to
        :param awaitable: Coroutine that should be called when the
         EventListener was dispatched
        :return: The newly created EventListener
        """
        event_name = event_name.replace('on_', '')
        if event_name not in self.available_events:
            raise UnknownEventError(
                "The passed event type is invalid/does not exist"
            )

        if self._active_listeners.get(event_name) is None:
            self._active_listeners[event_name] = []

        return MultiDispatchEventListener(self._client, event_name, awaitable)

    def add_single_listener(
            self,
            event_name: str,
            awaitable: Union[Callable, Coroutine]
    ) -> SingleDispatchEventListener:
        """
        Adds a new single dispatch event listener to the list of active
        listeners

        :param event_name: The key/name of the event the EventListener should
         be listening to
        :param awaitable: Coroutine that should be called when the
         EventListener was dispatched
        :return: The newly created EventListener
        """
        event_name = event_name.replace('on_', '')
        if event_name not in self.available_events:
            raise UnknownEventError(
                "The passed event type is invalid/does not exist"
            )

        if self._active_listeners.get(event_name) is None:
            self._active_listeners[event_name] = []

        return SingleDispatchEventListener(self._client, event_name, awaitable)
