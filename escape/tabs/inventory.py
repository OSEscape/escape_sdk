"""
Inventory tab module.
"""

from typing import List

from escape.types.box import Box, createGrid
from escape.types.gametab import GameTab, GameTabs
from escape.types.item import ItemIdentifier
from escape.types.itemcontainer import ItemContainer


class Inventory(GameTabs, ItemContainer):
    """Inventory tab for managing items in the player's backpack."""

    TAB_TYPE = GameTab.INVENTORY  # This tab represents the inventory
    INVENTORY_ID = 93  # RuneLite inventory container ID

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Actual initialization, runs once."""
        # Initialize GameTabs (which sets up tab areas)
        GameTabs.__init__(self)
        # Set ItemContainer attributes directly (can't call __init__ because items is a property)
        self.containerId = self.INVENTORY_ID
        self.slotCount = 28
        self._items = []

        # Create inventory slot grid (4 columns x 7 rows, 28 slots total)
        # Slot 0 starts at (563, 213), each slot is 36x32 pixels with 6px horizontal spacing
        # 2px padding on all sides to avoid misclicks on edges
        self.slots = createGrid(
            startX=563,
            startY=213,
            width=36,
            height=32,
            columns=4,
            rows=7,
            spacingX=6,
            spacingY=4,  # Vertical spacing between rows
            padding=1,  # 2px padding on all sides to avoid edge misclicks
        )

    @property
    def items(self):
        """Auto-sync items from cache when accessed."""
        from escape.client import client

        cached = client.cache.getItemContainer(self.INVENTORY_ID)
        self._items = cached.items
        return self._items

    def getSlotBox(self, slot_index: int) -> Box:
        """Get the Box area for a specific inventory slot."""
        return self.slots[slot_index]

    def hoverSlot(self, slot_index: int) -> bool:
        """Hover over a specific inventory slot (0-27)."""
        if 0 <= slot_index < 28:
            self.slots[slot_index].hover()
            return True
        return False

    def hoverItem(self, identifier: ItemIdentifier) -> bool:
        """Hover over an item by ID or name."""
        from escape.client import client

        found_slots = self.findItemSlots(identifier)
        if not found_slots:
            return False

        # Hover the first found slot
        if self.hoverSlot(found_slots[0]):
            return client.interactions.menu.waitHasOption("Examine")

    def clickSlot(
        self, slot_index: int, option: str | None = None, type: str | None = None
    ) -> bool:
        """Click a specific inventory slot, optionally selecting a menu option."""
        from escape.client import client

        if not self.hoverSlot(slot_index):
            return False

        if option:
            return client.interactions.menu.clickOption(option)
        if type:
            return client.interactions.menu.clickOptionType(type)

        client.input.mouse.leftClick()
        return True

    def clickItem(
        self,
        identifier: ItemIdentifier,
        option: str | None = None,
        type: str | None = None,
    ) -> bool:
        """Click an item by ID or name, optionally selecting a menu option."""
        slot = self.findItemSlot(identifier)
        if slot is None:
            return False

        return self.clickSlot(slot, option=option, type=type)

    def isShiftDropEnabled(self) -> bool:
        """Check if shift-click drop is enabled in game settings."""
        from escape._internal.resources import varps

        varbit_value = varps.getVarbitByName("DESKTOP_SHIFTCLICKDROP_ENABLED")
        return varbit_value == 1

    def waitDropOption(self, timeout: float = 0.5) -> bool:
        """Wait until 'Drop' option appears in menu."""
        import time

        from escape.client import client

        start_time = time.time()

        while time.time() - start_time < timeout:
            if client.interactions.menu.hasOption("Drop"):
                return True
            time.sleep(0.001)  # Small delay before checking again

        return False

    def dropItem(self, identifier: ItemIdentifier, force_shift: bool = False) -> int:
        """Drop all occurrences of an item. Returns count dropped."""
        # Find all slots containing this item
        slots = self.findItemSlots(identifier)
        if not slots:
            return 0

        # Use drop_slots for the actual dropping logic
        return self.dropSlots(slots, force_shift=force_shift)

    def dropItems(self, identifiers: List[ItemIdentifier], force_shift: bool = False) -> int:
        """Drop all occurrences of multiple items. Returns total count dropped."""
        # Collect all slots to drop (all occurrences of all items)
        all_slots = []
        for identifier in identifiers:
            slots = self.findItemSlots(identifier)
            all_slots.extend(slots)

        if not all_slots:
            return 0

        # Use drop_slots for the actual dropping logic
        return self.dropSlots(all_slots, force_shift=force_shift)

    def dropSlots(self, slot_indices: List[int], force_shift: bool = False) -> int:
        """Drop items from specific slot indices. Returns count dropped."""
        from time import sleep

        from escape.client import client

        if not slot_indices:
            return 0

        # Check if shift-drop is enabled or forced
        use_shift_drop = force_shift or self.isShiftDropEnabled()

        dropped_count = 0
        keyboard = client.input.keyboard

        if use_shift_drop:
            # Hold shift for all drops
            keyboard.hold("shift")
            sleep(0.025)

        try:
            for slot_index in slot_indices:
                self.hoverSlot(slot_index)

                if not self.waitDropOption():
                    continue

                if client.interactions.menu.clickOption("Drop"):
                    dropped_count += 1
        finally:
            if use_shift_drop:
                # Always release shift
                keyboard.release("shift")

        return dropped_count

    def selectSlot(self, slot_index: int) -> bool:
        """Select a slot for 'Use item on...' actions."""
        import escape.utilities.timing as timing
        from escape.client import client

        if not (0 <= slot_index < 28):
            return False

        # Click the item to select it
        if not self.hoverSlot(slot_index):
            return False
        if not client.interactions.menu.waitHasType("WIDGET_TARGET"):
            return False
        if client.interactions.menu.clickOptionType("WIDGET_TARGET"):
            return timing.waitUntil(self.isItemSelected, 1, 0.01)

    def isItemSelected(self) -> bool:
        """Check if an item is currently selected."""
        from escape.client import client

        widget = client.cache.getLastSelectedWidget()
        id = widget.get("selected_widget_id", -1)
        return id == client.InterfaceID.Inventory.ITEMS

    def getSelectedItemSlot(self) -> int:
        """Get the slot index of the currently selected item, or -1 if none."""
        from escape.client import client

        widget = client.cache.getLastSelectedWidget()
        selected_index = widget.get("index", -1)
        return selected_index

    def unselectItem(self) -> bool:
        """Unselect the currently selected item."""
        from escape.client import client

        if not self.isItemSelected():
            return True

        # Click outside the inventory to unselect
        client.interactions.menu.clickOptionType("CANCEL")

    def selectItem(self, identifier: ItemIdentifier) -> bool:
        """Select an item by ID or name for 'Use item on...' actions."""
        # Find the slot to click
        target_slot = self.findItemSlot(identifier)

        if target_slot is not None:
            return self.selectSlot(target_slot)
        return False

    def useSlotOnSlot(
        self,
        slot_1: int,
        slot_2: int,
    ) -> bool:
        """Use one inventory slot on another."""
        if self.selectSlot(slot_1):
            return self.clickSlot(slot_2, type="WIDGET_TARGET_ON_WIDGET")

        return False

    def useItemOnItem(self, item_1: ItemIdentifier, item_2: ItemIdentifier) -> bool:
        """Use first item on second item."""
        slot_1 = self.findItemSlot(item_1)
        slot_2 = self.findItemSlot(item_2)

        if slot_1 is not None and slot_2 is not None:
            return self.useSlotOnSlot(slot_1, slot_2)

        return False


# Module-level instance
inventory = Inventory()
