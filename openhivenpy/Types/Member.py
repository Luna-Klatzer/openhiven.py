from openhivenpy.Types import User
class Member(User):
    """openhivenpy.Types.Message: Data Class for a standard Hiven message
    
    The class inherits all the avaible data from Hiven(attr -> read-only) and the User Class!
    
    Returned with house house member list and House.get_member()
    
    """
    def __init__(self, data):
        super().__init__(data)
        #Nothing needed right now