class Client():
    def __init__(self, data): #Maybe make a ClientUser object to make this cleaner? :thinking:
        try:
            self._username = data['user']['username']
            self._name = data['user']['name']
            self._id = data['user']['id']
            try: self._icon = data['user']['icon'] if data['user']['icon'] != None else None 
            except: self._icon = None

            try: self._header = data["user"]["header"] if data["user"]["header"] != None else None
            except: self._header = None

            try: self._bot = data["user"]["bot"] if data["user"]["bot"] != None else False
            except: self._bot = False
                
            try: self._location = data["user"]["location"] if data["user"]["location"] != None else None
            except: self._location = None
            
            try: self._website = data["user"]["website"] if data["user"]["website"] != None else None
            except: self._website = None
        except AttributeError: #Audible pain.
            raise AttributeError("The data of the object User was not initialized correctly")
        except KeyError: #Client is trying to init twice
            pass 
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
    def location(self):
        return self._location

    @property
    def website(self):
        return self._website