import sys
import logging
import datetime
import asyncio
import time
import typing
from marshmallow import Schema, fields, post_load, ValidationError, RAISE

from . import HivenObject
from . import user
from . import relationship
from . import private_room
from . import presence
from .. import utils
from ..exceptions import exception as errs

logger = logging.getLogger(__name__)

__all__ = ['Client']


class Client(HivenObject):
    """
    Data Class that stores the data of the connected Client
    """
    def __init__(self, *, http=None, **kwargs):
        self._http = http if http is not None else self._http

        # Base data lists for all Objects in the scope of the HivenClient
        self._houses = []
        self._users = []
        self._rooms = []
        self._private_rooms = []
        self._relationships = []
        self._house_memberships = []
        self._client_user = None

        # Init Data that will be overwritten by the connection and websocket
        self._initialised = False
        self._connection_start = None
        self._startup_time = None
        self._ready = False

        self._event_handler = getattr(self, '_event_handler')
        self._execution_loop = getattr(self, '_execution_loop')

        # Appends the ready check function to the execution_loop
        self._execution_loop.add_to_startup(self.__check_if_data_is_complete())

    def __repr__(self) -> str:
        return repr(self.user)

    @property
    def connection_start(self) -> float:
        return getattr(self, "connection_start")

    async def initialise_hiven_client_data(self, data: dict = None) -> None:
        """
        Updates or creates the standard user data attributes of the Client

        :param data: Data used for Initialisation
        """
        try:
            raw_data = await self.http.request("/users/@me")
            user_data = raw_data.get('data')
            if user_data:
                # Initialising the Client-User object for storing the user data
                self._client_user = await user.User.from_dict(user_data, self.http)
                self._users.append(self._client_user)
            else:
                raise errs.HTTPReceivedNoData()

            # Initialising the client relationships
            _relationships = data.get('relationships')
            for key in _relationships:
                _rel_data = _relationships.get(key, {})
                _rel = relationship.Relationship(
                    data=_rel_data,
                    http=self.http)

                self._relationships.append(_rel)

            # Initialising the private rooms
            _private_rooms = data.get('private_rooms')
            for d in _private_rooms:
                type_ = utils.convert_value(int, d.get('type', 0))
                if type_ == 1:
                    r = await private_room.PrivateRoom.from_dict(d, self.http, client_user=self.user)
                elif type_ == 2:
                    r = await private_room.PrivateGroupRoom.from_dict(d,
                                                                      self.http,
                                                                      users=self.users,
                                                                      client_user=self.user)
                else:
                    r = await private_room.PrivateRoom.from_dict(d, self.http, self.users, client_user=self.user)

                self._private_rooms.append(r)

            # Passing the amount of houses as variable
            self._house_memberships = data.get('house_memberships')

        except Exception as e:
            utils.log_traceback(msg="[CLIENT] Traceback: ",
                                suffix="Failed to initialise the Client User Data: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            raise errs.FaultyInitialization(f"Failed to initialise the Client User Data: "
                                            f"{sys.exc_info()[0].__name__}: {e}")

    async def __check_if_data_is_complete(self):
        """
        Checks whether the meta data is complete and triggers on_ready
        """
        # boolean that will trigger the warning that the process is taking too long
        is_taking_long = False
        while True:
            # If all expected houses were received and the client was initialised it will trigger
            # on_ready()
            if self.amount_houses == len(self._houses) and self._initialised:
                self._startup_time = time.time() - self.connection_start
                self._ready = True
                logger.info("[CLIENT] Client loaded all data and is ready for usage! ")
                asyncio.create_task(self._event_handler.dispatch_on_ready())
                break

            # Triggering a warning if the Initialisation takes too long!
            if (time.time() - self.connection_start) > 30 and is_taking_long is not True:
                logger.warning("[CLIENT] Initialization takes unusually long! Possible connection or data issues!")
                is_taking_long = True

            # Checking after a small bit again => don't remove!
            await asyncio.sleep(0.05)

    async def edit(self, **kwargs) -> bool:
        """
        Edits the Clients data on Hiven

        Available options: header, icon, bio, location, website, username

        :return: True if the request was successful else False
        """
        try:
            for key in kwargs.keys():
                # Available keys
                if key in ['header', 'icon', 'bio', 'location', 'website', 'username']:
                    resp = await self.http.patch(endpoint="/users/@me", json={key: kwargs.get(key)})

                    if resp.status < 300:
                        return True
                    else:
                        raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")
                else:
                    raise NameError("The passed value does not exist in the user context!")

        except Exception as e:
            keys = "".join(str(key + " ") for key in kwargs.keys())

            utils.log_traceback(msg="[CLIENT] Traceback:",
                                suffix=f"Failed change the values {keys}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    @property
    def user(self):
        return getattr(self, '_client_user', None)

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
    def presence(self) -> presence.Presence:
        return getattr(self.user, 'presence', None)

    @property
    def joined_at(self) -> typing.Union[datetime.datetime, None]:
        if self.user.joined_at and self.user.joined_at != "":
            return datetime.datetime.fromisoformat(self.user.joined_at[:10])
        else:
            return None

    @property
    def houses(self) -> list:
        return getattr(self, '_houses', [])

    @property
    def private_rooms(self) -> list:
        return getattr(self, '_private_rooms', [])

    @property
    def users(self) -> list:
        return getattr(self, '_users', [])

    @property
    def rooms(self) -> list:
        return getattr(self, '_rooms', [])

    @property
    def amount_houses(self) -> int:
        return len(getattr(self, '_house_memberships', []))

    @property
    def house_memberships(self) -> dict:
        return getattr(self, '_house_memberships', [])

    @property
    def relationships(self) -> list:
        return getattr(self, '_relationships', [])

    @property
    def http(self):
        return getattr(self, '_http', None)
