import asyncio 
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class Events():
    """`openhivenpy.Events.Events` 
    
    Openhivenpy Event Handler
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Event Handler for the HivenClient Class. Functions will be called from the
    websocket class and if the user registered an event response with the
    decorator @HivenClient.event, it will be called and executed.
    
    """
    def event(self):
        """`openhivenpy.Events.Events.event`
        
        Event Decorator
        ---------------
        
        Decorator used for registering HivenClient Events
        
        """
        def decorator(func):
            @wraps(func) 
            async def wrapper(*args, **kwargs): 
                return await func(*args, **kwargs)
            
            setattr(self, func.__name__, wrapper) # Adding the function to the object

            logger.debug(f"Event {func.__name__} registered")

            return func # returning func means func can still be used normally

        return decorator

    async def ON_CONNECTION_START(self) -> None:
        if hasattr(self, 'on_connection_start'):
            logger.debug("Dispatching on_connection_start")
            await self.on_connection_start()
        else:
            logger.debug("on_connection_start not found. Returning")
            return    

    async def INIT_STATE(self, client) -> None:
        if hasattr(self, 'on_init'):
            logger.debug("Dispatching on_init")
            await self.on_init(client)
        else:
            logger.debug("on_init not found. Returning")
            return

    async def READY_STATE(self, ctx) -> None:
        if hasattr(self, 'on_ready'):
            logger.debug("Dispatching on_ready")
            await self.on_ready(ctx)
        else:
            logger.debug("on_ready not found. Returning")
            return    

    async def HOUSE_JOIN(self, ctx) -> None:
        if hasattr(self, 'on_house_add'):
            logger.debug("Dispatching on_house_add")
            await self.on_house_join(ctx)
        else:
            logger.debug("on_house_join not found. Returning")
            return

    async def HOUSE_EXIT(self, ctx) -> None:
        if hasattr(self, 'on_house_exit'):
            logger.debug("Dispatching on_house_exit")
            await self.on_house_exit(ctx)
        else:
            logger.debug("on_house_exit not found. Returning")
            return

    async def HOUSE_DOWN(self,house) -> None:
        if hasattr(self,"on_house_downage"):
            logger.debug("Dispatching on_house_downage")
            await self.on_house_downage(house)
        else:
            logger.debug("on_house_downage not found. Returning")
            return

    async def HOUSE_MEMBER_ENTER(self, ctx, member) -> None:
        if hasattr(self, 'on_house_enter'):
            logger.debug("Dispatching on_house_enter")
            await self.on_house_enter(ctx, member)
        else:
            logger.debug("on_house_enter not found. Returning")
            return

    async def HOUSE_MEMBER_EXIT(self, ctx, member) -> None:
        if hasattr(self, 'on_house_exit'):
            logger.debug("Dispatching on_house_exit")
            await self.on_house_exit(ctx, member)
        else:
            logger.debug("on_house_exit not found. Returning")
            return

    async def PRESENCE_UPDATE(self, precence, member) -> None:
        if hasattr(self, 'on_presence_update'):
            logger.debug("Dispatching on_presence_update")
            await self.on_presence_update(precence, member)
        else:
            logger.debug("on_presence_update not found. Returning")
            return

    async def MESSAGE_CREATE(self, message) -> None:
        if hasattr(self, 'on_message_create'):
            logger.debug("Dispatching on_message_create")
            await self.on_message_create(message)
        else:
            logger.debug("on_message_create not found. Returning")
            return

    async def MESSAGE_DELETE(self, message) -> None:
        if hasattr(self, 'on_message_delete'):
            logger.debug("Dispatching on_message_delete")
            await self.on_message_delete(message)
        else:
            logger.debug("on_message_delete not found. Returning")
            return

    async def MESSAGE_UPDATE(self, message) -> None:
        if hasattr(self, 'on_message_update'):
            logger.debug("Dispatching on_message_update")
            await self.on_message_update(message)
        else:
            logger.debug("on_message_update not found. Returning")
            return

    async def TYPING_START(self, member) -> None:
        if hasattr(self, 'on_typing_start'):
            logger.debug("Dispatching on_typing_start")
            await self.on_typing_start(member)
        else:
            logger.debug("on_typing_start not found. Returning")
            return

    async def TYPING_END(self, member) -> None:
        if hasattr(self, 'on_typing_end'):
            logger.debug("Dispatching on_typing_end")
            await self.on_typing_end(member)
        else:
            logger.debug("on_typing_end not found. Returning")
            return
