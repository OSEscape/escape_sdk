"""
Grouping tab module (Clan/Group activities).
"""

from escape.client import client
from escape.types.gametab import GameTab, GameTabs
from escape.types.interfaces.general_interface import GeneralInterface
from escape.types.widget import Widget, WidgetFields
from escape.utilities.timing import waitUntil


class Grouping(GameTabs):
    """Grouping tab for clan chat and minigame teleports."""

    TAB_TYPE = GameTab.GROUPING

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Actual initialization, runs once."""
        GameTabs.__init__(self)
        self.sub_tabs = GeneralInterface(
            client.InterfaceID.SIDE_CHANNELS,
            [
                client.InterfaceID.SideChannels.TAB_0,
                client.InterfaceID.SideChannels.TAB_1,
                client.InterfaceID.SideChannels.TAB_2,
                client.InterfaceID.SideChannels.TAB_3,
            ],
            get_children=False,
            use_actions=True,
        )

        for w in self.sub_tabs.buttons:
            w.enable(WidgetFields.getOnOpListener)

        self.sub_tab_names = ["Chat-channel", "Your Clan", "View another clan", "Grouping"]

        self.dropdown_button = GeneralInterface(
            client.InterfaceID.GROUPING,
            [client.InterfaceID.Grouping.CURRENTGAME],
            get_children=False,
        )

        self.dropdown_selector = GeneralInterface(
            client.InterfaceID.GROUPING,
            [client.InterfaceID.Grouping.DROPDOWN_CONTENTS],
            get_children=True,
            menu_text="Select",
            scrollbox=client.InterfaceID.Grouping.DROPDOWN_CONTENTS,
        )

        self.teleport_button = GeneralInterface(
            client.InterfaceID.GROUPING,
            [client.InterfaceID.Grouping.TELEPORT_TEXT1],
            get_children=False,
            menu_text="Teleport",
        )

    def getOpenSubTab(self) -> str | None:
        """Get the currently open sub-tab within the grouping tab.

        Returns:
            str | None: The name of the open sub-tab, or None if none are open.
        """
        if not self.open():
            return None

        info = self.sub_tabs.getWidgetInfo()

        for i, w in enumerate(info):
            if len(w.get("onOpListener", [])) == 3:
                return self.sub_tab_names[i]
        return None

    def openSubTab(self, sub_tab: str) -> bool:
        """Open a specific sub-tab within the grouping tab.

        Args:
            sub_tab (str): The sub-tab substring to open.
        Returns:
            bool: True if the sub-tab was opened successfully, False otherwise.
        """
        if not self.isOpen():
            self.open()

        for name in self.sub_tab_names:
            if sub_tab.lower() in name.lower():
                if self.getOpenSubTab() == name:
                    return True
                else:
                    if self.sub_tabs.interact(sub_tab):
                        return waitUntil(lambda: self.getOpenSubTab() == name, timeout=3.0)
        return False

    def getSelectedGame(self) -> str | None:
        """Get the currently selected game from the grouping dropdown.

        Returns:
            str | None: The name of the selected game, or None if not found.
        """
        if not self.open() and not self.openSubTab("Grouping"):
            return None

        info = self.dropdown_button.getWidgetInfo()
        if not info:
            return None
        text = info[0].get("text", "")
        return text if text else None

    def isGameSelected(self, game_name: str) -> bool:
        selected_game = self.getSelectedGame()
        return selected_game is not None and game_name.lower() in selected_game.lower()

    def dropdownFullyLoaded(self) -> bool:
        info = self.dropdown_selector.getWidgetInfo()
        return len(info) > 0 and info[-1].get("bounds")[0] >= 0

    def selectGame(self, game_name: str) -> bool:
        """Select a game from the grouping dropdown.

        Args:
            game_name (str): The name of the game to select.
        Returns:
            bool: True if the game was selected successfully, False otherwise.
        """
        if not self.open() or not self.openSubTab("Group"):
            return False

        current_game = self.getSelectedGame()
        if current_game and game_name.lower() in current_game.lower():
            return True  # Already selected

        if len(self.dropdown_selector.getWidgetInfo()) == 0:
            if not self.dropdown_button.interact("") or not waitUntil(
                self.dropdownFullyLoaded, timeout=3.0
            ):
                return False
        if self.dropdown_selector.interact(game_name):
            return waitUntil(lambda: self.isGameSelected(game_name), timeout=3.0)

        return False

    def clickTeleport(self) -> bool:
        """Click the teleport button in the grouping tab.

        Returns:
            bool: True if the teleport action was successful, False otherwise.
        """
        if not self.open() or not self.openSubTab("Group"):
            return False

        return bool(self.teleport_button.interact("Teleport"))

    def teleportToMinigame(self, game_name: str) -> bool:
        """Teleport to a specific minigame via the grouping tab.

        Args:
            game_name (str): The name of the minigame to teleport to.
        Returns:
            bool: True if the teleport action was successful, False otherwise.
        """
        if not self.selectGame(game_name):
            return False

        return self.clickTeleport()


# Module-level instance
grouping = Grouping()
