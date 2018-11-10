from pyntnclick.constants import GameConstants


# This module is imported before we've set up i18n. Anything here has to be
# explicitly translated later. However, marking strings with a call to _
# allows gettext translation tools to pick them up from the source code
# as strings for which translations are needed.
def _(x):
    return x


class SSConstants(GameConstants):
    title = _('Suspended Sentence')
    icon = 'suspended_sentence24x24.png'
    short_name = 'suspended-sentence'
