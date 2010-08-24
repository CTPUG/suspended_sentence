# Sound management for Suspended Sentence

# This re-implements some of the albow.resource code to
# a) work around an annoying bugs
# b) add some missing functionality (disable_sound)

from albow.resource import _resource_path, dummy_sound

sound_cache = {}

def get_sound(*names):
    if sound_cache is None:
        return dummy_sound
    path = _resource_path("sounds", names)
    sound = sound_cache.get(path)
    if not sound:
        try:
            from pygame.mixer import Sound
        except ImportError, e:
            no_sound(e)
            return dummy_sound
        try:
            sound = Sound(path)
        except pygame.error, e:
            missing_sound(e, path)
            return dummy_sound
        sound_cache[path] = sound
    return sound


def no_sound(e):
    global sound_cache
    print "get_sound: %s" % e
    print "get_sound: Sound not available, continuing without it"
    sound_cache = None

def disable_sound():
    global sound_cache
    sound_cache = None

def missing_sound(e, name):
    print "albow.resource.get_sound: %s: %s" % (name, e)

