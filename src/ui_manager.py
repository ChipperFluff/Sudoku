from __future__ import annotations
from data_structures import Size, Vec2
import pygame


class View:
    def __init__(self):
        pass

    def on_update(self):
        pass

    def on_draw(self):
        pass

    def on_mouse_click(self, up:bool, pos:Vec2, button:int):
        pass

    def on_keyboard(self, up:bool, key):
        pass

    def on_quit(self):
        pass

class Window:
    _INSTANCE:Window = None

    def __init__(self, screen_size:Size, title:str, icon_path:str=None, fps:int=60):
        self._screen_size = screen_size
        self._title = title
        self._icon_path = icon_path
        self._clock = pygame.time.Clock()
        self._create_screen()

        self._window_active = True
        self._active_view:View = None

        if self._INSTANCE is not None:
            raise Exception("window class duplicated")
        self._INSTANCE = self

    def _create_screen(self):
        self._screen = pygame.display.set_mode(self._screen_size.to_tuple)
        pygame.display.set_caption(self._title)
        if self._icon_path is not None:
            self._icon = pygame.image.load(self._icon_path)
            pygame.display.set_icon(icon)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._active_view.on_quit()
                self._window_active = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                position = Vec2(*pygame.mouse.get_pos())
                self._active_view.on_mouse_click(False, position, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                position = Vec2(*pygame.mouse.get_pos())
                self._active_view.on_mouse_click(True, position, event.button)

            if event.type == pygame.KEYDOWN:
                self._active_view.on_keyboard(False, event.key)
            elif event.type == pygame.KEYUP:
                self._active_view.on_keyboard(True, event.key)

    def _draw(self):
        self.screen.fill((0, 0, 0))  # Black background
        self._active_view.on_draw(self.screen)
        pygame.display.update()

    def _game_loop(self):
        while self._window_active:
            if self._active_view is None:
                continue

            self._handle_events()
            self._active_view.on_update()
            self._draw()

    def run(self):
        self._game_loop()
        pygame.quit()
        sys.exit()

def run():
    window = Window._INSTANCE
    if window is None:
        raise TypeError("window not initilized")
    window.run()