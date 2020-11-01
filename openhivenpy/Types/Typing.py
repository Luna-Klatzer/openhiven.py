from openhivenpy.Types import *
import datetime
class Typing():
    def __init__(self,data):
        self._MEMBER = data["author_id"]
        self._HOUSE = data["house_id"]
        self._ROOM = data["room_id"]
        self._TIMESTAMP = data["timestamp"]

    @property
    def timestamp(self):
        return datetime.datetime.fromtimestamp(self._TIMESTAMP)