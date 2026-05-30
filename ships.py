class ship:
    def __init__(self,name, size):
        self.name = name
        self.size = size
        self.hits = 0
        self.coordinates = None ##will be a list of coordinates occupied by the ship
        
    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.coordinates = [x, y]
    def hit(self):
        self.hits += 1
        if self.hits >= self.size:
            return True
    