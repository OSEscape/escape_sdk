"""Type stubs for tabs namespace."""

from shadowlib.tabs.account import Account
from shadowlib.tabs.combat import Combat
from shadowlib.tabs.emotes import Emotes
from shadowlib.tabs.equipment import Equipment
from shadowlib.tabs.friends import Friends
from shadowlib.tabs.grouping import Grouping
from shadowlib.tabs.inventory import Inventory
from shadowlib.tabs.logout import Logout
from shadowlib.tabs.magic import Magic
from shadowlib.tabs.music import Music
from shadowlib.tabs.prayer import Prayer
from shadowlib.tabs.progress import Progress
from shadowlib.tabs.settings import Settings
from shadowlib.tabs.skills import Skills
from shadowlib.types.gametab import GameTab, GameTabs

class Tabs:
    """Namespace for game tabs with lazy-loading."""

    combat: Combat
    skills: Skills
    progress: Progress
    inventory: Inventory
    equipment: Equipment
    prayer: Prayer
    magic: Magic
    grouping: Grouping
    friends: Friends
    account: Account
    settings: Settings
    logout: Logout
    emotes: Emotes
    music: Music

    def __init__(self, client) -> None: ...

__all__ = [
    "GameTab",
    "GameTabs",
    "Tabs",
    "Combat",
    "Skills",
    "Progress",
    "Inventory",
    "Equipment",
    "Prayer",
    "Magic",
    "Grouping",
    "Friends",
    "Account",
    "Settings",
    "Logout",
    "Emotes",
    "Music",
]
