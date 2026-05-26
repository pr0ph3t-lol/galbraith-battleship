Class Ship:
    def __init__(self,name, size):
        self.name = name
        self.size = size
        self.hits = 0
        self.coordinates = None
    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.coordinates = [x, y]
    