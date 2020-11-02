from .User import User

class Client(User):
    """openhivenpy.Types.Client: Data Class for the general HivenClient
    
    Used for the general data in the HivenClient and inherits all the avaible data from Hiven(attr -> readonly)!
    
    Returned as HivenClient(or specified Client Type) in on_init() and with UserClient(), BotClient() and HivenClient()
    
    """
    def update_client_data(self, data): #Maybe make a ClientUser object to make this cleaner? :thinking:
        """
        Updates or creates the standard data of the HivenClient
        
        Returns if the Client class inherited the caller class and else the Client Class itself
        
        """
        try: 
            self._username = data['user']['username'] if data['user']['username'] != None else None 
            self._name = data['user']['name'] if data['user']['name'] != None else None 
            self._id = data['user']['id'] if data['user']['id'] != None else None 
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

            self._HOUSES = [] #Python no likey appending to a read-only list
            self._USERS = []

            return self

        except AttributeError: #Audible pain.
            raise AttributeError("The data of the object User was not initialized correctly")
        except KeyError: #Client is trying to init twice
            try: self._username = self._username if self._username != None else None 
            except: self._username = None
            try: self._name = self._name if self._name != None else None 
            except: self._name = None
            try: self._id = self._id if self._id != None else None 
            except: self._id = None
            try: self._icon = self._icon if self._icon != None else None 
            except: self._icon = None

            try: self._header = self._header if self._header != None else None
            except: self._header = None
            try: self._bot = self._bot if self._bot != None else False
            except: self._bot = None
            try: self._location = self._location if self._location != None else None
            except: self._location = None
            try: self._website = self._website if self._website != None else None
            except: self._website = None #Didnt need to do this kudo

        except Exception as e: 
            raise Exception(e)
