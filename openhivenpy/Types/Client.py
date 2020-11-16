class Client():
    def __init__(self, data):
        try:
            self.username = data['user']['username']
            self.name = data['user']['name']
            self.id = data['user']['id']
            self.icon = data['user']['icon'] if data['user']['icon'] != None else None
        except AttributeError: 
            raise AttributeError("The data of the object User was not initialized correctly")
        except Exception as e: 
            raise Exception(e)