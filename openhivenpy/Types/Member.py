import requests
from .User import User
import openhivenpy.Exception as errs

class Member(User):
    """openhivenpy.Types.Member: Data Class for a Hiven member
    
    The class inherits all the avaible data from Hiven(attr -> read-only) and the User Class!
    
    Returned with house house member list and House.get_member()
    
    """
    def __init__(self, data: dict):
        super().__init__(data)
        if hasattr(data, 'user_id'): self._user_id = data['user_id']
        else: self._user_id = self._id
        if hasattr(data, 'house_id'): self._house_id = data['house_id']
        else: self._user_id = None
        if hasattr(data, 'joined_at'): self._joined_at = data['joined_at']
        else: self._joined_at = None
        if hasattr(data, 'roles'): self._roles = list(data['roles'])
        else: self._roles = None
        
    def __str__(self):
        return self.id()
        
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


    async def kick(self) -> bool:
        """`openhivenpy.Types.Member.kick()`
        
        Kick
        ~~~~

        Kicks a user from the house.

        The client needs permissions to kick, or else this will raise `HivenException.Forbidden`. 
            
        Returns `True` if succesful.
        
        """

        #DELETE api.hiven.io/houses/HOUSEID/members/MEMBERID
        res = await requests.delete(f"https://api.hiven.io/v1/houses/{self._house_id}/members/{self._id}")
        if not res.response_code == 204: #Why not continue using 200 instead of using 204 i have no idea.
            raise errs.Forbidden()
        else:
            return True