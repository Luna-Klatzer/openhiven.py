from .Room import Room
from .Member import Member
import datetime
import requests

class Message():
    """`openhivenpy.Types.Message`
    
    Data Class for a standard Hiven message
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with house room message list and House.get_message()
    
    """
    def __init__(self, data: dict):
        self._id = data['id']
        self._author = Member(data['author'])
        self._roomid = data["room_id"]
        self._room = None #Need to get room list as this returns room_id
        self._attatchment = data['attatchment']
        self._content = data['content']
        self._timestamp = datetime.datetime.fromtimestamp(data['timestamp'])
        self._edited_at = datetime.datetime.fromtimestamp(data['edited_at']) if hasattr(data,"edited_at") else None
        self._mentions = [(Member(x) for x in data['mentions'])] #Thats the first time I've ever done that. Be proud of me kudo!
        self._type = data['type'] # I believe, 0 = normal message, 1 = system.
        self._exploding = data['exploding'] #..I have no idea.


    @property
    def id(self):
        return self._id

    @property
    def author(self):
        return self._author

    @property
    def created_at(self):
        return self._timestamp

    @property
    def edited_at(self):
        return self._edited_at

    @property
    def room(self):
        return self._room

    @property
    def attatchment(self):
        return self._attatchment

    @property
    def content(self):
        return self._content

    @property
    def mentions(self):
        return self._mentions

    async def ack(self) -> bool:
        """openhivenpy.Types.Message.ack

        Marks the message as read. This doesn't need to be done for bot clients. Returns `True` if successful.
        """
        res = requests.post(f"https://api.hiven.io/v1/rooms/{self._roomid}/messages/{self._id}/ack")
        if not res.status_code == 204:
            return False
        else:
            return True


    async def delete(self) -> bool:
        """openhivenpy.Types.Message.delete()

        Deletes the message. Raises Forbidden if not allowed. Returns True if successful
        """
        print()