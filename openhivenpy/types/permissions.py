""" Permissions Class for representing and managing member permissions """
from enum import Enum

__all__ = [
    'Permissions'
]


class Permissions(Enum):
    """ Hiven Permissions ENUM """
    SEND_MESSAGES = 1 << 0
    READ_MESSAGES = 1 << 1
    ADMINISTRATOR = 1 << 2
    MODERATE_ROOM = 1 << 3
    EVICT_MEMBERS = 1 << 4
    KICK_MEMBERS = 1 << 5
    ATTACH_MEDIA = 1 << 6
    MANAGE_ROLES = 1 << 7
    MANAGE_BILLING = 1 << 8
    MANAGE_BOTS = 1 << 9
    MANAGE_INTEGRATIONS = 1 << 10
    MANAGE_ROOMS = 1 << 11
    START_PORTAL = 1 << 12
    STREAM_TO_PORTAL = 1 << 13
    TAKEOVER_PORTAL = 1 << 14
    POST_TO_FEED = 1 << 15
    MANAGE_USER_OVERRIDES = 1 << 16
    CREATE_INVITES = 1 << 17
    MANAGE_INVITES = 1 << 18
    HERE_MENTIONS = 1 << 19
