import logging
from functools import wraps

from openhivenpy.utils import dispatch_func_if_exists

logger = logging.getLogger(__name__) 


class EventHandler:
    """`openhivenpy.events.EventHandler` 
    
    Openhivenpy Event Handler
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Event Handler for the HivenClient Class. Functions will be called from the
    websocket class and if the user registered an event response with the
    decorator @HivenClient.event, it will be called and executed.
    
    """
    def __init__(self, call_obj: object = None):
        self._call_obj = call_obj
        if self._call_obj is None:
            logger.debug("[EVENT-HANDLER] Passed object where the events should be called from is None!")
            self._call_obj = self

    def event(self, func=None):
        """`openhivenpy.events.Events.event`
        
        Decorator used for registering Client Events
        
        Parameter:
        ----------
        
        func: `function` - Function that should be wrapped. Only usable if the wrapper is
                            used in the function syntax: 'event(func)'!
        
        """
        def decorator(func):
            @wraps(func) 
            async def wrapper(*args, **kwargs): 
                return await func(*args, **kwargs)
            
            setattr(self, func.__name__, wrapper)  # Adding the function to the object

            logger.debug(f"[EVENT-HANDLER] >> Event {func.__name__} registered")

            return func  # returning func means func can still be used normally

        if func is None:
            return decorator
        else:
            return decorator(func)

    async def dispatch_on_connection_start(self) -> None:
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_connection_start'
        )

    async def dispatch_on_init(self, time) -> None:
        param = [time]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_init',
            func_args=param
        )

    async def dispatch_on_ready(self) -> None:
        param = []
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_ready',
            func_args=param
        )

    async def dispatch_on_house_add(self, house) -> None:
        param = [house]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_house_join',
            func_args=param
        )

    async def dispatch_on_house_remove(self, house) -> None:
        param = [house]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_house_remove',
            func_args=param
        )

    async def dispatch_on_house_delete(self, house_id) -> None:
        param = [house_id]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_house_delete',
            func_args=param
        )

    async def dispatch_on_house_down_time(self, house_id) -> None:
        param = [house_id]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_house_downtime',
            func_args=param
        )

    async def dispatch_on_room_create(self, room) -> None:
        param = [room]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_room_create',
            func_args=param
        )

    async def dispatch_on_house_member_join(self, member, house) -> None:
        param = [member, house]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_house_member_join',
            func_args=param
        )

    async def dispatch_on_house_member_enter(self, member, house) -> None:
        param = [member, house]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_house_member_online',
            func_args=param
        )

    async def dispatch_on_house_member_leave(self, member, house) -> None:
        param = [member, house]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_house_member_leave',
            func_args=param
        )

    async def dispatch_on_house_member_exit(self, member, house) -> None:
        param = [member, house]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_house_member_offline',
            func_args=param
        )

    async def dispatch_on_relationship_update(self, relationship) -> None:
        param = [relationship]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_relationship_update',
            func_args=param
        )

    async def dispatch_on_presence_update(self, presence, user) -> None:
        param = [presence, user]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_presence_update',
            func_args=param
        )

    async def dispatch_on_message_create(self, message) -> None:
        param = [message]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_message_create',
            func_args=param
        )

    async def dispatch_on_message_delete(self, message) -> None:
        param = [message]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_message_delete',
            func_args=param
        )
        
    async def dispatch_on_message_update(self, message) -> None:
        param = [message]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_message_update',
            func_args=param
        )

    async def dispatch_on_typing_start(self, typing) -> None:
        param = [typing]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_typing_start',
            func_args=param
        )

    async def dispatch_on_typing_end(self, typing) -> None:
        param = [typing]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_typing_end',
            func_args=param
        )

    async def dispatch_on_member_update(self, old, new, house) -> None:
        param = [old, new, house]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_member_update',
            func_args=param
        )

    async def dispatch_on_house_member_chunk(self, members: list, house, data: dict) -> None:
        param = [members, house]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_house_member_chunk',
            func_args=param
        )

    async def dispatch_on_batch_house_member_update(self, house, members, data: dict) -> None:
        param = [members, data, house]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_batch_house_member_update',
            func_args=param
        )

    async def dispatch_on_house_entity_update(self, house, entity, data) -> None:
        param = [house, entity, data]
        await dispatch_func_if_exists(
            obj=self._call_obj,
            func_name='on_house_entity_update',
            func_args=param
        )
