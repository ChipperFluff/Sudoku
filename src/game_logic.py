from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Dict, Union

@dataclass
class Vec2:
    """Represents a 2D vector or position."""
    x: int
    y: int

    @property
    def pos(self) -> Tuple[int, int]:
        """Returns the position as a tuple."""
        return self.x, self.y

@dataclass
class Cell:
    """Represents a single cell in a Sudoku puzzle."""
    global_pos: Vec2
    local_pos: Vec2 = field(default=None)
    state: str = field(default=None)
    locked: bool = field(default=False)

    @classmethod
    def load(cls, data: Dict[str, Union[Tuple[int, int], str, bool]]) -> Cell:
        """Loads a cell from saved data."""
        global_pos = Vec2(*data["global_pos"])
        local_pos = Vec2(*data["local_pos"])
        state = data["state"]
        locked = data.get("locked", False)
        return Cell(global_pos, local_pos, state, locked)

    def save(self) -> Dict[str, Union[Tuple[int, int], str, bool]]:
        """Saves the cell to a dictionary format."""
        return {
            "global_pos": self.global_pos.pos,
            "local_pos": self.local_pos.pos if self.local_pos else None,
            "state": self.state,
            "locked": self.locked
        }

@dataclass
class Section:
    """Represents a section (block) in a Sudoku puzzle."""
    members: Dict[Tuple[int, int], Cell] = field(default_factory=dict)

class Board:
    """Represents the Sudoku puzzle board."""
    def __init__(self, board_size: Vec2, section_size: Vec2):
        """Initializes the board with the given dimensions."""
        self.board_size = board_size
        self.section_size = section_size
        self.active_cells: Dict[Tuple[int, int], Cell] = {}
        self.sections: Dict[Tuple[int, int], Section] = {}
        self._create_active_cells()
        self._divide_sections()

    def _create_active_cells(self) -> None:
        """Creates all active cells based on board size."""
        columns = self.board_size.x * self.section_size.x
        rows = self.board_size.y * self.section_size.y
        for cell_y in range(rows):
            for cell_x in range(columns):
                global_pos = Vec2(cell_x, cell_y)
                new_cell = Cell(global_pos)
                self.active_cells[global_pos.pos] = new_cell

    def _divide_single_section(self, start_column: Vec2) -> Section:
        """Divides and populates a single section."""
        section = Section()
        start = Vec2(start_column.x, start_column.y)
        end = Vec2(start_column.x + self.section_size.x,
                   start_column.y + self.section_size.y)
        for y_index, y in enumerate(range(start.y, end.y)):
            for x_index, x in enumerate(range(start.x, end.x)):
                cell = self.active_cells[(x, y)]
                cell.local_pos = Vec2(x_index, y_index)
                section.members[(x, y)] = cell
        return section

    def _divide_board_row(self, section_row_start: int) -> List[Section]:
        """Divides a row of the board into sections."""
        section_current_column = 0
        section_result = []
        for _ in range(self.board_size.x):
            start_pos = Vec2(section_current_column, section_row_start)
            section_result.append(self._divide_single_section(start_pos))
            section_current_column += self.section_size.x
        return section_result

    def _divide_sections(self) -> None:
        """Divides the entire board into sections."""
        section_row_start = 0
        for board_row in range(self.board_size.y):
            divided_rows = self._divide_board_row(section_row_start)
            for index, divided_section in enumerate(divided_rows):
                self.sections[(index, board_row)] = divided_section
            section_row_start += self.section_size.y
