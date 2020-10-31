class User():
    def __init__(self, data):
        try:
            self._username = data['user']['username']
            self._name = data['user']['name']
            self._id = data['user']['id']
            self._icon = data['user']['icon'] if data['user']['icon'] != None else None
            self._header = data["user"]["header"] if data["user"]["header"] != None else None
            self._bot = data["user"]["bot"] if data["user"]["bot"] != None else False
            self._location = data["user"]["location"] if data["user"]["location"] != None else None
            self._website = data["user"]["website"] if data["user"]["website"] != None else None
            #self._presence = data["user"]["presence"] if data["user"]["presence"] != None else None #ToDo: Presence class
        except AttributeError: 
            raise AttributeError("The data of the object User was not initialized correctly")
        except Exception as e: 
            raise Exception(e)

    @property
    def username(self):
        return self._username

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def icon(self):
        return self._icon

    @property
    def header(self):
        return self._header
    
    @property
    def bot(self):
        return self._bot

    @property
    def location(self):
        return self._location

    @property
    def website(self):
        return self._website