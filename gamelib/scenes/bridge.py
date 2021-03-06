"""Bridge where the final showdown with the AI occurs."""

import random

from pygame.rect import Rect

from pyntnclick.i18n import _
from pyntnclick.utils import (render_text, lookup_debug_color,
                              make_reversible_list)
from pyntnclick.cursor import CursorSprite
from pyntnclick.state import Scene, Item, Thing, Result
from pyntnclick.scenewidgets import (
    InteractNoImage, InteractRectUnion, InteractImage, InteractAnimated,
    GenericDescThing, TakeableThing, InteractText)

from gamelib.scenes.game_constants import PLAYER_ID
from gamelib.scenes.game_widgets import Door, BaseCamera, make_jim_dialog


class Bridge(Scene):

    FOLDER = "bridge"
    BACKGROUND = 'bridge.png'

    OFFSET = (0, -50)

    MUSIC = [
            'beep1.ogg',
            'beep2.ogg',
            'beep880.ogg',
            'beep660.ogg',
            'beep3.ogg',
            'silent.ogg',
            'creaking.ogg',
            'silent.ogg',
            ]

    INITIAL_DATA = {
        'ai status': 'online',  # online, looping, dead
        'ai panel': 'closed',  # closed, open, broken
        }

    def setup(self):
        self.background_playlist = None
        self.add_item_factory(Superconductor)
        self.add_item_factory(TapedSuperconductor)
        self.add_item_factory(Stethoscope)
        self.add_thing(ToMap())
        self.add_thing(MonitorCamera())
        self.add_thing(MassageChair())
        self.add_thing(MassageChairBase())
        self.add_thing(StethoscopeThing())
        self.add_thing(BridgeComputer())
        self.add_thing(LeftLights())
        self.add_thing(RightLights())
        self.add_thing(JimPanel())
        self.add_thing(StarField())
        self.add_thing(GenericDescThing(
            'bridge.wires', 1,
            _("The brightly coloured wires contrast with the drab walls."),
            ((46, 4, 711, 143),)))
        self.add_thing(GenericDescThing(
            'bridge.note', 2,
            _("\"Dammit JIM, I'm a doctor, not an engineer!\""),
            (
                (491, 494, 194, 105),
                (422, 533, 71, 66),
            )))
        self.doctor = GenericDescThing(
            'bridge.skel', 3,
            _("A skeleton hangs improbably from the wires."),
            (
                (632, 148, 40, 29),
                (683, 176, 30, 101),
                (652, 274, 45, 96),
                (639, 180, 11, 95),
            ))
        self.add_thing(self.doctor)

    def enter(self):
        pieces = [self.sound.get_music(x) for x in self.MUSIC]
        self.background_playlist = self.sound.get_playlist(pieces, random=True,
                                                           repeat=True)
        self.sound.change_playlist(self.background_playlist)

    def leave(self):
        self.sound.change_playlist(None)


class ToMap(Door):

    SCENE = "bridge"

    INTERACTS = {
        "door": InteractNoImage(707, 344, 84, 245),
        }

    INITIAL = "door"


class BridgeComputer(Thing):
    """The bridge computer. Gives status updates"""

    NAME = "bridge.comp"

    INTERACTS = {
        'screen': InteractNoImage(338, 296, 123, 74),
    }

    INITIAL = 'screen'

    def interact_without(self):
        return Result(detail_view='bridge_comp_detail')

    def interact_with_titanium_leg(self, item):
        return Result(_("You can't break the duraplastic screen."))

    def interact_with_machete(self, item):
        return Result(_("Scratching the screen won't help you."))

    def get_description(self):
        return _("The main bridge computer screen.")


class MassageChairBase(Thing):
    "The captain's massage chair, contains superconductor"

    NAME = 'bridge.massagechair_base'

    INTERACTS = {
        'chair': InteractNoImage(127, 518, 69, 64),
    }

    INITIAL = 'chair'

    INITIAL_DATA = {
            'contains_superconductor': True,
    }

    def interact_without(self):
        return Result(detail_view='chair_detail')

    def get_description(self):
        if self.get_data('contains_superconductor'):
            return _("A top of the line Massage-o-Matic Captain's Executive"
                     " Command Chair. It's massaging a skeleton.")
        return _("The chair won't work any more, it has no power.")


