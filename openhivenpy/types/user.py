import sys
import datetime
import logging
from typing import Union

import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTP

logger = logging.getLogger(__name__)

__all__ = ['LazyUser', 'User']


class LazyUser:
    """`openhivenpy.types.LazyUser` 
    
    Data Class for a reduced Hiven User
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Represents the standard Hiven User
    
    Attributes
    ~~~~~~~~~~
    
    """
    def __init__(self, data: dict):
        try:
            if data.get('user') is not None:
                data = data.get('user')

            self._username = data.get('username')
            self._name = data.get('name')
            self._id = int(data.get('id'))
            self._user_flags = data.get('user_flags')  # ToDo: Discord.py-esque way of user flags
            self._icon = data.get('icon')
            self._header = data.get('header')
            self._bot = data.get('bot')

        except AttributeError as e:
            logger.error(f"[USER] Failed to initialize the User object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Member object! Most likely faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

        except Exception as e:
            logger.error(f"[USER] Failed to initialize the User object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Member object! Possibly faulty data! "
                                    f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('username', self.username),
            ('name', self.name),
            ('id', self.id),
            ('icon', self.icon),
            ('header', self.header),
            ('bot', self.bot)
        ]
        return '<User {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def username(self) -> str:
        return self._username

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @property
    def icon(self) -> str:
        return f"https://media.hiven.io/v1/users/{self._id}/icons/{self._icon}"

    @property
    def header(self) -> str:
        return f"https://media.hiven.io/v1/users/{self._id}/headers/{self._header}"
    
    @property
    def bot(self) -> bool:
        return self._bot


class User(LazyUser):
    """`openhivenpy.types.User` 
    
    Data Class for a Hiven User
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Represents the extended Hiven User
    
    Returned with events, guilds user lists, getUser() and get_user()
    
    Attributes
    ~~~~~~~~~~
    
    """
    def __init__(self, data: dict, http: HTTP):
        try:
            super().__init__(data) 
            self._location = data.get('location', "")
            self._website = data.get('website', "") 
            self._presence = data.get('presence', "")  # ToDo: Presence class
            self._joined_at = data.get('joined_at', "")
            
            self._http = http
            
        except AttributeError as e: 
            logger.error(f"[USER] Failed to initialize the User object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize User object! Most likely faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"[USER] Failed to initialize the User object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize User object! Possibly faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    @property
    def location(self) -> str:
        return self._location

    @property
    def website(self) -> str:
        return self._website

    # Still needs to be worked out
    @property
    def presence(self):
        return self._presence

    @property
    def joined_at(self) -> Union[datetime.datetime, None]:
        if self._joined_at is not None and self._joined_at != "":
            return datetime.datetime.fromisoformat(self._joined_at[:10])
        else:
            return None