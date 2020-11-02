from .User import User
from .ClientUser import ClientUser

class Client():
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
                
            try: self._location = data["user"]["location"] if data["user"]["location"] != None else None
            except: self._location = None
            
            try: self._website = data["user"]["website"] if data["user"]["website"] != None else None
            except: self._website = None

            self._HOUSES = [] #Python no likey appending to a read-only list
            self._USERS = []
            self._USERCLIENT = ClientUser(data)
            return self

        except AttributeError: #Audible pain.
            raise AttributeError("The data of the object User was not initialized correctly")
        except KeyError as e:
            pass
        except Exception as e:
            raise e