class MassageChair(Thing):
    "The captain's massage chair, contains superconductor"

    NAME = 'bridge.massagechair'

    INTERACTS = {
        'chair': InteractRectUnion((
            (148, 418, 77, 68),
            (69, 363, 80, 156),
            (104, 514, 18, 40),
            (147, 487, 106, 32),
            (220, 518, 83, 49),
            (196, 502, 75, 34),
            (207, 534, 69, 51),
        )),
    }

    INITIAL = 'chair'

    def get_description(self):
        base = self.game.get_current_scene().things['bridge.massagechair_base']
        return base.get_description()

    def is_interactive(self, tool=None):
        return False


class Stethoscope(Item):
    "Used for cracking safes. Found on the doctor on the chair"

    NAME = 'stethoscope'
    INVENTORY_IMAGE = 'stethoscope.png'
    CURSOR = CursorSprite('stethoscope.png')


class StethoscopeThing(TakeableThing):
    "Stethoscope on the doctor"

    NAME = 'bridge.stethoscope'

    INTERACTS = {
        'stethoscope': InteractImage(650, 178, 'hanging_stethoscope.png'),
    }

    INITIAL = 'stethoscope'
    ITEM = 'stethoscope'

    def get_description(self):
        return _("A stethoscope hangs from the neck of the skeleton.")

    def interact_without(self):
        self.take()
        # Fill in the doctor's rect
        self.scene.doctor.rect.append(self.rect)
        return Result(_("You pick up the stethoscope and verify that the"
                        " doctor's heart has stopped. Probably a while ago."))


class TapedSuperconductor(Item):
    "Used for connecting high-powered parts of the ship up"

    NAME = 'taped_superconductor'
    INVENTORY_IMAGE = 'superconductor_taped.png'
    CURSOR = CursorSprite('superconductor_taped_cursor.png')


class Superconductor(Item):
    "Used for connecting high-powered parts of the ship up"

    NAME = 'superconductor'
    INVENTORY_IMAGE = 'superconductor_fixed.png'
    CURSOR = CursorSprite('superconductor_fixed.png')

    def interact_with_duct_tape(self, item):
        self.game.replace_inventory_item(self.name, 'taped_superconductor')
        return Result(_("You rip off a piece of duct tape and stick it on the"
                        " superconductor. It almost sticks to itself, but you"
                        " successfully avoid disaster."))


class SuperconductorThing(TakeableThing):
    "Superconductor from the massage chair."

    NAME = 'bridge.superconductor'

    INTERACTS = {
        'superconductor': InteractImage(158, 138, 'superconductor.png'),
    }

    INITIAL = 'superconductor'
    ITEM = 'superconductor'

    def interact_without(self):
        self.game.scenes['bridge'].things['bridge.massagechair_base'] \
                          .set_data('contains_superconductor', False)
        self.take()
        return (Result(_("The superconductor module unclips easily.")),
                make_jim_dialog(
                    _("Prisoner %s. That chair you've destroyed"
                      " was property of the ship's captain. "
                      "You will surely be punished.")
                    % PLAYER_ID, self.game))


class StarField(Thing):

    NAME = 'bridge.stars'

    INTERACTS = {
        'stars': InteractAnimated(190, 145,
                                  make_reversible_list(
                                      ['stars_%d.png' % (i + 1) for i
                                       in range(3)]
                                  ),
                                  30),
    }

    INITIAL = 'stars'

    def is_interactive(self, tool=None):
        return False


class BlinkingLights(Thing):

    def setup(self):
        self.description = None

    def is_interactive(self, tool=None):
        return False

    def leave(self):
        self.description = random.choice([
            _("The lights flash in interesting patterns."),
            _("The flashing lights don't mean anything to you."),
            _("The console lights flash and flicker."),
            ])

    def get_description(self):
        if not self.description:
            self.leave()
        return self.description


