from .data_structures import Board, Size
from .game_visual import Game

def main():
    num_sections = Size(3, 3)
    section_dimensions = Size(3, 3)
    screen_size = Size(500, 500)
    board = Board(num_sections, section_dimensions)
    game = game_visual.Game(screen_size, board)
    game.run()
