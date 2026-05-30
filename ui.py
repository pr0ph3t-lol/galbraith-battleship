import pygame

class Grid:
    def __init__(self, rows, cols, cell_width, cell_height):
        self.rows = rows
        self.cols = cols
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.origin = origin

    def draw(self, surface):
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(
                    col * self.cell_width,
                    row * self.cell_height,
                    self.cell_width,
                    self.cell_height,
                )
                pygame.draw.rect(surface, (0, 0, 0), rect, 1)

    def cell_at_pos(self, pos):
        x, y = pos
        ox, oy = self.origin
        if x < ox or y < oy:
            return None
        col = (x - ox) // self.cell_width
        row = (y - oy) // self.cell_height
        if row < 0 or col < 0 or row >= self.rows or col >= self.cols:
            return None
        return int(row), int(col)
    
class UI:
    empty = 0
    ship = 1
    hit = 2
    miss = 3
    forbidden = 4
    preview = 5
    pending = 6

    def __init__(self, screen, rows = 10, cols = 10, cell_size = 40, margin = 20):
        self.screen = screen
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.header_height = 50
        