class LeftLights(BlinkingLights):

    NAME = 'bridge.lights.1'

    INTERACTS = {
        "lights": InteractAnimated(176, 337,
                                   ["bridge_lights_1_1.png",
                                    "bridge_lights_1_2.png",
                                    "bridge_lights_1_3.png",
                                    "bridge_lights_1_2.png"], 5),
    }

    INITIAL = 'lights'


class RightLights(BlinkingLights):

    NAME = 'bridge.lights.2'

    INTERACTS = {
        "lights": InteractAnimated(559, 332,
                                   ["bridge_lights_2_1.png",
                                    "bridge_lights_2_2.png",
                                    "bridge_lights_2_3.png",
                                    "bridge_lights_2_2.png"], 5),
    }

    INITIAL = 'lights'


class JimPanel(Thing):
    "The panel to JIM's internals'"

    NAME = "jim_panel"

    INTERACTS = {
            'closed': InteractNoImage(506, 430, 137, 47),
            'open': InteractImage(500, 427, 'jim_panel_open.png'),
            'broken': InteractImage(488, 412, 'jim_panel_destroyed.png'),
            }

    INITIAL = 'closed'

    def get_description(self):
        if self.scene.get_data('ai panel') == 'closed':
            return _("The sign reads 'Warning: Authorized Techinicians Only'.")

    def select_interact(self):
        status = self.scene.get_data('ai panel')
        return status or self.INITIAL

    def interact_without(self):
        ai_status = self.state.get_jim_state()
        if ai_status == 'online':
            return self.interact_default(None)
        elif self.scene.get_data('ai panel') == 'closed':
            return Result(_("You are unable to open the panel with your"
                            " bare hands."))
        elif self.scene.get_data('ai panel') == 'open':
            self.scene.set_data('ai panel', 'broken')
            self.state.break_ai()
            self.set_interact()
            return Result(_("You unplug various important-looking wires."))

    def interact_with_machete(self, item):
        ai_status = self.state.get_jim_state()
        if ai_status == 'online':
            return self.interact_default(item)
        elif self.scene.get_data('ai panel') == 'closed':
            self.scene.set_data('ai panel', 'open')
            self.set_interact()
            return Result(_("Using the machete, you lever the panel off."))
        elif self.scene.get_data('ai panel') == 'open':
            self.scene.set_data('ai panel', 'broken')
            self.state.break_ai()
            self.set_interact()
            return Result(_("You smash various delicate components with"
                            " the machete."))

    def interact_default(self, item):
        if self.state.get_jim_state() == 'online':
            return (Result(_('You feel a shock from the panel.')),
                    make_jim_dialog(_("Prisoner %s. Please step away from the"
                                      " panel. You are not an authorized"
                                      " technician.") % PLAYER_ID, self.game))


class ChairDetail(Scene):

    FOLDER = 'bridge'
    BACKGROUND = 'chair_detail.png'
    NAME = 'chair_detail'

    def setup(self):
        self.add_thing(SuperconductorThing())


# classes related the computer detail


class LogTab(Thing):
    """Tab for log screen"""

    NAME = 'bridge_comp.screen'

    INTERACTS = {
        'log tab': InteractText(
            100, 53, 94, 37,  _("Logs"),
            'lightgreen', 20, 'DejaVuSans-Bold.ttf', True),
    }
    INITIAL = 'log tab'
    COMPUTER = 'bridge_comp_detail'

    def is_interactive(self, tool=None):
        return self.game.detail_views[self.COMPUTER].get_data('tab') != 'log'

    def interact_without(self):
        self.game.detail_views[self.COMPUTER].set_data('tab', 'log')
        self.game.detail_views[self.COMPUTER].set_background()
        return Result(soundfile='beep550.ogg')


