"""
Magic tab module.
"""

from shadowlib.types.gametab import GameTab, GameTabs


class Magic(GameTabs):
    """
    Magic tab - displays spellbook and available spells.
    """

    TAB_TYPE = GameTab.MAGIC
