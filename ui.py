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