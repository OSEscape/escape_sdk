"""
Magic tab module.
"""

from escape._internal.logger import logger
from escape.client import client
from escape.types.box import Box
from escape.types.gametab import GameTab, GameTabs
from escape.types.widget import Widget, WidgetFields


class Magic(GameTabs):
    """Magic tab for viewing and casting spells."""

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

        magic_on_classes = [
            client.SpriteID.Magicon,
            client.SpriteID._2XStandardSpellsOn,
            client.SpriteID.Magicon2,
            client.SpriteID._2XAncientSpellsOn,
            client.SpriteID._2XLunarSpellsOn,
            client.SpriteID.LunarMagicOn,
            client.SpriteID.MagicNecroOn,
            client.SpriteID._2XNecroSpellsOn,
        ]

        magic_off_classes = [
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
            v for cls in magic_on_classes for v in vars(cls).values() if isinstance(v, int)
        }
        self.off_sprites = {
            v for cls in magic_off_classes for v in vars(cls).values() if isinstance(v, int)
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

    def _get_info(self, spell: int):
        """Get spell info widget by spell ID."""
        w = Widget(spell)
        w.enable(WidgetFields.getBounds)
        w.enable(WidgetFields.isHidden)
        w.enable(WidgetFields.getSpriteId)
        return w.get()

    def _get_all_visible_sprites(self):
        """Get all visible spell sprites."""
        res = Widget.getBatch(self._allSpellWidgets)
        return [w["spriteId"] for w in res]

    def get_castable_spell_ids(self):
        vis = self._get_all_visible_sprites()
        return set(vis).intersection(self.on_sprites)

    def _can_cast_spell(self, sprite_id: int) -> bool:
        """Check if a spell can be cast by its widget ID.

        Args:
            spell (int): The widget ID of the spell to check.
        Returns:
            bool: True if the spell can be cast, False otherwise.
        """
        return sprite_id in self.get_castable_spell_ids()

    def cast_spell(self, spell: int, option: str = "Cast") -> bool:
        """Cast a spell by its widget ID."""
        from time import time

        if not self.open():
            return False
        t = time()
        w = self._get_info(spell)
        logger.info(f"part 1 took {time() - t:.4f}s")
        if self._can_cast_spell(w["spriteId"]) and not w["isHidden"]:
            bounds = w["bounds"]
            box = Box(bounds[0], bounds[1], bounds[0] + bounds[2], bounds[1] + bounds[3])
            print(box)
            logger.info(f"part 2 took {time() - t:.4f}s")
            res = box.clickOption(option)
            logger.info(f"part 3 took {time() - t:.4f}s")
            return res

        return False


# Module-level instance
magic = Magic()
