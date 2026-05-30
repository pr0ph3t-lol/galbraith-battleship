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

        left_origin = (margin, self.header_height + margin)
        right_origin = (margin * 2 + cols * cell_size, self.header_height + margin)
        self.player_grid = Grid(rows, cols, cell_size, cell_size, left_origin)
        self.enemy_grid = Grid(rows, cols, cell_size, cell_size, right_origin)

        self.player_board = self._new_board()
        self.enemy_board = self._new_board()

        self.phase = "placing"
        self.turn = "player"
        self.ready = False
        self.lock_input = False

        self.orientation = "H"
        self.preview_cells = []
        self.preview_valid = False

        self.ship_queue = {
            #placehold
            ("big boy", 5)
            ("wow boy", 4)
            ("medium boy", 3)
            ("medium boyy", 3)
            ("mohammad boy", 2)
        }
        
        self.placed_ships = []

        self.font = pygame.font.SysFont(None, 28)
        self.header_text = ""
        self.updateStatusHeader()

    def _new_board(self):
        return [[self.empty for _ in range(self.cols)] for _ in range (self.rows)]
        
    def updateStatusHeader(self):
        pass

    def drawGrids(self):
        self._draw_board(self.player_grid, self.player_board, show_ships = True)
        self._draw_board(self.enemy_grid, self.enemy_board, show_ships = False)
        self.player_grid.draw(self.screen)
        self.enemy_griod.draw(self.screen)

    def _draw_board(self, grid, board, show_ships):
        pass

    def placementPreview(self, mouse_pos):
        if self.phase != "placing" or not self.ship_queue:
            return
        
        cell = self.player_grid.cell_at_pos(mouse_pos)
        if cell is None:
            self.preview_cells = []
            self.preview_valid = False
            return
        
        start_row, start_col = cell
        _, ship_size = self.ship_queue[0]
        cells = []
        for i in range(ship_size):
            row = start_row + (i if self.orientation == "V" else 0)
            col = start_col + (i if self.orientation == "H" else 0)
            cells.append((row, col))

    def mouseClick(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        
        if event.button == 2:
            if self.phase == "placing":
                self.placementPreview(event.pos)
                return
        
        if event.button == 3:
            if self.phase == "placing":
                self._confirm_placement()
                return
            if self.phase == "game":
                self._attempt_shot(event.pos)
                return

    def toggleOrientation(self):
        pass

    def updateCell(self, board_name, row, col, state):
        pass

    def confirmPlacement(self):
        pass

    def attemptShot(self, mouse_pos):
        pass

    def validPlacement(self, cells):
        pass

    def forbidden(self, cells):
        pass

    