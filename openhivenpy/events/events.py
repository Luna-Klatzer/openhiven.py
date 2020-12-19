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
        self.call_obj = call_obj
        if self.call_obj is None:
            logger.debug("Passed object where the events should be called from is None!")
            self.call_obj = self

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

    async def ev_connection_start(self) -> None:
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_connection_start'
        )

    async def ev_init_state(self, time) -> None:
        param = [time]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_init',
            args=param
        )

    async def ev_ready_state(self) -> None:
        param = []
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_ready',
            args=param
        )

    async def ev_house_join(self, house) -> None:
        param = [house]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_house_add',
            args=param
        )

    async def ev_house_exit(self, house) -> None:
        param = [house]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_house_remove',
            args=param
        )

    async def ev_house_down(self, time, house) -> None:
        param = [time, house]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_house_downage',
            args=param
        )
        
    async def ev_house_member_enter(self, member, house) -> None:
        param = [member, house]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_house_enter',
            args=param
        )

    async def ev_house_member_exit(self, user, house) -> None:
        param = [user, house]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_house_exit',
            args=param
        )

    async def ev_relationship_update(self, relationship) -> None:
        param = [relationship]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_relationship_update',
            args=param
        )

    async def ev_presence_update(self, presence, user) -> None:
        param = [presence, user]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_presence_update',
            args=param
        )

    async def ev_message_create(self, message) -> None:
        param = [message]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_message_create',
            args=param
        )

    async def ev_message_delete(self, message) -> None:
        param = [message]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_message_delete',
            args=param
        )
        
    async def ev_message_update(self, message) -> None:
        param = [message]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_message_update',
            args=param
        )

    async def ev_typing_start(self, typing) -> None:
        param = [typing]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_typing_start',
            args=param
        )

    async def ev_typing_end(self, typing) -> None:
        param = [typing]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_typing_end',
            args=param
        )

    async def ev_house_member_update(self, old, new, house) -> None:
        param = [old, new, house]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_member_update',
            args=param
        )

    async def ev_house_member_chunk(self, members: list, house, data: dict) -> None:
        param = [members, house]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_house_member_chunk',
            args=param
        )

    async def ev_batch_house_member_update(self, house, members, data: dict) -> None:
        param = [members, data, house]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_batch_house_member_update',
            args=param
        )

    async def ev_house_entity_update(self, house, entity, data) -> None:
        param = [house, entity, data]
        await dispatch_func_if_exists(
            obj=self.call_obj,
            func_name='on_house_entity_update',
            args=param
        )
