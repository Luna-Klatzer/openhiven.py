from . import *
import openhivenpy
import requests

class ClientUser(User):
    def __init__(self, data: dict):
        super().__init__(data)


    async def edit(self,data) -> bool:
        """`openhivenpy.ClientUser.edit`
        
        Change the signed in user's data. Available options: header, icon, bio, location, website.
        
        """
        if not type(data) == dir:
            raise SyntaxError(f"Expected dir, got {type(data)}")
        res = requests.patch("https://api.hiven.io/v1/users/@me",headers={"authorization":self._TOKEN,"User-Agent":"openhiven.py","Content-Type":"application/json"},data=data)
        return res.status_code == 200