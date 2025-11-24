"""
GameTabs package - contains all game tab modules for OSRS.

Each tab inherits from the base GameTabs class and provides
tab-specific functionality for the Old School RuneScape interface.
"""

from shadowlib.types.gametab import GameTab, GameTabs

# Legacy imports for backwards compatibility
from .account import Account
from .combat import Combat
from .emotes import Emotes
from .equipment import Equipment
from .friends import Friends
from .grouping import Grouping
from .inventory import Inventory
from .logout import Logout
from .magic import Magic
from .music import Music
from .prayer import Prayer
from .progress import Progress
from .settings import Settings
from .skills import Skills


class Tabs:
    """Namespace for game tabs with lazy-loading."""

    _modules = {
        'combat': 'Combat',
        'skills': 'Skills',
        'progress': 'Progress',
        'inventory': 'Inventory',
        'equipment': 'Equipment',
        'prayer': 'Prayer',
        'magic': 'Magic',
        'grouping': 'Grouping',
        'friends': 'Friends',
        'account': 'Account',
        'settings': 'Settings',
        'logout': 'Logout',
        'emotes': 'Emotes',
        'music': 'Music',
    }

    def __init__(self, client):
        """
        Initialize tabs namespace.

        Args:
            client: The Client instance
        """
        self._client = client
        self._cache = {}

    def __getattr__(self, name):
        """Lazy-load tab modules."""
        if name.startswith('_'):
            raise AttributeError(name)

        if name in self._cache:
            return self._cache[name]

        if name not in self._modules:
            raise AttributeError(f"Tabs has no module '{name}'")

        class_name = self._modules[name]
        module_path = f'shadowlib.tabs.{name}'
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)

        instance = cls(client=self._client)
        self._cache[name] = instance
        return instance


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
