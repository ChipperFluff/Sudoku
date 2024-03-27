import arcade
from .game_logic import Board, Cell, Vec2
from typing import List, Dict, Union

class CellSprite(arcade.Sprite):
    SIZE = None

    def __init__(self, center_x:float, center_y:float, logic_cell:Cell, texture_setting:dict):
        self.logic_cell = logic_cell

        locked = "close" if self.logic_cell.locked else "open"
        texture_path = f'src/resources/imgs/cell_{texture_setting["type"]}_{locked}.png'

        super().__init__(filename=texture_path,
                         center_x=center_x,
                         center_y=center_y)

        self.angle = texture_setting["rotation"]
        self.width = self.SIZE.x + 5
        self.height = self.SIZE.x + 5

class Game(arcade.Window):
    def __init__(self, board:Board):
        super().__init__(title="Sudoku", height=900, width=900)

        self.board:Board = board
        self.cell_sprites = []
        self.board_dimensions:Vec2 = None
        self.cell_size:Vec2 = None
        self._create_board()

    def _calculate_board_size(self):
        MARGIN_PERCENTAGES_VERTICAL = 400
        MARGIN_PERCENTAGES_HORIZONTAL = 600

        vertical_margin = (MARGIN_PERCENTAGES_VERTICAL/self.height) * 100
        horizontal_margin = (MARGIN_PERCENTAGES_HORIZONTAL/self.width) * 100

        field_start = Vec2(horizontal_margin, self.height-vertical_margin) # top left corner
        field_stop = Vec2(self.width-horizontal_margin, vertical_margin) # bottom right corner
        self.board_dimensions = Vec2(field_start, field_stop)

        field_size = Vec2(field_stop.x - field_start.x,
                          field_stop.y - field_start.y)

        total_cells = self.board.total_board_size

        self.cell_size = Vec2(field_size.x / total_cells.x,
                         field_size.y / total_cells.y)
        CellSprite.SIZE = self.cell_size

        Vec2.apply_stack(field_start, field_stop, field_size, self.cell_size)

    def _choose_cell_texture(self, x_pos:int, y_pos:int) -> Dict[str, Union[str, int]]:
        section_dimensions = self.board.section_dimensions

        # Check for corners first
        if (x_pos, y_pos) == (1, 1):
            return {"type": "corner", "rotation": 0}
        elif (x_pos, y_pos) == (section_dimensions.x, 1):
            return {"type": "corner", "rotation": -90}
        elif (x_pos, y_pos) == (1, section_dimensions.y):
            return {"type": "corner", "rotation": 90}
        elif (x_pos, y_pos) == (section_dimensions.x, section_dimensions.y):
            return {"type": "corner", "rotation": 180}

        # Check for edge
        elif x_pos == 1:
            return {"type": "edge", "rotation": 0}
        elif x_pos == section_dimensions.x:
            return {"type": "edge", "rotation": 180}
        elif y_pos == 1:
            return {"type": "edge", "rotation": -90}
        elif y_pos == section_dimensions.y:
            return {"type": "edge", "rotation": 90}

        # Default to mid piece if not a edge or corner
        return {"type": "mid", "rotation": 0}


    def _create_board(self):
        self._calculate_board_size()
        section_dimensions = self.board.section_dimensions

        y_count = 0
        for index_y, y in enumerate(range(int(self.board_dimensions.x.y+(self.cell_size.y/2)), int(self.board_dimensions.y.y), self.cell_size.y)):
            y_count +=1
            x_count = 0

            for index_x, x in enumerate(range(int(self.board_dimensions.x.x+(self.cell_size.x/2)), int(self.board_dimensions.y.x), self.cell_size.x)):
                x_count += 1

                logic_cell:Cell = self.board.active_cells[(index_x, index_y)]
                texture_setting = self._choose_cell_texture(x_count, y_count)
                sprite_cell = CellSprite(x, y, logic_cell, texture_setting)
                self.cell_sprites.append(sprite_cell)

                if x_count >= section_dimensions.x:
                    x_count = 0

            if y_count >= section_dimensions.y:
                    y_count = 0

    def on_draw(self):
        arcade.start_render()
        for cell in self.cell_sprites:
            cell.draw()

    def run(self):
        arcade.run()
