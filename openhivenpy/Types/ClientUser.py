from openhivenpy.Types import *
import openhivenpy
import requests

class ClientUser(User):
    def __init__(self,data):
        super().__init__(data)


    async def edit(self,data) -> bool:
        """openhivenpy.ClientUser.edit
        Change the signed in user's data. Available options: header, banner, bio.
        """
        res = requests.patch("https://api.hiven.io/v1/users/@me")