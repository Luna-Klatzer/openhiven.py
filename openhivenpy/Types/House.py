class House():
    """openhivenpy.Types.House: Data Class for a Hiven House
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with events, the client guilds attribute and get_guild()
    
    """
    def __init__(self, data):
        self._ID = data["id"]
        self._NAME = data["name"]
        self._BANNER = data["banner"]
        self._ICON = data["icon"]
        #self.members = members #ToDo
        #self.rooms = data["rooms"]
        

    @property
    def id(self) -> int:
        return self._ID

    @property
    def name(self) -> str:
        return self._NAME

    @property
    def banner(self) -> str:
        return self._BANNER

    @property
    def icon(self) -> str:
        return self._ICON
