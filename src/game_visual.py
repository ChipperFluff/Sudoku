import arcade
from .game_logic import Board, Cell, Vec2

class CellSprite(arcade.Sprite):
    SIZE = None

    def __init__(self, center_x:float, center_y:float, logic_cell:Cell, texture_setting:dict):
        texture_types = {"corner": "src/resources/imgs/cell_corner.png",
                         "border": "src/resources/imgs/cell_border.png",
                         "mid": "src/resources/imgs/cell_mid.png"}

        super().__init__(filename=texture_types[texture_setting["type"]],
                         center_x=center_x,
                         center_y=center_y)

        self.angle = texture_setting["rotation"]
        self.logic_cell = logic_cell
        self.width = self.SIZE.x + 5
        self.height = self.SIZE.x + 5

class Game(arcade.Window):
    def __init__(self, board:Board):
        super().__init__(title="Sudoku", height=900, width=900)

        self.board:Board = board
        self.cell_sprites = []
        self._create_board()

    def _create_board(self):
        MARGIN_PERCENTAGES_VERTICAL = 400
        MARGIN_PERCENTAGES_HORIZONTAL = 600

        vertical_margin = (MARGIN_PERCENTAGES_VERTICAL/self.height) * 100
        horizontal_margin = (MARGIN_PERCENTAGES_HORIZONTAL/self.width) * 100

        field_start = Vec2(horizontal_margin, self.height-vertical_margin) # top left corner
        field_stop = Vec2(self.width-horizontal_margin, vertical_margin) # bottom right corner

        field_size = Vec2(field_stop.x - field_start.x,
                          field_stop.y - field_start.y)

        total_cells = self.board.total_board_size

        cell_size = Vec2(field_size.x / total_cells.x,
                         field_size.y / total_cells.y)
        CellSprite.SIZE = cell_size

        Vec2.apply_stack(field_start, field_stop, field_size, cell_size)

        x_count = 0
        y_count = 0
        section_dimensions = self.board.section_dimensions

        for index_y, y in enumerate(range(int(field_start.y+(cell_size.y/2)), int(field_stop.y), cell_size.y)):
            y_count +=1
            for index_x, x in enumerate(range(int(field_start.x+(cell_size.x/2)), int(field_stop.x), cell_size.x)):
                x_count += 1
                texture_setting = {"type": "mid", "rotation": 0}

                # border
                if x_count == 1:
                    texture_setting = {"type": "border", "rotation": 0}
                elif x_count == section_dimensions.x:
                    texture_setting = {"type": "border", "rotation": 180}
                elif y_count == 1:
                    texture_setting = {"type": "border", "rotation": -90}
                elif y_count == section_dimensions.y:
                    texture_setting = {"type": "border", "rotation": 90}

                # corner
                if x_count == y_count == 1:
                    texture_setting = {"type": "corner", "rotation": 0}
                elif x_count == section_dimensions.x and y_count == 1:
                    texture_setting = {"type": "corner", "rotation": -90}
                elif x_count == 1 and y_count == section_dimensions.y:
                    texture_setting = {"type": "corner", "rotation": 90}
                elif x_count == section_dimensions.x and y_count == section_dimensions.y:
                    texture_setting = {"type": "corner", "rotation": 180}

                logic_cell:Cell = self.board.active_cells[(index_x, index_y)]
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
