from openhivenpy.Utils import utils
class Room():
    """`openhivenpy.Types.Room`
    
    Data Class for a Hiven Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with house room lists and House.get_room()
    
    """
    def __init__(self, data: dict,token): #These are all the attribs rooms have for now. Will add more when Phin says theyve been updated. Theres no functions. Yet.
        self._id = data['id']
        self._name = data['name']
        self._house = data["house_id"]
        self._position = data["position"]
        self._type = data["type"] # 0 = Text, 1 = Portal
        self._emoji = data["emoji"]
        self._description = data["description"]
        self._TOKEN = token

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def house(self):
        return None #ToDo

    @property
    def position(self):
        return self._position
    
    @property
    def type(self):
        return self._type #ToDo: Other room classes.

    @property
    def emoji(self):
        return self._emoji["data"] #Random type attrib there aswell
    
    @property
    def description(self):
        return self._description