class AlertTab(Thing):
    """Tab for alert screen"""

    NAME = 'bridge_comp.alert_tab'

    INTERACTS = {
        'alert tab': InteractText(
            12, 53, 88, 37, _("Alerts"),
            'orange', 20, 'DejaVuSans-Bold.ttf', True),
    }
    INITIAL = 'alert tab'
    COMPUTER = 'bridge_comp_detail'

    def is_interactive(self, tool=None):
        return (self.game.detail_views[self.COMPUTER].get_data('tab')
                != 'alert')

    def interact_without(self):
        self.game.detail_views[self.COMPUTER].set_data('tab', 'alert')
        self.game.detail_views[self.COMPUTER].set_background()
        return Result(soundfile='beep550.ogg')


class NavTab(Thing):
    """Tab for the Navigation screen"""

    NAME = 'bridge_comp.nav_tab'

    INTERACTS = {
        'nav tab': InteractText(
            197, 53, 126, 37, _("Navigation"),
            'darkblue', 20, 'DejaVuSans-Bold.ttf', True),
    }
    INITIAL = 'nav tab'
    COMPUTER = 'bridge_comp_detail'

    def is_interactive(self, tool=None):
        return self.game.detail_views[self.COMPUTER].get_data('tab') != 'nav'

    def interact_without(self):
        self.game.detail_views[self.COMPUTER].set_data('tab', 'nav')
        self.game.detail_views[self.COMPUTER].set_background()
        return Result(soundfile='beep550.ogg')


class DestNavPageLine(Thing):
    """The destination navigation lines."""

    INITIAL = 'line'
    COMPUTER = 'bridge_comp_detail'

    def __init__(self, number, rect, ai_blocked, dest):
        super(DestNavPageLine, self).__init__()
        self.name = 'bridge_comp.nav_line%s' % number
        # set debugging higlight color for when DEBUG is on.
        self._interact_hilight_color = lookup_debug_color(number)
        r = Rect(rect)
        # We dynamically generate the interact rect here.
        self.interacts = {}
        self.interacts['line'] = InteractText(
            r.x, r.y, r.w, r.h,
            dest, 'darkblue', 16, 'DejaVuSans-Bold.ttf', False)
        # Whether JIM blocks this
        self.ai_blocked = ai_blocked
        self.set_interact()

    def is_interactive(self, tool=None):
        return self.game.detail_views[self.COMPUTER].get_data('tab') == 'nav'

    def interact_without(self):
        if self.game.scenes['bridge'].get_data('ai status') == 'online':
            return make_jim_dialog(_("You are not authorized to change the"
                                     " destination."), self.game)
        if not self.ai_blocked:
            return Result(_("There's no good reason to choose to go to the"
                            " penal colony."))
        if self.game.scenes['bridge'].get_data('ai status') == 'looping':
            return Result(_("You could change the destination, but when JIM"
                            " recovers, it'll just get reset."))
        if self.game.scenes['bridge'].get_data('ai status') == 'dead':
            return Result(_("You change the destination."),
                          soundfile="beep550.ogg", end_game=True)


class CompUpButton(Thing):
    """Up button on log screen"""

    NAME = 'bridge_comp.up_button'

    INTERACTS = {
            'up': InteractNoImage(594, 82, 30, 58),
            }
    INITIAL = 'up'
    COMPUTER = 'bridge_comp_detail'

    def is_interactive(self, tool=None):
        tab = self.game.detail_views[self.COMPUTER].get_data('tab')
        page = self.game.detail_views[self.COMPUTER].get_data('log page')
        return tab == 'log' and page > 0

    def interact_without(self):
        page = self.game.detail_views[self.COMPUTER].get_data('log page')
        self.game.detail_views[self.COMPUTER].set_data('log page', page - 1)
        self.game.detail_views[self.COMPUTER].set_background()
        return Result(soundfile='beep550.ogg')


