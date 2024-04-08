from .data_structures import Board, Size
from .game_visual import Window
from .ui_manager import run

def main():
    screen_size = Size(500, 500)
    window = Window(screen_size)
    run()
