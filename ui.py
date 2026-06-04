import pygame

# grid class helper handles board drawing and finds which cell is under the mouse
class Grid:
    def __init__(self, rows, cols, cell_width, cell_height, origin):
        self.rows = rows
        self.cols = cols
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.origin = origin

# draw grid lines for each cell on the board
    def draw(self, surface):
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(
                    self.origin[0] + col * self.cell_width,
                    self.origin[1] + row * self.cell_height,
                    self.cell_width,
                    self.cell_height,
                )
                pygame.draw.rect(surface, (0, 0, 0), rect, 1)

# convert a mouse position into a grid row/col if inside the grid
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
    
# ui state and game board logic for battleship placement and firing
class UI:
    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3
    FORBIDDEN = 4
    PREVIEW = 5
    PENDING = 6

    def __init__(self, screen, rows=10, cols=10, cell_size=40, margin=20):
        self.screen = screen
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.header_height = 50
        self.totalhits = 0
        left_origin = (margin, self.header_height + margin)
        right_origin = (margin * 2 + cols * cell_size, self.header_height + margin)
        self.player_grid = Grid(rows, cols, cell_size, cell_size, left_origin)
        self.enemy_grid = Grid(rows, cols, cell_size, cell_size, right_origin)

        self.player_board = self._new_board()
        self.enemy_board = self._new_board()
        self.totalhits = 0
        self.phase = "placing"
        self.turn = "player"
        self.ready = False
        self.lock_input = False
        self.game_over = False
        self.winner_text = None

        self.shot_fired = False
        self.shot_coordinates = None
        self.aim_cell = None

        self.orientation = "H"
        self.preview_cells = []
        self.preview_valid = False

# list of ships that must be placed in order before the game begins
        self.ship_queue = [
            ("Aircraft Carrier", 5),
            ("Battleship", 4),
            ("Submarine", 3),
            ("Destroyer", 3),
            ("Patrol Boat", 2),
        ]
        self.totalcells = sum(size for _, size in self.ship_queue)
        self.placed_ships = []

        self.font = pygame.font.SysFont(None, 28)
        self.header_text = ""
        self.updateStatusHeader()