class CompDownButton(Thing):
    """Down button on log screen"""

    NAME = 'bridge_comp.down_button'

    INTERACTS = {
            'down': InteractNoImage(594, 293, 30, 58),
            }
    INITIAL = 'down'
    COMPUTER = 'bridge_comp_detail'

    def is_interactive(self, tool=None):
        tab = self.game.detail_views[self.COMPUTER].get_data('tab')
        page = self.game.detail_views[self.COMPUTER].get_data('log page')
        max_page = self.game.detail_views[self.COMPUTER].get_data('max page')
        return tab == 'log' and (page + 1) < max_page

    def interact_without(self):
        page = self.game.detail_views[self.COMPUTER].get_data('log page')
        self.game.detail_views[self.COMPUTER].set_data('log page', page + 1)
        self.game.detail_views[self.COMPUTER].set_background()
        return Result(soundfile='beep550.ogg')


class MonitorCamera(BaseCamera):
    "A camera on the bridge"

    NAME = "bridge.camera"

    INTERACTS = {
        'online': InteractImage(33, 192, 'camera_small.png'),
        'dead': InteractImage(33, 192, 'camera_small_gray.png'),
        'looping': InteractAnimated(33, 192, ('camera_small.png',
                                              'camera_small_gray.png'),
                                    15),
    }


