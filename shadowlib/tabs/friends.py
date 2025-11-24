"""
Friends tab module.
"""

from shadowlib.types.gametab import GameTab, GameTabs


class Friends(GameTabs):
    """
    Friends tab - displays friends list and ignore list.
    """

    TAB_TYPE = GameTab.FRIENDS
