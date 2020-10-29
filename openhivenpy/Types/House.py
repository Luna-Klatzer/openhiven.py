class House():
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        #self.members = members #ToDo
        #self.rooms = data["rooms"]
        self.banner = data["banner"]
        self.icon = data["icon"]

    @property
    def name(self):
        return self.name
