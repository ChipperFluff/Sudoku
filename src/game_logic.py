from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Union, Callable
import random

@dataclass
class Vec2:
    """Represents a 2D vector or position."""
    x: int
    y: int

    @property
    def pos(self) -> Tuple[int, int]:
        """Returns the position as a tuple."""
        return self.x, self.y

    def apply(self, func: Callable[[int], int]) -> None:
        """
        Applies a function to `x` and `y` attributes, updating them with the result.

        Args:
            func: A function that modifies the value of `x` and `y`.
        """
        self.x = func(self.x)
        self.y = func(self.y)

    @staticmethod
    def apply_stack(*vecs:Vec2, func:Callable=int):
        for vec in vecs:
            vec.apply(func)

    def is_within(self, point_a: Vec2, point_b: Vec2):
        return (min(point_a.x, point_b.x) <= self.x <= max(point_a.x, point_b.x)
                and min(point_a.y, point_b.y) <= self.y <= max(point_a.y, point_b.y))

@dataclass
class Cell:
    """Represents a single cell in a Sudoku puzzle."""
    global_pos: Vec2
    local_pos: Vec2 = field(default=None)
    state: str = field(default=None)
    locked: bool = field(default_factory=lambda: random.random() > .8)

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
    members:Dict[Tuple[int, int], Cell] = field(default_factory=dict)

class Board:
    """Represents the Sudoku puzzle board."""
    def __init__(self, num_sections:Vec2, section_dimensions:Vec2):
        """
        Initializes the Sudoku board with specific dimensions.

        :param num_sections: The number of sections across the x and y axes of the board.
        :param section_dimensions: The dimensions (width and height) of each section.
        """
        self.num_sections = num_sections
        self.section_dimensions = section_dimensions

        # Calculate the total size of the board in cells
        total_columns = self.num_sections.x * self.section_dimensions.x
        total_rows = self.num_sections.y * self.section_dimensions.y

        self.total_board_size =Vec2(total_columns, total_rows)
        self.active_cells:Dict[Tuple[int, int], Cell] = {}
        self.sections:Dict[Tuple[int, int], Section] = {}

        self._create_active_cells()
        self._divide_sections()

    def _create_active_cells(self) -> None:
        """Creates all active cells based on board size."""
        for cell_y in range(self.total_board_size.y):
            for cell_x in range(self.total_board_size.x):
                global_pos = Vec2(cell_x, cell_y)
                new_cell = Cell(global_pos)
                self.active_cells[global_pos.pos] = new_cell

    def _divide_single_section(self, start_column:Vec2) -> Section:
        """Divides and populates a single section."""
        section = Section()
        start = Vec2(start_column.x, start_column.y)
        end = Vec2(start_column.x + self.section_dimensions.x,
                   start_column.y + self.section_dimensions.y)
        for y_index, y in enumerate(range(start.y, end.y)):
            for x_index, x in enumerate(range(start.x, end.x)):
                cell = self.active_cells[(x, y)]
                cell.local_pos = Vec2(x_index, y_index)
                section.members[(x, y)] = cell
        return section

    def _divide_board_row(self, section_row_start:int) -> List[Section]:
        """Divides a row of the board into sections."""
        section_current_column = 0
        section_result = []
        for _ in range(self.num_sections.x):
            start_pos = Vec2(section_current_column, section_row_start)
            section_result.append(self._divide_single_section(start_pos))
            section_current_column += self.section_dimensions.x
        return section_result

    def _divide_sections(self) -> None:
        """Divides the entire board into sections."""
        section_row_start = 0
        for board_row in range(self.num_sections.y):
            divided_rows = self._divide_board_row(section_row_start)
            for index, divided_section in enumerate(divided_rows):
                self.sections[(index, board_row)] = divided_section
            section_row_start += self.section_dimensions.y
