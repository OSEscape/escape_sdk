"""
Prayer tab module.
"""

from enum import Enum

from escape.client import client
from escape.types.gametab import GameTab, GameTabs
from escape.types.interfaces.buttons import Buttons
from escape.utilities.timing import sleep, waitTicks, waitUntil


class PrayerType(Enum):
    """Enumeration of prayer types."""

    THICK_SKIN = 0
    BURST_OF_STRENGTH = 1
    CLARITY_OF_THOUGHT = 2
    ROCK_EYE = 3
    SUPERHUMAN_STRENGTH = 4
    IMPROVED_REFLEXES = 5
    RAPID_RESTORE = 6
    RAPID_HEAL = 7
    PROTECT_ITEM = 8
    STEEL_SKIN = 9
    ULTIMATE_STRENGTH = 10
    INCREDIBLE_REFLEXES = 11
    PROTECT_FROM_MAGIC = 12
    PROTECT_FROM_MISSILES = 13
    PROTECT_FROM_MELEE = 14
    RETRIBUTION = 15
    REDEMPTION = 16
    SMITE = 17
    SHARP_EYE = 18
    MYSTIC_WILL = 19
    HAWK_EYE = 20
    MYSTIC_LORE = 21
    EAGLE_EYE = 22
    MYSTIC_MIGHT = 23
    RIGOUR = 24
    CHIVALRY = 25
    PIETY = 26
    AUGURY = 27
    PRESERVE = 28


