from __future__ import annotations
from .data_structures import Board, Cell, Vec2, Size, Area
from typing import List, Dict, Union
from enum import Enum
import pygame
import sys
import random

pygame.init()

def to_pygame(coords, height):
    """Convert coordinates into pygame coordinates (lower-left => top left)."""
    return (coords[0], height - coords[1])

class CellStates(Enum):
    editable = "editable"
    locked = "locked"
    select = "select"

class CellSprite:
    SIZE:Size = None

    def __init__(self, game, screen, center_x:float, center_y:float, logic_cell:Cell, texture_setting:dict):
        self.game = game
        self.screen = screen
        self.logic_cell = logic_cell
        self.text = None

        self.cell_mode:CellStates = CellStates.locked if self.logic_cell.locked else CellStates.editable

        self.pos = Vec2(*to_pygame((center_x, center_y), self.game.screen_size.height))
        self.point_a = Vec2(center_x-(self.SIZE.width/2), (center_y-self.SIZE.height/2))
        self.point_b = Vec2(center_x+(self.SIZE.width/2), (center_y+self.SIZE.height/2))
        self.area = pygame.Rect(*self.point_a.to_tuple,
                                *self.point_b.to_tuple)

        self._load_textures(texture_setting)
        self.create_surface()

    def _load_textures(self, texture_setting:dict):
        textur_paths = {
            CellStates.editable: f'resources/imgs/editable_cell_{texture_setting["type"]}.png',
            CellStates.locked: f'resources/imgs/locked_cell_{texture_setting["type"]}.png',
            CellStates.select: f'resources/imgs/select_cell_{texture_setting["type"]}.png',
        }
        self.texture_map = {}
        for key, path in textur_paths.items():
            texture = pygame.image.load(path)
            texture = pygame.transform.rotate(texture, texture_setting["rotation"])
            self.texture_map[key] = texture

    def create_surface(self):
        self.texture = self.texture_map[self.cell_mode]
        resized_texture = pygame.transform.scale(self.texture, self.SIZE.to_tuple)
        self.texture_surface = pygame.Surface(self.SIZE.to_tuple)
        self.texture_surface.blit(resized_texture, (0, 0))

    def set_char(self, char:str|int):
        self.create_surface()
        font = pygame.font.Font(None, 80)
        self.text = font.render(str(char), True, (255, 255, 255))
        text_pos = Vec2((self.SIZE.width/2)-(self.text.get_width()/2),
                       (self.SIZE.height/2)-(self.text.get_height()/2))
        self.texture_surface.blit(self.text, text_pos.to_tuple)

    def update(self):
        self.create_surface()
        if self.logic_cell.state is not None:
            self.set_char(self.logic_cell.state)

    def draw(self):
        self.screen.blit(self.texture_surface, self.point_a.to_tuple)

        # debug
        # pygame.draw.circle(self.screen, (255,0,0,0), self.point_a.to_tuple, 6)
        # pygame.draw.circle(self.screen, (0,255,0,0), self.point_b.to_tuple, 6)

class Game:
    def _create_screen(self):
        self.screen = pygame.display.set_mode(self.screen_size.to_tuple)
        pygame.display.set_caption("Sudok")
        icon = pygame.image.load('resources/imgs/icon.png')
        pygame.display.set_icon(icon)

    def __init__(self, screen_size:Size, board:Board):
        self.game_active = True
        self.screen_size = screen_size
        self._create_screen()

        self.board:Board = board
        self.cell_sprites = []
        self._create_board()

        self.selected_cell = None

    def _calculate_board_size(self):
        total_cells = self.board.total_board_size
        self.cell_size = Size(self.screen_size.width / total_cells.width,
                         self.screen_size.height / total_cells.height)
        CellSprite.SIZE = self.cell_size
        self.cell_size.apply(int)

    def _choose_cell_texture(self, x_pos:int, y_pos:int) -> Dict[str, Union[str, int]]:
        section_dimensions = self.board.section_dimensions

        # Check for corners first
        if (x_pos, y_pos) == (1, 1):
            return {"type": "corner", "rotation": 0}
        elif (x_pos, y_pos) == (section_dimensions.width, 1):
            return {"type": "corner", "rotation": -90}
        elif (x_pos, y_pos) == (1, section_dimensions.height):
            return {"type": "corner", "rotation": 90}
        elif (x_pos, y_pos) == (section_dimensions.width, section_dimensions.height):
            return {"type": "corner", "rotation": 180}

        # Check for edge
        elif x_pos == 1:
            return {"type": "edge", "rotation": 0}
        elif x_pos == section_dimensions.width:
            return {"type": "edge", "rotation": 180}
        elif y_pos == 1:
            return {"type": "edge", "rotation": -90}
        elif y_pos == section_dimensions.height:
            return {"type": "edge", "rotation": 90}

        # Default to mid piece if not a edge or corner
        return {"type": "mid", "rotation": 0}


    def _create_board(self):
        self._calculate_board_size()
        section_dimensions = self.board.section_dimensions

        y_count = 0
        for index_y, y in zip(range(0, self.board.total_board_size.height), range(int(self.cell_size.height/2), int(self.screen_size.height), self.cell_size.height)):
            y_count +=1
            x_count = 0

            for index_x, x in zip(range(0, self.board.total_board_size.width), range(int(self.cell_size.width/2), int(self.screen_size.width), self.cell_size.width)):
                x_count += 1

                logic_cell:Cell = self.board.active_cells.get((index_x, index_y))
                texture_setting = self._choose_cell_texture(x_count, y_count)
                sprite_cell = CellSprite(self, self.screen, x, y, logic_cell, texture_setting)
                self.cell_sprites.append(sprite_cell)

                if x_count >= section_dimensions.width:
                    x_count = 0

            if y_count >= section_dimensions.height:
                    y_count = 0

    def on_draw(self):
        for cell in self.cell_sprites:
            cell.draw()

        # debug
        # pygame.draw.circle(self.screen, (255,0,0,0), (10, 10), 6)
        # pygame.draw.circle(self.screen, (0,255,0,0), (self.screen_size.x-10, self.screen_size.y-10), 6)

    def on_update(self):
        for cell in self.cell_sprites:
            cell.update()

    def on_cell_click(self, new_cell:CellSprite):
        if new_cell.logic_cell.locked:
            return

        old_cell:CellSprite = self.selected_cell
        if old_cell is not None:
            old_cell.cell_mode = CellStates.editable

        new_cell.cell_mode = CellStates.select
        self.selected_cell = new_cell

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_active = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = Vec2(*pygame.mouse.get_pos())
                if event.button == 1:
                    for cell in self.cell_sprites:
                        cell:CellSprite
                        if position.is_within(cell.point_a, cell.point_b):
                            self.on_cell_click(cell)
                            break
            if event.type == pygame.KEYDOWN:
                num = None
                if pygame.K_KP1 <= event.key <= pygame.K_KP9:
                    num = event.key - pygame.K_KP0
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    num = event.key - pygame.K_0
                if num is not None and self.selected_cell is not None:
                    self.selected_cell.logic_cell.state = num

    def _game_loop(self):
        while self.game_active:
            self._handle_events()
            self.on_update()
            self.screen.fill((0, 0, 0))  # Black background
            self.on_draw()
            pygame.display.update()

    def run(self):
        self._game_loop()
        pygame.quit()
        sys.exit()
