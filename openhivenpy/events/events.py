import logging
import sys
from functools import wraps

from openhivenpy.utils import dispatch_func_if_exists

logger = logging.getLogger(__name__) 
    
class EventHandler():
    """`openhivenpy.events.EventHandler` 
    
    Openhivenpy Event Handler
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Event Handler for the HivenClient Class. Functions will be called from the
    websocket class and if the user registered an event response with the
    decorator @HivenClient.event, it will be called and executed.
    
    """
    def __init__(self, call_obj: object):
        self.call_obj = call_obj
        if call_obj == None: 
            logger.debug("Passed object where the events should be called from is None!")

    def event(self, func = None):
        """`openhivenpy.events.Events.event`
        
        Decorator used for registering Client Events
        
        Parameter:
        ----------
        
        func: `function` - Function that should be wrapped. Only usable if the wrapper is used in the function syntax: 'event(func)'!
        
        """
        def decorator(func):
            @wraps(func) 
            async def wrapper(*args, **kwargs): 
                return await func(*args, **kwargs)
            
            setattr(self, func.__name__, wrapper) # Adding the function to the object

            logger.debug(f"Event {func.__name__} registered")

            return func # returning func means func can still be used normally

        if func == None:    
            return decorator
        else:
            return decorator(func)

    async def connection_start(self) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_connection_start') 

    async def init_state(self, time) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_init', 
                                time=time) 

    async def ready_state(self, ctx) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_ready', 
                                    ctx=ctx) 

    async def house_join(self, ctx, house) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_house_add', 
                                    ctx=ctx, house=house) 

    async def house_exit(self, ctx, house) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_house_remove', 
                                    ctx=ctx, house=house) 

    async def house_down(self, ctx, house) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_house_downage', 
                                    ctx=ctx, house=house) 

    async def house_member_enter(self, member, house) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_house_enter',
                                    member=member, house=house) 

    async def house_member_exit(self, ctx, user) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_house_exit',
                                    ctx=ctx, user=user) 

    async def presence_update(self, precence, user) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_presence_update',
                                    precence=precence, user=user) 

    async def message_create(self, message) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_message_create',
                                    message=message) 

    async def message_delete(self, message) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_message_delete',
                                    message=message) 

    async def message_update(self, message) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_message_update',
                                    message=message) 

    async def typing_start(self, user) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_typing_start',
                                    user=user) 

    async def typing_end(self, user) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_typing_end',
                                    user=user) 

    async def house_member_update(self, member, house) -> None:
        await dispatch_func_if_exists(obj=self.call_obj, func_name='on_user_update',
                                    member=member, house=house) 
