from .Room import Room

class Message():
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.author = data['author'] 
        self.author_id = data['author_id']
        self.time = data['time']
        self.room = Room(data)