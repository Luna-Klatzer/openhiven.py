from functools import wraps
import asyncio 

class Events():
    """openhivenpy.Events.Events Openhivenpy Event Handler
    
    Event Handler for the HivenClient Class. Functions will be called from the
    websocket class and if the user specified a event response with the
    decorator @HivenClient.event, it will be called and executed.
    
    """
    def event(self):
        """openhivenpy.Events.Events.event
        
        Decorator used for creating HivenClient Events
        
        """
        def decorator(func):
            @wraps(func) 
            async def wrapper(*args, **kwargs): 
                return await func(*args, **kwargs)
            
            setattr(self, func.__name__, wrapper) # Adding the function to the object

            return func # returning func means func can still be used normally

        return decorator

    async def ON_CONNECTION_START(self) -> None:
        if hasattr(self, 'on_connection_start'):
            await self.on_connection_start()

    async def INIT_STATE(self, client) -> None:
        if hasattr(self, 'on_init'):
            await self.on_init(client)

    async def READY_STATE(self, ctx) -> None:
        if hasattr(self, 'on_ready'):
            await self.on_ready(ctx)

    async def HOUSE_JOIN(self, ctx) -> None:
        if hasattr(self, 'on_house_add'):
            await self.on_house_join(ctx)

    async def HOUSE_EXIT(self, ctx) -> None:
        if hasattr(self, 'on_house_exit'):
            await self.on_house_exit(ctx)

    async def HOUSE_DOWN(self,house) -> None:
        if hasattr(self,"on_house_downage"):
            await self.on_house_downage(house)

    async def HOUSE_MEMBER_ENTER(self, ctx, member) -> None:
        if hasattr(self, 'on_house_enter'):
            await self.on_house_enter(ctx, member)

    async def HOUSE_MEMBER_EXIT(self, ctx, member) -> None:
        if hasattr(self, 'on_house_exit'):
            await self.on_house_exit(ctx, member)

    async def PRESENCE_UPDATE(self, precence, member) -> None:
        if hasattr(self, 'on_presence_update'):
            await self.on_presence_update(precence, member)

    async def MESSAGE_CREATE(self, message) -> None:
        if hasattr(self, 'on_message_create'):
            await self.on_message_create(message)

    async def MESSAGE_DELETE(self, message) -> None:
        if hasattr(self, 'on_message_delete'):
            await self.on_message_delete(message)

    async def MESSAGE_UPDATE(self, message) -> None:
        if hasattr(self, 'on_message_update'):
            await self.on_message_update(message)

    async def TYPING_START(self, member) -> None:
        if hasattr(self, 'on_typing_start'):
            await self.on_typing_start(member)

    async def TYPING_END(self, member) -> None:
        if hasattr(self, 'on_typing_end'):
            await self.on_typing_end(member)

