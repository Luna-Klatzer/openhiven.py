from functools import wraps
import asyncio 

class Events():
    def event(self):
        def decorator(func):
            @wraps(func) 
            async def wrapper(*args, **kwargs): 
                return await func(*args, **kwargs)
            
            setattr(self, func.__name__, wrapper) # Adding the function to the object

            return func # returning func means func can still be used normally

        return decorator

    async def INIT_STATE(self, client):
        if hasattr(self, 'on_init'):
            await self.on_init(client)

    async def HOUSE_JOIN(self, ctx):
        if hasattr(self, 'on_house_add'):
            await self.on_house_join(ctx)

    async def HOUSE_EXIT(self,ctx):
        if hasattr(self, "on_house_exit"):
            await self.on_house_exit(ctx)

    async def HOUSE_MEMBER_ENTER(self, ctx, member):
        if hasattr(self, 'on_house_enter'):
            await self.on_house_enter(ctx, member)

    async def HOUSE_MEMBER_EXIT(self, ctx, member):
        if hasattr(self, 'on_house_exit'):
            await self.on_house_exit(ctx, member)

    async def PRESENCE_UPDATE(self, precence, member):
        if hasattr(self, 'on_presence_update'):
            await self.on_presence_update(precence, member)

    async def MESSAGE_CREATE(self, message):
        if hasattr(self, 'on_message_create'):
            await self.on_message_create(message)

    async def MESSAGE_DELETE(self, message):
        if hasattr(self, 'on_message_delete'):
            await self.on_message_delete(message)

    async def MESSAGE_UPDATE(self, message):
        if hasattr(self, 'on_message_update'):
            await self.on_message_update(message)

    async def TYPING_START(self, member):
        if hasattr(self, 'on_typing_start'):
            await self.on_typing_start(member)

    async def TYPING_END(self, member):
        if hasattr(self, 'on_typing_end'):
            await self.on_typing_end(member)

