"""
Magic tab module.
"""

from shadowlib.client import client
from shadowlib.types.box import Box
from shadowlib.types.gametab import GameTab, GameTabs
from shadowlib.types.widget import Widget, WidgetFields


class Magic(GameTabs):
    """
    Singleton magic tab - displays spellbook and available spells.

    Example:
        from shadowlib.tabs.magic import magic

        magic.open()
    """

    TAB_TYPE = GameTab.MAGIC

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Actual initialization, runs once."""
        GameTabs.__init__(self)

        magicOnClasses = [
            client.SpriteID.Magicon,
            client.SpriteID._2XStandardSpellsOn,
            client.SpriteID.Magicon2,
            client.SpriteID._2XAncientSpellsOn,
            client.SpriteID._2XLunarSpellsOn,
            client.SpriteID.LunarMagicOn,
            client.SpriteID.MagicNecroOn,
            client.SpriteID._2XNecroSpellsOn,
        ]

        magicOffClasses = [
            client.SpriteID.Magicoff,
            client.SpriteID._2XStandardSpellsOff,
            client.SpriteID.Magicoff2,
            client.SpriteID._2XAncientSpellsOff,
            client.SpriteID._2XLunarSpellsOff,
            client.SpriteID.LunarMagicOff,
            client.SpriteID.MagicNecroOff,
            client.SpriteID._2XNecroSpellsOff,
        ]

        self.on_sprites = {
            v for cls in magicOnClasses for v in vars(cls).values() if isinstance(v, int)
        }
        self.off_sprites = {
            v for cls in magicOffClasses for v in vars(cls).values() if isinstance(v, int)
        }

        self.spells = client.InterfaceID.MagicSpellbook

        self._allSpellWidgets = []

        for i in range(
            client.InterfaceID.MagicSpellbook.SPELLLAYER + 1,
            client.InterfaceID.MagicSpellbook.INFOLAYER,
        ):
            w = Widget(i)
            w.enable(WidgetFields.getSpriteId)
            self._allSpellWidgets.append(w)

    def _getInfo(self, spell: int):
        """Get spell info widget by spell ID."""
        w = Widget(spell)
        w.enable(WidgetFields.getBounds)
        w.enable(WidgetFields.isHidden)
        w.enable(WidgetFields.getSpriteId)
        return w.get()

    def _getAllVisibleSprites(self):
        """Get all visible spell sprites."""
        res = Widget.getBatch(self._allSpellWidgets)
        return [w["spriteId"] for w in res]

    def getCastableSpellIds(self):
        vis = self._getAllVisibleSprites()
        return set(vis).intersection(self.on_sprites)

    def _canCastSpell(self, spriteId: int) -> bool:
        """Check if a spell can be cast by its widget ID.

        Args:
            spell (int): The widget ID of the spell to check.
        Returns:
            bool: True if the spell can be cast, False otherwise.
        """
        return spriteId in self.getCastableSpellIds()

    def castSpell(self, spell: int, option: str = "Cast") -> bool:
        """Casts a spell by its widget ID.

        Args:
            spell (int): The widget ID of the spell to cast.

        Returns:
            bool: True if the spell was successfully cast, False otherwise.
        """
        from time import time

        if not self.open():
            return False
        t = time()
        w = self._getInfo(spell)
        print(f"part 1 took {time() - t:.4f}s")
        if self._canCastSpell(w["spriteId"]) and not w["isHidden"]:
            bounds = w["bounds"]
            box = Box(bounds[0], bounds[1], bounds[0] + bounds[2], bounds[1] + bounds[3])
            print(box)
            print(f"part 2 took {time() - t:.4f}s")
            res = box.clickOption(option)
            print(f"part 3 took {time() - t:.4f}s")
            return res

        return False


# Module-level singleton instance
magic = Magic()
