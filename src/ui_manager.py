from .data_structures import Size
import pygame


class View:
    def __init__(self):

class Window:
    def __init__(self, screen_size:Size):
        self.screen_size = screen_size
        self._window_active = True
        self._active_view:View = None
        self._create_screen()

    def _create_screen(self):
        self.screen = pygame.display.set_mode(self.screen_size.to_tuple)
        pygame.display.set_caption("Sudok")
        icon = pygame.image.load('resources/imgs/icon.png')
        pygame.display.set_icon(icon)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = Vec2(*pygame.mouse.get_pos())
                if event.button == 1:
            if event.type == pygame.KEYDOWN:
                key = event.key

    def _update(self):
        pass

    def _draw(self):
        self.screen.fill((0, 0, 0))  # Black background
        self._active_view.on_draw(self.screen)
        pygame.display.update()

    def _game_loop(self):
        while self._window_active:
            if self._active_view is None:
                continue

            self._handle_events()
            self._update()
            self._draw()

    def run(self):
        self._game_loop()
        pygame.quit()
        sys.exit()
