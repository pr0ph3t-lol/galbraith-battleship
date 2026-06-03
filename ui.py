import pygame

class Grid:
    def __init__(self, rows, cols, cell_width, cell_height, origin):
        self.rows = rows
        self.cols = cols
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.origin = origin

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

        self.shot_fired = False
        self.shot_coordinates = None

        self.orientation = "H"
        self.preview_cells = []
        self.preview_valid = False

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

    def _new_board(self):
        return [[self.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        
    def updateStatusHeader(self):
        if self.phase == "placing":
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
            self.header_text = f"Game phase - {turn_text}"
        else:
            self.header_text = "Unknown phase"

        header_rect = pygame.Rect(0, 0, self.screen.get_width(), self.header_height)
        pygame.draw.rect(self.screen, (230, 230, 230), header_rect)
        text_surf = self.font.render(self.header_text, True, (20, 20, 20))
        self.screen.blit(text_surf, (self.margin, 12))

    def drawGrids(self):
        self._draw_board(self.player_grid, self.player_board, show_ships=True)
        self._draw_board(self.enemy_grid, self.enemy_board, show_ships=False)
        self.player_grid.draw(self.screen)
        self.enemy_grid.draw(self.screen)

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

    def mouseClick(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        
        if event.button == 1:
            if self.phase == "placing":
                self.placementPreview(event.pos)
                return
        
        if event.button == 3:
            if self.phase == "placing":
                self.confirmPlacement()
                return
            if self.phase == "game":
                self.attemptShot(event.pos)
                return

    def toggleOrientation(self):
        self.orientation = "V" if self.orientation == "H" else "H"
        self.updateStatusHeader()

    def updateCell(self, board_name, row, col, state):
        board = self.player_board if board_name == "player" else self.enemy_board
        if 0 <= row < self.rows and 0 <= col < self.cols:
            board[row][col] = state

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
    def attemptShot(self, mouse_pos):
        if self.lock_input or self.turn != "player":
            return
        cell = self.enemy_grid.cell_at_pos(mouse_pos)
        if cell is None:
            return
        row, col = cell
        current = self.enemy_board[row][col]
        if current in (self.HIT, self.MISS, self.PENDING):
            return

        self.updateCell("enemy", row, col, self.PENDING)
        self.lock_input = True
        self.shot_fired = True
        self.shot_coordinates = (row, col)

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
                        


    def _mark_forbidden(self, cells):
        for row, col in cells:
            for n_row in range(row - 1, row + 2):
                for n_col in range(col - 1, col + 2):
                    if 0 <= n_row < self.rows and 0 <= n_col < self.cols:
                        if self.player_board[n_row][n_col] == self.EMPTY:
                            self.player_board[n_row][n_col] = self.FORBIDDEN


class Button:
    def __init__(self, x, y, w, h, text, font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.Font(None, 32) if font is None else font
        self.color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.active_color = (50, 150, 255)
        self.current_color = self.color
        self.hovered = False

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 3)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