# build a blank grid filled with EMPTY cell states
    def _new_board(self):
        return [[self.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        
# draw the header text describing current phase and actions
    def updateStatusHeader(self):
        if self.game_over:
            if self.winner_text:
                self.header_text = f"Game over - {self.winner_text}"
            else:
                self.header_text = "Game over"
        elif self.phase == "placing":
            if self.ship_queue:
                ship_name, ship_size = self.ship_queue[0]
                self.header_text = (
                    f"Placing: {ship_name} ({ship_size}) | "
                    f"Orientation: {self.orientation} | MB1 preview, MB2 confirm"
                )
            else:
                self.header_text = "All ships placed. Waiting for opponent."
        elif self.phase == "game":
            turn_text = "Your turn" if self.turn == "player" else "Enemy's turn"
            if self.turn == "player":
                self.header_text = f"Game phase - {turn_text} | MB1 preview, MB2 confirm"
            else:
                self.header_text = f"Game phase - {turn_text}"
        else:
            self.header_text = "Unknown phase"

        header_rect = pygame.Rect(0, 0, self.screen.get_width(), self.header_height)
        pygame.draw.rect(self.screen, (230, 230, 230), header_rect)
        text_surf = self.font.render(self.header_text, True, (20, 20, 20))
        self.screen.blit(text_surf, (self.margin, 12))

# draw both player and enemy battle grids onto the screen
    def drawGrids(self):
        self._draw_board(self.player_grid, self.player_board, show_ships=True)
        self._draw_board(self.enemy_grid, self.enemy_board, show_ships=False)
        self.player_grid.draw(self.screen)
        self.enemy_grid.draw(self.screen)

# helper to draw a single grid board and any preview squares
    def _draw_board(self, grid, board, show_ships):
        for row in range(self.rows):
            for col in range(self.cols):
                state = board[row][col]
                rect = pygame.Rect(
                    grid.origin[0] + col * grid.cell_width,
                    grid.origin[1] + row * grid.cell_height,
                    grid.cell_width,
                    grid.cell_height,
                )
                color = None
                if state == self.SHIP and show_ships:
                    color = (30, 30, 30)
                elif state == self.HIT:
                    color = (200, 60, 60)
                elif state == self.MISS:
                    color = (200, 200, 200)
                elif state == self.PENDING:
                    color = (220, 180, 60)
                elif state == self.PREVIEW:
                    color = (80, 130, 200)
                if color:
                    pygame.draw.rect(self.screen, color, rect)

        if grid is self.player_grid and self.preview_cells:
            preview_color = (80, 180, 80) if self.preview_valid else (200, 80, 80)
            for row, col in self.preview_cells:
                rect = pygame.Rect(
                    grid.origin[0] + col * grid.cell_width,
                    grid.origin[1] + row * grid.cell_height,
                    grid.cell_width,
                    grid.cell_height,
                )
                pygame.draw.rect(self.screen, preview_color, rect)

# compute the preview placement cells when mouse is over the player grid
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

        self.preview_cells = cells
        self.preview_valid = self._valid_placement(cells)

# route mouse clicks to placement preview/confirmation or shot preview/confirmation
    def mouseClick(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        
        if event.button == 1:
# left click previews a placement or a shot target
            if self.phase == "placing":
                self.placementPreview(event.pos)
                return
            if self.phase == "game":
                self.previewShot(event.pos)
                return
        
        if event.button == 3:
# right click confirms the current preview action
            if self.phase == "placing":
                self.confirmPlacement()
                return
            if self.phase == "game":
                self.confirmShot(event.pos)
                return

# flip ship placement orientation and update the status header
    def toggleOrientation(self):
        self.orientation = "V" if self.orientation == "H" else "H"
        self.updateStatusHeader()

# safely update a board cell state if the coordinates are valid
    def updateCell(self, board_name, row, col, state):
        board = self.player_board if board_name == "player" else self.enemy_board
        if 0 <= row < self.rows and 0 <= col < self.cols:
            board[row][col] = state

# confirm the current ship preview placement and lock it onto the board
    def confirmPlacement(self):
        if not self.preview_cells or not self.preview_valid:
            return
        
        ship_name, ship_size = self.ship_queue.pop(0)
        for row, col in self.preview_cells:
            self.updateCell("player", row, col, self.SHIP)

        self._mark_forbidden(self.preview_cells)
        self.placed_ships.append(
            {"name": ship_name, "size": ship_size, "cells": list(self.preview_cells), "hits": 0}
        )

        self.preview_cells = []
        self.preview_valid = False

        if not self.ship_queue:
            self.ready = True
            self.phase = "game"
            
        self.updateStatusHeader()
# clear any aiming preview from the enemy grid
    def clear_shot_preview(self):
        if self.aim_cell:
            row, col = self.aim_cell
            if self.enemy_board[row][col] == self.PREVIEW:
                self.updateCell("enemy", row, col, self.EMPTY)
        self.aim_cell = None

# show shot preview on the enemy grid when player can fire
    def previewShot(self, mouse_pos):
        if self.lock_input or self.turn != "player" or self.game_over:
            return
        cell = self.enemy_grid.cell_at_pos(mouse_pos)
        if cell is None:
            return
        row, col = cell
        current = self.enemy_board[row][col]
        if current in (self.HIT, self.MISS, self.PENDING):
            return
        self.clear_shot_preview()
        self.updateCell("enemy", row, col, self.PREVIEW)
        self.aim_cell = (row, col)

# confirm the shot and mark it pending until result arrives
    def confirmShot(self, mouse_pos):
        if self.lock_input or self.turn != "player" or self.game_over:
            return
        if self.aim_cell is None:
            return
        row, col = self.aim_cell
        if self.enemy_board[row][col] != self.PREVIEW:
            return
        self.updateCell("enemy", row, col, self.PENDING)
        self.lock_input = True
        self.shot_fired = True
        self.shot_coordinates = (row, col)
        self.aim_cell = None

# validate that the ship cells fit and do not collide with existing ships
    def _valid_placement(self, cells):
        for row, col in cells:
            if row < 0 or col < 0 or row >= self.rows or col >= self.cols:
                return False
            if self.player_board[row][col] in (self.SHIP, self.FORBIDDEN):
                return False
        
        for row, col in cells:
            for n_row in range(row - 1, row + 2):
                for n_col in range(col - 1, col + 2):
                    if 0 <= n_row < self.rows and 0 <= n_col < self.cols:
                        if self.player_board[n_row][n_col] == self.SHIP:
                            return False
        return True
                        


# mark surrounding cells as forbidden after placing a ship
    def _mark_forbidden(self, cells):
        for row, col in cells:
            for n_row in range(row - 1, row + 2):
                for n_col in range(col - 1, col + 2):
                    if 0 <= n_row < self.rows and 0 <= n_col < self.cols:
                        if self.player_board[n_row][n_col] == self.EMPTY:
                            self.player_board[n_row][n_col] = self.FORBIDDEN

# compute all border cells around a sunk ship for marking misses
    def surrounding_cells(self, cells):
        border = set()
        cell_set = set(cells)
        for row, col in cell_set:
            for n_row in range(row - 1, row + 2):
                for n_col in range(col - 1, col + 2):
                    if 0 <= n_row < self.rows and 0 <= n_col < self.cols:
                        if (n_row, n_col) not in cell_set:
                            border.add((n_row, n_col))
        return list(border)

# find which placed ship occupies a specific board cell
    def ship_at(self, row, col):
        for ship in self.placed_ships:
            if (row, col) in ship["cells"]:
                return ship
        return None

# register a hit on a ship and return it if sunk
    def register_hit(self, row, col):
        ship = self.ship_at(row, col)
        if not ship:
            return None
        ship["hits"] += 1
        if ship["hits"] >= ship["size"]:
            return ship
        return None

# return true when every placed ship has been sunk
    def all_ships_sunk(self):
        return all(ship["hits"] >= ship["size"] for ship in self.placed_ships)


# button class helper for mode selection and basic hover rendering
class Button:
# button constructor creates the clickable rectangle and text style
    def __init__(self, x, y, w, h, text, font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.Font(None, 32) if font is None else font
        self.color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.active_color = (50, 150, 255)
        self.current_color = self.color
        self.hovered = False

# return true when this button is clicked by the mouse
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# update hover state and button color based on mouse position
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

# draw the button rectangle and text onto the surface
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 3)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

