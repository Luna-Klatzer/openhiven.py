class Room():
    """openhivenpy.Types.Room: Data Class for a Hiven Room
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with house room lists and House.get_room()
    
    """
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']