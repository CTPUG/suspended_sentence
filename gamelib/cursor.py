# cursor.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Sprite Cursor

from albow.resource import get_image
from albow.widget import Widget
from pygame.sprite import Sprite, RenderUpdates
import pygame
import pygame.color
import pygame.cursors
import pygame.mouse

class CursorSprite(Sprite):
    "A Sprite that follows the Cursor"

    def __init__(self, filename, x=None, y=None):
        Sprite.__init__(self)
        self.filename = filename
        self.pointer_x = x
        self.pointer_y = y
        self.highlighted = False

    def load(self):
        if not hasattr(self, 'plain_image'):
            self.plain_image = get_image('items', self.filename)
            self.image = self.plain_image
            self.rect = self.image.get_rect()

            if self.pointer_x is None:
                self.pointer_x = self.rect.size[0] // 2
            if self.pointer_y is None:
                self.pointer_y = self.rect.size[1] // 2

            self.highlight = pygame.Surface(self.rect.size)
            color = pygame.color.Color(255, 100, 100, 0)
            self.highlight.fill(color)

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.left = pos[0] - self.pointer_x
        self.rect.top = pos[1] - self.pointer_y

    def set_highlight(self, enable):
        if enable != self.highlighted:
            self.load()
            self.highlighted = enable
            self.image = self.plain_image.copy()
            if enable:
                self.image.blit(self.highlight, self.highlight.get_rect(),
                                None, pygame.BLEND_MULT)


HAND = CursorSprite('hand.png', 12, 0)


class CursorWidget(Widget):
    """Mix-in widget to ensure that mouse_move is propogated to parents"""

    cursor = HAND

    def __init__(self, screen, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self._cursor_group = RenderUpdates()
        self._loaded_cursor = None
        self.screen = screen

    def enter_screen(self):
        pygame.mouse.set_visible(0)

    def leave_screen(self):
        pygame.mouse.set_visible(1)

    def draw_all(self, _surface):
        Widget.draw_all(self, _surface)
        item = self.screen.state.tool
        if item is None:
            self.set_cursor(HAND)
        else:
            self.set_cursor(item.CURSOR)
        surface = self.get_root().surface
        if self.cursor != self._loaded_cursor:
            self._loaded_cursor = self.cursor
            if self.cursor is None:
                pygame.mouse.set_visible(1)
                self._cursor_group.empty()
            else:
                pygame.mouse.set_visible(0)
                self.cursor.load()
                self._cursor_group.empty()
                self._cursor_group.add(self.cursor)
        if self.cursor is not None:
            self._cursor_group.update()
            self._cursor_group.draw(surface)

    def mouse_delta(self, event):
        self.invalidate()

    def set_cursor(self, cursor):
        CursorWidget.cursor = cursor

    def cursor_highlight(self, enable):
        self.cursor.set_highlight(enable)
