from .game_logic import Board, Vec2
from .game_visual import Game

def main():
    num_sections = Vec2(3, 3)
    section_dimensions = Vec2(3, 3)
    screen_size = Vec2(500, 500)
    board = Board(num_sections, section_dimensions)
    game = game_visual.Game(screen_size, board)
    game.run()
