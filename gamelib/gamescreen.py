# gamescreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

import textwrap

from albow.controls import Button, Label, Widget
from albow.layout import Row
from albow.palette_view import PaletteView
from albow.screen import Screen
from pygame import Rect, mouse
from pygame.color import Color
from pygame.locals import BLEND_ADD

from constants import SCREEN, BUTTON_SIZE, SCENE_SIZE
from cursor import CursorWidget
from hand import HandButton
from popupmenu import PopupMenu, PopupMenuButton
from state import initial_state, Item
from widgets import BoomLabel


class InventoryView(PaletteView, CursorWidget):

    sel_color = Color("yellow")
    sel_width = 2

    def __init__(self, state, handbutton):
        CursorWidget.__init__(self)
        PaletteView.__init__(self, (BUTTON_SIZE, BUTTON_SIZE), 1, 6, scrolling=True)
        self.state = state
        self.handbutton = handbutton

    def num_items(self):
        return len(self.state.inventory)

    def draw_item(self, surface, item_no, rect):
        item_image = self.state.inventory[item_no].get_inventory_image()
        surface.blit(item_image, rect, None, BLEND_ADD)

    def draw_over(self, surface):
        PaletteView.draw_over(self, surface)
        CursorWidget.draw_over(self, surface)

    def click_item(self, item_no, event):
        self.state.set_tool(self.state.inventory[item_no])
        self.handbutton.unselect()

    def item_is_selected(self, item_no):
        return self.state.tool is self.state.inventory[item_no]

    def unselect(self):
        self.state.set_tool(None)


class MessageDialog(BoomLabel, CursorWidget):

    def __init__(self, text, wrap_width, **kwds):
        CursorWidget.__init__(self)
        paras = text.split("\n\n")
        text = "\n".join([textwrap.fill(para, wrap_width) for para in paras])
        Label.__init__(self, text, **kwds)
        self.set_margin(5)
        self.border_width = 1
        self.border_color = (0, 0, 0)
        self.bg_color = (127, 127, 127)
        self.fg_color = (0, 0, 0)

    def draw_over(self, surface):
        CursorWidget.draw_over(self, surface)

    def mouse_down(self, event):
        self.dismiss()


class StateWidget(CursorWidget):

    def __init__(self, state):
        CursorWidget.__init__(self, Rect(0, 0, SCENE_SIZE[0], SCENE_SIZE[1]))
        self.state = state

    def draw(self, surface):
        self.state.draw(surface)

    def mouse_down(self, event):
        result = self.state.interact(event.pos)
        if result:
            if result.sound:
                result.sound.play()
            if result.message:
                # Display the message as a modal dialog
                MessageDialog(result.message, 60).present()
                # queue a redraw to show updated state
                self.invalidate()

    def animate(self):
        if self.state.animate():
            # queue a redraw
            self.invalidate()

    def mouse_move(self, event):
        if not self.subwidgets:
            self.state.mouse_move(event.pos)
        CursorWidget.mouse_move(self, event)


class DetailWindow(CursorWidget):
    def __init__(self, state):
        CursorWidget.__init__(self, Rect(0, 0, SCENE_SIZE[0], SCENE_SIZE[1]))
        self.state = state
        self.draw_area = Rect(0, 0, 300, 300)
        self.draw_area.center = self.center

    def draw(self, surface):
        surface.fill(Color('green'), self.draw_area)

    def mouse_down(self, event):
        if self.draw_area.collidepoint(event.pos):
            # TODO: Interact with detail view
            pass
        else:
            self.parent.remove(self)

    def mouse_move(self, event):
        if self.draw_area.collidepoint(event.pos):
            # TODO: mouse_move stuff
            pass
        CursorWidget.mouse_move(self, event)


class ToolBar(Row, CursorWidget):
    def __init__(self, items):
        CursorWidget.__init__(self)
        Row.__init__(self, items, spacing=0, width=SCREEN[0])


class GameScreen(Screen):
    def __init__(self, shell):
        Screen.__init__(self, shell)
        self.running = False

    def _clear_all(self):
        for widget in self.subwidgets[:]:
            self.remove(widget)

    def start_game(self):
        self._clear_all()
        # TODO: Randomly plonk the state here for now
        self.state = initial_state()
        self.state_widget = StateWidget(self.state)
        self.add(self.state_widget)

        self.popup_menu = PopupMenu(self.shell)
        self.menubutton = PopupMenuButton('Menu',
                action=self.popup_menu.show_menu)

        self.handbutton = HandButton(action=self.hand_pressed)

        self.inventory = InventoryView(self.state, self.handbutton)

        self.testbutton = Button('Test', action=self.show_detail)

        self.toolbar = ToolBar([
                self.menubutton,
                self.handbutton,
                self.inventory,
                self.testbutton,
                ])
        self.toolbar.bottomleft = self.bottomleft
        self.add(self.toolbar)

        self.detail = DetailWindow(self.state)

        self.running = True

    def show_detail(self):
        self.state_widget.add_centered(self.detail)

    # Albow uses magic method names (command + '_cmd'). Yay.
    # Albow's search order means they need to be defined here, not in
    # PopMenu, which is annoying.
    def hide_cmd(self):
        # This option does nothing, but the method needs to exist for albow
        return

    def main_menu_cmd(self):
        mouse.set_visible(1)
        self.shell.show_screen(self.shell.menu_screen)

    def quit_cmd(self):
        self.shell.quit()

    def add_item(self):
        self.state.add_inventory_item("triangle")

    def hand_pressed(self):
        self.handbutton.toggle_selected()
        self.inventory.unselect()

    def begin_frame(self):
        if self.running:
            self.state_widget.animate()

    def mouse_delta(self, event):
        w = self.shell.find_widget(event.pos)
        if not isinstance(w, CursorWidget):
            mouse.set_visible(1)
