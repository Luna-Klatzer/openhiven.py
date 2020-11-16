from .hivenclient import HivenClient

class UserClient(HivenClient):
    def __init__(self, token: str, heartbeat=30000, debug_mode=False, print_output=False):
        self.client_type = "HivenClient.UserClient"
        super().__init__(token=token, client_type=self.client_type, heartbeat=heartbeat, print_output=print_output, debug_mode=debug_mode)

    def __repr__(self):
        return str(self.client_type)

    def __str__(self):
        return str(self.client_type)