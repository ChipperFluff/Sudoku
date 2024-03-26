from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Union

@dataclass
class Vec2:
    x:int
    y:int

    @property
    def pos(self) -> Tuple[int, int]:
        return self.x, self.y

@dataclass
class Cell:
    global_pos:Vec2
    local_pos:Vec2 = field(default=None)
    state:str = field(default=None)

    @classmethod
    def load(cls, data:Dict[str, Union[Tuple, str]]) -> Cell:
        """
        load cell from save data

        Args:
            data (dict): saved cell

        Returns:
            Cell: loaded cell
        """
        global_pos = Vec2(*data["global_pos"])
        local_pos = Vec2(*data["local_pos"])
        state = data["state"]
        return Cell(global_pos, local_pos, state)

    def save(self) -> Dict[str, Union[Tuple, str]]:
        """
        returns a dict version of the cell

        Returns:
            dict: cell in dict format
        """
        return {
            "global_pos": self.global_pos,
            "local_pos": self.local_pos,
            "state": self.state
        }

@dataclass
class Section:
    members:Dict[Cell] = field(default_factory=dict)

class Board:
    def _create_active_cells(self) -> None:
        columns = self.board_size.x * self.section_size.x
        rows = self.board_size.y * self.section_size.y

        for cell_y in range(rows):
            for cell_x in range(columns):
                global_pos = Vec2(cell_x, cell_y)
                new_cell = Cell(global_pos)
                self.active_cells[global_pos.pos] = new_cell

    def _divide_single_section(self, start_column:Vec2) -> Section:
        section:Section = Section()
        print(f"Div single cell:\n{start_column=}")
        start = Vec2(start_column.x, start_column.y)
        end = Vec2(start_column.x+self.section_size.x,
                   start_column.y+self.section_size.y)
        for y_index, y in enumerate(range(start.y, end.y)):
            for x_index, x in enumerate(range(start.x, end.x)):
                print(f"Add: {(x, y)}")
                cell = self.active_cells[(x, y)]
                cell.local_pos = Vec2(x_index, y_index)
                section.members[(x, y)] = self.active_cells[(x, y)]

        return section

    def _divide_board_row(self, section_row_start:int):
        section_current_column = 0
        section_result = []

        for _ in range(self.board_size.x):
            start_pos = Vec2(section_current_column, section_row_start)
            section_result.append(self._divide_single_section(start_pos))

            section_current_column += self.section_size.x

        return section_result

    def _divide_sections(self):
        section_row_start = 0

        for board_row in range(self.board_size.y):
            divided_rows = self._divide_board_row(section_row_start)

            for index, divided_section in enumerate(divided_rows):
                self.sections[(index, board_row)] = divided_section

            section_row_start += self.section_size.y


    def __init__(self, board_size:Vec2, section_size:Vec2):
        self.board_size = board_size
        self.section_size = section_size

        self.active_cells:Dict[Tuple] = {}
        self.sections:Dict[Tuple, Section] = {}

        self._create_active_cells()
        self._divide_sections()

board_size = Vec2(3, 3)
section_size = Vec2(1, 3)
board = Board(board_size, section_size)

for y in range(board_size.y * section_size.y):
    line = ""
    for x in range(board_size.x * section_size.x):
        line += f"{board.active_cells[(x, y)].local_pos.pos} "
    print(y, "|", line)