class Prayer(GameTabs):
    """
    Singleton prayer tab - displays available prayers and prayer points.

    Example:
        from escape.tabs.prayer import prayer

        prayer.open()
    """

    TAB_TYPE = GameTab.PRAYER

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Actual initialization, runs once."""
        GameTabs.__init__(self)
        self.prayer_buttons = Buttons(
            client.InterfaceID.PRAYERBOOK,
            [
                client.InterfaceID.Prayerbook.PRAYER1,
                client.InterfaceID.Prayerbook.PRAYER2,
                client.InterfaceID.Prayerbook.PRAYER3,
                client.InterfaceID.Prayerbook.PRAYER4,
                client.InterfaceID.Prayerbook.PRAYER5,
                client.InterfaceID.Prayerbook.PRAYER6,
                client.InterfaceID.Prayerbook.PRAYER7,
                client.InterfaceID.Prayerbook.PRAYER8,
                client.InterfaceID.Prayerbook.PRAYER9,
                client.InterfaceID.Prayerbook.PRAYER10,
                client.InterfaceID.Prayerbook.PRAYER11,
                client.InterfaceID.Prayerbook.PRAYER12,
                client.InterfaceID.Prayerbook.PRAYER13,
                client.InterfaceID.Prayerbook.PRAYER14,
                client.InterfaceID.Prayerbook.PRAYER15,
                client.InterfaceID.Prayerbook.PRAYER16,
                client.InterfaceID.Prayerbook.PRAYER17,
                client.InterfaceID.Prayerbook.PRAYER18,
                client.InterfaceID.Prayerbook.PRAYER19,
                client.InterfaceID.Prayerbook.PRAYER20,
                client.InterfaceID.Prayerbook.PRAYER21,
                client.InterfaceID.Prayerbook.PRAYER22,
                client.InterfaceID.Prayerbook.PRAYER23,
                client.InterfaceID.Prayerbook.PRAYER24,
                client.InterfaceID.Prayerbook.PRAYER25,
                client.InterfaceID.Prayerbook.PRAYER26,
                client.InterfaceID.Prayerbook.PRAYER27,
                client.InterfaceID.Prayerbook.PRAYER28,
                client.InterfaceID.Prayerbook.PRAYER29,
            ],
            [
                "Thick Skin",
                "Burst of Strength",
                "Clarity of Thought",
                "Rock Skin",
                "Superhuman Strength",
                "Improved Reflexes",
                "Rapid Restore",
                "Rapid Heal",
                "Protect Item",
                "Steel Skin",
                "Ultimate Strength",
                "Incredible Reflexes",
                "Protect from Magic",
                "Protect from Missiles",
                "Protect from Melee",
                "Retribution",
                "Redemption",
                "Smite",
                "Sharp Eye",
                "Mystic Will",
                "Hawk Eye",
                "Mystic Lore",
                "Eagle Eye",
                "Mystic Might",
                "Rigour",
                "Chivalry",
                "Piety",
                "Augury",
                "Preserve",
            ],
        )

        self.quickprayer_orb = Buttons(
            client.InterfaceID.ORBS, [client.InterfaceID.Orbs.PRAYERBUTTON], ["Quick-prayers"]
        )

        self.close_quickprayer_button = Buttons(
            client.InterfaceID.QUICKPRAYER, [client.InterfaceID.Quickprayer.CLOSE], ["Done"]
        )

    def getActivePrayerVarbit(self) -> int | None:
        """
        Get the varp value representing active prayers.

        Returns:
            Integer bitmask of active prayers, or None if unavailable
        """
        return client.resources.varps.getVarbitByName("PRAYER_ALLACTIVE")

    def getQuickPrayerVarbit(self) -> int | None:
        """
        Get the varp value representing active quick-prayers.

        Returns:
            Integer bitmask of active quick-prayers, or None if unavailable
        """
        return client.resources.varps.getVarbitByName("QUICKPRAYER_SELECTED")

    def isPrayerActive(self, prayer: PrayerType) -> bool | None:
        """
        Check if a specific prayer is active.

        Args:
            prayer: The PrayerType enum value to check
        Returns:
            True if the prayer is active, False if not, or None if unavailable
        """
        varbit_value = self.getActivePrayerVarbit()
        if varbit_value is None:
            return None
        prayer_bit = 1 << Prayer.value
        return (varbit_value & prayer_bit) != 0

    @property
    def active_prayers(self) -> list[PrayerType] | None:
        """
        Get a dictionary of all prayers and their active status.

        Returns:
            Dict mapping PrayerType to bool (True if active), or None if unavailable
        """
        varbit_value = self.getActivePrayerVarbit()
        if varbit_value is None:
            return None
        result = []
        for prayer in PrayerType:
            prayer_bit = 1 << prayer.value
            if (varbit_value & prayer_bit) != 0:
                result.append(prayer)
        return result

    def activate(self, prayer: PrayerType, safe: bool = True) -> bool:
        """
        Activate a specific prayer via the interface.

        Args:
            prayer: The PrayerType enum value to activate
        Returns:
            True if the interaction was successful, False otherwise
        """
        if not self.open():
            return False

        if not self.isPrayerActive(prayer) or not safe:
            return self.prayer_buttons.interact(self.prayer_buttons.names[prayer.value])
        return True

    def deactivate(self, prayer: PrayerType) -> bool:
        """
        Deactivate a specific prayer via the interface.

        Args:
            prayer: The PrayerType enum value to deactivate
        Returns:
            True if the interaction was successful, False otherwise
        """
        if not self.open():
            return False

        if self.isPrayerActive(prayer):
            return self.prayer_buttons.interact(self.prayer_buttons.names[prayer.value])
        return True

    def getPrayerPoints(self) -> int | None:
        """
        Get the current prayer points.

        Returns:
            Integer prayer points, or None if unavailable
        """
        return client.tabs.skills.getLevel("Prayer")

    @property
    def selected_quick_prayers(self) -> list[PrayerType] | None:
        """
        Get a list of active quick-prayers.

        Returns:
            List of PrayerType enums that are active as quick-prayers, or None if unavailable
        """
        varbit_value = self.getQuickPrayerVarbit()
        if varbit_value is None:
            return None
        result = []
        for prayer in PrayerType:
            prayer_bit = 1 << prayer.value
            if (varbit_value & prayer_bit) != 0:
                result.append(prayer)
        return result

    def isQuickPrayerActive(self) -> bool | None:
        """
        Check if quick-prayers are active.

        Returns:
            True if quick-prayers are active, False if not, or None if unavailable
        """
        varbit_value = client.resources.varps.getVarbitByName("QUICKPRAYER_ACTIVE")
        if varbit_value is None:
            return None
        return varbit_value == 1

    def activateQuickPrayer(self) -> bool:
        """
        Activate quick-prayers via the orb.

        Returns:
            True if the interaction was successful, False otherwise
        """
        if not self.open():
            return False

        if not self.isQuickPrayerActive():
            return self.quickprayer_orb.interact("Quick-prayers")
        return True

    def deactivateQuickPrayer(self) -> bool:
        """
        Deactivate quick-prayers via the orb.

        Returns:
            True if the interaction was successful, False otherwise
        """
        if not self.open():
            return False

        if self.isQuickPrayerActive():
            return self.quickprayer_orb.interact("Quick-prayers")
        return True

    def isQuickPrayerSetupOpen(self) -> bool:
        """
        Check if the quick-prayer setup interface is open.

        Returns:
            True if the quick-prayer setup interface is open, False otherwise
        """
        return client.InterfaceID.QUICKPRAYER in client.interfaces.getOpenInterfaces()

    def openQuickPrayerSetup(self) -> bool:
        """
        Open the quick-prayer setup interface.

        Returns:
            True if the interaction was successful, False otherwise
        """
        if client.InterfaceID.QUICKPRAYER in client.interfaces.getOpenInterfaces():
            return True

        if self.quickprayer_orb.interact(menu_option="Setup"):
            if not waitUntil(self.isQuickPrayerSetupOpen, timeout=3.0):
                raise TimeoutError("Timed out waiting for quick-prayer setup interface to open.")
            return True
        return False

    def closeQuickPrayerSetup(self) -> bool:
        """
        Close the quick-prayer setup interface.

        Returns:
            True if the interaction was successful, False otherwise
        """
        if not self.isQuickPrayerSetupOpen():
            return True

        if self.close_quickprayer_button.interact("Done"):
            if not waitUntil(lambda: not self.isQuickPrayerSetupOpen(), timeout=3.0):
                raise TimeoutError("Timed out waiting for quick-prayer setup interface to close.")
            return True
        return False

    def configureQuickPrayers(self, prayers: list[PrayerType]) -> bool:
        """
        Configure the quick-prayer setup with the specified prayers.

        Args:
            prayers: List of PrayerType enums to set as quick-prayers
        Returns:
            True if the configuration was successful, False otherwise
        """
        if not self.prayer_buttons.is_ready:
            if self.isQuickPrayerSetupOpen():
                self.closeQuickPrayerSetup()
            self.prayer_buttons.setBoxes()
        if not self.openQuickPrayerSetup():
            return False

        current_quick_prayers = set(self.selected_quick_prayers)
        prayer_set = set(prayers)

        should_activate = prayer_set.difference(current_quick_prayers)
        should_deactivate = current_quick_prayers.difference(prayer_set)

        # Deactivate prayers not in the desired set
        for prayer in should_deactivate:
            if not self.prayer_buttons.interact(self.prayer_buttons.names[prayer.value]):
                return False
        if should_deactivate:
            waitTicks(1)  # Wait for interface to update
        # Activate prayers in the desired set
        for prayer in should_activate:
            if not self.prayer_buttons.interact(self.prayer_buttons.names[prayer.value]):
                return False
        if should_activate:
            waitTicks(1)  # Wait for interface to update

        return self.closeQuickPrayerSetup() and set(self.selected_quick_prayers) == prayer_set


# Module-level singleton instance
prayer = Prayer()