class BridgeCompDetail(Scene):

    FOLDER = 'bridge'
    NAME = 'bridge_comp_detail'

    ALERT_BASE = 'comp_alert_base.png'
    ALERTS = {
        'hull breach': _("Hull breach detected: Engine Room"),
        'ai looping': _("AI Status: 3D scene reconstruction failed."
                        " Recovery in progress"),
        'ai offline': _("AI System Offline"),
        'engine offline': _("Engine Offline"),
        'life support': _("Life Support System: 20% operational"),
        'life support partial': _("Life Support System: 40% operational"),
    }

    # Point to start drawing changeable alerts
    ALERT_OFFSET = (16, 100)
    ALERT_SPACING = 4

    LOG_BACKGROUND = 'comp_log_start.png'

    LOGS = [_("<Error: Log corrupted. Unable to open Log>")]

    NAVIGATION = 'bridge_nav_base.png'

    NAV_MESSAGES = {
        'engine offline': [
            _("Engine Offline: Navigation Disabled")],
        'life support': [
            _("Life Support Marginal."),
            _("Emergency Navigation Protocol Engaged."),
            '',
            _("Destination locked to:"),
            _("Bounty Penal Colony Space Port, New South Australia")],
    }

    BACKGROUND = ALERT_BASE

    INITIAL_DATA = {
            'tab': 'alert',
            'log page': 0,
            'max page': len(LOGS),
    }

    def setup(self):
        self.add_thing(LogTab())
        self.add_thing(AlertTab())
        self.add_thing(NavTab())
        #  Navigation buttons were implemented but then later abandoned
        #  because we couldn't think of funny enough logs. :)
        #  self.add_thing(CompUpButton())
        #  self.add_thing(CompDownButton())
        self._scene_playlist = None
        self._alert = self.get_image(self.FOLDER, self.ALERT_BASE)
        self._alert_messages = {}
        self._nav_messages = {}
        for key, text in self.ALERTS.items():
            self._alert_messages[key] = render_text(
                text, 'DejaVuSans-Bold.ttf', 18, 'orange', (0, 0, 0, 0),
                self.resource, (600, 25), False)
        self._nav_background = self.get_image(self.FOLDER, self.NAVIGATION)
        #  See note above about funny navigation logs
        #  for key, name in self.NAVIGATION.items():
        #      self._nav_messages[key] = self.get_image(self.FOLDER, name)
        self._nav_lines = []
        self._nav_lines.append(DestNavPageLine(
            1, (12, 99, 610, 25), False,
            _("1. Bounty Penal Colony Space Port, New South Australia"
              " (397 days)")))
        self._nav_lines.append(DestNavPageLine(
            2, (12, 135, 610, 25), True,
            _("2. Hedonia Space Station (782 days)")))
        self._nav_lines.append(DestNavPageLine(
            3, (12, 167, 610, 25), True,
            _("3. Spinosa Health Resort, Prunus Secundus (1231 days)")))
        self._nav_lines.append(DestNavPageLine(
            4, (12, 203, 610, 25), True,
            _("4. Achene Space Port, Indica Prspinosame (1621 days)")))
        self._nav_lines.append(DestNavPageLine(
            5, (12, 239, 610, 25), True,
            _("5. Opioid Space Port, Gelatinosa Prime (1963 days)")))
        self._log_background = self.get_image(self.FOLDER, self.LOG_BACKGROUND)
        self._logs = []
        for text in self.LOGS:
            log_page = self._log_background.copy()
            log_page.blit(render_text(
                text, 'DejaVuSans-Bold.ttf', 18,
                'lightgreen', (0, 0, 0, 0), self.resource, (600, 25), False),
                self.ALERT_OFFSET)
            self._logs.append(log_page)

    def enter(self):
        self._scene_playlist = self.sound.get_current_playlist()
        self.sound.change_playlist(None)
        self.set_background()

    def leave(self):
        self.sound.change_playlist(self._scene_playlist)

    def set_background(self):
        if self.get_data('tab') == 'alert':
            self._clear_navigation()
            self._background = self._alert.copy()
            self._draw_alerts()
        elif self.get_data('tab') == 'log':
            self._clear_navigation()
            self._background = self._logs[self.get_data('log page')].copy()
        elif self.get_data('tab') == 'nav':
            self._background = self._get_nav_page()

    def _clear_navigation(self):
        "Remove navigation things if necessary"
        for thing in self._nav_lines:
            if thing.name in self.things:
                # Much fiddling to do the right thing when we reinsert it
                del self.things[thing.name]
                thing.scene = None

    def _draw_nav_text(self, key):
        surface = self._nav_background.copy()
        xpos, ypos = self.ALERT_OFFSET
        for line in self.NAV_MESSAGES[key]:
            text = render_text(
                line, 'DejaVuSans-Bold.ttf', 18,
                'darkblue', (0, 0, 0, 0), self.resource, (600, 25), False)
            surface.blit(text, (xpos, ypos))
            ypos = ypos + text.get_height() + self.ALERT_SPACING
        return surface

    def _get_nav_page(self):
        if not self.game.scenes['engine'].get_data('engine online'):
            return self._draw_nav_text('engine offline')
        elif (not self.game.scenes['mess'].get_data('life support status')
              == 'fixed'):
            return self._draw_nav_text('life support')
        else:
            for thing in self._nav_lines:
                if thing.name not in self.things:
                    self.add_thing(thing)
            return self._nav_background.copy()

    def _draw_alerts(self):
        xpos, ypos = self.ALERT_OFFSET
        self._background.blit(
            self._alert_messages['hull breach'], (xpos, ypos))
        ypos += (
            self._alert_messages['hull breach'].get_size()[1]
            + self.ALERT_SPACING)
        if self.game.scenes['bridge'].get_data('ai status') == 'looping':
            self._background.blit(
                self._alert_messages['ai looping'], (xpos, ypos))
            ypos += (self._alert_messages['ai looping'].get_size()[1]
                     + self.ALERT_SPACING)
        if self.game.scenes['bridge'].get_data('ai status') == 'dead':
            self._background.blit(
                self._alert_messages['ai offline'], (xpos, ypos))
            ypos += (self._alert_messages['ai offline'].get_size()[1]
                     + self.ALERT_SPACING)
        if not self.game.scenes['engine'].get_data('engine online'):
            self._background.blit(
                self._alert_messages['engine offline'], (xpos, ypos))
            ypos += (self._alert_messages['engine offline'].get_size()[1]
                     + self.ALERT_SPACING)
        if (self.game.scenes['mess'].get_data('life support status')
                == 'broken'):
            self._background.blit(
                self._alert_messages['life support'], (xpos, ypos))
            ypos += (self._alert_messages['life support'].get_size()[1]
                     + self.ALERT_SPACING)
        if (self.game.scenes['mess'].get_data('life support status')
                == 'replaced'):
            self._background.blit(
                self._alert_messages['life support partial'], (xpos, ypos))
            ypos += (self._alert_messages['life support partial'].get_size()[1]
                     + self.ALERT_SPACING)


SCENES = [Bridge]
DETAIL_VIEWS = [ChairDetail, BridgeCompDetail]
