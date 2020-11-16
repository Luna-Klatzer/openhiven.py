class House():
    def __init__(self, data):
        self.id = data["id"]
        print("id set")
        self.name = data["name"]
        print("name set")
        #self.members = members #ToDo
        #self.rooms = data["rooms"]
        self.banner = data["banner"]
        print("banner set")
        self.icon = data["icon"]
        print("icon set")
        

    @property
    def name(self):
        return self.name
