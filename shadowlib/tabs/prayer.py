"""
Prayer tab module.
"""

from shadowlib.types.gametab import GameTab, GameTabs


class Prayer(GameTabs):
    """
    Prayer tab - displays available prayers and prayer points.
    """

    TAB_TYPE = GameTab.PRAYER
