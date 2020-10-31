try:
    from .client import *
except ImportError:
    from .Client import *
from .Events import *
from .Types import *
from .Websocket import Websocket