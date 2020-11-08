from .Room import Room
from .Member import Member
import datetime

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
        self._time = data['time']
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
        return self._time

    @property
    def edited_at(self):
        return self._edited_at