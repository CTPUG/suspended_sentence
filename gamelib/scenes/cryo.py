"""Cryo room where the prisoner starts out."""

import random

from gamelib.state import Scene, Item, Thing


class Cryo(Scene):

    FOLDER = "cryo"
    BACKGROUND = "cryo_room.png"

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Cryo, self).__init__(state)
        self.add_item(Triangle("triangle"))
        self.add_item(TitaniumLeg("titanium_leg"))
        self.add_thing(CryoUnitAlpha("cryo.unit.1", (20, 20, 400, 500)))
        self.add_thing(CryoRoomDoor("cryo.door", (30, 30, 400, 300)))


class Triangle(Item):
    "Test item. Needs to go away at some point."

    INVENTORY_IMAGE = "triangle.png"


class TitaniumLeg(Item):
    "Titanium leg, found on a piratical corpse."

    INVENTORY_IMAGE = "titanium_leg.png"


class CryoUnitAlpha(Thing):
    pass


class CryoRoomDoor(Thing):
    "Door to the cryo room."

    FOLDER = "cryo"
    IMAGE = "cryo_door_closed"

    def interact_with_titanium_leg(self, item):
        self.message("You wedge the titanium leg into the chain and twist. With a satisfying *snap*, the chain breaks and the door opens.")
        self.scene.remove_thing(self)

    def interact_without(self):
        self.message("It moves slightly and then stops. A chain on the other side is preventing it from opening completely.")

    def interact_default(self, item):
        self.message(random.choice([
                    "Sadly, this isn't that sort of game.",
                    "Your valiant efforts are foiled by the Evil Game Designer.",
                    "The door resists. Try something else, perhaps?",
                    ]))


SCENES = [Cryo]