from __future__ import annotations
from .data_structures import Board, Cell, Vec2, Size, Area
from .ui_manager import Window, View
from typing import List, Dict, Union
from enum import Enum
import pygame


def to_pygame(coords, height):
    """Convert coordinates into pygame coordinates (lower-left => top left)."""
    return (coords[0], height - coords[1])

class CellStates(Enum):
    editable = "editable"
    locked = "locked"
    select = "select"
    error = "error"

class CellSprite:
    SIZE:Size = None

    def __init__(self, game, center_x:float, center_y:float, logic_cell:Cell, texture_setting:dict):
        self.game = game
        self.screen = game.window.screen
        self.logic_cell = logic_cell
        self.text = None

        self.cell_mode:CellStates = CellStates.locked if self.logic_cell.locked else CellStates.editable

        self.pos = Vec2(*to_pygame((center_x, center_y), self.game.window.screen_size.height))
        self.point_a = Vec2(center_x-(self.SIZE.width/2), (center_y-self.SIZE.height/2))
        self.point_b = Vec2(center_x+(self.SIZE.width/2), (center_y+self.SIZE.height/2))
        self.area = pygame.Rect(*self.point_a.to_tuple,
                                *self.point_b.to_tuple)

        self._load_textures(texture_setting)
        self.create_surface()
        self.selected = False

    def _load_textures(self, texture_setting:dict):
        textur_paths = {
            CellStates.editable: f'resources/imgs/editable_cell_{texture_setting["type"]}.png',
            CellStates.locked: f'resources/imgs/locked_cell_{texture_setting["type"]}.png',
            CellStates.select: f'resources/imgs/select_cell_{texture_setting["type"]}.png',
            CellStates.error: f'resources/imgs/error_cell_{texture_setting["type"]}.png',
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
        self.game.window.screen.blit(self.texture_surface, self.point_a.to_tuple)

        # debug
        # pygame.draw.circle(self.game.window.screen, (255,0,0,0), self.point_a.to_tuple, 6)
        # pygame.draw.circle(self.game.window.screen, (0,255,0,0), self.point_b.to_tuple, 6)

class BasicGame(View):
    def __init__(self, board:Board):
        super().__init__()
        self.board:Board = board
        self.cell_sprites = []
        self._create_board()

        self.can_select_locked = False
        self.can_edit_locked = False

        self.selected_cell:CellSprite = None

    def _calculate_board_size(self):
        total_cells = self.board.total_board_size
        self.cell_size = Size(self.window.screen_size.width / total_cells.width,
                         self.window.screen_size.height / total_cells.height)
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
        for index_y, y in zip(range(0, self.board.total_board_size.height), range(int(self.cell_size.height/2), int(self.window.screen_size.height), self.cell_size.height)):
            y_count +=1
            x_count = 0

            for index_x, x in zip(range(0, self.board.total_board_size.width), range(int(self.cell_size.width/2), int(self.window.screen_size.width), self.cell_size.width)):
                x_count += 1

                logic_cell:Cell = self.board.active_cells.get((index_x, index_y))
                texture_setting = self._choose_cell_texture(x_count, y_count)
                sprite_cell = CellSprite(self, x, y, logic_cell, texture_setting)
                logic_cell.sprite = sprite_cell
                self.cell_sprites.append(sprite_cell)

                if x_count >= section_dimensions.width:
                    x_count = 0

            if y_count >= section_dimensions.height:
                    y_count = 0

    def on_draw(self, screen):
        for cell in self.cell_sprites:
            cell.draw()

        # debug
        # pygame.draw.circle(screen, (255,0,0,0), (10, 10), 6)
        # pygame.draw.circle(screen, (0,255,0,0), (self.window.screen_size.x-10, self.window.screen_size.y-10), 6)

    def on_update(self):
        for cell in self.cell_sprites:
            cell.update()

        self.check_board()

    def check_section(self, objects):
        state_map = {}  # Dictionary to map state to objects with that state
        duplicates = []  # List to hold objects with duplicate states

        for obj in objects:
            state = obj.state
            # Skip the object if its state is None
            if state is None:
                continue
            if state in state_map:
                state_map[state].append(obj)
            else:
                state_map[state] = [obj]

        for state_objects in state_map.values():
            if len(state_objects) > 1:  # If more than one object shares the same state
                duplicates.extend(state_objects)  # Add all objects with this state to the duplicates list

        return duplicates

    def check_board(self):
        for pos, section in self.board.sections.items():
            for cell in section.members.values():
                if cell.locked or cell.sprite.selected:
                    continue
                cell.sprite.cell_mode = CellStates.editable
            wrong = self.check_section(section.members.values())
            for cell in wrong:
                if cell.locked or cell.sprite.selected:
                    continue
                cell.sprite.cell_mode = CellStates.error

    def on_cell_click(self, new_cell:CellSprite):
        if self.selected_cell is None:
            self.select_cell(new_cell)
            return

        old_cell = self.selected_cell
        old_cell_pos = old_cell.logic_cell.global_pos.to_tuple
        new_cell_pos = new_cell.logic_cell.global_pos.to_tuple

        if old_cell_pos == new_cell_pos:
            self.deselect_cell()
            return

        self.deselect_cell()
        self.select_cell(new_cell)

    def select_cell(self, new_cell:CellSprite):
        if new_cell.logic_cell.locked and not self.can_select_locked:
            return

        old_cell:CellSprite = self.selected_cell
        if old_cell is not None:
            old_cell.cell_mode = CellStates.editable

        new_cell.cell_mode = CellStates.select
        self.selected_cell = new_cell
        self.selected_cell.selected = True

    def deselect_cell(self):
        if self.selected_cell is None:
            return
        self.selected_cell.selected = False
        self.selected_cell.cell_mode = CellStates.editable
        self.selected_cell = None

    def move_selection(self, dx: int, dy: int):
        current_cell = self.selected_cell
        if current_cell is None:
            print("No cell is currently selected.")
            return

        # Remember the initial position in case we need to revert the selection.
        initial_cell = current_cell

        pointer = current_cell

        # Counter to prevent infinite loops.
        attempt_counter = 0
        max_attempts = self.board.total_board_size.height  # Arbitrary large number to prevent infinite loops

        while attempt_counter < max_attempts:
            next_pos = pointer.logic_cell.global_pos.add(dx, dy)

            # Ensuring .to_tuple() is called correctly if it's a method.
            next_cell = self.board.active_cells.get(next_pos.to_tuple() if callable(next_pos.to_tuple) else next_pos.to_tuple)

            if next_cell is None:
                print(f"Reached edge or empty spot at {next_pos}. No movement due to locked cells or board edge.")
                # Instead of re-selecting the current cell, revert to the initial cell.
                self.deselect_cell()
                self.select_cell(initial_cell)
                return
            next_cell = next_cell.sprite

            if not next_cell.logic_cell.locked:
                print(f"Moving to next cell at {next_pos}.")
                self.deselect_cell()
                self.select_cell(next_cell)
                return
            else:
                print(f"Cell at {next_pos} is locked. Trying next cell.")

            pointer = next_cell
            attempt_counter += 1

        if attempt_counter >= max_attempts:
            print("Max attempts reached. Stopping to prevent infinite loop.")
            # Revert to the initial selection if all attempts fail.
            self.deselect_cell()
            self.select_cell(initial_cell)

    def on_mouse_click(self, up:bool, pos:Vec2, button:int):
        found_cell:CellSprite = None
        for cell in self.cell_sprites:
            cell:CellSprite
            if pos.is_within(cell.point_a, cell.point_b):
                found_cell = cell
                break
        if found_cell is None:
            return
        if button == 1 and not up:
            found_cell.logic_cell.locked = True
            found_cell.cell_mode = CellStates.locked
        if button == 3 and not up:
            self.on_cell_click(found_cell)

    def on_keyboard(self, up:bool, key):
        if key == pygame.K_ESCAPE:
            self.deselect_cell()
            return
        if key == pygame.K_DELETE or key == pygame.K_BACKSPACE:
            if self.selected_cell is None:
                return
            self.selected_cell.logic_cell.state = None
            return

        if not up:
            if key == pygame.K_LEFT:  # Left arrow key
                self.move_selection(-1, 0)
            elif key == pygame.K_RIGHT:  # Right arrow key
                self.move_selection(1, 0)
            elif key == pygame.K_UP:  # Up arrow key
                self.move_selection(0, -1)
            elif key == pygame.K_DOWN:  # Down arrow key
                self.move_selection(0, 1)

        num = None
        if pygame.K_KP1 <= key <= pygame.K_KP9:
            num = key - pygame.K_KP0
        elif pygame.K_1 <= key <= pygame.K_9:
            num = key - pygame.K_0
        if num is None:
            return
        if self.selected_cell is None:
            return
        if self.selected_cell.logic_cell.locked and not self.can_edit_locked:
            return
        self.selected_cell.logic_cell.state = num

class Window(Window):
    def __init__(self, screen_size:Size):
        super().__init__(screen_size, "Sudoku", r"resources\imgs\icon.png", 15)
        num_sections = Size(3, 3)
        section_dimensions = Size(3, 3)
        board = Board(num_sections, section_dimensions)
        game_view = BasicGame(board)
        self.show_view(game_view)
