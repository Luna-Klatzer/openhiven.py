from .Room import Room

class Message():
    """openhivenpy.Types.Message: Data Class for a standard Hiven message
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with house room message list and House.get_message()
    
    """
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.author = data['author'] 
        self.author_id = data['author_id']
        self.time = data['time']
        self.room = Room(data)