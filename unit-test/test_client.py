import openhivenpy


def test_user_client(token):
    """ Testing specifically targeted at the UserClient Class """
    user = openhivenpy.UserClient(token)
    assert isinstance(user, openhivenpy.UserClient)

    @user.event()
    async def on_ready():
        await user.close()

    user.run()
