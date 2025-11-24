"""
Combat tab module.
"""

from shadowlib.types.gametab import GameTab, GameTabs


class Combat(GameTabs):
    """
    Combat tab - displays combat stats and special attack.
    """

    TAB_TYPE = GameTab.COMBAT
