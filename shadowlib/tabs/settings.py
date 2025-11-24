"""
Settings tab module.
"""

from shadowlib.types.gametab import GameTab, GameTabs


class Settings(GameTabs):
    """
    Settings tab - displays game settings and controls.
    """

    TAB_TYPE = GameTab.SETTINGS
