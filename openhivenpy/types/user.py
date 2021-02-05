import sys
import logging
from marshmallow import Schema, fields, post_load, ValidationError, RAISE

from . import HivenObject
from .. import utils
from ..exceptions import exception as errs

logger = logging.getLogger(__name__)

__all__ = ['LazyUser', 'User']


class LazyUser(HivenObject):
    """
    Represents the standard Hiven User
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

        except Exception as e:
            utils.log_traceback(msg="[LAZYUSER] Traceback:",
                                suffix="Failed to initialize the User object; \n"
                                       f"{sys.exc_info()[0].__name__}: {e} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Member object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}: {e}")

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
    """
    Represents the regular extended Hiven User
    """
    def __init__(self, data: dict, http):
        try:
            super().__init__(data) 
            self._location = data.get('location', "")
            self._website = data.get('website', "") 
            self._presence = data.get('presence', "")  # ToDo: Presence class
            
            self._http = http
        
        except Exception as e:
            utils.log_traceback(msg="[USER] Traceback:",
                                suffix="Failed to initialize the User object; \n"
                                       f"{sys.exc_info()[0].__name__}: {e} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize User object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}: {e}")

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
