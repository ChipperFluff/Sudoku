from .game_logic import Board, Vec2
from .game_visual import Game

def main():
    num_sections = Vec2(4, 2)
    section_dimensions = Vec2(2, 4)
    board = Board(num_sections, section_dimensions)
    game = game_visual.Game(board)
    game.run()
