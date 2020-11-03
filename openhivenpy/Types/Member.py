from openhivenpy.Types import User

class Member(User):
    """openhivenpy.Types.Message: Data Class for a standard Hiven message
    
    The class inherits all the avaible data from Hiven(attr -> read-only) and the User Class!
    
    Returned with house house member list and House.get_member()
    
    """
    def __init__(self, data):
        super().__init__(data)
        if hasattr(data, 'user_id'): self._user_id = data['user_id']
        else: self._user_id = self._id
        if hasattr(data, 'house_id'): self._house_id = data['house_id']
        else: self._user_id = None
        if hasattr(data, 'joined_at'): self._joined_at = data['joined_at']
        else: self._joined_at = None
        if hasattr(data, 'roles'): self._roles = list(data['roles'])
        else: self._roles = None
        
    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def joined_at(self) -> str:
        return self._joined_at

    @property
    def house_id(self) -> int:
        return self._house_id

    @property
    def roles(self) -> list:
        return self._roles