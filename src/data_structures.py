from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Union, Callable
try:
    from .game_visual import CellSprite
except ImportError:
    pass
import random

@dataclass
class Vec2:
    """Represents a 2D vector or position."""
    x: int
    y: int

    @property
    def to_tuple(self) -> Tuple[int, int]:
        """Returns the position as a tuple."""
        return self.x, self.y

    def add(self, dx, dy):
        return Vec2(self.x+dx, self.y+dy)

    def apply(self, func: Callable[[int], int]) -> None:
        """
        Applies a function to `x` and `y` attributes, updating them with the result.

        Args:
            func: A function that modifies the value of `x` and `y`.
        """
        self.x = func(self.x)
        self.y = func(self.y)

    def is_within(self, point_a: Vec2, point_b: Vec2):
        return (min(point_a.x, point_b.x) <= self.x <= max(point_a.x, point_b.x)
                and min(point_a.y, point_b.y) <= self.y <= max(point_a.y, point_b.y))

@dataclass
class Area:
    a:Vec2
    b:Vec2

    def is_within(self, point:Vec2):
        return point.is_within(self.a, self.b)

@dataclass
class Size:
    width:int
    height:int

    @property
    def to_tuple(self) -> Tuple[int, int]:
        """Returns the size as a tuple."""
        return self.width, self.height

    def apply(self, func: Callable[[int], int]) -> None:
        self.width = func(self.width)
        self.height = func(self.height)

@dataclass
class Color:
    red:int
    green:int
    blue:int

@dataclass
class Cell:
    """Represents a single cell in a Sudoku puzzle."""
    global_pos: Vec2
    sprite:CellSprite = field(default=None)
    local_pos: Vec2 = field(default=None)
    state: str = field(default=None)
    locked: bool = field(default=False)

@dataclass
class Section:
    """Represents a section (block) in a Sudoku puzzle."""
    members:Dict[Tuple[int, int], Cell] = field(default_factory=dict)

class Board:
    """Represents the Sudoku puzzle board."""

    def __init__(self, num_sections:Size, section_dimensions:Size):
        """
        Initializes the Sudoku board with specific dimensions.

        :param num_sections: The number of sections across the x and y axes of the board.
        :param section_dimensions: The dimensions (width and height) of each section.
        """

        self._check_size_param(num_sections, section_dimensions)
        self.num_sections = num_sections
        self.section_dimensions = section_dimensions

        # Calculate the total size of the board in cells
        total_columns = self.num_sections.width * self.section_dimensions.width
        total_rows = self.num_sections.height * self.section_dimensions.height

        self.total_board_size = Size(total_columns, total_rows)
        self.active_cells:Dict[Tuple[int, int], Cell] = {}
        self.sections:Dict[Tuple[int, int], Section] = {}

        self._create_active_cells()
        self._divide_sections()

    def _check_size_param(self, num_sections:Size, section_dimensions:Size):
        if num_sections.height > 0 and num_sections.height > 0:
            return
        if section_dimensions.width > 0 and section_dimensions.height > 0:
            return

        raise AttributeError(f"board could not be created with this args:\n{num_sections=} {section_dimensions=}")

    def _create_active_cells(self) -> None:
        """Creates all active cells based on board size."""
        for cell_y in range(self.total_board_size.height):
            for cell_x in range(self.total_board_size.width):
                global_pos = Vec2(cell_x, cell_y)
                new_cell = Cell(global_pos)
                self.active_cells[global_pos.to_tuple] = new_cell

    def _divide_single_section(self, start_column:Vec2) -> Section:
        """Divides and populates a single section."""
        section = Section()
        start = Vec2(start_column.x, start_column.y)
        end = Vec2(start_column.x + self.section_dimensions.width,
                    start_column.y + self.section_dimensions.height)

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

        for _ in range(self.num_sections.width):
            start_pos = Vec2(section_current_column, section_row_start)
            section_result.append(self._divide_single_section(start_pos))
            section_current_column += self.section_dimensions.width

        return section_result

    def _divide_sections(self) -> None:
        """Divides the entire board into sections."""
        section_row_start = 0

        for board_row in range(self.num_sections.height):
            divided_rows = self._divide_board_row(section_row_start)
            for index, divided_section in enumerate(divided_rows):
                self.sections[(index, board_row)] = divided_section
            section_row_start += self.section_dimensions.height
