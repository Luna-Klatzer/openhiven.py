import sys
import logging
import datetime
import asyncio
import time
from typing import Union

from ._get_type import getType
import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

__all__ = ['Client']


class Client:
    """`openhivenpy.types.Client`

    Date Class for a Client
    ~~~~~~~~~~~~~~~~~~~~~~~

    Data Class that stores the data of the connected client

    """
    def __init__(self, *, http=None, **kwargs):
        self._http = http if http is not None else self._http

        self._amount_houses = 0
        self._houses = []
        self._users = []
        self._rooms = []
        self._private_rooms = []
        self._relationships = []
        self._USER = None

        # Init Data that will be overwritten by the connection and websocket
        self._initialized = False
        self._connection_start = None
        self._startup_time = None
        self._ready = False

        self._event_handler = getattr(self, '_event_handler')
        self._execution_loop = getattr(self, '_execution_loop')

        # Appends the ready check function to the execution_loop
        self._execution_loop.add_to_startup(self.__check_meta_data)

    def __str__(self) -> str:
        return str(repr(self))

    def __repr__(self) -> str:
        return repr(self.user)

    @property
    def connection_start(self) -> float:
        return getattr(self, "connection_start")

    async def init_meta_data(self, data: dict = None) -> None:
        """`openhivenpy.types.client.update_client_user_data()`
        Updates or creates the standard user data attributes of the Client
        """
        try:
            # Using a USER object to actually store all user data
            self._USER = await getType.a_user(data, self.http)

            _relationships = data.get('relationships')
            if _relationships:
                for key in _relationships:
                    _rel_data = _relationships.get(key, {})
                    _rel = await getType.a_relationship(
                        data=_rel_data,
                        http=self.http)

                    self._relationships.append(_rel)
            else:
                raise errs.WSFailedToHandle("Missing 'relationships' in 'INIT_STATE' event message!")

            _private_rooms = data.get('private_rooms')
            if _private_rooms:
                for private_room in _private_rooms:
                    t = int(private_room.get('type', 0))
                    if t == 1:
                        room = await getType.a_private_room(private_room, self.http)
                    elif t == 2:
                        room = await getType.a_private_group_room(private_room, self.http)
                    else:
                        room = await getType.a_private_room(private_room, self.http)
                    self._private_rooms.append(room)
            else:
                raise errs.WSFailedToHandle("Missing 'private_rooms' in 'INIT_STATE' event message!")

            _house_ids = data.get('house_memberships')
            if _house_ids:
                self._amount_houses = len(_house_ids)
            else:
                raise errs.WSFailedToHandle("Missing 'house_memberships' in 'INIT_STATE' event message!")

            # Requesting user data of the client itself
            _raw_data = await self.http.request("/users/@me", timeout=15)
            if _raw_data:
                _data = _raw_data.get('data')
                if _data:
                    self._USER = getType.user(data=data, http=self.http)
                else:
                    raise errs.HTTPReceivedNoData()
            else:
                raise errs.HTTPReceivedNoData()

        except Exception as e:
            logger.error(f"[CLIENT] FAILED to update client data! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.FaultyInitialization(f"FAILED to update client data! Possibly faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    async def __check_meta_data(self):
        """
        Checks whether the meta data is complete and triggers on_ready
        """
        check = True
        while True:
            if self._amount_houses == len(self._houses) and self._initialized:
                self._startup_time = time.time() - self.connection_start
                self._ready = True
                logger.info("[CLIENT] Client loaded all data and is ready for usage! ")
                asyncio.create_task(self._event_handler.ev_ready_state())
                break
            if (time.time() - self.connection_start) > 30 and check:
                logger.warning("[CLIENT] Initialization takes unusually long! Possible connection or data issues!")
                check = False
            await asyncio.sleep(0.05)

    async def edit(self, **kwargs) -> bool:
        """`openhivenpy.types.Client.edit()`

        Change the signed in user's/bot's data.

        Available options: header, icon, bio, location, website

        Returns `True` if successful

        """
        try:
            for key in kwargs.keys():
                if key in ['header', 'icon', 'bio', 'location', 'website']:
                    resp = await self.http.patch(endpoint="/users/@me", data={key: kwargs.get(key)})

                    if resp.status < 300:
                        return True
                    else:
                        raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")
                else:
                    logger.error("[CLIENT] The passed value does not exist in the user context!")
                    raise NameError("The passed value does not exist in the user context!")

        except Exception as e:
            keys = "".join(str(" " + key) for key in kwargs.keys())
            logger.error(f"[CLIENT] Failed change the values {keys} on the client Account! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.HTTPError(f"Failed change the values {keys} on the client Account!")

    @property
    def user(self):
        return getattr(self, '_USER', object)

    @property
    def username(self) -> str:
        return getattr(self.user, 'username', None)

    @property
    def name(self) -> str:
        return getattr(self.user, 'name', None)

    @property
    def id(self) -> int:
        return getattr(self.user, 'id', None)

    @property
    def icon(self) -> str:
        return getattr(self.user, 'icon', None)

    @property
    def header(self) -> str:
        return getattr(self.user, 'header', None)

    @property
    def bot(self) -> bool:
        return getattr(self.user, 'bot', None)

    @property
    def location(self) -> str:
        return getattr(self.user, 'location', None)

    @property
    def website(self) -> str:
        return getattr(self.user, 'website', None)

    @property
    def presence(self) -> getType.presence:
        return getattr(self.user, 'presence', None)

    @property
    def joined_at(self) -> Union[datetime.datetime, None]:
        if self.user.joined_at and self.user.joined_at != "":
            return datetime.datetime.fromisoformat(self.user.joined_at[:10])
        else:
            return None

    @property
    def houses(self):
        return getattr(self.user, '_houses', [])

    @property
    def private_rooms(self):
        return getattr(self.user, '_private_rooms', [])

    @property
    def users(self):
        return getattr(self.user, '_users', [])

    @property
    def rooms(self):
        return getattr(self.user, '_rooms', [])

    @property
    def amount_houses(self) -> int:
        return getattr(self.user, '_amount_houses', [])

    @property
    def relationships(self) -> list:
        return getattr(self.user, '_relationships', [])

    @property
    def http(self):
        return getattr(self, 'http', None)
